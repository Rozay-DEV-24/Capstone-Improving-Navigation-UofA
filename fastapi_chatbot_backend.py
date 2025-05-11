from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import json
import re
import difflib
from pathlib import Path
import pandas as pd

from dotenv import load_dotenv
from models.llama_vision import query_vision_llm
from geo_api.ocr_utils import extract_text_from_image, extract_address_from_text, extract_building_info
from geo_api.osm_helper import geocode_address, get_nearby_places
from geo_api.route_api import get_osm_route
from geo_api.accessibility_helper import get_accessibility_info
from models.text_llm_helper import query_text_llm
from geo_api.route_api import get_ramp_destination_coords


load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("static/homepage.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

session_state = {
    "image_path": "",
    "address": "",
    "building_name": "",
    "building_number": "",
    "location": None,
    "nearby": []
}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    os.makedirs("data", exist_ok=True)
    path = "data/uploaded_map.png"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    session_state["image_path"] = path
    ocr_text = extract_text_from_image(path)
    print("[DEBUG] Raw OCR text:\n", ocr_text)

    address = extract_address_from_text(ocr_text)
    if not address:
        return JSONResponse(status_code=400, content={"error": "Address not found in image."})
    session_state["address"] = address

    building_name, building_number = extract_building_info(ocr_text)
    building_name = building_name.strip() if building_name else ""
    building_number = building_number.strip() if building_number else ""

    df = pd.read_csv("data/buildings.csv")

    def fuzzy_match_csv(name, number, addr):
        name = name.lower()
        addr = addr.lower() if addr else ""
        names = df["Name"].str.lower().tolist()
        match_names = difflib.get_close_matches(name, names, n=1, cutoff=0.6)
        if match_names:
            row = df[df["Name"].str.lower() == match_names[0]]
            return "name", row.iloc[0]
        row = df[df["Number"].astype(str).str.strip() == number]
        if not row.empty:
            return "number", row.iloc[0]
        addresses = df["Address"].str.lower().tolist()
        match_addresses = difflib.get_close_matches(addr, addresses, n=1, cutoff=0.6)
        if match_addresses:
            row = df[df["Address"].str.lower() == match_addresses[0]]
            return "address", row.iloc[0]
        return None, None

    match_source, row = fuzzy_match_csv(building_name, building_number, address)

    if row is not None:
        session_state["building_name"] = row["Name"]
        session_state["building_number"] = str(row["Number"])
        session_state["address"] = row["Address"]
        print(f"[MATCHED via {match_source.upper()}]:", row.to_dict())
    else:
        fallback_prompt = """
        You are a helpful assistant. From this map screenshot popup, extract:
        - Building Name
        - Building Number

        Format your response exactly as:
        Name: <building name>
        Number: <building number>
        """
        try:
            fallback_result = query_vision_llm(path, fallback_prompt)
            print("[LLM Fallback] Response:\n", fallback_result)

            match_name = re.search(r"Name:\s*(.+)", fallback_result)
            match_number = re.search(r"Number:\s*(\d+)", fallback_result)

            if match_name:
                session_state["building_name"] = match_name.group(1).strip()
            if match_number:
                session_state["building_number"] = match_number.group(1).strip()
        except Exception as e:
            print("[ERROR] Fallback LLM failed:", e)
            session_state["building_name"] = "Unknown"

    if not session_state["building_number"]:
        session_state["building_number"] = "N/A"

    location = geocode_address(session_state["address"])
    if not location:
        return JSONResponse(status_code=400, content={"error": "Failed to geocode address."})

    session_state["location"] = location
    session_state["nearby"] = get_nearby_places(location["lat"], location["lon"])

    return {
        "building_name": session_state["building_name"],
        "building_number": session_state["building_number"],
        "address": session_state["address"],
        "nearby": session_state["nearby"],
        "match_source": match_source if row is not None else "llm_fallback",
        "matched_row": row.to_dict() if row is not None else None
    }

@app.post("/manual_start")
async def manual_start(request: Request):
    body = await request.json()
    user_input = body.get("building_name", "").strip().lower()

    df = pd.read_csv("data/buildings.csv")

    # Fuzzy match by name
    matched = df[df["Name"].str.lower().str.contains(user_input)]
    if matched.empty:
        return JSONResponse(status_code=404, content={"error": "Building not found in CSV."})

    row = matched.iloc[0]
    building_name = row["Name"]
    building_number = str(row["Number"])
    address = row["Address"]

    # ✅ Use address → geocode for location
    location = geocode_address(address)
    if not location:
        return JSONResponse(status_code=400, content={"error": f"Could not geocode address: {address}."})

    session_state.update({
        "building_name": building_name,
        "building_number": building_number,
        "address": address,
        "location": location,
        "image_path": None,
        "nearby": get_nearby_places(location["lat"], location["lon"])
    })

    return {
        "building_name": building_name,
        "building_number": building_number,
        "address": address,
        "nearby": session_state["nearby"]
    }

@app.get("/nearby")
async def get_nearby():
    return {"nearby": session_state["nearby"]}

@app.post("/directions")
async def directions(request: Request):
    body = await request.json()
    building_name = body.get("building_name")
    accessibility_enabled = body.get("accessibility", False)

    matched = max(
        session_state["nearby"],
        key=lambda b: difflib.SequenceMatcher(None, b["name"].lower(), building_name.lower()).ratio(),
        default=None
    )
    if not matched:
        return {
            "directions": [],
            "llm_response": f"Could not find {building_name} in nearby buildings."
        }

    # Use ramp coordinates if accessibility is enabled
    if accessibility_enabled:
        ramp_coords = get_ramp_destination_coords(matched["name"])
        destination = ramp_coords if ramp_coords else {"lat": matched["lat"], "lon": matched["lon"]}
    else:
        destination = {"lat": matched["lat"], "lon": matched["lon"]}

    directions = get_osm_route(session_state["location"], destination)
    directions = [step for step in directions if not step.startswith("[")]

    accessibility_info = {}
    if accessibility_enabled:
        accessibility_info = get_accessibility_info(matched["name"])

    if directions:
        return {
            "directions": directions,
            "llm_response": "",
            "accessibility": accessibility_info
        }
    elif session_state["image_path"]:
        prompt = f"""
        You are a helpful assistant.
        The user is currently at: {session_state['building_name']} (Building {session_state['building_number']}), {session_state['address']}.
        They are trying to reach: {matched['name']} nearby.

        Since routing data is unavailable, try to provide visual navigation help by describing:
        - What's nearby or between the two buildings
        - What's on the left, right, or opposite if visible in the image
        - General navigation assistance if possible
        Only respond with the step-by-step navigation instructions starting from the heading 'Navigate to...'. Omit introductions or summaries.
        """
        llm_response = query_vision_llm(session_state["image_path"], prompt, matched["name"])
        lines = llm_response.strip().splitlines()
        trimmed = "\n".join([line for line in lines if line.strip()])

        return {
            "directions": [],
            "llm_response": trimmed,
            "accessibility": accessibility_info
        }
    else:
        text_prompt = f"""
            You are a helpful campus navigation assistant. The user is currently at:
            **{session_state['building_name']}** (Building {session_state['building_number']}), **{session_state['address']}**.
            They want to walk to **{matched['name']}** nearby.

            Since map routing failed, provide a **step-by-step walking guide**:
            - Break your response into clear, short steps (1, 2, 3, ...)
            - Use approximate directions (left, right, north, etc.)
            - Mention landmarks if helpful
            - Keep it concise and easy to follow

            Start directly with the numbered list.
        """
        text_response = query_text_llm(text_prompt, matched["name"])

        return {
            "directions": [],
            "llm_response": text_response.strip(),
            "accessibility": accessibility_info
        }

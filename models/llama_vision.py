import base64
import os
import requests
from dotenv import load_dotenv
from geo_api.ramp_coordinates import RAMP_COORDS  # Import ramp data

load_dotenv()

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"

def get_ramp_name(building_name):
    ramps = RAMP_COORDS.get(building_name)
    if ramps:
        return next(iter(ramps.keys()))  # Return first ramp name
    return None

def query_vision_llm(image_path, user_prompt, building_name=None):
    url = os.environ["LLM_BASE"] + "/v1/chat/completions"
    token = os.environ["OPENAI_API_KEY"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    ramp_name = get_ramp_name(building_name) if building_name else None

    if ramp_name:
        user_prompt += f"\n\nPlease guide the user to the ramp entrance labeled: '{ramp_name}'. Avoid describing main entrances if ramps are available."
    else:
        user_prompt += "\n\nGuide the user to the building entrance."

    image_b64 = encode_image_to_base64(image_path)

    payload = {
        "model": "Llama-3.2-11B-Vision-Instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that analyzes campus maps."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_b64}}
                ]
            }
        ],
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("[ERROR] LLM API returned:", response.status_code)
        print("[DEBUG] Response text:", response.text)
        return "Sorry, I couldn't generate a description due to an API issue."

    try:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("[ERROR] Failed to parse LLM JSON:", e)
        print("[DEBUG] Response content:", response.content)
        return "Sorry, the LLM response couldn't be processed."

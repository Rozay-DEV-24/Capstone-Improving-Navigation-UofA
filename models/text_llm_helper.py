import os
import requests
from dotenv import load_dotenv
from geo_api.ramp_coordinates import RAMP_COORDS

load_dotenv()

def get_ramp_name(building_name):
    ramps = RAMP_COORDS.get(building_name)
    if ramps:
        return next(iter(ramps.keys()))
    return None

def query_text_llm(prompt: str, building_name: str = None) -> str:
    url = os.environ["LLM_BASE"] + "/v1/chat/completions"
    token = os.environ["OPENAI_API_KEY"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Add ramp detail if available
    ramp_name = get_ramp_name(building_name) if building_name else None

    system_prompt = (
        "You are a highly detailed campus navigation assistant. "
        "Always give step-by-step, realistic walking directions between two buildings, including turn-by-turn movements, approximate distances, and specific landmarks. "
        "Use accessible paths only. If a ramp is known, guide the user explicitly to it."
    )

    if ramp_name:
        prompt += (
            f"\n\nBe sure to guide the user to the accessible ramp: '{ramp_name}', "
            f"and mention nearby landmarks or orientation hints (e.g., 'next to Starbucks', 'adjacent to the south entrance')."
        )
    else:
        prompt += "\n\nGuide to the main entrance if no ramp is known."

    payload = {
        "model": "anvilgpt/gemma:latest",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("[ERROR] Text LLM API returned:", response.status_code)
        print("[DEBUG] Response text:", response.text)
        return "I couldn't process your request due to an API error."

    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("[ERROR] Failed to parse text LLM response:", e)
        return "There was a problem parsing the LLM response."

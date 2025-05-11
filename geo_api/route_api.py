import requests
from geo_api.ramp_coordinates import RAMP_COORDS

def get_ramp_destination_coords(building_name):
    ramps = RAMP_COORDS.get(building_name)
    if ramps:
        first_ramp = next(iter(ramps.values()))  # get first available ramp
        return first_ramp
    return None


def get_osm_route(start_coords, end_coords, profile="walking"):
    # ❌ No snapping, use raw coordinates
    print("[DEBUG] Start Coords:", start_coords)
    print("[DEBUG] End Coords:", end_coords)

    base_url = "https://router.project-osrm.org/route/v1"
    coords = f"{start_coords['lon']},{start_coords['lat']};{end_coords['lon']},{end_coords['lat']}"
    url = f"{base_url}/{profile}/{coords}?overview=full&steps=true"

    print("[DEBUG] Routing URL:", url)

    try:
        response = requests.get(url)

        if response.status_code != 200 or not response.content:
            print("[ERROR] OSRM response error:", response.status_code)
            return ["[Route unavailable]"]

        data = response.json()

        if "routes" not in data or not data["routes"]:
            print("[ERROR] No routes found in OSRM response.")
            return ["[Route unavailable]"]

        steps = data["routes"][0]["legs"][0]["steps"]
        directions = []

        for step in steps:
            instruction = step.get("maneuver", {}).get("instruction")
            if instruction:
                directions.append(instruction)
            else:
                directions.append("[Step missing instruction]")

        return directions

    except Exception as e:
        print("[ERROR] Failed to fetch route:", e)
        return ["[Routing failed due to exception]"]

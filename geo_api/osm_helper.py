import pandas as pd
from math import radians, cos, sin, sqrt, atan2

CSV_PATH = "data/buildings.csv"  # ensure path is correct

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of Earth in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def geocode_address(address):
    df = pd.read_csv(CSV_PATH)
    match = df[df["Address"].str.lower().str.contains(address.lower())]
    if not match.empty:
        row = match.iloc[0]
        return {
            "lat": float(row["Latitude"]),
            "lon": float(row["Longitude"])
        }
    return None

def get_nearby_places(center_lat, center_lon, radius_m=200):
    df = pd.read_csv(CSV_PATH)
    nearby = []

    for _, row in df.iterrows():
        try:
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
            dist = haversine(center_lat, center_lon, lat, lon)
            if dist <= radius_m:
                nearby.append({
                    "name": row["Name"],
                    "lat": lat,
                    "lon": lon,
                    "address": row["Address"],
                    "building_number": str(row["Number"]),
                    "distance": round(dist, 2)
                })
        except:
            continue

    return sorted(nearby, key=lambda x: x["distance"])

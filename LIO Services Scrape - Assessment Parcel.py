import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# Define the API details
url = "https://ws.lioservices.lrc.gov.on.ca/arcgis4/rest/services/AIA/Assessment_Parcel_Map/MapServer/identify?"
headers = {
    "User-Agent": "Mozilla/5.0",
    # Add other necessary headers here
}
token = "923_MS1mM6bQ9d-ReA9qleKYOHlqrpBhtQNMDCmAX8iPDemZVCZ2LrLwhrDm4uAd"  # Replace with your token. Use the Inspect tool when visiting the Agricultural Information Atlas (AgMaps)

ward = ["Tiles/Alta Vista.csv","Alta Vista"]
ward = ["Tiles/Barrhaven East.csv","Barrhaven East"]
ward = ["Tiles/Barrhaven West.csv","Barrhaven West"]
ward = ["Tiles/Bay.csv","Bay"]
ward = ["Tiles/Beacan Hill-Cyrville.csv","Beacan Hill-Cyrville"]
ward = ["Tiles/Capital.csv","Capital"]
ward = ["Tiles/College.csv","College"]
ward = ["Tiles/Gloucester-Southgate.csv","Gloucester-Southgate"]
ward = ["Tiles/Kanata North.csv","Kanata North"]
ward = ["Tiles/Kanata South.csv","Kanata South"]
ward = ["Tiles/Kichissippi.csv","Kichissippi"]
ward = ["Tiles/Knoxdale-Merivale.csv","Knoxdale-Merivale"]
ward = ["Tiles/Orleans East-Cumberland.csv","Orleans East-Cumberland"]
ward = ["Tiles/Orleans East-Cumberland.csv","Orleans East-Cumberland - Becketts Creek"]
ward = ["Tiles/Orleans South-Navan.csv","Orleans South-Navan"]
ward = ["Tiles/Orleans West-Innes.csv","Orleans West-Innes"]
ward = ["Tiles/Osgood.csv","Osgood"] #over 1000 tiles.
ward = ["Tiles/Osgood_2500.csv","Osgood"]
ward = ["Tiles/Rideau-Jock.csv","Rideau-Jock"] #over 1500 tiles
ward = ["Tiles/Rideau-Jock_2500.csv","Rideau-Jock"]
ward = ["Tiles/Rideau-Rockliffe.csv","Rideau-Rockliffe"]
ward = ["Tiles/Rideau-Vanier.csv","Rideau-Vanier"]
ward = ["Tiles/River.csv","River"]
ward = ["Tiles/Riverside South-Findlay Creek.csv","Riverside South-Findlay Creek"]
ward = ["Tiles/Sommerset.csv","Sommerset"]
ward = ["Tiles/Stittsville.csv","Stittsville"]
ward = ["Tiles/West Carleton-March.csv","West Carleton-March"] #over 1500 tiles
ward = ["Tiles/West Carleton-March_2500.csv","West Carleton-March"] 

tiles = pd.read_csv(
    ward[0],
    usecols=["fid", "id", "left", "top", "right", "bottom"]
).to_records(index=False)

all_results = []

for i, tile in enumerate(tiles, start=1):
    fid, tile_id, left, top, right, bottom = tile

    # ArcGIS envelope should be xmin, ymin, xmax, ymax
    geometry = {
        "xmin": float(left),
        "ymin": float(bottom),
        "xmax": float(right),
        "ymax": float(top)
    }

    query_params = {
        "f": "json",
        "token": token,
        "geometry": str(geometry).replace("'", '"'),
        "geometryType": "esriGeometryEnvelope",
        "sr": "3857",              # change if your tile coords are in a different CRS
        "mapExtent": f"{left},{bottom},{right},{top}",
        "imageDisplay": "932,521,96",
        "tolerance": 0,
        "returnGeometry": "true",
        "layers": "all:0"
    }

    try:
        response = requests.get(url, headers=headers, params=query_params, timeout=30)
        response.raise_for_status()
        data = response.json()

        #print(data)

        if "error" in data:
            print(f"{i}/{len(tiles)} ERROR for tile {tile_id}: {data['error']}")
            continue

        results = data.get("results", [])
        if results:
            all_results.extend(results)
            print(f"{i}/{len(tiles)} results={len(results)} tile={tile_id}")
        else:
            print(f"{i}/{len(tiles)} no results tile={tile_id}")

    except requests.exceptions.RequestException as e:
        print(f"{i}/{len(tiles)} request error for tile {tile_id}: {e}")
    except ValueError as e:
        print(f"{i}/{len(tiles)} JSON parse error for tile {tile_id}: {e}")

df = pd.json_normalize(all_results)

output_dir = Path("Output/Assessment Roll Raw")
output_dir.mkdir(parents=True, exist_ok=True)

filename = output_dir / f"AssessmentParcel_{ward[1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(filename, index=False)

print(f"CSV saved to '{filename}'")
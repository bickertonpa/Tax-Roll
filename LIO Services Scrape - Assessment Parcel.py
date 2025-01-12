import requests
import pandas as pd
from datetime import datetime

# Define the API details
url = "https://ws.lioservices.lrc.gov.on.ca/arcgis4/rest/services/AIA/Assessment_Parcel_Map/MapServer/identify"
headers = {
    "User-Agent": "Mozilla/5.0",
    # Add other necessary headers here
}
token = "923_MS1mM6bQ9d-ReA9qld6QbfSx-gFMm6ps8de6UTrV6fKfTBCbf_Z0SHw4xbzQ"  # Replace with your token

##ward = ["Tiles/Alta Vista.csv","Alta Vista"]
##ward = ["Tiles/Barrhaven East.csv","Barrhaven East"]
##ward = ["Tiles/Barrhaven West.csv","Barrhaven West"]
##ward = ["Tiles/Bay.csv","Bay"]
##ward = ["Tiles/Beacan Hill-Cyrville.csv","Beacan Hill-Cyrville"]
##ward = ["Tiles/Capital.csv","Capital"]
##ward = ["Tiles/College.csv","College"]
##ward = ["Tiles/Gloucester-Southgate.csv","Gloucester-Southgate"]
##ward = ["Tiles/Kanata North.csv","Kanata North"]
##ward = ["Tiles/Kanata South.csv","Kanata South"]
##ward = ["Tiles/Kichissippi.csv","Kichissippi"]
##ward = ["Tiles/Knoxdale-Merivale.csv","Knoxdale-Merivale"]
##ward = ["Tiles/Orleans East-Cumberland.csv","Orleans East-Cumberland"]
ward = ["Tiles/Orleans East-Cumberland.csv","Orleans East-Cumberland - Becketts Creek"]
##ward = ["Tiles/Orleans South-Navan.csv","Orleans South-Navan"]
##ward = ["Tiles/Orleans West-Innes.csv","Orleans West-Innes"]
##ward = ["Tiles/Osgood.csv","Osgood"] #over 1000 tiles.
##ward = ["Tiles/Osgood_2500.csv","Osgood"]
##ward = ["Tiles/Rideau-Jock.csv","Rideau-Jock"] #over 1500 tiles
##ward = ["Tiles/Rideau-Jock_2500.csv","Rideau-Jock"]
##ward = ["Tiles/Rideau-Rockliffe.csv","Rideau-Rockliffe"]
##ward = ["Tiles/Rideau-Vanier.csv","Rideau-Vanier"]
##ward = ["Tiles/River.csv","River"]
##ward = ["Tiles/Riverside South-Findlay Creek.csv","Riverside South-Findlay Creek"]
##ward = ["Tiles/Sommerset.csv","Sommerset"]
##ward = ["Tiles/Stittsville.csv","Stittsville"]
##ward = ["Tiles/West Carleton-March.csv","West Carleton-March"] #over 1500 tiles
##ward = ["Tiles/West Carleton-March_2500.csv","West Carleton-March"] 

tiles = pd.read_csv(ward[0],usecols=["fid","id", "left", "top", "right", "bottom"])
tiles = tiles.to_records(index=False)

# Initialize an empty list to store results
all_results = []

iteration = 1

# Loop through each tile
for tile in tiles:
    fid,id,left, top, right, bottom = tile
    querystring = {
        "token": token,
        "f": "json",
        "tolerance": "0",
        "returnGeometry": "true",
        "imageDisplay": "932^%^2C521^%^2C96",
        "geometry": f'{{"xmin":{left},"ymin":{top},"xmax":{right},"ymax":{bottom}}}',
        "geometryType": "esriGeometryEnvelope",
        "mapExtent": f"{left}^%^2C{top}^%^2C{right}^%^2C{bottom}"
    }

    try:
        # Send the API request
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        # Check if results are present and append to the list
        if "results" in data and data["results"]:
            all_results.extend(data["results"])
            print(iteration,' of ',len(tiles))
            iteration += 1
        else:
            print(f"No results for tile: {tile}")
            iteration += 1

    except requests.exceptions.RequestException as e:
        print(f"Error querying tile {tile}: {e}")
        iteration += 1

# Convert the results into a DataFrame
df = pd.json_normalize(all_results)

# Save to a CSV file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
filename = f"Output/Assessment Roll Raw/AssessmentParcel_{ward[1]}.csv"
df.to_csv(filename, index=False)
print(f"CSV saved to '{filename}'")

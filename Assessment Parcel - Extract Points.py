import pandas as pd
import json

# Read the original CSV file
wards = [["Output/Assessment Roll Raw/AssessmentParcel_Alta Vista.csv","Alta Vista"],
["Output/Assessment Roll Raw/AssessmentParcel_Barrhaven East.csv","Barrhaven East"],
["Output/Assessment Roll Raw/AssessmentParcel_Barrhaven West.csv","Barrhaven West"],
["Output/Assessment Roll Raw/AssessmentParcel_Bay.csv","Bay"],
["Output/Assessment Roll Raw/AssessmentParcel_Beacan Hill-Cyrville.csv","Beacan Hill-Cyrville"],
["Output/Assessment Roll Raw/AssessmentParcel_Capital.csv","Capital"],
["Output/Assessment Roll Raw/AssessmentParcel_College.csv","College"],
["Output/Assessment Roll Raw/AssessmentParcel_Gloucester-Southgate.csv","Gloucester-Southgate"],
["Output/Assessment Roll Raw/AssessmentParcel_Kanata North.csv","Kanata North"],
["Output/Assessment Roll Raw/AssessmentParcel_Kanata South.csv","Kanata South"],
["Output/Assessment Roll Raw/AssessmentParcel_Kichissippi.csv","Kichissippi"],
["Output/Assessment Roll Raw/AssessmentParcel_Knoxdale-Merivale.csv","Knoxdale-Merivale"],
["Output/Assessment Roll Raw/AssessmentParcel_Orleans East-Cumberland.csv","Orleans East-Cumberland"],
["Output/Assessment Roll Raw/AssessmentParcel_Orleans East-Cumberland - Becketts Creek.csv","Orleans East-Cumberland - Becketts Creek"],
["Output/Assessment Roll Raw/AssessmentParcel_Orleans South-Navan.csv","Orleans South-Navan"],
["Output/Assessment Roll Raw/AssessmentParcel_Orleans West-Innes.csv","Orleans West-Innes"],
["Output/Assessment Roll Raw/AssessmentParcel_Osgood.csv","Osgood"],
["Output/Assessment Roll Raw/AssessmentParcel_Rideau-Jock.csv","Rideau-Jock"],
["Output/Assessment Roll Raw/AssessmentParcel_Rideau-Rockliffe.csv","Rideau-Rockliffe"],
["Output/Assessment Roll Raw/AssessmentParcel_Rideau-Vanier.csv","Rideau-Vanier"],
["Output/Assessment Roll Raw/AssessmentParcel_River.csv","River"],
["Output/Assessment Roll Raw/AssessmentParcel_Riverside South-Findlay Creek.csv","Riverside South-Findlay Creek"],
["Output/Assessment Roll Raw/AssessmentParcel_Sommerset.csv","Sommerset"],
["Output/Assessment Roll Raw/AssessmentParcel_Stittsville.csv","Stittsville"],
["Output/Assessment Roll Raw/AssessmentParcel_West Carleton-March.csv","West Carleton-March"]
]


for ward in wards:
    df = pd.read_csv(ward[0])

    # Initialize an empty list to store reformatted data
    reformatted_data = []

    # Iterate through rows of the original CSV
    for index, row in df.iterrows():
        value = row['value']
        ODF_ID = row['attributes.OGF_ID']  # Adjust column name as per your CSV
        PARCEL_ASSESSMENT_ROLL_NUMBER = row['attributes.ASSESSMENT_ROLL_NUMBER']
        OBJECT_ID = row['attributes.OBJECTID']
        geometry_rings = json.loads(row['geometry.rings'])  # Adjust column name as per your CSV
        vertices  = []  # List to store vertices of the current polygon
        
        # Extract vertices from the geometry.rings column
        for ring in geometry_rings:
            for lon, lat in ring:
                vertices.append((lon,lat))
        
        # Append vertices along with polygon ID to reformatted data
        for vertex in vertices:
            reformatted_data.append({'value':value,'ODF_ID': ODF_ID, 'OBJECT_ID':OBJECT_ID,'ASSESSMENT_ROLL_NUMBER':ASSESSMENT_ROLL_NUMBER,'lon': vertex[0], 'lat': vertex[1]})

    # Convert reformatted data to a DataFrame
    reformatted_df = pd.DataFrame(reformatted_data)

    # Write reformatted data to a new CSV file
    filename = f"Output/Points/Points_{ward[1]}.csv"
    reformatted_df.to_csv(filename, index=False)
    print(f"CSV saved to '{filename}'")


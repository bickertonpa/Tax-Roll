import json
import csv
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).resolve().parent

# Find all JSON files in this directory
json_files = list(script_dir.glob("*.json"))

if not json_files:
    print("No JSON files found in the script directory.")

for json_file_path in json_files:
    csv_file_path = json_file_path.with_suffix(".csv")

    try:
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        # Skip empty or invalid structures
        if not isinstance(data, list):
            print(f"Skipping {json_file_path.name}: not a list of records.")
            continue

        # Collect all unique keys
        keys_set = set()
        for record in data:
            if isinstance(record, dict):
                keys_set.update(record.keys())

        all_keys = sorted(keys_set)

        # Write CSV
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=all_keys)
            writer.writeheader()

            for record in data:
                if isinstance(record, dict):
                    writer.writerow({key: record.get(key, '') for key in all_keys})

        print(f"✔ Converted {json_file_path.name} → {csv_file_path.name}")

    except json.JSONDecodeError as e:
        print(f"✖ Error parsing {json_file_path.name}: {e}")
    except Exception as e:
        print(f"✖ Error processing {json_file_path.name}: {e}")
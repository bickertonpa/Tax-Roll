import json
import csv

# File paths
json_file_path = r'Output\Reformatted_College.json'
csv_file_path = r'Output\TaxRoll_College.csv'

try:
    # Load the JSON file
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)  # Since it's a list, load the entire file
    
    # Collect all unique keys across all records
    keys_set = set()
    for record in data:
        keys_set.update(record.keys())
    
    # Convert the set of keys into a sorted list for consistent CSV column order
    all_keys = sorted(keys_set)

    # Write data to CSV
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=all_keys)
        
        # Write the header row
        writer.writeheader()
        
        # Write each row of data
        for record in data:
            writer.writerow({key: record.get(key, '') for key in all_keys})

    print(f"Data has been successfully written to {csv_file_path}")

except json.JSONDecodeError as e:
    print(f"Error parsing JSON file: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

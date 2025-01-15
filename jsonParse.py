import json

# File paths
input_file_path = r'Output\College - by address.json'
output_file_path = r'Output\Reformatted_College - by address.json'

# Read and restructure JSON
try:
    with open(input_file_path, 'r') as input_file:
        # Attempt to load each line as a JSON object
        data = []
        for line in input_file:
            try:
                json_object = json.loads(line.strip())
                data.append(json_object)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line: {line.strip()} - Error: {e}")
    
    # Save the restructured JSON as an array
    with open(output_file_path, 'w') as output_file:
        json.dump(data, output_file, indent=4)

    print(f"Reformatted JSON saved to {output_file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
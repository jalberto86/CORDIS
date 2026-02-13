import json

# Path to your JSON file
json_file_path = r"C:\Users\merca\Desktop\EXTRACTION_1996141792_20250403222614160\project.json"

# Open and load the JSON file
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Count the number of records (assuming it's a list)
record_count = len(data)

print(f"Total number of results: {record_count}")

# This program inputs 2 files from a CORDIS search, the "project.json" and the "organization.json"
# It processes them into a .csv that contains in each row the total ammount of the project, and the
# participation of countries

# Participation of countries is done by aggregating all the organizations with the same "country" value

import os
import json
import pandas as pd
import math
from datetime import datetime
from collections import defaultdict
from tkinter import Tk, filedialog

projects = list()
organizations = list()

# Step 0. Select a folder from a CORDIS QUERY in JSON format

# Open folder selection dialog
folder_path = filedialog.askdirectory(title="Select the folder containing CORDIS JSON files")
query_result = input("Name of the file to store the results: ")
# Confirm selection
if not folder_path:
    print("No folder selected. Exiting.")
    exit()

# Construct file paths
project_path = os.path.join(folder_path, "project.json")
organization_path = os.path.join(folder_path, "organization.json")

# Load the JSON files
try:
    with open(project_path, "r", encoding="utf-8") as f:
        projects = json.load(f)
    with open(organization_path, "r", encoding="utf-8") as f:
        organizations = json.load(f)
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit()

# Output confirmation
print(f"Loaded {len(projects)} projects and {len(organizations)} organizations from:")
print(f"- {project_path}")
print(f"- {organization_path}")


# Step 1: Extract all unique country codes
country_codes = sorted(set(org['country'] for org in organizations if org['country']))
print(f"Unique country codes: {country_codes}")

# Step 2: Initialize project dataframe
project_data = []
for proj in projects:
    start_year = datetime.strptime(proj['startDate'], "%Y-%m-%d").year if proj['startDate'] else None
    end_year = datetime.strptime(proj['endDate'], "%Y-%m-%d").year if proj['endDate'] else None
    total_cost = float(proj['totalCost']) if proj['totalCost'] else 0.0

    row = {
        "id": proj["id"],
        "start_year": start_year,
        "end_year": end_year,
        "totalCost": total_cost,
    }
    # Initialize country columns with 0
    for code in country_codes:
        row[code] = float('nan')

    project_data.append(row)

df = pd.DataFrame(project_data)
#df.to_csv("projects_Keywords.csv", index=False)

# Step 3: Aggregate totalCost by projectID and country
costs_by_proj_country = defaultdict(float)
for org in organizations:
    #print(org)
    pid = org.get("projectID")
    country = org.get("country")
    #cost = float(org.get("totalCost", 0))
    cost_str = org.get("totalCost", "0")
    try:
        cost =  float(cost_str) if cost_str else 1.0  # 1.0 means 'participated but missing cost'
    except ValueError:
        cost = 1.0
    if pid and country:
        costs_by_proj_country[(pid, country)] += cost

#print(costs_by_proj_country)

#Step 4: Fill country cost values into the DataFrame
for (proj_id, country), total_cost in costs_by_proj_country.items():
    if proj_id in df["id"].values and country in df.columns:
        df.loc[df["id"] == proj_id, country] = total_cost

# Step 5: Save the final DataFrame
output_file = f"{query_result}.csv"
df.to_csv(output_file, index=False)
print(f"Saved to: {output_file}")


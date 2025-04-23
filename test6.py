import json
import pandas as pd
from collections import defaultdict
from tkinter import Tk, filedialog

# Open file dialog to select organization.json
Tk().withdraw()
file_path = filedialog.askopenfilename(title="Select organization.json", filetypes=[("JSON files", "*.json")])
if not file_path:
    print("No file selected. Exiting.")
    exit()
file_name = input("Select an output file name: ")

# Load JSON
with open(file_path, "r", encoding="utf-8") as f:
    org_data = json.load(f)

# Step 1: Organize data
org_info = dict()
org_projects = defaultdict(set)  # orgID → set of projectIDs
project_orgs = defaultdict(set)  # projectID → set of orgIDs

for org in org_data:
    org_id = org["organisationID"]
    short_name = org.get("shortName", "").strip()
    country = org.get("country", "").strip()
    city = org.get("city", "").strip()
    project_id = org["projectID"]

    # Keep first occurrence of short name if there's a conflict
    if org_id not in org_info:
        org_info[org_id] = {
            "shortName": short_name,
            "country": country,
            "city": city
        }

    org_projects[org_id].add(project_id)
    project_orgs[project_id].add(org_id)

org_project_costs = defaultdict(lambda: defaultdict(float))

for org in org_data:
    org_id = org["organisationID"]
    short_name = org.get("shortName", "").strip()
    country = org.get("country", "").strip()
    city = org.get("city", "").strip()
    project_id = org["projectID"]

    # Safe cost parsing
    try:
        cost = float(org.get("totalCost", 0)) if org.get("totalCost") else 0.0
    except ValueError:
        cost = 0.0

    # Keep first occurrence of short name
    if org_id not in org_info:
        org_info[org_id] = {
            "shortName": short_name,
            "country": country,
            "city": city
        }

    org_projects[org_id].add(project_id)
    org_project_costs[org_id][project_id] += cost  # sum in case of multiple entries
    project_orgs[project_id].add(org_id)

# Step 2: Build collaboration matrix
collab = defaultdict(lambda: defaultdict(int))

for orgs in project_orgs.values():
    for org1 in orgs:
        for org2 in orgs:
            if org1 != org2:
                collab[org1][org2] += 1

# Step 3: Get all unique orgIDs and projectIDs
all_orgs = sorted(org_info.keys())
all_projects = sorted(project_orgs.keys())

# Step 4: Build final table
rows = []
for org_id in all_orgs:
    row = {
        "organisationID": org_id,
        "shortName": org_info[org_id]["shortName"],
        "country": org_info[org_id]["country"],
        "city": org_info[org_id]["city"]
    }

    # Add collaboration counts
    for other_org in all_orgs:
        if other_org != org_id:
            row[str(other_org)] = collab[org_id].get(other_org, 0)

    # Add project participation flags
    # for pid in all_projects:
    #     row[f"project_{pid}"] = 1 if pid in org_projects[org_id] else 0

    # Add project totalCost values instead of 1/0 flags
    for pid in all_projects:
        row[f"project_{pid}"] = org_project_costs[org_id].get(pid, 0.0)

    rows.append(row)

# Step 5: Export to CSV
df = pd.DataFrame(rows)
df.to_csv(f"{file_name}.csv", index=False)
print(f"Saved: {file_name}.csv")

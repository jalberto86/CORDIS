# This program inputs several organizations.json files, BUT THEY MUST BE IN THE SAME FOLDER. So it needs some prep before
# running it
# It produces a matrix of colaborations focused on the organizations.
# It uses the unique organization id, then assigns the org to all possible projects and the partnerships.

# We could improve by including the duration of the colaboration by project.

import json
import pandas as pd
from collections import defaultdict
from tkinter import Tk, filedialog

# Open one dialog to select multiple files
root = Tk()
root.withdraw()
file_paths = filedialog.askopenfilenames(
    title="Select one or more organization.json files",
    filetypes=[("JSON files", "*.json")]
)
root.destroy()

# Load all JSON files selected files
org_data = []
for path in file_paths:
    print(f"Loading {path}...")
    with open(path, "r", encoding="utf-8") as f:
        org_data.extend(json.load(f))
if not file_paths:
    print("No files selected. Exiting.")
    exit()

file_name = input("Select an output file name: ")

# Step 1: Organize data
org_info = dict()
org_projects = defaultdict(set)  # orgID → set of projectIDs
project_orgs = defaultdict(set)  # projectID → set of orgIDs

for org in org_data:
    try:
        org_id = int(org["organisationID"])
        project_id = int(org["projectID"])
    except (KeyError, ValueError, TypeError):
        continue
    name = org.get("name","").strip()
    short_name = org.get("shortName", "").strip()
    country = org.get("country", "").strip()
    city = org.get("city", "").strip()

    # Store only the first occurrence of organisationID to avoid overwriting.
    if org_id not in org_info:
        org_info[org_id] = {
            "name": name,
            "shortName": short_name,
            "country": country,
            "city": city
        }

    org_projects[org_id].add(project_id)
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
        "Name": org_info[org_id]["name"],
        "shortName": org_info[org_id]["shortName"],
        "country": org_info[org_id]["country"],
        "city": org_info[org_id]["city"]
    }

    # Add collaboration counts
    for other_org in all_orgs:
        if other_org != org_id:
            row[str(other_org)] = collab[org_id].get(other_org, 0)

    # Add project participation flags
    for pid in all_projects:
        row[f"project_{pid}"] = 1 if pid in org_projects[org_id] else 0

    rows.append(row)

# Step 5: Export to CSV
df = pd.DataFrame(rows)
df.to_csv(f"{file_name}.csv", index=False)
print(f"Saved: {file_name}.csv")

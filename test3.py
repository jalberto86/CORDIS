import json
import pandas as pd
from datetime import datetime
from collections import defaultdict

projects = list()
organizations = list()

# Get paths for files. Projects are going to be the first 2. Organization the second 2.
paths = [r"G:\My Drive\ApogeeBio\ISS\Cordis\Keyword_Extractions\FP1_FP7\project.json",
r"G:\My Drive\ApogeeBio\ISS\Cordis\Keyword_Extractions\H2020_Horizon\project.json",
r"G:\My Drive\ApogeeBio\ISS\Cordis\Keyword_Extractions\FP1_FP7\organization.json",
r"G:\My Drive\ApogeeBio\ISS\Cordis\Keyword_Extractions\H2020_Horizon\organization.json"]

# print(f"first 2 {paths[:2]}")
# print(f"Second 2 {paths[2:]}")

# Load JSON files
for path in paths[:2]:
    with open(path, "r", encoding="utf-8") as f:
        projects.extend(json.load(f))
for path in paths[2:]:
    with open(path, "r", encoding="utf-8") as f:
        organizations.extend(json.load(f))


record_count = [len(projects), len(organizations)]

print(f"Total number of results in projects: {record_count[0]}\n"
      f"Total number of results in organizations: {record_count[0]}")


# with open(r"C:\Users\merca\PycharmProjects\CORDIS\EXTRACTION_1996141792_20250403222614160\project.json", "r", encoding="utf-8") as f:
#     projects = json.load(f)
#
# with open(r"C:\Users\merca\PycharmProjects\CORDIS\EXTRACTION_1996141792_20250403222614160\organization.json", "r", encoding="utf-8") as f:
#     organizations = json.load(f)

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
        row[code] = 0.0

    project_data.append(row)

df = pd.DataFrame(project_data)
df.to_csv("projects_Keywords.csv", index=False)

# Step 3: Aggregate totalCost by projectID and country
costs_by_proj_country = defaultdict(float)
for org in organizations:
    print(org)
    pid = org.get("projectID")
    country = org.get("country")
    #cost = float(org.get("totalCost", 0))
    cost_str = org.get("totalCost", "0")
    try:
        cost = float(cost_str) if cost_str else 0.0
    except ValueError:
        cost = 0.0
    if pid and country:
        costs_by_proj_country[(pid, country)] += cost

# Step 4: Fill country cost values into the DataFrame
for (proj_id, country), total_cost in costs_by_proj_country.items():
    if proj_id in df["id"].values and country in df.columns:
        df.loc[df["id"] == proj_id, country] = total_cost

# Step 5: Save the final DataFrame
output_file = "projects_country_costs_Keywords.csv"
df.to_csv(output_file, index=False)
print(f"Saved to: {output_file}")






# # Step 3: Fill country participation using organization data
# for org in organizations:
#     pid = org["projectID"]
#     country = org.get("country")
#     if country in country_codes:
#         df.loc[df["id"] == pid, country] = 1
#
# # Step 4: Export to CSV
# output_file = "project_with_country_participation.csv"
# df.to_csv(output_file, index=False)
# print(f"Saved to: {output_file}")

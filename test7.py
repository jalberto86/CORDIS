# # This program takes inputs both organization.json and project.json for 2 queries. Then it constructs a matrix
# of project participation by year. If the year of the project goes beyond 2025, we cut it on 2025.
# The yearly cost for each organization on the projects is the total costs, divided by the length of the project. Again,
# projects extends beyond 2025, we use the total length to get the yearly cost.

# IMPORTANT. We save the colaboration matrix in sparce mode, so it has to be reconstituted for use. See Test8.py

###############################
###############################
###############################

import json
import pandas as pd
import numpy as np
from scipy.sparse import lil_matrix, save_npz
from collections import defaultdict
from datetime import datetime

# --------------- Paths to files ---------------
paths = [
    r"G:\My Drive\ApogeeBio\ISS\Cordis\Keyword_Extractions\FP1_FP7\project.json",
    r"G:\My Drive\ApogeeBio\ISS\Cordis\Keyword_Extractions\H2020_Horizon\project.json",
    r"G:\My Drive\ApogeeBio\ISS\Cordis\Keyword_Extractions\FP1_FP7\organization.json",
    r"G:\My Drive\ApogeeBio\ISS\Cordis\Keyword_Extractions\H2020_Horizon\organization.json"
]

# --------------- Step 1: Load data ---------------
projects = []
for path in paths[:2]:
    with open(path, "r", encoding="utf-8") as f:
        projects.extend(json.load(f))

organizations = []
for path in paths[2:]:
    with open(path, "r", encoding="utf-8") as f:
        organizations.extend(json.load(f))

# --------------- Step 2: Build project_years mapping ---------------
project_years = dict()

for proj in projects:
    try:
        pid = int(proj['id'])
        start = proj.get('startDate')
        end = proj.get('endDate')
        if start and end:
            start_year = datetime.strptime(start, "%Y-%m-%d").year
            end_year = datetime.strptime(end, "%Y-%m-%d").year
            #
            # # Cap end year to 2025 if it's in the future
            # if end_year > 2025:
            #     end_year = 2025
            project_years[pid] = list(range(start_year, end_year + 1))
    except (KeyError, ValueError, TypeError):
        continue

# --------------- Step 3: Prepare organization data ---------------
org_info = dict()
org_project_costs = defaultdict(lambda: defaultdict(float))

for org in organizations:
    try:
        org_id = int(org["organisationID"])
        project_id = int(org["projectID"])
    except (KeyError, ValueError, TypeError):
        continue

    name = org.get("name", "").strip()
    short_name = org.get("shortName", "").strip()
    country = org.get("country", "").strip()
    city = org.get("city", "").strip()

    try:
        cost = float(org.get("totalCost", 0)) if org.get("totalCost") else 0.0
    except ValueError:
        cost = 0.0

    if org_id not in org_info:
        org_info[org_id] = {
            "name": name,
            "shortName": short_name,
            "country": country,
            "city": city
        }

    org_project_costs[org_id][project_id] += cost

# --------------- Step 4: Build sparse matrix ---------------

# Build list of unique orgs and project-year combinations
all_orgs = sorted(org_info.keys())
all_project_years = set()

for pid, years in project_years.items():
    for year in years:
        if year <= 2025:
            all_project_years.add((pid, year))

all_project_years = sorted(all_project_years)  # sorted tuples (project_id, year)

# Map org_id <--> row index, project_year <--> column index
org_id_to_row = {org_id: idx for idx, org_id in enumerate(all_orgs)}
project_year_to_col = {p_y: idx for idx, p_y in enumerate(all_project_years)}

# Initialize a LIL sparse matrix (efficient for building)
sparse_matrix = lil_matrix((len(all_orgs), len(all_project_years)))

# Fill the matrix
for org_id in all_orgs:
    for pid, total_cost in org_project_costs[org_id].items():
        years = project_years.get(pid)
        if years:
            yearly_cost = total_cost / len(years)
            for year in years:
                col_idx = project_year_to_col.get((pid, year))
                if col_idx is not None:
                    row_idx = org_id_to_row[org_id]
                    sparse_matrix[row_idx, col_idx] = yearly_cost

# --------------- Step 5: Save outputs ---------------

# Save sparse matrix
save_npz("organization_project_year_matrix.npz", sparse_matrix.tocsr())

# Save mapping files
pd.DataFrame.from_dict(org_id_to_row, orient='index').to_csv("org_id_to_row.csv", header=["row_idx"])
pd.DataFrame.from_dict(project_year_to_col, orient='index').to_csv("project_year_to_col.csv", header=["col_idx"])

print("Saved: organization_project_year_matrix.npz, org_id_to_row.csv, project_year_to_col.csv")

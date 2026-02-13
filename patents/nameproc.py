# In this Module we attemp to create a MASTER list of all nodes. We will use 3 sources of data,  the patent data
# (WO_pats2.csv), the CORDIS data (organizationFP1_FP7.json','organizationH2020.json', and the demo plants
# ("Demoplants 112024.xlsx")
#
###################################
# Cleaning the Patent data
###################################

# 1. Shared Cleaning Function
# Use this one function for both files:
# import re
# import unicodedata
#
# def clean_name(name):
#     if not isinstance(name, str):
#         return ""
#     name = re.sub(r"\[.*?\]", "", name)  # Remove country tags like [US]
#     name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")  # Remove accents
#     name = re.sub(r"[^\w\s]", "", name)  # Remove punctuation
#     name = re.sub(r"\s+", " ", name)     # Normalize whitespace
#     return name.upper().strip()          # Uppercase and strip


#2. Apply to modified_dataset.csv (patent file)

# import pandas as pd
#
# df = pd.read_csv("WO_pats2.csv")
#
# # Remove columns that are completely empty (all NaN or empty strings)
# df = df.dropna(axis=1, how='all')  # Drop columns with all NaN
# df = df.loc[:, ~(df == '').all()]  # Drop columns with all empty strings
#
# # Select all columns that start with applicant.name.
# applicant_cols = [col for col in df.columns if col.startswith("applicant.name")]
#
# # Apply clean_name to each of those columns
# for col in applicant_cols:
#     df[f"{col}_clean"] = df[col].apply(clean_name)
#
# # Optionally: save a cleaned version
# df.to_csv("modified_dataset_cleaned.csv", index=False)
# print("Patents cleaned and saved to: modified_dataset_cleaned.csv")


#3. Apply to organization.json
#
# import json
# files = ['organizationFP1_FP7.json','organizationH2020.json']
# org_lookup = {}
#
# for file in files:
#     with open(file, "r", encoding="utf-8") as f:
#         org_data = json.load(f)
#
#     # Build a dictionary: cleaned_name → organization record
#     for org in org_data:
#         name_clean = clean_name(org.get("name", ""))
#         if name_clean:
#             org_lookup[name_clean] = org
# print(org_lookup)

###################################
# Regex matching
###################################
# Reload the cleaned patent dataset
# import pandas as pd
#
# df = pd.read_csv("modified_dataset_cleaned.csv")
#
# # Extract just the applicant clean columns
# clean_cols = [col for col in df.columns if col.endswith("_clean")]
#
# # Add a new column to store the first matched org name
# df["matched_org_name"] = None
# df["matched_org_id"] = None
#
# # Match logic
# for idx, row in df.iterrows():
#     for col in clean_cols:
#         name = row[col]
#         if pd.notna(name) and name in org_lookup:
#             matched_org = org_lookup[name]
#             df.at[idx, "matched_org_name"] = matched_org.get("name")
#             df.at[idx, "matched_org_id"] = matched_org.get("organisationID")
#             break  # Stop at first match
#
# # Save result
# df.to_csv("matched_patents.csv", index=False)
# print("Matching completed and saved to: matched_patents.csv")
#
# match_count = df["matched_org_name"].notna().sum()
# print(f"Matched rows: {match_count} / {len(df)}")
#
# unmatched_df = df[df["matched_org_name"].isna()]
# unmatched_df.to_csv("unmatched_patents.csv", index=False)

###################################
# Regex matching for ALL applicants
###################################

# import pandas as pd
#
# # Reload the cleaned patent dataset
# df = pd.read_csv("modified_dataset_cleaned.csv")
#
# # Extract just the applicant clean columns
# clean_cols = [col for col in df.columns if col.endswith("_clean")]
#
# # Initialize match columns dynamically
# max_applicants = len(clean_cols)  # Assume worst case
# for i in range(1, max_applicants + 1):
#     df[f"matched_org_name_{i}"] = None
#     df[f"matched_org_id_{i}"] = None
#
# # Perform matching
# for idx, row in df.iterrows():
#     match_num = 1
#     for col in clean_cols:
#         name = row[col]
#         if pd.notna(name) and name in org_lookup:
#             matched_org = org_lookup[name]
#             df.at[idx, f"matched_org_name_{match_num}"] = matched_org.get("name")
#             df.at[idx, f"matched_org_id_{match_num}"] = matched_org.get("organisationID")
#             match_num += 1
#
# df = df.dropna(axis=1, how='all')  # Drop columns with all NaN
# df = df.loc[:, ~(df == '').all()]  # Drop columns with all empty strings
# # Optionally: save the enriched file
# df.to_csv("patent_matches_full.csv", index=False)
# print("Matches saved to: patent_matches_full.csv")


###################################
# Fuzzy matching
###################################

# from rapidfuzz import process, fuzz
# import pandas as pd
# from tqdm import tqdm
#
# # Reload cleaned dataset and assume org_lookup is already built
# df = pd.read_csv("modified_dataset_cleaned.csv")
#
# # Columns to check for applicants
# clean_cols = [col for col in df.columns if col.endswith("_clean")]
#
# # Target organization names (the keys of org_lookup)
# org_names_clean = list(org_lookup.keys())
#
# # Threshold for matching quality (tune this!)
# THRESHOLD = 80
#
# # Add new columns to store best fuzzy match
# df["fuzzy_matched_org_name"] = None
# df["fuzzy_matched_org_id"] = None
# df["fuzzy_score"] = None

# Wrap with tqdm
# for idx, row in tqdm(df.iterrows(), total=len(df), desc="Fuzzy Matching Progress"):
#     for col in clean_cols:
#         name = row[col]
#         if pd.notna(name) and name:
#             match = process.extractOne(name, org_names_clean, scorer=fuzz.token_sort_ratio)
#             if match and match[1] >= THRESHOLD:
#                 best_match_name, score = match[0], match[1]
#                 matched_org = org_lookup[best_match_name]
#                 df.at[idx, "fuzzy_matched_org_name"] = matched_org.get("name")
#                 df.at[idx, "fuzzy_matched_org_id"] = matched_org.get("organisationID")
#                 df.at[idx, "fuzzy_score"] = score
#                 break  # Stop at first good match
#
# df.to_csv("fuzzy_matched_patents80.csv", index=False)
# print("Fuzzy matching completed.")

###################################
# Fuzzy matching. All Applicants
###################################

# from rapidfuzz import process, fuzz
# import pandas as pd
# from tqdm import tqdm
#
# # Reload cleaned dataset and assume org_lookup is already built
# df = pd.read_csv("modified_dataset_cleaned.csv")
#
# # Columns with applicant names
# clean_cols = [col for col in df.columns if col.endswith("_clean")]
# org_names_clean = list(org_lookup.keys())
#
# THRESHOLD = 85  # Adjust if needed
#
# # Initialize match columns dynamically (max 20)
# max_matches = 20
# for i in range(1, max_matches + 1):
#     df[f"fuzzy_matched_org_name_{i}"] = None
#     df[f"fuzzy_matched_org_id_{i}"] = None
#     df[f"fuzzy_score_{i}"] = None
#
# # Matching loop with progress bar
# for idx, row in tqdm(df.iterrows(), total=len(df), desc="Fuzzy Matching Progress"):
#     match_num = 1
#     for col in clean_cols:
#         if match_num > max_matches:
#             break
#         name = row[col]
#         if pd.notna(name) and name:
#             match = process.extractOne(name, org_names_clean, scorer=fuzz.token_sort_ratio)
#             if match and match[1] >= THRESHOLD:
#                 best_match_name, score = match[0], match[1]
#                 matched_org = org_lookup[best_match_name]
#                 df.at[idx, f"fuzzy_matched_org_name_{match_num}"] = matched_org.get("name")
#                 df.at[idx, f"fuzzy_matched_org_id_{match_num}"] = matched_org.get("organisationID")
#                 df.at[idx, f"fuzzy_score_{match_num}"] = score
#                 match_num += 1
#
# df = df.dropna(axis=1, how='all')  # Drop columns with all NaN
# df = df.loc[:, ~(df == '').all()]  # Drop columns with all empty strings
# # Save the result
# df.to_csv("fuzzy_matched_patents_multi85.csv", index=False)
# print("Fuzzy multi-matching completed and saved.")

###################################
# Join the patent-Cordis names to the demoplants
###################################

# Start by reducing the size of the data
# Load your dataset
import pandas as pd
df = pd.read_csv("fuzzy_matched_patents_multi85Cleaned.csv")

# Select only the needed columns
selected_columns = [
    'publication.reference', 'publication.date', 'application.reference', 'application.date',
    'family.id', 'year',
    'applicant.name.1_clean', 'applicant.name.2_clean', 'applicant.name.3_clean',
    'applicant.name.4_clean', 'applicant.name.5_clean', 'applicant.name.6_clean',
    'applicant.name.7_clean', 'applicant.name.8_clean', 'applicant.name.9_clean',
    'applicant.name.10_clean', 'applicant.name.11_clean', 'applicant.name.12_clean',
    'applicant.name.13_clean', 'applicant.name.14_clean', 'applicant.name.15_clean',
    'applicant.name.16_clean', 'applicant.name.17_clean', 'applicant.name.18_clean',
    'applicant.name.19_clean',
    'fuzzy_matched_org_name_1', 'fuzzy_matched_org_id_1',
    'fuzzy_matched_org_name_2', 'fuzzy_matched_org_id_2',
    'fuzzy_matched_org_name_3', 'fuzzy_matched_org_id_3'
]

df_filtered = df[selected_columns].copy()

# Rename the fuzzy matched org name columns
df_filtered.rename(columns={
    'fuzzy_matched_org_name_1': 'CORDIS_fm_org_name_1',
    'fuzzy_matched_org_id_1':'CORDIS_fm_org_id_1',
    'fuzzy_matched_org_name_2': 'CORDIS_fm_org_name_2',
    'fuzzy_matched_org_id_2':'CORDIS_fm_org_id_2',
    'fuzzy_matched_org_name_3': 'CORDIS_fm_org_name_3',
    'fuzzy_matched_org_id_3':'CORDIS_fm_org_id_3',
}, inplace=True)

# Save to new CSV
df_filtered.to_csv("filtered_patent_data.csv", index=False)
# Print all column names
print("Column names in new the dataset:")
print(df_filtered.columns.tolist())
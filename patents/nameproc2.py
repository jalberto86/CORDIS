from rapidfuzz import process, fuzz
import pandas as pd

# Reload cleaned dataset and assume org_lookup is already built
df = pd.read_csv("modified_dataset_cleaned.csv")

# Columns to check for applicants
clean_cols = [col for col in df.columns if col.endswith("_clean")]

# Target organization names (the keys of org_lookup)
org_names_clean = list(org_lookup.keys())

# Threshold for matching quality (tune this!)
THRESHOLD = 90

# Add new columns to store best fuzzy match
df["fuzzy_matched_org_name"] = None
df["fuzzy_matched_org_id"] = None
df["fuzzy_score"] = None

for idx, row in df.iterrows():
    for col in clean_cols:
        name = row[col]
        if pd.notna(name) and name:
            # Find best match among org names
            match = process.extractOne(name, org_names_clean, scorer=fuzz.token_sort_ratio)
            if match and match[1] >= THRESHOLD:
                best_match_name, score = match[0], match[1]
                matched_org = org_lookup[best_match_name]
                df.at[idx, "fuzzy_matched_org_name"] = matched_org.get("name")
                df.at[idx, "fuzzy_matched_org_id"] = matched_org.get("organisationID")
                df.at[idx, "fuzzy_score"] = score
                break  # Stop at first good match

# Save results
df.to_csv("fuzzy_matched_patents.csv", index=False)
print("Fuzzy matching completed and saved to: fuzzy_matched_patents.csv")

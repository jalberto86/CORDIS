import pandas as pd
import os
from tqdm import tqdm
from rapidfuzz.fuzz import ratio
from itertools import combinations
import networkx as nx

# Get the current working directory
wd = os.getcwd()

# Print the current working directory
print("Current Working Directory:", wd)
#
#
# # Load the CSV file
# df = pd.read_csv("WO_pats2.csv")
#
# # Remove columns that start with "references.cited." and "inventor.name"
# # columns_to_remove = [col for col in df.columns if col.startswith('references.cited.') or col.startswith('inventor.name')]
# df = df.drop(columns='year')
#
# # Create new columns for the year
# df['application.year'] = df['application.date'].astype(str).str[:4]
# df['publication.year'] = df['publication.date'].astype(str).str[:4]
#
# # Save the modified dataset
# df.to_csv('modified_dataset.csv', index=False)
#
# # Print all column names
# print("Column names in the dataset:")
# for col in df.columns:
#     print(col)

###########################
###########################
###########################

# Load the CSV file
#df = pd.read_csv("modified_dataset_cleaned.csv")
df = pd.read_csv("fuzzy_matched_patents_multi85Cleaned.csv")

# Print all column names
print("Column names in the dataset:")
print(df.columns.tolist())

###########################
# Check for duplicates
###########################

# Define the columns to check
# columns_to_check = ['publication.reference', 'application.reference', 'family.id']
#
# # Loop through each column and display duplicated values and their counts
# for col in columns_to_check:
#     print(f"\nDuplicated values in column: '{col}'")
#
#     # Count occurrences
#     value_counts = df[col].value_counts()
#
#     # Filter only duplicated values (appearing more than once)
#     duplicates = value_counts[value_counts > 1]
#
#     if not duplicates.empty:
#         print(duplicates)
#     else:
#         print("No duplicates found.")

###########################
# Print some patent families
###########################

# # Set display options for full visibility
# pd.set_option('display.max_columns', None)      # Show all columns
# pd.set_option('display.max_colwidth', None)     # Show full content in each column
# pd.set_option('display.width', None)            # Allow full width without truncation
# pd.set_option('display.expand_frame_repr', False)  # Don't wrap DataFrame display
#
# # Adjusted row indices based on Excel rows (minus 2 for header and 0-based indexing)
# rows_to_display = [7, 8, 9, 10, 11, 17, 18, 46, 47, 69, 70, 126, 127, 128]
#
# # Print the selected rows
# print(df.iloc[rows_to_display])

###########################
# Identify patent families
###########################

# # Normalize relevant fields
# df['invention.title'] = df['invention.title'].fillna('').str.lower().str.strip()
# df['application.date'] = pd.to_datetime(df['application.date'], errors='coerce')
# df['publication.date'] = pd.to_datetime(df['publication.date'], errors='coerce')
#
# # Create blocking key to limit comparisons
# df['block_key'] = df['country.id'].astype(str) + '_' + df['application.date'].astype(str)
#
# # Store suspected duplicates
# matches = []
#
# # Iterate over groups with tqdm for progress
# for _, group in tqdm(df.groupby('block_key'), desc="Processing blocks"):
#
#     if len(group) < 2:
#         continue  # Skip groups with only 1 entry
#
#     # Compare all combinations within each block
#     for i, j in combinations(group.index, 2):
#         row1 = group.loc[i]
#         row2 = group.loc[j]
#
#         if row1['family.id'] == row2['family.id']:
#             continue
#
#         # Filter: same publication date
#         if row1['publication.date'] != row2['publication.date']:
#             continue
#
#         # Title similarity (fast fuzzy match)
#         title_sim = ratio(row1['invention.title'], row2['invention.title']) / 100.0
#         if title_sim < 0.9:
#             continue
#
#         # Optional: compare numeric publication references
#         pub1 = ''.join(filter(str.isdigit, str(row1['publication.reference'])))
#         pub2 = ''.join(filter(str.isdigit, str(row2['publication.reference'])))
#         pub_similar = pub1[:-2] == pub2[:-2] if len(pub1) > 2 and len(pub2) > 2 else False
#
#         if pub_similar or title_sim > 0.95:
#             matches.append({
#                 'index_1': i,
#                 'index_2': j,
#                 'publication_1': row1['publication.reference'],
#                 'publication_2': row2['publication.reference'],
#                 'family_1': row1['family.id'],
#                 'family_2': row2['family.id'],
#                 'application.date': row1['application.date'],
#                 'publication.date': row1['publication.date'],
#                 'country': row1['country.id'],
#                 'title_1': row1['invention.title'],
#                 'title_2': row2['invention.title']
#             })
#
# # Save matches to file
# df_matches = pd.DataFrame(matches)
# df_matches.to_csv("suspected_duplicate_inventions.csv", index=False)
#
# print(f"\nDone. {len(df_matches)} suspected duplicates saved to 'suspected_duplicate_inventions.csv'.")

###########################
# Deduplicate patent families
###########################

#In this case are not strictly patent families, but multiple submissions. That is, in esence is the same invention, but
# each has a slightly different family.id number. For our purposes, we should count one

# pairs = pd.read_csv("suspected_duplicate_inventions.csv")
#
# # Step 1: Build an undirected graph of connected patent indices
# G = nx.Graph()
# G.add_edges_from(pairs[['index_1', 'index_2']].values)
#
# # Step 2: Find connected components (each is a group of linked patents)
# components = list(nx.connected_components(G))
#
# # Step 3: For each group, keep the lowest index as representative
# representative_indices = set()
# for group in components:
#     representative_indices.add(min(group))  # Keep only the first (lowest index)
#
# # Step 4: Identify all indices that are part of any duplicate group
# all_grouped_indices = set().union(*components)
#
# # Step 5: Get final set of rows to keep
# # - Include all original entries not in any group
# # - Add one representative per duplicate group
# indices_to_keep = (
#     (set(df.index) - all_grouped_indices)  # not involved in any group
#     | representative_indices               # representative of each group
# )
#
# # Step 6: Filter the original dataset
# deduplicated_df = df.loc[sorted(indices_to_keep)]
#
# # Step 7: Save to CSV
# deduplicated_df.to_csv("deduplicated_dataset.csv", index=False)
#
# print(f"Saved deduplicated dataset with {len(deduplicated_df)} rows to 'deduplicated_dataset.csv'.")

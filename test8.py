# Check the files
# organization_project_year_matrix.npz | The sparse matrix storing costs
# org_id_to_row.csv | Map organization ID → row index
# project_year_to_col.csv | Map (projectID, year) → column index

import pandas as pd
from scipy.sparse import load_npz
import ast

# Load sparse matrix
matrix = load_npz("organization_project_year_matrix.npz")

# Load row and column mappings
org_id_to_row = pd.read_csv("org_id_to_row.csv", index_col=0).squeeze("columns").to_dict()
project_year_to_col = pd.read_csv(
    "project_year_to_col.csv", index_col=0, dtype={0: str}
).squeeze("columns").to_dict()

# Reverse mappings
row_to_org_id = {v: k for k, v in org_id_to_row.items()}
col_to_project_year = {v: k for k, v in project_year_to_col.items()}

# Build ordered row and column labels
row_labels = [row_to_org_id[i] for i in range(matrix.shape[0])]
col_labels = [f"project_{pid}_{year}" for i in range(matrix.shape[1])
              for (pid, year) in [ast.literal_eval(col_to_project_year[i])]]

# Convert to dense DataFrame
df = pd.DataFrame(matrix.todense(), index=row_labels, columns=col_labels)

# Save to CSV (optional)
df.to_csv("organization_project_year_full_matrix.csv")
print("Saved: organization_project_year_full_matrix.csv")

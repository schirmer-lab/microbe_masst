import pandas as pd
import csv

pos_neg = "neg"

# set paths according to positive or negative value
exp = f"files/{pos_neg}_expression.tsv"
viewer_table = f"files/{pos_neg}_viewerTable.tsv"

# read files
exp = pd.read_csv(exp, sep="\t", index_col=0)
viewer_table = pd.read_csv(viewer_table, sep="\t", quoting=csv.QUOTE_NONE)

# rename columns of viewer table to match ID of expression table and remove unnecessary
viewer_table.rename(columns={
    "General|All|ID": "feature",
    "General|All|rtmed": "rtmed",
    "General|All|mzmed": "mzmed",
    "General|Extended|mzmin": "mzmin",
    "General|Extended|mzmax": "mzmax",
    "General|Extended|rtmin": "rtmin",
    "General|Extended|rtmax": "rtmax",
    "General|Extended|npeaks": "npeaks"
}, inplace=True)

# remove redundant columns of the viewer table
viewer_table = viewer_table[["feature", "mzmed", "mzmin", "mzmax", "rtmed", "rtmin", "rtmax", "npeaks"]]

# set index for viewer table
viewer_table.set_index("feature", inplace=True)

# filter: column names that start with "B" and continue with a digit from 1 to 23
valid_columns = [col for col in exp.columns if col.startswith('B') and col[1:].isdigit() and 1 <= int(col[1:]) <= 23]

# apply filter
exp = exp[valid_columns]

# convert columns names of expression table to mzXML file names
new_col_names = []
for col_name in exp.columns:
    if col_name != "feature":
        new_col_names.append(f"241008_M274_01_HILIC_{pos_neg}_{col_name}.mzXML")
    else:
        new_col_names.append(col_name)

exp.columns = new_col_names

# concat both dfs
complete_df = pd.concat([viewer_table, exp], axis=1)

# replace NAs with "NA" string
complete_df = complete_df.fillna("NA")

complete_df.to_csv(f"files/FBMN/{pos_neg}_feature_table.tsv", sep="\t")

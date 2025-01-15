import pandas as pd

exp = "files/pos_expression.tsv"
viewer_table = "files/pos_viewerTable.tsv"

exp = pd.read_csv(exp, sep="\t")
viewer_table = pd.read_csv(viewer_table, sep="\t")

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

viewer_table = viewer_table[["feature", "mzmed", "mzmin", "mzmax", "rtmed", "rtmin", "rtmax", "npeaks"]]

complete_df = pd.concat([viewer_table, exp])

complete_df.to_csv("files/FBMN/pos_feature_table.tsv", sep="\t")

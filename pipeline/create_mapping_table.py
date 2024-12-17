import pandas as pd
import argparse

def create_argparser():
    parser = argparse.ArgumentParser(description="Mapper for the input of microbeMASST and its results")

    parser.add_argument('--feature_counts', type=str, required=True, help='Path to counts with features file')
    parser.add_argument('--sample_species', type=str, required=True, help='Path to the mapping file for sampleID to species')
    parser.add_argument('--expression_table', type=str, required=True, help='Path to the expression table of xcmsViewer')

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = create_argparser()

    # read in output of microbeMASST -> tsv with features
    df = pd.read_csv(args.feature_counts, sep="\t", index_col="feature")

    # read in the mapping of sample ID and according species
    sampleID_species_mapping = pd.read_excel(args.sample_species, sheet_name="Sheet1")

    # read in expression table of xcmsViewer
    expression_table = pd.read_csv(args.expression_table, sep="\t", index_col="feature")

    print(expression_table)

    # get list of expressed sample IDs for each feature
    feature_sampleIDs = {}
    for feature, row in expression_table.iterrows():
        sampleIDs = row[row > 0].index.tolist()

        # translate sample IDs to species names
        species_names = []
        for sampleID in sampleIDs:
            try:
                species_names.append(sampleID_species_mapping.loc[sampleID_species_mapping["Strain_ID"] == sampleID, "Species"].values[0])
            except Exception as e:
                print(f"sampleID not in mapping table: {e}")

        # add collected species names to feature
        feature_sampleIDs[feature] = species_names




import pandas as pd
import argparse
import sys

def create_argparser():
    parser = argparse.ArgumentParser(description="Mapper for the input of microbeMASST and its results")

    parser.add_argument('--feature_counts', type=str, required=True, help='Path to counts with features file')
    parser.add_argument('--sample_species', type=str, required=True, help='Path to the mapping file for sampleID to species')
    parser.add_argument('--expression_table', type=str, required=True, help='Path to the expression table of xcmsViewer')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help="activates printing of messages to console")
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to output file.')

    args = parser.parse_args()

    return args


def split_and_concat(taxaname):
    splits = taxaname.split(" ")
    if len(splits) >= 2:
        return f"{splits[0]}_{splits[1]}"
    return taxaname


if __name__ == "__main__":
    args = create_argparser()

    # read in output of microbeMASST -> tsv with features
    df = pd.read_csv(args.feature_counts, sep="\t", index_col="Feature")

    # reshape to Feature as unique index and taxaname_file as a list
    df = df.groupby("Feature")["Taxaname_file"].apply(set).reset_index()
    df = df.set_index("Feature")
    df = df.set_index(df.index.str.upper())

    # reshape taxa names to format of mapping sample ID to taxa
    df["Taxaname_file_split"] = df["Taxaname_file"].apply(lambda x: {split_and_concat(name) for name in x})

    # read in the mapping of sample ID and according species
    sampleID_species_mapping = pd.read_excel(args.sample_species, sheet_name="Sheet1")

    # read in expression table of xcmsViewer
    expression_table = pd.read_csv(args.expression_table, sep="\t", index_col="feature")

    # get list of expressed sample IDs for each feature
    feature_sampleIDs = {}
    for feature, row in expression_table.iterrows():
        sampleIDs = row[row > 0].index.tolist()

        # translate sample IDs to species names
        species_names = set()
        for sampleID in sampleIDs:
            try:
                species_names.add(sampleID_species_mapping.loc[sampleID_species_mapping["Strain_ID"] == sampleID, "Species"].values[0])
            except Exception as e:
                if args.verbose:
                    print(f"sampleID ({sampleID}) not in mapping table")

        # add collected species names to feature
        feature_sampleIDs[feature] = species_names

    # add dictionary values as new column of df
    df["Taxaname_samples"] = pd.Series(feature_sampleIDs)

    # add column which includes Taxanames that are in both
    df["Taxaname_intersection"] = df.apply(lambda row: row["Taxaname_file"].intersection(row["Taxaname_samples"]), axis=1)

    # write mapping_table as tsv
    df.to_csv(args.output, sep='\t')

"python pipeline/create_mapping_table.py --feature_counts files/summary_counts_microbe.tsv --sample_species files/Bacterial_strain_ID.xlsx --expression_table files/pos_expression.tsv -o output/mapping.tsv"






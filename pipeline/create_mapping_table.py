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
    splits = taxaname.split("_")
    if len(splits) >= 2:
        return f"{splits[0]} {splits[1]}"
    return taxaname


def compare_first_split_value(row, col1, col2):
    # compare each genus with the other genera and check for matches
    genera = set()
    for taxa_name1 in row[col1]:
        genus1 = taxa_name1.split(" ")[0]

        for taxa_name2 in row[col2]:
            genus2 = taxa_name2.split(" ")[0]

            if genus1 == genus2:
                genera.add(genus1)

    return genera


def set_2_comma_seperated(df: pd.DataFrame, columns: list):
    # convert the set in a comma seperated string
    for column in columns:
        df[column] = df.apply(lambda row: ", ".join(row[column]), axis=1)


if __name__ == "__main__":
    args = create_argparser()

    # read in output of microbeMASST -> tsv with features
    df = pd.read_csv(args.feature_counts, sep="\t", index_col="Feature")

    # reshape to Feature as unique index and taxaname_file as a list
    df = df.groupby("Feature")["Taxaname_file"].apply(set).reset_index()
    df = df.set_index("Feature")
    df = df.set_index(df.index.str.upper())

    # rename column for species of microbeMASST
    df.rename(columns={"Taxaname_file": "species_microbeMASST"}, inplace=True)

    # add column with number of microbeMASST species
    df["#_microbeMASST"] = df.apply(lambda row: len(row["species_microbeMASST"]), axis=1)

    # add ncbi species as set to df
    temp_df = pd.read_csv(args.feature_counts, sep="\t", index_col="Feature")

    df_ncbi_species = temp_df.groupby("Feature")["ncbi_species"].apply(set).reset_index()
    df_ncbi_species = df_ncbi_species.set_index("Feature")
    df_ncbi_species = df_ncbi_species.set_index(df.index.str.upper())

    # rename to species_ncbi to match rest of columns
    df["species_ncbi"] = df_ncbi_species["ncbi_species"]

    # add column with number of ncbi species
    df["#_ncbi"] = df.apply(lambda row: len(row["species_ncbi"]), axis=1)

    # read in the mapping of sample ID and according species
    sampleID_species_mapping = pd.read_excel(args.sample_species, sheet_name="Sheet1")

    # read in expression table of xcmsViewer
    expression_table = pd.read_csv(args.expression_table, sep="\t", index_col="feature")

    # get list of expressed sample IDs for each feature
    feature_species_sample = {}
    feature_sample_IDs = {}
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

        # add collected species names and sample IDs to feature
        feature_species_sample[feature] = species_names
        feature_sample_IDs[feature] = sampleIDs

    # add dictionary values as new column of df
    df["species_samples"] = pd.Series(feature_species_sample)
    df["sample_IDs"] = pd.Series(feature_sample_IDs)

    # add column to show the number of samples found for feature
    df["#_samples"] = df.apply(lambda row: len(row["sample_IDs"]), axis=1)

    # reshape taxa names to format of mapping sample ID to taxa
    df["species_samples"] = df["species_samples"].apply(lambda x: {split_and_concat(name) for name in x})

    # add column which includes Taxanames that are in both, microbeMASST result and sample
    df["matching_species_microbeMASST"] = df.apply(lambda row: row["species_microbeMASST"].intersection(row["species_samples"]), axis=1)

    # add column with number of matching species microbeMASST
    df["#_matching_species_microbeMASST"] = df.apply(lambda row: len(row["matching_species_microbeMASST"]), axis=1)

    # compare genera file
    df['matching_genera_microbeMASST'] = df.apply(lambda row: compare_first_split_value(row, 'species_microbeMASST', 'species_samples'), axis=1)

    # add column with number of matching genera microbeMASST
    df["#_matching_genera_microbeMASST"] = df.apply(lambda row: len(row["matching_genera_microbeMASST"]), axis=1)

    # add column which includes species that are in both, microbeMASST result and sample
    df["matching_species_ncbi"] = df.apply(lambda row: row["species_ncbi"].intersection(row["species_samples"]), axis=1)

    # add column with number of matching species ncbi
    df["#_matching_species_ncbi"] = df.apply(lambda row: len(row["matching_species_ncbi"]), axis=1)

    # compare genera file
    df['matching_genera_ncbi'] = df.apply(lambda row: compare_first_split_value(row, 'species_ncbi', 'species_samples'), axis=1)

    # add column with number of matching species
    df["#_matching_genera_ncbi"] = df.apply(lambda row: len(row["matching_genera_ncbi"]), axis=1)

    # convert the set columns into comma seperated strings
    set_2_comma_seperated(df, ["species_microbeMASST", "species_ncbi", "species_samples", "sample_IDs", "matching_species_microbeMASST", "matching_genera_microbeMASST", "matching_species_ncbi", "matching_genera_ncbi"])

    # write mapping_table as tsv
    df.to_csv(args.output, sep='\t')

"python pipeline/create_mapping_table.py --feature_counts files/summary_counts_microbe.tsv --sample_species files/Bacterial_strain_ID.xlsx --expression_table files/pos_expression.tsv -o output/mapping.tsv"






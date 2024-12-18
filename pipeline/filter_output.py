import pandas as pd
import argparse

def filter(args, file_path:str):
    # tsv to pandas df
    df = pd.read_csv(file_path, sep='\t')
    # filter for either species level, genus query or species query
    splits = df["Taxaname_file"].str.split(" ")
    if args.species_level:
        filtered_df = df[splits.str.len() > 1]
    elif args.genus:
        filtered_df = df[splits.str[0].str.lower() == args.genus.lower()]
    elif args.species:
        valid_splits = splits[splits.str.len() > 1]
        combined_splits = valid_splits.str[0] + " " + valid_splits.str[1]
        filtered_df = df.loc[valid_splits.index[combined_splits.str.lower() == args.species.lower()]]
    else:
        filtered_df = df

    # save filtered df as tsv
    filtered_df.to_csv(f'{args.output}/filtered_{file_path.split("/")[-1]}', sep='\t')

if __name__ == "__main__":
    # ArgParser
    parser = argparse.ArgumentParser(description="Filter for output of MicrobeMASST")

    group = parser.add_mutually_exclusive_group(required=True) # only allow --species_level, --genus or --species

    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the input TSV file (requires --output)')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to the directory, name is automatically generated! (requires --input)')
    #parser.add_argument('--overview', default=False, action="store_true", help='Input is a overview tsv with group and file path to summary feature as columns')

    # choose 1 of these 3
    group.add_argument('--species_level', default=False, action="store_true", help='Filter by species level')
    group.add_argument('--genus', type=str, help='Genus to filter by')
    group.add_argument('--species', type=str, help='Species to filter by')

    args = parser.parse_args()

    # if args.overview: # multiple file for output filtering
    #     # read overview file
    #     overview = pd.read_csv(args.input, sep='\t')

    #     # run for each summary tsv
    #     for index, row in overview.iterrows():
    #         #try: 
    #         filter(args, row["FilePath"])
    #         #except Exception as e:
    #         #    print(f"Processing Error: {e}")
    #         #    continue
    # else:
       # one file for output filtering
    filter(args, args.input)

    




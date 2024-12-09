import pandas as pd
import argparse


# ArgParser
parser = argparse.ArgumentParser(description="Filter for output of MicrobeMASST")

group = parser.add_mutually_exclusive_group(required=True) # only allow --species_level, --genus or --species

parser.add_argument('-i', '--input', type=str, required=True, help='Path to the input TSV file')
parser.add_argument('-o', '--output', type=str, required=True, help='Path to the directory, name is automatically generated!')
group.add_argument('--species_level', default=False, action="store_true", help='Filter by species level')
group.add_argument('--genus', type=str, help='Genus to filter by')
group.add_argument('--species', type=str, help='Species to filter by')

args = parser.parse_args()

# tsv to pandas df
df = pd.read_csv(args.input, sep='\t')

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
filtered_df.to_csv(f'{args.output}/filtered_{args.input.split("/")[-1]}', sep='\t')
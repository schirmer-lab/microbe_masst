import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Filter for output of MicrobeMASST")
parser.add_argument('-i','--input', type=str, required=True, help='Path to the input TSV file')
parser.add_argument('-o','--output', type=str, required=True, help='Path to the output TSV file')
parser.add_argument('--species_level', default=False, action=argparse.BooleanOptionalAction, help='Filter by species level')
parser.add_argument('--genus', type=str, help='Genus to filter by')
parser.add_argument('--species', type=str, help='Species to filter by')

args = parser.parse_args()

df = pd.read_csv(args.input, sep='\t')

splits = df["Taxaname_file"].str.split(" ")
if args.species_level:
    filtered_df = df[splits.str.len() > 1]
elif args.genus:
    filtered_df = df[splits.str[0] == args.genus]
elif args.species:
    filtered_df = df[' '.join([splits.str[0],splits.str[1]]) == args.species] #TODO: Check if this works
else:
    filtered_df = df


filtered_df.to_csv(f'{args.output}/filtered_{args.input.split("/")[-1]}', sep='\t')
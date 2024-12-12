import pandas as pd
import argparse
import requests


def setup_argparser():
    parser = argparse.ArgumentParser(description="Filter for output of MicrobeMASST")

    group = parser.add_mutually_exclusive_group(required=True)  # only allow --species_level or --species

    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to the input TSV file')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Path to the directory, name is automatically generated!')
    group.add_argument('--species_level', default=False, action="store_true",
                       help='Filter by species level')
    group.add_argument('--species', type=str,
                       help='Species to filter by')

    args = parser.parse_args()

    return args


def get_taxonomy_rank(tax_ids):
    # check for valid tax IDS, if none return NAs of length input
    valid_tax_ids = [tax_id for tax_id in tax_ids if tax_id.isdigit()]
    if not valid_tax_ids:
        return [pd.NA] * len(tax_ids)

    # URL and input for NCBI taxa information
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "taxonomy",
        "id": ",".join(map(str, valid_tax_ids)),  # Join TaxIDs with commas
        "retmode": "json",
    }

    # output and its jsonification
    response = requests.get(url, params=params)
    data = response.json()

    # extract ranks from output, incorporate invalids accordingly
    ranks = []
    for tax_id in tax_ids:
        if tax_id.isdigit():
            rank = data['result'][str(tax_id)]['rank']
            ranks.append(rank)
        else:
            ranks.append(pd.NA)

    return ranks


def batch_query(tax_ids, batch_size=10):
    for i in range(0, len(tax_ids), batch_size):
        yield tax_ids[i:i+batch_size]

if __name__ == "__main__":
    # retrieve arguments from argparser
    args = setup_argparser()

    # tsv to pandas df
    df = pd.read_csv(args.input, sep='\t')

    # get ranks fpr each taxonomy ID
    ranks = []
    for batch in batch_query(df["Taxa_NCBI"], 50):
        ranks.extend(get_taxonomy_rank(batch))

    # append rank column to df
    df["ranks"] = ranks

    # filter for either species level, genus query or species query
    if args.species_level:
        filtered_df = df[df["ranks"].isin(["species", ""])]
    elif args.species:
        splits = df["Taxaname_file"].str.split(" ")
        valid_splits = splits[splits.str.len() > 1]
        combined_splits = valid_splits.str[0] + " " + valid_splits.str[1]
        filtered_df = df[df["ranks"].isin(["species", ""]) & (combined_splits.str.lower() == args.species.lower())]
    else:
        filtered_df = df

    # save filtered df as tsv
    filtered_df.to_csv(f'{args.output}/filtered_{args.input.split("/")[-1]}', sep='\t')

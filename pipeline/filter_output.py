import pandas as pd
import argparse
import requests
import os


def setup_argparser():
    parser = argparse.ArgumentParser(description="Filter for output of MicrobeMASST")

    group = parser.add_mutually_exclusive_group(required=True)  # only allow --species_level, --genus or --species

    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to the input TSV file')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Path to the directory, name is automatically generated!')
    group.add_argument('--species_level', default=False, action="store_true",
                       help='Filter by species level')
    group.add_argument('--species', type=str,
                       help='Species to filter by')
    parser.add_argument('--bacteria', default=False, action="store_true",
                       help='Filter only bacteria genbank division')

    args = parser.parse_args()

    return args


def get_ncbi_info(tax_ids):
    # check for valid tax IDS, if none return NAs of length input
    valid_tax_ids = [tax_id for tax_id in tax_ids if str(tax_id).isdigit()]
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
    scientific_names = []
    genbank_divisions = []
    for tax_id in tax_ids:
        # consider rare case all tax IDs given -> column is int
        if str(tax_id).isdigit():
            # get rank & catch error returns of NCBI
            if not "error" in data["result"][str(tax_id)].keys():
                rank = data['result'][str(tax_id)]['rank']
                scientific_name = data["result"][str(tax_id)]["scientificname"]
                genbank_division = data["result"][str(tax_id)]["genbankdivision"]
            else:
                rank = pd.NA
                scientific_name = pd.NA
                genbank_division = pd.NA

            ranks.append(rank)
            scientific_names.append(scientific_name)
            genbank_divisions.append(genbank_division)
        else:
            ranks.append(pd.NA)
            scientific_names.append(pd.NA)
            genbank_divisions.append(pd.NA)

    return ranks, scientific_names, genbank_divisions


def batch_query(tax_ids, batch_size=10):
    for i in range(0, len(tax_ids), batch_size):
        yield tax_ids[i:i+batch_size]


if __name__ == "__main__":
    # retrieve arguments from argparser
    args = setup_argparser()

    # tsv to pandas df
    df = pd.read_csv(args.input, sep='\t')

    # get ranks fpr each taxonomy ID
    scientific_names = []
    ranks = []
    genbank_divisions = []
    for batch in batch_query(df["Taxa_NCBI"], 50):
        new_ranks, new_scientific_names, new_genbank_divisions = get_ncbi_info(batch)
        ranks.extend(new_ranks)
        scientific_names.extend(new_scientific_names)
        genbank_divisions.extend(new_genbank_divisions)

    # append new columns to df
    df["ranks"] = ranks
    df["ncbi_species"] = scientific_names
    df["genbank_division"] = genbank_divisions

    # filter for either species level, genus query or species query
    if args.species_level:
        filtered_df = df[df["ranks"].isin(["species"])]
    elif args.species:
        splits = df["Taxaname_file"].str.split(" ")
        valid_splits = splits[splits.str.len() > 1]
        combined_splits = valid_splits.str[0] + " " + valid_splits.str[1]
        filtered_df = df[df["ranks"].isin(["species"]) & (combined_splits.str.lower() == args.species.lower())]
    else:
        filtered_df = df

    # filter by genbank division
    if args.bacteria:
        filtered_df = filtered_df[filtered_df["genbank_division"] == "Bacteria"]

    # ensure deep copy for filtered_df!
    filtered_df = filtered_df.copy()

    # if, even though ncbi gives species, Taxaname_file holds more names, cut it
    filtered_df.loc[:, "Taxaname_file"] = filtered_df["Taxaname_file"].apply(lambda name: " ".join(name.split(" ")[:2]))

    # if directory doesn't exist, create it!
    os.makedirs(args.output, exist_ok=True)

    # save filtered df as tsv
    filtered_df.to_csv(f'{args.output}/filtered_{args.input.split("/")[-1]}', sep='\t')

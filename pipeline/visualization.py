import pandas as pd
from ete3 import NCBITaxa
import argparse

def extract_taxids(count_matrix_file:str) -> list: # this works
    """
    Returns a list of all unique taxIds from a given count matrix
    Args:   - path to count_matrix, String
    returns: - list of all unique taxID
    """
    count_matrix = pd.read_csv(count_matrix_file, sep = "\t", index_col=0)
    return list(set(count_matrix["Taxa_NCBI"].tolist()))


def create_tree(taxIds: list, out_path: str, prefix: str):
    """
    Create a newick file with the taxonomic tree.
    Args:   - taxIds, list
            - output directory path, String
            - file prefix, String
    """
    ncbi = NCBITaxa()

    tree = ncbi.get_topology(taxIds)

    # Replace TaxIDs with taxonomic names in the tree
    for node in tree.traverse():
        if node.is_leaf():  # Rename only leaf nodes
            node.name = ncbi.get_taxid_translator([int(node.name)])[int(node.name)] # translate taxId to name

    tree.write(outfile=f"{out_path}/{prefix}_tree.nw")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Newick File for Visualization of the Taxnomic Tree.')
    parser.add_argument("--count_matrix", "-c", required=True, help='Path to the count matrix file')
    parser.add_argument("--out_path", "-o", required=True, help='Path to directory for output saving')
    parser.add_argument("--prefix", "-p", default="taxonomic", help='Prefix for filename')
    args = parser.parse_args()

    taxIds = extract_taxids(args.count_matrix)
    create_tree(taxIds, args.out_path, args.prefix)

# python visualization.py -c "../files/level4/filtered_prefix_counts_microbe.tsv" -o . -p filtered_prefix_counts_microbe
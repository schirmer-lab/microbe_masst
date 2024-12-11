import pandas as pd
from ete3 import NCBITaxa
import argparse
import random

def extract_taxids(count_matrix_file:str) -> list: # this works
    """
    Returns a list of all unique taxIds from a given count matrix
    Args:   - path to count_matrix, String
    returns: - list of all unique taxID
    """
    count_matrix = pd.read_csv(count_matrix_file, sep = "\t", index_col=0)
    return list(set(count_matrix["Taxa_NCBI"].tolist()))


def create_tree(taxIds: list, out_path: str, prefix: str, ncbi):
    """
    Create a newick file with the taxonomic tree.
    Args:   - taxIds, list
            - output directory path, String
            - file prefix, String
    """
    tree = ncbi.get_topology(taxIds)

    # save tree with taxIDs for annotation
    tree_with_taxIds = tree.copy()

    # Replace TaxIDs with taxonomic names in the tree
    for node in tree.traverse():
        if node.is_leaf():  # Rename only leaf nodes
            node.name = ncbi.get_taxid_translator([int(node.name)])[int(node.name)] # translate taxId to name

    tree.write(outfile=f"{out_path}/{prefix}_tree.nw")
    return tree_with_taxIds


def get_phylum_name(ncbi, taxid:list):
    """
    Get Phylum per taxID.
    """
    # Get the lineage of the TaxID
    lineage = ncbi.get_lineage(taxid)
    
    # Get the ranks of the lineage
    ranks = ncbi.get_rank(lineage)
    
    # Get the scientific names of the lineage
    names = ncbi.get_taxid_translator(lineage)
    
    # Find the TaxID for the rank "phylum"
    for taxid in lineage:
        if ranks[taxid] == 'phylum':
            return names[taxid]
    
    return None


def create_annotation(out_dir:str, prefix: str, tree, ncbi):
    """
    Creates annotation file with random colors and annotates on phylum level
    """
    # Assign phylum names to leaf nodes
    phylum_annotations = {}
    for node in tree.traverse():
        if node.is_leaf():  # Rename only leaf nodes
            taxid = int(node.name)
            phylum_name = get_phylum_name(ncbi, taxid)
            node.name = ncbi.get_taxid_translator([taxid])[taxid]
            if phylum_name:
                phylum_annotations[node.name] = phylum_name

    # Generate random colors for each phylum
    phylum_colors = {}
    for phylum in set(phylum_annotations.values()):
        phylum_colors[phylum] = "#{:06x}".format(random.randint(0, 0xFFFFFF)) #todo specify color palate

    # Create the iTOL annotation file
    with open(f"{out_dir}/{prefix}_itol_annotations.txt", "w") as f:
        f.write("DATASET_COLORSTRIP\n")
        f.write("SEPARATOR TAB\n")
        f.write("DATASET_LABEL\tPhylum Annotations\n")
        f.write("COLOR\t#ff0000\n")
        f.write("LEGEND_TITLE\tPhylum\n")
        f.write("LEGEND_SHAPES\t{}\n".format("\t".join(["1"] * len(phylum_colors))))
        f.write("LEGEND_COLORS\t{}\n".format("\t".join(phylum_colors.values())))
        f.write("LEGEND_LABELS\t{}\n".format("\t".join(phylum_colors.keys())))
        f.write("BORDER_WIDTH\t1\n")
        f.write("BORDER_COLOR\t#000000\n")
        f.write("DATA\n")
        for leaf_name, phylum_name in phylum_annotations.items():
            f.write("{}\t{}\n".format(leaf_name, phylum_colors[phylum_name]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Newick File for Visualization of the Taxnomic Tree.')
    parser.add_argument("--count_matrix", "-c", required=True, help='Path to the count matrix file')
    parser.add_argument("--out_path", "-o", required=True, help='Path to directory for output saving')
    parser.add_argument("--prefix", "-p", default="taxonomic", help='Prefix for filename')
    args = parser.parse_args()

    ncbi = NCBITaxa()
    taxIds = extract_taxids(args.count_matrix)
    tree = create_tree(taxIds, args.out_path, args.prefix,ncbi)
    create_annotation(args.out_path, args.prefix, tree, ncbi)

# run in pipeline folder: python visualization.py -c "../files/level4/filtered_prefix_counts_microbe.tsv" -o . -p filtered_prefix_counts_microbe
# see outputfiles: /workspaces/microbe_masst/pipeline/filtered_prefix_counts_microbe_tree.nw
#                  /workspaces/microbe_masst/pipeline/filtered_prefix_counts_microbe_itol_annotations.txt
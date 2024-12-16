import pandas as pd
from ete3 import NCBITaxa
import argparse
import random
import matplotlib.pyplot as plt

def extract_taxids(count_matrix_file:str, sep:str) -> list: # this works
    """
    Returns a list of all unique taxIds from a given count matrix
    Args:   - path to count_matrix, String
    returns: - list of all unique taxID
    """
    
    count_matrix = pd.read_csv(count_matrix_file, sep = sep, index_col=0)
    taxids = list(set(count_matrix["Taxa_NCBI"].tolist()))
    #filtered_taxids = [item for item in taxids if item.lower() != "blank" and item.lower() != "qc"]
    filtered_taxids = [item for item in taxids if str(item).lower() != "blank" and str(item).lower() != "qc"]
    return filtered_taxids


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


def create_annotation(out_dir:str, prefix: str,  tree, ncbi, color_map="Pastel1"):
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

    num_colors = len(set(phylum_annotations.values()))
    cmap = plt.get_cmap(color_map)
    colors = [cmap(i) for i in range(cmap.N-1)] # cmap.N size is + 1 for some reason
    hex_colors = ["#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255)) for r, g, b, _ in colors]
     
    # If there are more phyla than colors in the colormap, add random colors UNTESTED
    if num_colors > cmap.N:
        additional_colors = num_colors - len(colors)
        for _ in range(additional_colors):
            hex_colors.append("#{:06x}".format(random.randint(0, 0xFFFFFF)))

    # Assign colors to each phylum
    phylum_colors = {}
    for phylum, color in zip(set(phylum_annotations.values()), hex_colors):
        phylum_colors[phylum] = color


    # # Generate random colors for each phylum
    # phylum_colors = {}
    # for phylum in set(phylum_annotations.values()):
    #     phylum_colors[phylum] = "#{:06x}".format(random.randint(0, 0xFFFFFF)) #todo specify color palate

    # Create the iTOL annotation file
    with open(f"{out_dir}/{prefix}_itol_annotations.txt", "w") as f:
        #f.write("\nTREE_COLORS\n")
        f.write("DATASET_COLORSTRIP\n")
        f.write("SEPARATOR TAB\n")
        f.write("DATASET_LABEL\tPhylum Annotations\n")
        f.write("COLOR\t#ff0000\n")
        f.write("COLOR_BRANCHES\t1\n")
        f.write("LEGEND_TITLE\tPhylum\n")
        f.write("LEGEND_SHAPES\t{}\n".format("\t".join(["1"] * len(phylum_colors))))
        f.write("LEGEND_COLORS\t{}\n".format("\t".join(phylum_colors.values())))
        f.write("LEGEND_LABELS\t{}\n".format("\t".join(phylum_colors.keys())))
        f.write("BORDER_WIDTH\t1\n")
        f.write("BORDER_COLOR\t#000000\n")
        f.write("SHOW_STRIP_LABELS\t1\n")
        f.write("DATA\n")
        f.write("#NODE_ID\tCOLOR\n")
        for leaf_name, phylum_name in phylum_annotations.items():
             f.write("{}\t{}\n".format(leaf_name, phylum_colors[phylum_name]))
        
        
        # f.write("SEPARATOR TAB\n")
        # f.write("DATA\n")
        # f.write("#NODE_ID\tTYPE\tCOLOR\tLABEL_OR_STYLE\n")
        # for leaf_name, phylum_name in phylum_annotations.items():
        #     f.write("{}\trange\t{}\t{}\n".format(leaf_name, phylum_colors[phylum_name], phylum_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Newick File for Visualization of the Taxnomic Tree.')
    parser.add_argument("--count_matrix", "-c", required=True, help='Path to the count matrix file')
    parser.add_argument("--out_path", "-o", required=True, help='Path to directory for output saving')
    parser.add_argument("--prefix", "-p", default="taxonomic", help='Prefix for filename')
    parser.add_argument("--sep", "-s", default="\t", help='separator for input file')
    parser.add_argument("--color_map", "-cm", default="Set1", help='color map for tree coloring')
    args = parser.parse_args()

    ncbi = NCBITaxa()
    taxIds = extract_taxids(args.count_matrix, args.sep)
    tree = create_tree(taxIds, args.out_path, args.prefix,ncbi)
    create_annotation(args.out_path, args.prefix, tree, ncbi, args.color_map)

# run in pipeline folder: python visualization.py -c "../files/level4/filtered_prefix_counts_microbe.tsv" -o "../report/output" -p filtered_prefix_counts_microbe
# see outputfiles: /workspaces/microbe_masst/pipeline/filtered_prefix_counts_microbe_tree.nw
#                  /workspaces/microbe_masst/pipeline/filtered_prefix_counts_microbe_itol_annotations.txt

# python visualization.py -c "../data/microbe_masst_table.csv" -o "../report/output" -p data_microbe_csv -s ","
#
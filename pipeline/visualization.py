import pandas as pd
from ete3 import NCBITaxa
import argparse
import random
import matplotlib.pyplot as plt
import pickle
import csv
import re

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

def create_translation(taxIds: list):
    """
    Translate ncbi taxID to name and write in dataframe and save in csv.
    Args:   - taxIds, list
    """

    # translate ncbi taxID to name and write in dataframe
    taxid2name =  ncbi.get_taxid_translator(taxIds)
    df = pd.DataFrame(list(taxid2name.items()), columns=["taxIds", "name"])

    # write to csv
    df.to_csv(f"{out_path}/{prefix}_taxId_translation.csv", index=False)

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
    Args:   - ncbi, object of NCBITaxa
            - taxIds, list
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

def load_color_dict_from_csv(csv_path):
    color_dict = {}
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            phylum = row[0].strip()
            color = row[1].strip()
            color_dict[phylum] = color
    return color_dict


def create_annotation(out_dir:str, prefix: str,  tree, ncbi, color_map="Set1", color_dict_path=None, max_phylum_groups=8):
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
                # remove all special letters and replace with _
                parsed_node = re.sub(r'[=:()\[\]]', '_', node.name)
                phylum_annotations[parsed_node] = phylum_name


    # Count occurrences of each phylum
    phylum_counts = {}
    for phylum in phylum_annotations.values():
        phylum_counts[phylum] = phylum_counts.get(phylum, 0) + 1

    # Determine phyla to keep and group others
    sorted_phyla_by_size = sorted(phylum_counts.items(), key=lambda x: (-x[1], x[0]))
    if len(sorted_phyla_by_size) > max_phylum_groups:
        # Keep the 8 largest phyla, group the rest into "Other"
        phyla_to_keep = sorted([phylum for phylum, count in sorted_phyla_by_size[:max_phylum_groups]])
        phyla_to_keep.append("Other")
        for leaf_name, phylum_name in phylum_annotations.items():
            if phylum_name not in phyla_to_keep:
                phylum_annotations[leaf_name] = "Other"
    else:
        # Keep all phyla if 8 or fewer
        phyla_to_keep = sorted(phylum_counts.keys())

    if color_dict_path==None:
        # using "Set1" color map
        # get colors from color map for phylum_groups
        num_colors = min(max_phylum_groups, len(phyla_to_keep)) 

        cmap = plt.get_cmap(color_map)
        colors = [cmap(i / (9 - 1)) for i in range(9)]  # Compute exactly num_colors(8) colors
        hex_colors = ["#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255)) for r, g, b, _ in colors]

        # Assign colors to phyla, ensuring "Other" is grey
        phylum_colors = {phylum: hex_colors[i] for i, phylum in enumerate(phyla_to_keep) if phylum != "Other"}
        other_color = '#999999'
        if "Other" in phyla_to_keep:
            phylum_colors["Other"] = other_color
        
    
    else:
        # use color_dict_path to get colors
        if color_dict_path.endswith('.pkl'):
            # Load from pickle file
            with open(color_dict_path, "rb") as file:
                color_dict = pickle.load(file)
        elif color_dict_path.endswith('.csv'):
            # Load from CSV file
            color_dict = load_color_dict_from_csv(color_dict_path)
        else:
            raise ValueError("Color dictionary file must be a .pkl or .csv file.")

        phylum_colors = color_dict
        if "Other" not in phylum_colors.keys():
            phylum_colors["Other"] = '#999999'

        for leaf_name, phylum_name in phylum_annotations.items():
            if phylum_name not in phylum_colors.keys():
                phylum_annotations[leaf_name] = "Other"


    
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
    parser.add_argument("--color_dict_path", "-cd", default=None, help='path to pickle: color dict for tree coloring')
    parser.add_argument("--max_phylum_groups", "-mpg", default=8, help='maximum number of phylum groups to show in tree')
    args = parser.parse_args()

    ncbi = NCBITaxa()
    taxIds = extract_taxids(args.count_matrix, args.sep)
    #create_translation(taxIds)
    tree = create_tree(taxIds, args.out_path, args.prefix,ncbi)
    create_annotation(args.out_path, args.prefix, tree, ncbi, args.color_map, args.color_dict_path, args.max_phylum_groups)

# run in pipeline folder: python visualization.py -c "../files/level4/filtered_prefix_counts_microbe.tsv" -o "../report/output" -p filtered_prefix_counts_microbe
# see outputfiles: /workspaces/microbe_masst/pipeline/filtered_prefix_counts_microbe_tree.nw
#                  /workspaces/microbe_masst/pipeline/filtered_prefix_counts_microbe_itol_annotations.txt

# use no color dict
# python visualization.py -c "../data/microbe_masst_table.csv" -o "../report/output" -p data_microbe_csv -s ","
# python visualization.py -c "../data/microbe_masst_table.csv" -o "../report/output" -p sorted_data_microbe_csv -s ","

# use a color dict: pkl or csv
# python visualization.py -c "../data/microbe_masst_table.csv" -o "../report/output" -p sorted_cdict_pkl_data_microbe_csv -s "," -cd "color_dict.pkl"
# python visualization.py -c "../data/microbe_masst_table.csv" -o "../report/output" -p sorted_cdict_csv_microbe_csv -s "," -cd "color_dict.csv"

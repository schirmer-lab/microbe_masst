from ete3 import NCBITaxa,Tree
import argparse
import matplotlib.pyplot as plt
import re

parser = argparse.ArgumentParser(description='Create Newick File for Visualization of the Taxnomic Tree.')
parser.add_argument("--nw", required=True, help='Path to the newick file')
parser.add_argument("--out_dir", "-o", required=True, help='Path to directory for output saving')
parser.add_argument("--prefix", "-p", default="db", help='Prefix for filename')
parser.add_argument("--color_map", "-cm", default="Set1", help='color map for tree coloring')
args = parser.parse_args()

# Path to your Newick file
newick_file = args.nw

# Load the tree from the Newick file
tree = Tree(newick_file)


def translate_tree(tree, out_dir: str, prefix: str, ncbi):
    """
    Create a newick file with the taxonomic name from tree with taxIds.
    Args:   - tree with taxIds
            - output directory path, String
            - file prefix, String
    """

    # create copy of tree for translated node names
    tree_translate = tree.copy()

    # Replace TaxIDs with taxonomic names in the tree
    for node in tree_translate.traverse():
        if node.is_leaf():  # Rename only leaf nodes
            node.name = ncbi.get_taxid_translator([int(node.name)])[int(node.name)] # translate taxId to name

    tree_translate.write(outfile=f"{out_dir}/{prefix}_tree.nw")

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


def create_annotation(out_dir:str, prefix: str,  tree, ncbi, color_map="Set1", max_phylum_groups=8):
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

    #get colors
    cmap = plt.get_cmap(color_map)
    colors = [cmap(i / (9 - 1)) for i in range(9)]  # Compute exactly num_colors(8) colors
    hex_colors = ["#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255)) for r, g, b, _ in colors]

    # Assign colors to phyla, ensuring "Other" is grey
    phylum_colors = {phylum: hex_colors[i] for i, phylum in enumerate(phyla_to_keep) if phylum != "Other"}
    other_color = '#999999'
    if "Other" in phyla_to_keep:
        phylum_colors["Other"] = other_color
        
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
        

ncbi = NCBITaxa()
translate_tree(tree, args.out_dir, args.prefix, ncbi)
create_annotation(args.out_dir, args.prefix, tree, ncbi, args.color_map)

# python visualize_database.py --nw "../trees/microbe_masst_tree/microbemasst_tree_trimmed.nw" -o "output_rerun" -p "db_microbe_trimmed"
"""
i got this warning when running:
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 335058 was translated into 93681
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 137779 was translated into 184924
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 1796621 was translated into 1505
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 40452 was translated into 3028765
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 139420 was translated into 2498619
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 507467 was translated into 2922229
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 76330 was translated into 1125955
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 40433 was translated into 2028083
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 492052 was translated into 64659
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
/opt/conda/lib/python3.10/site-packages/ete3/ncbi_taxonomy/ncbiquery.py:243: UserWarning: taxid 346642 was translated into 3094984
  warnings.warn("taxid %s was translated into %s" %(taxid, merged_conversion[taxid]))
"""

# python visualize_database.py --nw "output/microbe_tree_from_json_taxId.nw" -o "output_rerun" -p "db_microbe_json"
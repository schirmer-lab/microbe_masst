from ete3 import Tree
import pandas as pd
from ete3 import NCBITaxa,Tree
import argparse
import random

parser = argparse.ArgumentParser(description='Create Newick File for Visualization of the Taxnomic Tree.')
parser.add_argument("--nw", required=True, help='Path to the newick file')
parser.add_argument("--out_dir", "-o", required=True, help='Path to directory for output saving')
parser.add_argument("--prefix", "-p", default="db", help='Prefix for filename')
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

ncbi = NCBITaxa()
translate_tree(tree, args.out_dir, args.prefix, ncbi)
create_annotation(args.out_dir, args.prefix, tree, ncbi)

# python visualize_database.py --nw "../trees/microbe_masst_tree/microbemasst_tree_raw.nw" -o "output" -p "db_microbe_raw"
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

# python visualize_database.py --nw "output/microbe_tree_from_json_taxId.nw" -o "output" -p "db_microbe_json"
import json
from ete3 import NCBITaxa
import argparse
import re
import matplotlib.pyplot as plt


"""
Goal translate masst_tree.json to .nw files and create annotation file to visualize the microbeMASST database
"""

def get_str_of_species(node, key="NCBI") -> str:
    """
    Extract from all leaf nodes the key information if rank is species and returns them all ',' seperated.
    Args:
      - node: node of json file
      - key (str): key to get from node, default is to get the taxaID
    """
    if "name" in node and node["name"] == "Blank" or node["name"] == "QC":
        return ""
    # Base case: Leaf node
    if "children" not in node or not node["children"]:
    #if "type" in node and node["type"] == "leaf":
      return f"{node[f'{key}'] if f'{key}' in node and 'Rank' in node and node['Rank'].lower() == 'species' else ''}"
    
    # Recursive case: Internal node with children
    children_newick = ",".join(
        child_newick for child_newick in (get_str_of_species(child, key) for child in node["children"]) if child_newick
    )
    return f"{children_newick},{node[f'{key}'] if f'{key}' in node else ''}"


def str_to_newick(species_str,out_path, prefix, ncbi):
    """
    From a string containing species taxaIDs and ',' separated as topological newick tree
    Args:
      - node: node of json file
      - key (str): key to get from node, default is to get the taxaID
    """
    all_species_unique = list(set(species_str.split(",")))
    all_species_unique = [s for s in all_species_unique if s != ""] # drop empty entries
    tree = ncbi.get_topology(all_species_unique)

    # save tree with taxIDs for annotation
    tree_with_taxIds = tree.copy()

    # Replace TaxIDs with taxonomic names in the tree for the leafs
    for node in tree.traverse():
        if node.is_leaf():  # Rename only leaf nodes
            node.name = ncbi.get_taxid_translator([int(node.name)])[int(node.name)] # translate taxId to name

    # write to newick file
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


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Create Newick File for Visualization of the Taxnomic Tree.')
  parser.add_argument("--json", required=True, help='Path to the json file')
  parser.add_argument("--out_dir", "-o", required=True, help='Path to directory for output saving')
  parser.add_argument("--prefix", "-p", default="db", help='Prefix for filename')
  parser.add_argument("--color_map", "-cm", default="Set1", help='color map for tree coloring')
  args = parser.parse_args()

  # Load the JSON file
  with open(args.json, "r") as file:
      tree_data = json.load(file)
  ncbi = NCBITaxa()

  # write nw file with taxIds
  species_str_id = get_str_of_species(tree_data, "NCBI")
  tree = str_to_newick(species_str_id, args.out_dir, args.prefix, ncbi)
  
  # create annotation
  create_annotation(args.out_dir, args.prefix, tree, ncbi, args.color_map)



# run example: python visualize_db_from_json.py --json "../data/microbe_masst_tree.json" -o "output_vis_db" -p "data_microbe_json"
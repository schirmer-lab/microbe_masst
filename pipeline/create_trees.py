from ete3 import NCBITaxa, Tree

# Initialize NCBITaxa
ncbi = NCBITaxa()

# List of TaxIDs
taxid_list = [9606, 562, 7227]  # Example: Human, E. coli, Drosophila

# Get lineages
lineage_dict = {taxid: ncbi.get_lineage(taxid) for taxid in taxid_list}

lineages = [ncbi.get_lineage(taxid) for taxid in taxid_list]

# Build a taxonomic tree
tree = ncbi.get_topology(taxid_list)

def get_phylum_name(taxid):
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

# # EITHER: Assign phylum names to leaf nodes
# # Assign phylum names to leaf nodes
# use_phylum = False
# if use_phylum:
#     for node in tree.traverse():
#         if node.is_leaf():  # Rename only leaf nodes
#             node.name = get_phylum_name(int(node.name))
# else:
#     #OR: Assign scientific names to internal nodes
#     for node in tree.traverse():
#         if node.is_leaf():  # Rename only leaf nodes
#             node.name = f"{ncbi.get_taxid_translator([int(node.name)])}"
import random

# Assign phylum names to leaf nodes
phylum_annotations = {}
for node in tree.traverse():
    if node.is_leaf():  # Rename only leaf nodes
        taxid = int(node.name)
        phylum_name = get_phylum_name(taxid)
        node.name = ncbi.get_taxid_translator([taxid])[taxid]
        if phylum_name:
            phylum_annotations[node.name] = phylum_name

# Generate random colors for each phylum
phylum_colors = {}
for phylum in set(phylum_annotations.values()):
    phylum_colors[phylum] = "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Create the iTOL annotation file
with open("itol_annotations.txt", "w") as f:
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

# Visualize the tree
print(tree)
#tree.show()

# Optionally, save to Newick format
tree.write(outfile="test.phylogenetic_tree.nw")


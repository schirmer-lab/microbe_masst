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

# EITHER: Assign phylum names to leaf nodes
# Assign phylum names to leaf nodes
use_phylum = False
if use_phylum:
    for node in tree.traverse():
        if node.is_leaf():  # Rename only leaf nodes
            node.name = get_phylum_name(int(node.name))
else:
    #OR: Assign scientific names to internal nodes
    for node in tree.traverse():
        if node.is_leaf():  # Rename only leaf nodes
            node.name = f"{ncbi.get_taxid_translator([int(node.name)])}"
# Visualize the tree
print(tree)
#tree.show()

# Optionally, save to Newick format
tree.write(outfile="test.phylogenetic_tree.nw")


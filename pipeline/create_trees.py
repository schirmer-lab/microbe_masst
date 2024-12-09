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

# Visualize the tree
print(tree)
#tree.show()

# Optionally, save to Newick format
tree.write(outfile="test.phylogenetic_tree.nw")


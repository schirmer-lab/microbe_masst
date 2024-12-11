# does not work yet
import pandas as pd
from ete3 import Tree, NCBITaxa

def extract_taxids(path:str): # this works
    """
    Returns a list of all unique taxIds from a given count matrix
    Args:   - path to count_matrix, String
    returns: - list of all unique taxID
    """
    count_matrix = pd.read_csv(path, sep = "\t", index_col=0)
    return list(set(count_matrix["Taxa_NCBI"].tolist()))

def extract_lineage(taxIds: list): # this works too
    """
    gets the lineage per taxid and translates the taxid to actual name for printing out
    Args:   - taxids, list
    returns: - returns the lineages per taxid
    """
    # Initialize the NCBI Taxa database
    ncbi = NCBITaxa()

    # Fetch lineage for each TaxID
    lineages = {taxid: ncbi.get_lineage(taxid) for taxid in taxids}

    # Get names for each TaxID in the lineages
    lineage_names = {
        taxid: [ncbi.get_taxid_translator([t])[t] for t in lineage]
        for taxid, lineage in lineages.items()
    }

    # Print lineages for verification
    for taxid, names in lineage_names.items():
        print(f"TaxID: {taxid}, Lineage: {names}")
    
    return lineages

def create_newick(lineages): # this does NOT work yet apparently newick string is wrong or not readable??
    """
    Create a Newick representation from lineages.
    """
    tree_structure = {}
    
    # Populate tree structure
    for taxid, lineage in lineages.items():
        current_level = tree_structure
        for tax in lineage:
            if tax not in current_level:
                current_level[tax] = {}
            current_level = current_level[tax]
    
    # Recursive function to convert the nested dictionary to Newick format
    def dict_to_newick(d):
        if not d:
            return ""
        return "(" + ",".join(f"{k}{dict_to_newick(v)}" for k, v in d.items()) + ")"

    return dict_to_newick(tree_structure) + ";"


if __name__ == "__main__":
    taxids = extract_taxids("../files/level4/filtered_prefix_counts_microbe.tsv")
    lineages = extract_lineage(taxids)

    # Generate Newick string
    newick = create_newick(lineages)
    print("Newick string:", newick)

    # Create and render tree
    tree = Tree(newick)
    tree.render("phylogenetic_tree.png", w=800, units="px")
    print("Tree saved as 'phylogenetic_tree.png'")
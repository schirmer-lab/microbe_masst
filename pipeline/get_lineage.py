#from ncbi_taxonomist import Taxonomist
import pandas as pd
from ete3 import Tree, NCBITaxa

def extract_taxids(path:str):
    """
    Get all the feature ids that have the specified annotation level
    Args:   - path to count_matrix, String
    returns: - list of all unique taxID
    """
    count_matrix = pd.read_csv(path, sep = "\t", index_col=0)
    return list(set(count_matrix["Taxa_NCBI"].tolist()))

def extract_lineage(taxIds: list):
    # Initialize the NCBI Taxa database
    ncbi = NCBITaxa()

    newick = ""
    for taxid in taxIds:
        try:
            lineage = ncbi.get_lineage(taxid)
            lineage_names = ncbi.get_taxid_translator(lineage)
        except ValueError as e:
            print(f"Could not find lineage to taxID: {taxid}")

        # Construct Newick format from the lineage
        newick = "(" + ",".join(f"{lineage_names[tax]}" for tax in lineage) + ");"

    # Create a tree from the Newick string
    tree = Tree(newick)

    # Display the tree structure
    print(tree)

    # Render the tree to an image
    tree.render("phylogenetic_tree.png", w=500, units="px")

    """# Specify the TaxID
    taxid = 9606  # Example: Human

    # Get lineage TaxIDs
    #rank = ncbi.get_rank(taxid)
    lineage = ncbi.get_lineage(taxid)

    # Get lineage names
    lineage_names = [ncbi.get_taxid_translator([tid])[tid] for tid in lineage]
    matching_rank = [ncbi.get_rank([tid])[tid] for tid in lineage]
    print(matching_rank)
    print(lineage_names)
    combined_dict = {k: v for k, v in zip(matching_rank, lineage_names)}

    # Create a Newick string for the tree
    newick = "(" + ",".join(f"{lineage_names[tax]}" for tax in lineage) + ");"

    # Build the tree
    tree = Tree(newick)"""

    """# Print the lineage
    print("TaxID Lineage:", lineage)
    print("Lineage Names:", lineage_names)
        # Initialize Taxonomist
        taxonomist = Taxonomist()

        newick = ""
        for taxid in taxIds:
            try:
                lineage = taxonomist.lineage(taxid)  # Nonexistent TaxID
                print(lineage)
            except ValueError as e:
                print(f"Could not find lineage to taxID: {taxid}")

            # Construct Newick format from the lineage
            newick = "(" + ",".join(f"{node['name']}" for node in lineage) + ");"

        # Create a tree from the Newick string
        tree = Tree(newick)

        # Display the tree structure
        print(tree)

        # Render the tree to an image
        tree.render("phylogenetic_tree.png", w=500, units="px")"""

if __name__ == "__main__":
    taxids = extract_taxids("../files/level4/filtered_prefix_counts_microbe.tsv")
    extract_lineage(taxids)
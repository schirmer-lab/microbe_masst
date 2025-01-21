import os
import pandas as pd
import re
import argparse
import csv

def merge_tsv_files_by_schema(input_directory, output_directory, pattern=r"_counts_.*\.tsv$"):
    """
    Merges TSV files by their schema (suffix) and adds a 'Feature' column.

    Parameters:
    - input_directory (str): Directory containing the TSV files.
    - output_directory (str): Directory to save the summary TSV files.
    - pattern (str): Regex pattern to identify files with the desired suffix schema.
    """
    schema_files = {}  # Dictionary to hold files grouped by their schema example for schema: microbe or microbiome

    # Step 1: Identify and group files based on the suffix schema
    for filename in os.listdir(input_directory):
        if re.search(pattern, filename):  # Match files following '_counts_*.tsv' pattern
            schema = re.search(pattern, filename).group()  # Extract schema suffix r"_counts_.*\.tsv$"
            schema_files.setdefault(schema, []).append(filename)

    if not schema_files:
        print("No matching TSV files found.")
        return

    #overview = [["FilePath"]]
    # Step 2: Process each group e.g. microbe microbiome ect
    for schema, files in schema_files.items():
        print(f"Processing schema: {schema} with {len(files)} file(s)")
        merged_dataframes = []  # List to hold dataframes for the current schema
        header_columns = None   # To validate consistent headers

        for filename in files:
            file_path = os.path.join(input_directory, filename)

            # Extract the 'Feature' prefix (everything before '_counts_')
            feature = filename.split("_counts_")[0]

            try:
                # Read the TSV file
                df = pd.read_csv(file_path, sep="\t")

                # Validate headers match across files
                if header_columns is None:
                    header_columns = list(df.columns)
                elif list(df.columns) != header_columns:
                    print(f"Warning: Headers in {filename} do not match. Skipping file.")
                    continue

                # Add the 'Feature' column
                df['Feature'] = feature

                # Append to the list of dataframes
                merged_dataframes.append(df)

                print(f"Processed file: {filename} (Feature: {feature})")

            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue

        # Merge all files for the current schema
        if merged_dataframes:
            merged_df = pd.concat(merged_dataframes, ignore_index=True)

            # Generate an output file name based on the schema
            output_file = os.path.join(output_directory, f"summary{schema}")
            merged_df.to_csv(output_file, sep="\t", index=False)
            print(f"Summary for schema '{schema}' saved to: {output_file}")
            # get group from schema (the * in _counts_*.tsv)
            #match = re.search(r"_counts_(.*?)\.tsv", schema).group(1)
            #overview.append([output_file])
        else:
            print(f"No valid files found for schema '{schema}'")
    # if len(overview) > 1:
    #     with open(f"{output_directory}/feature_summary_overview.csv", mode='w', newline='') as csv_file:
    #         csv_writer = csv.writer(csv_file, delimiter='\t')
    #         csv_writer.writerows(overview)

if __name__ == "__main__":
    # Command-line argument parser
    parser = argparse.ArgumentParser(
        description="Merge TSV files by suffix schema and add a 'Feature' column."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Directory containing TSV files."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Directory to save summary TSV files."
    )
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Run the TSV merging function
    merge_tsv_files_by_schema(args.input, args.output)

# python /workspaces/microbe_masst/pipeline/merge_tsvs.py -i /workspaces/microbe_masst/files/test_mai/out_dir -o /workspaces/microbe_masst/files/test_mai/out_dir
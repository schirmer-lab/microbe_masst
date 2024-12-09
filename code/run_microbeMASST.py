import logging
import sys
import argparse
import csv
import masst_batch_client
import masst_utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# python3 run_microbeMASST.py --input_file /path/to/input.mgf --output_dir /path/to/output_dir
# or
# python3 run_microbeMASST.py --input_csv /path/to/input.csv

def parse_args():
    parser = argparse.ArgumentParser(description="Run microbeMASST with specified input and output files or a CSV file.")
    parser.add_argument('--input_file', help='Path to the input .mgf file')
    parser.add_argument('--output_dir', help='Path to the output directory')
    parser.add_argument('--csv_file', help='Path to the CSV file containing MGF file paths in 1st col and output directories in 2nd col')
    return parser.parse_args()

def run_microbeMASST(input_file, output_dir):
    try:
        logger.info("Starting new job for input: {}".format(input_file))
        sep = (
            "," if input_file.endswith("csv") else "\t"
        )  # only used if tabular format not for mgf
        masst_batch_client.run_on_usi_list_or_mgf_file(
            in_file=input_file,
            out_file_no_extension=output_dir,
            min_cos=0.7,
            mz_tol=0.02,
            precursor_mz_tol=0.02,
            min_matched_signals=3,
            database=masst_utils.DataBase.metabolomicspanrepo_index_latest,
            parallel_queries=5,
            skip_existing=True,
            analog=False,
            sep=sep,
        )
    except Exception as e:
        logger.error(f"Error processing file {input_file}: {e}")

def read_csv_file(csv_file):
    files = []
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                raise ValueError(f"Invalid format in CSV file {csv_file}. Each row must have exactly two columns.")
            files.append((row[0], row[1]))
    return files

if __name__ == "__main__":
    args = parse_args()
    
    if args.csv_file and not args.input_file and not args.output_dir:
        files = read_csv_file(args.csv_file)
        for file, out_file in files:
            run_microbeMASST(file, out_file)
    elif args.input_file and args.output_dir:
        run_microbeMASST(args.input_file, args.output_dir)
    else:
        logger.error("You must provide either --csv_file or both --input_file and --output_dir.")
        sys.exit(1)
    
    # exit with OK
    sys.exit(0)
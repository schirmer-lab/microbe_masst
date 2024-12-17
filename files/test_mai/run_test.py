import pandas as pd
import subprocess
import argparse

parser = argparse.ArgumentParser(description='Run MicrobeMasst for each mgf')
parser.add_argument('--csv', required=True, help='Path to the input csv file')
parser.add_argument('--out', required=True, help='Path to the output dir')
args = parser.parse_args()

mgfs = pd.read_csv(args.csv, sep = ",")

for _, row in mgfs.iterrows():
    feature = row[0]
    path = row[1]
    
    subprocess.run(f"python /workspaces/microbe_masst/code/run_microbeMASST.py --input_file {path} --output_dir {args.out}/{feature}", shell = True, executable="/bin/bash")
    
# python run_test.py --csv /workspaces/microbe_masst/files/test_mai/mgfs/mgfs.csv --out /workspaces/microbe_masst/files/test_mai/out_dir/
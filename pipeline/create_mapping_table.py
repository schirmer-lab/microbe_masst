import pandas as pd
import argparse

def create_argparser():
    parser = argparse.ArgumentParser(description="Mapper for the input of microbeMASST and its results")

    parser.add_argument('--mm_output', type=str, required=True, help='Path to microbeMASST output directory')
    parser.add_argument('--sample_species', type=str, required=True, help='Path to the mapping file for sampleID to species')
    parser.add_argument('--expression_table', type=str, required=True, help='Path to the expression table of xcmsViewer')

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = create_argparser()

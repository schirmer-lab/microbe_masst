import logging
import sys
import argparse
import masst_batch_client
import masst_utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# python3 run_microbeMASST.py --input_file /Users/merit/Documents/Master_bioinfo/Semester1/SystemsBioMed/MBX/files/XcmsViewer_out/allMS2Spec_HILIC_neg_01_02.mgf --output_dir /Users/merit/Documents/Master_bioinfo/Semester1/SystemsBioMed/MBX/files/test_out/new_script
# python3 run_microbeMASST.py --input_file /Users/merit/Documents/Master_bioinfo/Semester1/SystemsBioMed/MBX/files/allMS2Spec_HILIC_neg_01_02_filtered_consensus_only.mgf --output_dir /Users/merit/Documents/Master_bioinfo/Semester1/SystemsBioMed/MBX/files/test_out/filtered/filtered_consensus_only
# python3 run_microbeMASST.py --input_file /Users/merit/Documents/Master_bioinfo/Semester1/SystemsBioMed/MBX/files/test.mgf --output_dir /Users/merit/Documents/Master_bioinfo/Semester1/SystemsBioMed/MBX/files/test_out/minimtest/test
def run_microbeMASST(input_file, output_dir):
    try:   
        logger.info("Starting new job for input: {}".format(input_file))
        sep = (
            "," if input_file.endswith("csv") else "\t"
        )  # only used if tabular format not for mgf
        # Debugging: Check if the input file is being read correctly
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
    #except:
    #    pass
    except Exception as e:
        logger.error(f"Error processing file {input_file}: {e}")

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run microbeMASST with specified input and output files')
    parser.add_argument('--input_file', required=True, help='Path to the input .mgf file')
    parser.add_argument('--output_dir', required=True, help='Path to the output directory')
    args = parser.parse_args()

    run_microbeMASST(args.input_file, args.output_dir)
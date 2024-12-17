import argparse
import pandas as pd
from pyteomics import mgf
import os
import csv


def filter_for_annotation_level(feature_table_file, annotation_level):
    """
    Get all the feature ids that have the specified annotation level
    Args:   - feature_table_file, String
            - annotation_level, int
    returns: -feature_table, set of Strings
    """
    feature_table = pd.read_csv(feature_table_file, delimiter='\t')
    # Replace "NI" with 0 and convert other values to integers
    feature_table['General|All|annot_ms2'] = feature_table['General|All|annot_ms2'].replace("NI", 0).astype(int)
    filtered_feature_table = feature_table[feature_table['General|All|annot_ms2'] >= annotation_level]
    filtered_features = set(filtered_feature_table['General|All|ID']) 
    return filtered_features

def filter_mgf_file_byID(mgf_file, filtered_features, consensus_only=False, min_ions=3):
    """
    read the given girlfriend file and filter by given ids
    Args:   - mgf_file, String 
            - filtered_features, set of Strings, output of filter_for_annotation_level
            - consensus_only, Boolean
            - min_ions, int, min number of ions to keep the spectrum
    returns: - filtered_spectra, list of dictionaries
    """
    filtered_spectra = []
    with mgf.MGF(mgf_file) as reader:
        for spectrum in reader:
            #get id
            title = spectrum.get('params', {}).get('title', '')
            start_pos = title.lower().find('feature:') + 8
            end_pos = title.find('|', start_pos)
            feature_id = title[start_pos:end_pos]

            # get number of ions
            num_ions = len(spectrum.get('m/z array', []))
            if num_ions >= min_ions:
                if consensus_only:
                    if feature_id in filtered_features and 'consensus' in title.lower():
                        filtered_spectra.append(spectrum)
                else:
                    if feature_id in filtered_features:
                        filtered_spectra.append(spectrum)
    return filtered_spectra

def filter_mgf_file_byConsensus(mgf_file, min_ions=3):
    """
    read the given girlfriend file and filter consensus spectra
    Args:   - mgf_file, String 
            - min_ions, int, min number of ions to keep the spectrum
    returns: - filtered_spectra, list of dictionaries
    """
    filtered_spectra = []
    with mgf.MGF(mgf_file) as reader:
        for spectrum in reader:
            #get id
            title = spectrum.get('params', {}).get('title', '')
            # get number of ions
            num_ions = len(spectrum.get('m/z array', []))
            if num_ions >= min_ions and 'consensus' in title.lower():
                filtered_spectra.append(spectrum)
    return filtered_spectra


def write_mgf_file(filtered_spectra, output_file):
    """
    Write the filtered spectra to a new MGF file
    Args:   - filtered_spectra, list of dictionaries
            - output_file, String
    """
   
    with open(output_file, 'w') as writer:
        for spectrum in filtered_spectra:
            writer.write('BEGIN IONS\n')
            for key, value in spectrum['params'].items():
                if key.upper() == 'PEPMASS':
                    # Handle PEPMASS separately to avoid incorrect formatting
                    if isinstance(value, tuple):
                        writer.write(f'{key.upper()}={value[0]}\n')
                    else:
                        writer.write(f'{key.upper()}={value}\n')
                else:
                    writer.write(f'{key.upper()}={str(value).upper()}\n')
            for mz, intensity in zip(spectrum['m/z array'], spectrum['intensity array']):
                writer.write(f'{str(mz).upper()} {str(intensity).upper()}\n')
            writer.write('END IONS\n\n')

def write_mgf_file_per_spectrum(filtered_spectra, output_directory):
    """
    Write each spectrum to a separate MGF file in the specified output directory
    Args:   - filtered_spectra, list of dictionaries
            - output_directory, String
    """
    # create output dir
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)
        print("create dir")
    
    csv_file_path = os.path.join(output_directory, "mgfs.csv")
    csv_rows = []
    
    for spectrum in filtered_spectra:
        #extract feature name from title
        feature_name = spectrum['params']['title'].lower().split('|')[0].replace("feature:", "").strip()
        #prepare paths
        out = os.path.join( "results", feature_name)
        output_file = os.path.join(output_directory, f"{feature_name}.mgf")
        #write mgf file
        with open(output_file, 'w') as writer:
            writer.write('BEGIN IONS\n')
            for key, value in spectrum['params'].items():
                if key.upper() == 'PEPMASS':
                    if isinstance(value, tuple):
                        writer.write(f'{key.upper()}={value[0]}\n')
                    else:
                        writer.write(f'{key.upper()}={value}\n')
                else:
                    writer.write(f'{key.upper()}={str(value).upper()}\n')
            for mz, intensity in zip(spectrum['m/z array'], spectrum['intensity array']):
                writer.write(f'{str(mz).upper()} {str(intensity).upper()}\n')
            writer.write('END IONS\n\n')
        
         # Add the file name and full path to the CSV rows
        csv_rows.append([output_file, out])
    
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(csv_rows)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter MGF file by annotation level')
    parser.add_argument('--mgf', required=True, help='Path to the input MGF file')
    parser.add_argument('--out_dir', required=True, help='Path to the output MGF file')
    parser.add_argument('--consensus_only', action='store_true', help='Boolean to filter only consensus spectra')
    parser.add_argument('--min_ions',  help='int, number of requiered ions to keep the spectrum', default=3, type=int)
    parser.add_argument('--filter_by_annotation', action='store_true', help='Boolean to filter by annotation level')
    parser.add_argument('--features',  help='Path to the feature table file', default="")
    parser.add_argument('--ann_level', help='min annotation level', default=4 , type=int)
    args = parser.parse_args()

    if args.filter_by_annotation:
        # filter by annotation level
        if args.features == "": # or not args.ann_level
            parser.error('--features is required when --filter_by_annotation is used') #and --ann_level
        filtered_features = filter_for_annotation_level(args.features, annotation_level=args.ann_level)
        filtered_spectra = filter_mgf_file_byID(args.mgf, filtered_features, consensus_only=args.consensus_only, min_ions=args.min_ions)
    
    elif args.consensus_only:
        print("Filtering only consensus spectra")
        # filter only consensus spectra
        filtered_spectra = filter_mgf_file_byConsensus(mgf_file = args.mgf, min_ions=args.min_ions)

    else:
        with mgf.MGF(args.mgf) as reader:
            filtered_spectra = [
                spectrum for spectrum in reader
                if len(spectrum.get('m/z array', [])) >= args.min_ions
            ]

    #write_mgf_file(filtered_spectra, args.out_file)
    write_mgf_file_per_spectrum(filtered_spectra, args.out_dir)

    #python3 filter_by_annotation_level.py --mgf /path/allMS2Spec_HILIC_neg_01_02.mgf --features /path/viewerTable_pos_01_02.tsv --consensus_only --out_file /path/allMS2Spec_HILIC_neg_01_02_filtered_consensus_only.mgf
    #python3 filter_by_annotation_level.py --mgf /path/allMS2Spec_HILIC_neg_01_02.mgf --features /path/viewerTable_pos_01_02.tsv --consensus_only --out_file /path/allMS2Spec_HILIC_neg_01_02_filtered_consensus_only_ann4.mgf --filter_by_annotation 

    #python3 filter_input.py --mgf ../files/allMS2Spec2024-11-27_neg.mgf --features ../files/neg_viewerTable.tsv --consensus_only --out_dir ../output/test_splitMGF --filter_by_annotation 
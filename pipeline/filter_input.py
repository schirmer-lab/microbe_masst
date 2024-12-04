import argparse
import pandas as pd
from pyteomics import mgf


def filter_for_annotation_level(feature_table_file, annotation_level):
    """
    Get all the feature ids that have the specified annotation level
    Args:   - feature_table_file, String
            - annotation_level, Char
    returns: -feature_table, set of Strings
    """
    feature_table = pd.read_csv(feature_table_file, delimiter='\t')
    feature_table = feature_table[feature_table['General|All|annot_ms2'] == annotation_level]

    return set(feature_table['General|All|ID'])

def filter_mgf_file_byID(mgf_file, filtered_features, consensus_only=False):
    """
    read the given girlfriend file and filter by given ids
    Args:   - mgf_file, String 
            - filtered_features, set of Strings, output of filter_for_annotation_level
    returns: - filtered_spectra, list of dictionaries
    """
    filtered_spectra = []
    with mgf.MGF(mgf_file) as reader:
        for spectrum in reader:
            #get id
            title = spectrum.get('params', {}).get('title', '')
            start_pos = title.find('Feature:') + 8
            end_pos = title.find('|', start_pos)
            feature_id = title[start_pos:end_pos]
            if consensus_only:
                if feature_id in filtered_features and 'Consensus' in title:
                    filtered_spectra.append(spectrum)
            else:
                if feature_id in filtered_features:
                    filtered_spectra.append(spectrum)
    return filtered_spectra

def filter_mgf_file_byConsensus(mgf_file):
    """
    read the given girlfriend file and filter consensus spectra
    Args:   - mgf_file, String 
    returns: - filtered_spectra, list of dictionaries
    """
    filtered_spectra = []
    with mgf.MGF(mgf_file) as reader:
        for spectrum in reader:
            #get id
            title = spectrum.get('params', {}).get('title', '')
            if 'Consensus' in title:
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter MGF file by annotation level')
    parser.add_argument('--mgf', required=True, help='Path to the input MGF file')
    parser.add_argument('--out_file', required=True, help='Path to the output MGF file')
    parser.add_argument('--consensus_only', action='store_true', help='Boolean to filter only consensus spectra')
    parser.add_argument('--filter_by_annotation', action='store_true', help='Boolean to filter by annotation level')
    parser.add_argument('--features',  help='Path to the feature table file')
    parser.add_argument('--ann_level', help='Annotation level to filter by, character')
    args = parser.parse_args()

    if args.filter_by_annotation:
        # filter by annotation level
        if not args.features or not args.ann_level:
            parser.error('--features and --ann_level are required when --filter_by_annotation is used')
        filtered_features = filter_for_annotation_level(args.features, annotation_level=args.ann_level)
        filtered_spectra = filter_mgf_file_byID(args.mgf, filtered_features, consensus_only=args.consensus_only)
    
    elif args.consensus_only:
        print("Filtering only consensus spectra")
        # filter only consensus spectra
        filtered_spectra = filter_mgf_file_byConsensus(args.mgf)

    else:
        # no filtering
        with mgf.MGF(args.mgf) as reader:
            filtered_spectra = [spectrum for spectrum in reader]

    write_mgf_file(filtered_spectra, args.out_file)

    #python3 filter_by_annotation_level.py --mgf /Users/merit/Documents/Master_bioinfo/Semester1/SystemsBioMed/MBX/files/XcmsViewer_out/allMS2Spec_HILIC_neg_01_02.mgf --features /Users/merit/Documents/Master_bioinfo/Semester1/SystemsBioMed/MBX/files/XcmsViewer_out/viewerTable_pos_01_02.tsv --consensus_only --out_file /Users/merit/Documents/Master_bioinfo/Semester1/SystemsBioMed/MBX/files/allMS2Spec_HILIC_neg_01_02_filtered_consensus_only.mgf
params.mgf = "/workspaces/microbe_masst/files/test_microbe_neg.mgf"
params.features = "/workspaces/microbe_masst/files/neg_viewerTable.tsv"
params.out_dir = "/workspaces/microbe_masst/files/out_test/"


process prepareInput {
    input:
    path mgf
    path features

    
    output:
    path "consensus.mgf"

    """
    echo "Preparing input..."
    echo "MGF file: $mgf"
    echo "Features file: $features"
    
    python /workspaces/microbe_masst/pipeline/filter_input.py \
        --mgf $mgf \
        --filter_by_annotation  \
        --features $features \
        --out_file consensus.mgf \
        --ann_level 1 
    """
}

process runMicrobemasst {
    input:
    path consensus
    path out_dir

    output:
    path "$out_dir"

    """
    echo "Running MicrobeMASST..."
    if [ ! -d "$out_dir" ]; then
        echo "Creating output directory: $out_dir"
        mkdir -p "$out_dir"
    fi
    python /workspaces/microbe_masst/code/run_microbeMASST.py \
        --input_file $consensus \
        --output_dir $out_dir
    """
}

workflow {
    consensus = prepareInput(params.mgf, params.features)
    runMicrobemasst(consensus, params.out_dir)
}

/* Open
    output is only saved in work dir
    parameter are fixed -> implent flags
    
*/
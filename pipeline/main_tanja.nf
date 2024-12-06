params.mgf = "/workspaces/microbe_masst/files/allMS2Spec2024-11-27_neg.mgf"
params.features = "/workspaces/microbe_masst/files/neg_viewerTable.tsv"
params.out_dir = "/workspaces/microbe_masst/files/level4"


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
        --consensus_only \
        --ann_level 4 \
        --min_ions 7
    """
}

process createOutputDir {
    input:
    val out_dir

    output:
    val out_dir

    """
    if [ ! -d "$out_dir" ]; then
        mkdir -p "$out_dir"
    fi
    """
}

process runMicrobemasst {
    input:
    path consensus
    path out_dir

    output:
    path "$out_dir"

    """
    python /workspaces/microbe_masst/code/run_microbeMASST.py \
        --input_file $consensus \
        --output_dir "${out_dir}/prefix"
    """
}

workflow {
    consensus = prepareInput(params.mgf, params.features)
    out_dir = createOutputDir(params.out_dir)
    runMicrobemasst(consensus, params.out_dir)
}

/* Open
    output is only saved in work dir
    parameter are fixed -> implent flags
    
*/
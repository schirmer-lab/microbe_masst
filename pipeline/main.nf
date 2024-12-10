
process prepareInput {
    input:
    path mgf
    path features

    output:
    path "consensus.mgf"

    script:
    // check if parameters are set
    def filter_flag = params.filter_by_annotation ? '--filter_by_annotation' : ''
    def consensus_flag = params.consensus_only ? '--consensus_only' : ''
    

    """
    echo "Preparing input..."
    echo "MGF file: $mgf"
    echo "Features file: $features"


    python /workspaces/microbe_masst/pipeline/filter_input.py \
        --mgf $mgf \
        $filter_flag  \
        --features $features \
        --out_file consensus.mgf \
        $consensus_flag \
        --ann_level ${params.ann_level} \
        --min_ions ${params.min_ions}
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
    runMicrobemasst(consensus, out_dir)
}


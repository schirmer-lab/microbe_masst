
process prepareInput {
    input:
    path mgf
    path features
    
    output:
    path "./mgf_file"

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
        --out_dir "./mgf_file" \
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
    path mgfs_file_dir
    path out_dir

    output:
    publishDir "$out_dir", mode: 'copy'

    """
    python /workspaces/microbe_masst/code/run_microbeMASST.py \
        --csv_file ${mgfs_file_dir}/mgfs.csv
    
   
    """
}

workflow {
    log_params(params.out_dir)
    mgfs_file_dir = prepareInput(params.mgf, params.features)
    out_dir = createOutputDir(params.out_dir)
    runMicrobemasst(mgfs_file_dir, out_dir)
}


def log_params(out_dir) {
    def pipeline_info_dir = "${out_dir}/pipeline_info"
    
    new File(pipeline_info_dir).mkdirs()

    def params_log = "${pipeline_info_dir}/run_parameters.log"
    new File(params_log).text = """
    Workflow Parameters:
    --------------------
    mgf file: ${params.mgf ?: 'not provided'}
    features file: ${params.features ?: 'not provided'}
    output directory: ${params.out_dir ?: 'not provided'}
    annotation level: ${params.ann_level ?: 'default'}
    min ions: ${params.min_ions ?: 'default'}
    filter by annotation: ${params.filter_by_annotation ?: false}
    consensus only: ${params.consensus_only ?: false}
    """
}
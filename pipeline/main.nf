
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

process runMicrobemasst {
    input:
    path mgfs_file_dir
    //path out_dir

    output:
    path "results"
    //publishDir "$out_dir", mode: 'copy'

    """
    python /workspaces/microbe_masst/code/run_microbeMASST.py \
        --csv_file ${mgfs_file_dir}/mgfs.csv

    """
}

process merge_tsv {
    // merge the count tsvs per feature output of microbeMasst per group (e.g. microbe, microbiome)
    input:
    path dir

    output:
    path "${dir}/summary_counts_*.tsv", emit: summary_files
    
    """
    python /workspaces/microbe_masst/pipeline/merge_tsvs.py \
            -i ${dir} \
            -o ${dir}
    """
}

process filter_output {
    // rn im setting filtering by species as default for all nextflow runs... but TODO allow options as scripts shows
    input:
    path summary_files

    output:
    path "filtered_*", emit: filtered_files

    """
    python /workspaces/microbe_masst/pipeline/filter_output.py \
        --input "${summary_files}" \
        --output '.'\
        --species_level 

    """
}

process create_mapping{
    input:
    path filtered_files
    path out_dir

    output:
    publishDir "$out_dir", mode: 'copy'

    """
    # create mapping folder
    mkdir -p $out_dir/mapping

    python /workspaces/microbe_masst/pipeline/create_mapping_table.py \
        --feature_counts "${filtered_files}" \
        --sample_species ${params.sample_species}\
        --expression_table ${params.expression_table}\
        -o '$out_dir/mapping/mapping.tsv'
    """
}

process visualization {
    // visualize every group which has a summary
    input:
    path filtered_files
    path out_dir

    output:
    publishDir "$out_dir", mode: 'copy'

    """
    # get group name from input file name
    basename=\$(basename ${filtered_files} .tsv)
    group=\${basename#filtered_summary_counts_} 

    # create visualization folder
    mkdir -p $out_dir/visualization

    python /workspaces/microbe_masst/pipeline/visualization.py \
        -c "${filtered_files}"\
        -o "$out_dir/visualization"\
        -p \$group\
        -s "\t" 
    """
}


workflow {
    log_params(params.out_dir)
    mgfs_file_dir = prepareInput(params.mgf, params.features)
    // out_dir = createOutputDir(params.out_dir) // dont need this
    out_microbeMasst = runMicrobemasst(mgfs_file_dir)
    summary_files = merge_tsv(out_microbeMasst)
    filtered_tsv_channel = filter_output(summary_files)
    mapping = create_mapping(filtered_tsv_channel, params.out_dir)
    visualization(filtered_tsv_channel, params.out_dir)
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
    sample_species = ${params.sample_species ?: 'not provided'}
    expression_table = ${params.expression_table ?: 'not provided'}
    """
}
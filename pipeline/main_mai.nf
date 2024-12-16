params.mgf = "/workspaces/microbe_masst/files/test_microbe_neg.mgf"
params.features = "/workspaces/microbe_masst/files/neg_viewerTable.tsv"
params.out_dir = "/workspaces/microbe_masst/files/out_dir/"


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
    path "out_dir" 
    publishDir "${params.out_dir}", mode: 'copy'

    """
    echo "Running MicrobeMASST..."
    
    python /workspaces/microbe_masst/code/run_microbeMASST.py \
        --input_file $consensus \
        --output_dir "out_dir/prefix"
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
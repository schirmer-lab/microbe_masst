params.mgf = "/workspaces/microbe_masst/files/test_microbe_neg.mgf"
params.features = "/workspaces/microbe_masst/files/viewerTable_neg_01_02.tsv"
params.consensus = "/workspaces/microbe_masst/files/test_filtered_consensus_only_neg.mgf"
params.out_dir = "/workspaces/microbe_masst/files/out_test/"


process prepareInput {
    input:
    path mgf
    path features
    path consensus
    
    output:
    path "../log/input_prepare.out"
    path "../log/input_prepare.err"

    """
    echo "Preparing input..."
    python filter_input.py --mgf $mgf --consensus_only --filter_by_annotation  --features $features --out_file $consensus > ../log/input_prepare.txt 2> ../log/input_prepare.err
    """
}

process runMicrobemasst {
    input:
    path consensus
    path out_dir

    output:
    path "../log/runMicrobemasst.out"
    path "../log/runMicrobemasst.err"

    """
    if [ ! -d "$out_dir" ]; then
        mkdir -p "$out_dir"
    fi
    cd ../code/
    python run_microbeMASST.py --input_file $consensus --output_dir $out_dir > "../log/runMicrobemasst.out" 2> "../log/runMicrobemasst.err"
    """
}

workflow {
    prepareInput(params.mgf, params.features, params.consensus)
    runMicrobemasst(params.consensus, params.out_dir)
}
### not tested yet!
params.mgf = "../files/allMS2Spec2024-11-27_neg.mgf" # sb should push their mgfs? or should everybody have them locally?
params.features = "../files/viewerTable_pos_01_02.tsv"
params.consenus = "../files/filtered_consensus_only_neg.mgf"
params.out_dir = "../outdir/"


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
    python filter_by_annotation_level.py --mgf $mgf --consensus_only --features $features --out_file $consenus > ../log/input_prepare.txt 2> ../log/input_prepare.err
    """
}

process runMicrobemasst {
    input:
    path consenus
    path out_dir

    output:
    path "../log/runMicrobemasst.out"
    path "../log/runMicrobemasst.err"

    """
    if [ ! -d "$out_dir" ]; then
        mkdir -p "$out_dir"
    fi
    python run_microbeMASST.py --input_file $consensus --output_dir $out_dir > "../log/runMicrobemasst.out" 2> "../log/runMicrobemasst.err"
    """
}

workflow {
    prepareInput(params.mgf, params.features, params.consenus)
    runMicrobemasst(params.consenus, params.out_dir)
}

process prepareInput {
    output:
    stdout

    """
    echo "Preparing input..."
    """
}

process runMicrobemasst {

    //define as input:
    //provide path to input mgf
    //provide path to output folder/prefix

    """
    python /workspaces/microbe_masst/code/jobs.py
    """
}

workflow {
    prepareInput()
    runMicrobemasst()
}
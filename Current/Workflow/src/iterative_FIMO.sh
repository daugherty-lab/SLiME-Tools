#!/bin/zsh

# "$#" = value of the total number of command line args passed
# As long as "$#" is greater than (-gt) 0 args, keep while loop alive
while [[ "$#" -gt 0 ]]; do
    # Check each case (options/flags) until match is found
    case $1 in
        # get input following arg option, then shift to next str
        -i|--inputdir) inputdir="$2"; shift ;;
        -m|--motif) motif="$2"; shift ;;
        -p|--pval) pval="$2"; shift ;;
        -o|--oc) outputdir="$2"; shift ;;
        
        # if extra, unmatched options show up, exit
        # Exit code 0 - Success
        # Exit code 1 - General/misc errors, such as "divide by zero" and other impermissible operations
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    
    # end case search (case spelled backwards)
    esac
    shift # to the next str, if any, then loop
done

# echo "Set inputdir: $inputdir"
# echo "Set motif: $motif"
# echo "Set pval: $pval"
# echo "Set outputdir: $outputdir"

# if [ -d "$outputdir" ]
# then
#     echo "Writing files to: $outputdir."
# else
#     echo "Creating directory: $outputdir."
#     mkdir $outputdir
#     echo "Writing files to: $outputdir."
# fi

for f in $inputdir/*
do
    echo "Processing $f file..."
    # get basename of filepath
    baseFname=`basename $f .fa`
    # FIMO on each file
    fimo --oc "$outputdir" --verbosity 1 --text --thresh $pval --max-stored-scores 8000000 "$motif" "$f" > "$outputdir/$baseFname""_fimo.tsv" 2> /dev/null
done
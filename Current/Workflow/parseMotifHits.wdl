version 1.0
# This workflow takes a tab separated file where each row is a set of data to be used in each 
# of the independent scattered task series that you have as your workflow process.  This file 
# will, for example, have column names `sampleName`, `bamLocation`, and `bedlocation`.  This
# allows you to know that regardless of the order of the columns in your batch file, the correct
# inputs will be used for the tasks you define. Adapted from: https://github.com/FredHutch/diy-cromwell-server/

workflow parseMotifHits {
  input {
    String aln_inputdir
    String FIMO_dir
    String FIMO_motif
    Float FIMO_pval
    File concat_hitsum
    String PSG_inputdir
    String concat_hitsum_out
    File merge_to_db
    String db_to_merge
    String merge_to_db_key
    String merged_out
  }
  call recursive_FIMO {
    input: infiles=aln_inputdir, motif=FIMO_motif, pval=FIMO_pval, FIMO_out=FIMO_dir
  }
  Boolean FIMO_status=recursive_FIMO.success
  call pyconcat_hitsum {
    input: Pass=FIMO_status, pyscript=concat_hitsum, FIMO_files=FIMO_dir, concat_outfile=concat_hitsum_out, 
    aln_files=aln_inputdir, PSG_files=PSG_inputdir
  }
  Boolean pyconcat_status=pyconcat_hitsum.success
  call pymerge_to_db {
    input: Pass=pyconcat_status, pyscript=merge_to_db, concat_infile=concat_hitsum_out, 
    annotated_outfile=merged_out, dbfile=db_to_merge, merge_key=merge_to_db_key
  }
  output {
    Boolean workflow_status=pymerge_to_db.success
  }
# End workflow
}

#### TASK DEFINITIONS
task recursive_FIMO {
  input {
    String infiles
    String motif
    Float pval
    String FIMO_out
  }
    command <<<
      # Create directory, if it doesn't already exist
      echo "Checking target directory for FIMO output..."
      if [ -d ~{FIMO_out} ]
      then
          echo "Writing files to: ~{FIMO_out}."
      else
          echo "Creating directory: ~{FIMO_out}."
          mkdir ~{FIMO_out}
          echo "Writing files to: ~{FIMO_out}."
      fi

      # Run FIMO on every file in specified directory
      echo "Running recursive_FIMO..."
      for f in ~{infiles}/*.fa
      do
        echo "Processing $f file..."
        # get basename of filepath
        baseFname=$(basename $f .fa)
        # FIMO on each file
        fimo --oc ~{FIMO_out} --verbosity 1 --text --thresh ~{pval} --max-stored-scores 8000000 \
        ~{motif} $f > "~{FIMO_out}/$baseFname""_fimo.tsv" 2> /dev/null
      done
      echo "recursive_FIMO completed."

      # Delete empty .tsv files created by FIMO
      echo "Cleaning empty FIMO .tsv files..."
      find ~{FIMO_out} -size 0 -print -delete
      echo "Directory cleaned."
    >>>
  output {
    Boolean success = true
  }
}

task pyconcat_hitsum {
  input {
    Boolean Pass
    File pyscript
    String FIMO_files
    String concat_outfile
    String aln_files
    String PSG_files
  }
    command <<<
      echo "Continue: ~{Pass}"
      echo "Running concat_hitsum..."
      python ~{pyscript} -fimodir ~{FIMO_files} -o ~{concat_outfile} -alndir ~{aln_files} -PSGdir ~{PSG_files}
      echo "concat_hitsum completed."
    >>>
  output {
    Boolean success = true
  }
}

task pymerge_to_db {
  input {
    Boolean Pass
    File pyscript
    String concat_infile
    String annotated_outfile
    String dbfile
    String merge_key
  }
    command <<<
      echo "Continue: ~{Pass}"
      echo "Running merge_to_db..."
      python ~{pyscript} -i ~{concat_infile} -db ~{dbfile} -keycolumn ~{merge_key} -o ~{annotated_outfile}
      echo "merge_to_db completed."
    >>>
  output {
    Boolean success = true
  }
}
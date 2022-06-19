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
    call prepare_FIMO {
      input: infiles=aln_inputdir, FIMO_out=FIMO_dir
    }
  Array[String] fafiles=prepare_FIMO.fafiles
  scatter(path in fafiles) {
    call FIMO {
      input: infile=path, motif=FIMO_motif, pval=FIMO_pval, FIMO_out=FIMO_dir
    }
  }
  # Array[File] FIMO.tsvs
  # call pyconcat_hitsum {
  #   input: pyscript=concat_hitsum, FIMO_files=FIMO_dir, concat_outfile=concat_hitsum_out, 
  #   aln_files=aln_inputdir, PSG_files=PSG_inputdir
  # }
  # call pymerge_to_db {
  #   input: pyscript=merge_to_db, concat_infile=concat_hitsum_out, 
  #   annotated_outfile=merged_out, dbfile=db_to_merge, merge_key=merge_to_db_key
  # }

# End workflow
}

#### TASK DEFINITIONS
task prepare_FIMO {
  input {
    String infiles
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
    >>>
  output {
    Array[String] fafiles = glob("~{infiles}/*.fa")
  }
}
task FIMO {
  input {
    String infile
    String motif
    Float pval
    String FIMO_out
    String baseFname=basename(infile, ".fa")
  }
    command <<<
      # Run FIMO on every file in specified directory
      echo "Processing ~{infile} file..."
      # FIMO on each file
      fimo --oc ~{FIMO_out} --verbosity 1 --text --thresh ~{pval} --max-stored-scores 8000000 \
      ~{motif} $f > "~{FIMO_out}/~{baseFname}_fimo.tsv" 2> /dev/null
    >>>
  output {
    Array[String] tsvs = glob("~{FIMO_out}/*.tsv")
  }
}
#       # Delete empty .tsv files created by FIMO
#       echo "Cleaning empty FIMO .tsv files..."
#       find ~{FIMO_out} -size 0 -print -delete
#       echo "Directory cleaned."
# task pyconcat_hitsum {
#   input {
#     File pyscript
#     String FIMO_files
#     String concat_outfile
#     String aln_files
#     String PSG_files
#   }
#     command <<<
#       echo "Running concat_hitsum..."
#       python ~{pyscript} -fimodir ~{FIMO_files} -o ~{concat_outfile} -alndir ~{aln_files} -PSGdir ~{PSG_files}
#       echo "concat_hitsum completed."
#     >>>
# }

# task pymerge_to_db {
#   input {
#     File pyscript
#     String concat_infile
#     String annotated_outfile
#     String dbfile
#     String merge_key
#   }
#     command <<<
#     echo "Running merge_to_db..."
#     python ~{pyscript} -i ~{concat_infile} -db ~{dbfile} -keycolumn ~{merge_key} -o ~{annotated_outfile}
#     echo "merge_to_db completed."
#     >>>
# }
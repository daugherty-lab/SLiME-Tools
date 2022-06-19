version 1.0
# This workflow takes a tab separated file where each row is a set of data to be used in each 
# of the independent scattered task series that you have as your workflow process.  This file 
# will, for example, have column names `sampleName`, `bamLocation`, and `bedlocation`.  This
# allows you to know that regardless of the order of the columns in your batch file, the correct
# inputs will be used for the tasks you define. Adapted from: https://github.com/FredHutch/diy-cromwell-server/

workflow parseMotifHits {
  input {
  String FIMO_inputdir
  String FIMO_outputdir
  String FIMO_motif
  Int FIMO_pval
  # File batchFile2
  }
  call gen_inArr {
    input: FIMO_in=FIMO_inputdir
  }
  output {
    Array[File] inArr
  }
  call confirm_fimodir {
    input: FIMO_out=FIMO_outputdir
  }
  scatter(path in ~{sep=' ' gen_inArr.inArr}) {
    call recursive_FIMO {
      input: infile=path, motif=FIMO_motif, pval=FIMO_pval, FIMO_out=FIMO_outputdir
    }
  }
  # End Scatter over fimo_infiles

#     Array[Object] batchInfo2 = read_objects(batchFile2)
#   scatter (job in batchInfo2){
#     String sampleName2 = job.sampleName
#     File bamFile2 = job.bamLocation
#     File bedFile2 = job.bedLocation

#     ## INSERT YOUR WORKFLOW TO RUN PER LINE IN YOUR BATCH FILE HERE!!!!
#     call test2 {
#         input: in1=sampleName, in2=bamFile, in3=bedFile
#     }

#   }  # End Scatter over the batch file
# # Outputs that will be retained when execution is complete
#   output {
#     Array[File] outputArray = test.item_out
#     Array[File] outputArray2 = test2.item_out
#   }

# End workflow
}

#### TASK DEFINITIONS
# echo some text to stdout, treats files as strings just to echo them as a dummy example
task gen_inArr {
  input {
    String FIMO_in
  }
    command {ls ~{FIMO_in}}
    output {
        Array[File] inArr = readlines(stdout())
    }
}
task confirm_fimodir {
  input {
    String FIMO_out
  }
    command <<<
      if [ -d ~{FIMO_out} ]
      then
          echo "Writing files to: ~{FIMO_out}."
      else
          echo "Creating directory: ~{FIMO_out}."
          mkdir ~{FIMO_out}
          echo "Writing files to: ~{FIMO_out}."
      fi
    >>>
}

task recursive_FIMO {
  input {
    File infile
    String motif
    String pval
    String FIMO_out
    String baseFname=basename(infile, ".fa")
  }
    command {
    echo "Running FIMO on: ~{baseFname}"
    fimo --oc ~{FIMO_out} --verbosity 1 --text --thresh ~{pval} --max-stored-scores 8000000 ~{motif} ~{infile} > "~{FIMO_out}/~{baseFname}_fimo.tsv" 2> /dev/null
    }
    # output { # don't really need this right now
    #     File item_out = stdout()
    # }
}

# task test2 {
#   input {
#     String in1
#     String in2
#     String in3
#   }
#     command {
#     echo ~{in1}
#     echo ~{in2}
#     echo ~{in3}
#     }
#     output {
#         File item_out = stdout()
#     }
# }
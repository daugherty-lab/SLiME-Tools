# SLiME-Tools
Short Linear Motif Evolution Tools

# In progress:
1. Detail creating config file (.ini)
2. Detail upstream motif generation (mostly manual in Geneious) and threshold testing
3. Use miniWDL/Cromwell->WDL pipeline for user-friendly control

### Major pre-req:
1. Python3 set up Anaconda: http://docs.continuum.io/anaconda/install.html
2. This will create a minimal environment for this work.
```conda create -n [name_of_my_env]```
3. To put your self inside this environment run:
```source activate [name_of_my_env]```
* Optional: You can also set this up in your bash or zsh profile

# Stage: Pre-motif generation

## fa_filter
### Pre-reqs:
1. mafft
* ```conda install -c bioconda mafft```

(Optional) If you need to obtain your own set of protein alignments, see below:
1. One of the following sets of protein alignments (knownCanonical.protAA.fa.gz):

* Option 1:
FASTA alignments of 99 vertebrate genomes with human for CDS regions
http://hgdownload.soe.ucsc.edu/goldenPath/hg38/multiz100way/alignments/

* Option 2:
FASTA alignments of 30 mammalian (27 primate) genomes with human for CDS regions
http://hgdownload.soe.ucsc.edu/goldenPath/hg38/multiz30way/alignments/

2. wget (if you have anaconda, this should exist)
* To install: ```conda install -c anaconda wget```
* Download FASTAs via URLs: ```wget [URL from above]```

3. faSplit
* ```conda install -c bioconda ucsc-fasplit```

4. Biopython
* ```conda install -c conda-forge biopython```

### Usage steps:
1. Create a .txt with list of orgs to filter (see examples/orgFilter.txt)
2. Filter for desired orgs (Example using just primates):
* ```python faFilter.py -bl 'examples/orgFilter.txt' -i knownCanonical.protAA.fa -o primate_knownCanonical.protAA.fa```
3. faSplit 
3. Optional: MSA using only a subset of the primates to start (expand later if promising)
    * Expect gaps after subsetting primates, purge all shared gaps
    * ```linsi [path/to/fasta-to-be-aligned.fa] > [path/to/desired-aligned-out.fa]```

# Stage: Motif generation

# Stage: Post-motif generation
## find-vpro-hits
### Pre-reqs:
1. MEME Suite
* Option 1 if your Python3 version allows: ```conda install -c bioconda meme```
* Option 2 if your Python3 is incompatible:
    * ```wget https://meme-suite.org/meme/meme-software/4.11.2/meme_4.11.2_2.tar.gz```
    * ```tar xzf meme_4.11.2_2.tar.gz```
    * ```cd meme_4.11.2```
    * ```./configure --prefix=$HOME/apps/meme4.11.2_2 --with-url=http://meme-suite.org --enable-build-libxml2 --enable-build-libxslt```
    * ```make```
    * ```make test``` # We only care about MEME and FIMO
    * ```make install```
    * ```export PATH=$HOME/apps/meme4.11.2_2/bin:$PATH```

### Usage:
1. Use motif to search against each alignment. Caveat: Data will be lost for poorly aligned regions, as FIMO converts "-" to "X", so any potential motifs separated by gaps will be largely ignored.
* ```./recursive_FIMO.sh -i [inputdir] -m [motif_file] -p [pval_thresh] -o [recursive_FIMO_outdir]```

2. Delete 0byte FIMO output files
* ```find [path/to/fimo.tsv_dir] -size 0 -print -delete```

## concat-hitsum.py
### Pre-reqs:
1. glob2
* ```conda install -c conda-forge glob2```
2. pandas (should be installed with Anaconda)
* ```conda install -c conda-forge glob2```
3. Biopython (to install, see fa_filter.py)
### Usage:
1. Collapse each fimo.tsv into one line per hit (e.g. a seq w/ 15 unique sites across the primate aln has 15 lines)
```python concat-hitsum.py -fimodir [path/to/recursive_FIMO_outdir] -o [path/to/desired_concat_output.csv]```
* OPTIONAL, but recommended:
    * Get motif sequences associated w/ nonhit species
        * Specify alignment directory with -alndir flag
    * Get FUBAR associated calls for residues under positive selection (PSRs)
        * Specify FUBAR outfile directory with -PSGdir flag
    * With both options: ~265s run-time w/ 12 primate proteomes, 20k canonical seq alignments)
    * ~575s run-time w/ 12 primate proteomes, all seq alns 

## merge_dbs.py
### Pre-reqs:
1. glob2 (to install, see concat-hitsum.py)
2. pandas (to install, see concat-hitsum.py)
### Usage: 
1. Merge desired database (db) .csv files, if you don't already have one.
* ```python merge_dbs.py -i [path/to/main_db.csv] -db_dir [path/to/db_directory] -o [path/to/desired_merged_output.csv]```
* Current version: the database file(s) must have exactly ONE matching/shared key column
    * Shared key column is auto-detected (either between input.csv and db.csv OR db.csv and another db.csv)
    * For our purposes, this key column is usually 'sequenceID' or 'gene_sym'
* Future versions: >1 matching/shared key columns are tolerated, if specified
* Record merge settings for each database file in a separate text file to be handled in a pipeline

## merge-to-db.py
### Pre-reqs:
1. pandas (to install, see concat-hitsum.py)
### Usage: 
1. Create config file (.ini) - In progress for detailed instructions
* Config file contains filepath, column to join, and specific columns to add
2. Merge concat-hitsum output to a merged-database file using a config file as reference
```python merge-to-db.py -i [path/to/concat-hitsum-out.csv] -dbconfig [path/to/config.ini] -o [path/to/annotated-concat-hitsum-out.csv]```
# Stage: Visualize using clv data dashboard
## SLiME.py
### Pre-reqs:
1. Streamlit
* ```conda install -c conda-forge streamlit```
2. Altair
* ```conda install -c conda-forge altair```

### Usage: 
1. Visualize clvdata (annotated-concat-hitsum-out.csv) using Streamlit, Altair on localhost
* ```streamlit run propredict.py -- -clvdata [path/to/clvdata.csv] -flatdata [path/to/flatdata.csv]```
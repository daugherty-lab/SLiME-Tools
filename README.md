# SLiME-Tools
Short Linear Motif Evolution Tools
### Major pre-req:
1. Python3 set up in conda

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

* ```wget [URL from above]```

2. faSplit

* ```conda install -c bioconda ucsc-fasplit```

3. Biopython

* ```conda install -c conda-forge biopython```

# Stage: Post-motif generation
## find-vpro-hits
### Pre-reqs:
1. MEME Suite
* Option 1 if your Python3 version allows: ```conda install -c bioconda meme=```
* Option 2 if your Python3 is incompatible:
    * ```wget https://meme-suite.org/meme/meme-software/4.11.2/meme_4.11.2_2.tar.gz```
    * ```tar xzf meme_4.11.2_2.tar.gz```
    * ```cd meme_4.11.2```
    * ```./configure --prefix=$HOME/apps/meme4.11.2_2 --with-url=http://meme-suite.org --enable-build-libxml2 --enable-build-libxslt```
    * ```make```
    * ```make test``` # We only care about MEME and FIMO
    * ```make install```
    * ```export PATH=$HOME/apps/meme4.11.2_2/bin:$PATH```

## concat-hitsum
### Pre-reqs:
1. glob2
```conda install -c conda-forge glob2```

### Steps:
1. Create a .txt with list of orgs to filter (see examples/orgFilter.txt)
2. Filter for desired orgs (Example using just primates):
* ```python faFilter.py -bl 'examples/orgFilter.txt' -i knownCanonical.protAA.fa -o primate_knownCanonical.protAA.fa```
3. faSplit 
3. Optional: MSA using only a subset of the primates to start (expand later if promising)
    * Expect gaps after subsetting primates, purge all shared gaps
    * ```linsi

4. Use motif to search against each alignment. Caveat: Data will be lost for poorly aligned regions, as FIMO converts "-" to "X", so any potential motifs separated by gaps will be largely ignored.
* ```./recursive_FIMO.sh -i [inputdir] -m [motif file] -p [pval thresh] -o [outputdir]```

* OPTIONAL: Delete 0byte FIMO output files
    * find '/Users/britsu/Desktop/test/20220606-fimo' -size 0 -print -delete

5. Collapse each fimo.tsv into one line per hit (e.g. a seq w/ 13 unique sites across the primate aln has 13 lines)
```python concat-hitsum.py -fimodir [path/to/fimo_tsv_directory] -o [path/to/desired_concat_output.csv]```
* OPTIONAL: 
    * Get motif sequences associated w/ nonhit species
        * Specify alignment directory with -alndir flag
    * Get FUBAR associated calls for residues under positive selection (PSRs)
        * Specify FUBAR outfile directory with -PSGdir flag
    * With both options: ~265s run-time w/ 12 primate proteomes, 20k canonical seq alignments)

6. Merge desired database (db) .csv files
```python merge_dbs.py -i [path/to/main_db.csv] -db_dir [path/to/db_directory] -o [path/to/desired_merged_output.csv]```
* Current version: the database file(s) must have exactly ONE matching/shared key column
    * Shared key column is auto-detected (either between input.csv and db.csv OR db.csv and another db.csv)
    * For our purposes, this key column is usually 'sequenceID' or 'gene_sym'
* Future versions: >1 matching/shared key columns are tolerated, if specified
* Record merge settings for each database file in a separate text file to be handled in a pipeline

7: Merge database file using a config file
* Config file (.ini) contains filepath, column to join, and specific columns to add
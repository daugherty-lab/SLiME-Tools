# SLiME-Tools
Short Linear Motif Evolution Tools

# find-vpro-hits
## Stage: Post-motif generation

### Pre-reqs:
1. Python3 set up in conda

2. MEME Suite
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

3. mafft
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

### Steps:
1. Create a .txt with list of orgs to filter (see examples/orgFilter.txt)
2. Filter for desired orgs (Example using just primates):
* ```python faFilter.py -bl 'examples/orgFilter.txt' -i knownCanonical.protAA.fa -o primate_knownCanonical.protAA.fa```
3. faSplit 
3. Optional: MSA using only a subset of the primates to start (expand later if promising)
    * Expect gaps after subsetting primates, purge all shared gaps
    * ```linsi 
4. Use motif to search against only the human version
5. Map indices to MSA
6. Collect +/- 4 (8mer slices) from cleavage site across every sequence
    * Ignore gaps
7. Use motif search against each slice, referenced by orgname and slice index in human, ONLY if site is not identical to human version
    * This reduces huge burden of searching across rest of sequence that has no human match
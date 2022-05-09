# SLiME-Tools
Short Linear Motif Evolution Tools

# find-vpro-hits
## Stage: Post-motif generation

### Pre-reqs:
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
* ```python faFilter.py 'examples/orgFilter.txt' knownCanonical.protAA.fa primate_knownCanonical.protAA.fa```
3. MSA using only a subset of the primates to start (expand later if promising)
    * Expect gaps after subsetting primates, purge all shared gaps
4. Use motif to search against only the human version
5. Map indices to MSA
6. Collect +/- 4 (8mer slices) from cleavage site across every sequence
    * Ignore gaps
7. Use motif search against each slice, referenced by orgname and slice index in human, ONLY if site is not identical to human version
    * This reduces huge burden of searching across rest of sequence that has no human match
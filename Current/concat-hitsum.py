#!/usr/bin/env python3
import argparse
import glob
# import logging
import os.path
import pandas as pd
import sys
from time import perf_counter

# set logging
# logger=logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# formatter=logging.Formatter('[%(asctime)s:%(levelname)s:%(lineno)d %(message)s', datefmt='%H:%M:%S') #time:levelname:message:line#

# file_handler=logging.FileHandler('log/concat-hitsum.log')
# # file_handler=logging.FileHandler('log/merge_db-error.log')
# # file_handler.setLevel(logging.ERROR)
# file_handler.setFormatter(formatter)

# stream_handler=logging.StreamHandler()
# stream_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)

def parse_args():
    parser = argparse.ArgumentParser(prog = 'concat-hitsum.py', conflict_handler = 'resolve')
    # parser.add_argument('-bl', type = str, required = True, help = '=> .txt with organism blacklist e.g. mm10')
    parser.add_argument('-fimodir', type = str, required = True, help = '=> path/to/fimo_directory')
    parser.add_argument('-alndir', type = str, required = False, 
                        help = '=> path/to/alignments_directory. ONLY if you want to list orgs w/o motif hits')
    parser.add_argument('-PSGdir', type = str, required = False, 
                        help = '=> path/to/directory_with_FUBAR_outfiles. ONLY if you want to position-specific +ve info')
    parser.add_argument('-o', type = str, required = True, help = '=> path/to/outfile.csv')
    return(parser.parse_args())

def glob_files(path: str) -> list[str]:
    return(glob.glob(f'{path}/*.tsv'))

def expand_motif_aln(aln_dir: str, in_seqID: str, seq_sites: list[int]) -> (int, list[str]):
    '''Default shows only the species sequences with motif hits.
    When an aln dir is specified, this function is invoked to
    show the motif alignment across both hits and nonhits.'''
    from Bio.SeqIO.FastaIO import SimpleFastaParser

    # collect species name from title and relevant motif alignment from sequence
    with open(f'{aln_dir}/{in_seqID}.12taxa.fa') as aln_file:
        species_regions = []
        seq_length = 0
        for title, sequence in SimpleFastaParser(aln_file):
            species_name = title.split('_')[-1]
            if species_name == 'hg38':
                seq_length = len(sequence.replace('-',''))
            species_regions.append([f'{species_name}: {sequence[pos-1:pos+7]}' for pos in seq_sites])
    return(seq_length, list(map(list, zip(*species_regions))))

def map_PSRs(PSG_dir: str, in_seqID: str, seq_sites: list[int]) -> list[list[str]]:
    '''Returns stringmap of Positive Selection at Residues (PSRs) from dir of FUBAR files, 
    if relevant to the motif range (pos-1:pos+7). PSRs are recorded as '+', 
    and non-PSRs are recorded as '-'.'''
    site_map = [list(range(pos-1,pos+7)) for pos in seq_sites]
    PSRs = []
    try: # File may or may not exist, but if it does, collect PSR entries
        with open(f'{PSG_dir}/{in_seqID}.12taxa.fa.12taxon.tree.grid_info.posteriors.csv') as PSG_file:
            next(PSG_file) # Skip first line
            for line in PSG_file:
                PSR = int(line.split('0.')[0])
                PSRs.append(PSR)
        
        # map sites with presence '+' or absence '_' of PSR
        for site_i, site in enumerate(site_map):
            for pos_i, pos in enumerate(site):
                if pos in PSRs:
                    site_map[site_i][pos_i] = '+'
                else:
                    site_map[site_i][pos_i] = '-'
            site_map[site_i] = ''.join(site)
        return(site_map)
    except IOError: #if file doesn't exist, return default string
        return(['--------' for _ in range(len(seq_sites))])
    except StopIteration: #if file exists, but there are no sites, return default string
        return(['--------' for _ in range(len(seq_sites))])

def exclude_hits(hits_to_exclude: list[str], all_hits: list[str]) -> list[str]:
    nonhit_regions = []
    for hit_index, species in enumerate(hits_to_exclude):
        nonhit_regions.append(set(all_hits[hit_index]).symmetric_difference(species))
    return(nonhit_regions)

# pandas .agg func rename
def Num_Unique(series: pd.Series) -> int:
    return(len(set(series)))

def human_hit(series: pd.Series) -> str:
    if series.str.contains('hg38').any():
        return('Yes')
    else:
        return('No')

def main():
    """
    Takes fimo files and aln files (optional) and generates
    summary dataframe containing one motif hit per line
    with the following info: 
    seq ID|AA pos|species hit: seq|min pval|hg38? (yes/no)|hg38 site|hg38 pval|species absent
    """
    t1_start = perf_counter()

    args = parse_args()

    if os.path.isfile(args.o):
        sys.exit(f"File {args.o} exists")
    else:
        print (f"Building {args.o}...")

    #Set files and columns to extract from
    infimo_files = glob_files(args.fimodir.rstrip('/'))
    infile_ind = [1, 2, 6, 8] # 'sequence name', 'start', 'p-value', 'matched sequence'

    agg_func_text = {'seqIDs': ['first'], # get one representative seqID (first occurrence)
                    'start': ['first', 'count'], # get representative start val, and count of species hits
                    'species_seqs': [tuple], # summarize species seq hits as tuple
                    'matchedseq': [Num_Unique], # num of unique seq hits found
                    'species_pvals': [tuple], # scores for each species hit
                    'pvalue': 'min', # best hit, no matter what species
                    'species': [human_hit]} # Is this a human hit? Yes or No

    for ind, file in enumerate(infimo_files):

        #Create dataframe with selected data from fimo file
        tsv_data = pd.read_csv(file, sep = '\t', usecols = infile_ind, 
                                names = ['seqname', 'start', 'pvalue', 'matchedseq'])
        tsv_data[['seqIDs', 'species']] = tsv_data.seqname.str.split('.12taxa.fa_', expand=True)
        tsv_data['species_seqs'] = tsv_data['species'].astype(str) + ': ' + tsv_data['matchedseq']
        tsv_data['species_pvals'] = tsv_data['species'].astype(str) + ': ' + tsv_data['pvalue'].astype(str)

        #Retain unmerged data: hg38 matchedseq and pvalue data
        hg_data = tsv_data[tsv_data['species'] == 'hg38'].sort_values('start', axis = 0, ascending = True)

        #collapse tsv_data to one line per motif hit across orgs
        tsv_data = (tsv_data.iloc[1: , 1:]
                    .groupby(['seqIDs', 'start'], as_index = False)
                    .agg(agg_func_text))
        
        # hard-coded -- this order doesn't need to change
        tsv_data.columns = ['sequenceID', 'start', 'count', 'concat_sites', 'Num_Unique', 'org_pvals', 'best_pval', 'human_hit'] # replace w/ readable colnames 

        #merge tsv_data to retained hg38 data and export
        merged_data = pd.merge(tsv_data, hg_data[['start', 'matchedseq', 'pvalue']],on='start', how='left')

        #OPTIONAL: use seqID, start pt, and species hits to scrape sequences of orgs with no detectable motif
        if args.alndir:
            #collect species-relevant motif info
            aln_directory = args.alndir.rstrip('/')
            grp_seqID = tsv_data['sequenceID'][0]
            mstarts = tsv_data.start.astype(int) #motif start sites
            sp_hits_to_exclude = tsv_data.concat_sites

            #extract protein (AA) seq length, [aln of each motif across all primates] regardless of score
            AA_length, sp_mregions = expand_motif_aln(aln_directory, grp_seqID, mstarts)

            #exclude hits already examined
            nonhit_mregions = exclude_hits(sp_hits_to_exclude, sp_mregions)
            
            #create nonhit df to merge
            nonhit_df = pd.DataFrame(columns = ['start', 'Non_hits'])
            nonhit_df['Non_hits'] = nonhit_mregions
            nonhit_df['start'] = tsv_data.start
            nonhit_df['AA_seqlength'] = AA_length

            #merge nonhit df to merged_data
            merged_data = pd.merge(merged_data, nonhit_df[['start', 'Non_hits', 'AA_seqlength']],on='start', how='left')

        #OPTIONAL: use seqID and start pt to scrape residues under pos sel (PSRs)
        if args.PSGdir:
            #collect PSG relevant info
            PSG_directory = args.PSGdir.rstrip('/')
            grp_seqID = tsv_data['sequenceID'][0]
            mstarts = tsv_data.start.astype(int) #motif start sites

            #extract protein (AA) seq length, [aln of each motif across all primates] regardless of score
            PSR_stringmap = map_PSRs(PSG_directory, grp_seqID, mstarts)

            #create nonhit df to merge
            PSR_df = pd.DataFrame(columns = ['start', 'PSRs'])
            PSR_df['start'] = tsv_data.start
            PSR_df['FUBAR_PSRs'] = PSR_stringmap

            #merge nonhit df to merged_data
            merged_data = pd.merge(merged_data, PSR_df[['start', 'FUBAR_PSRs']],on='start', how='left')

        #Create csv file if first glob file initiated, otherwise append to existing csv
        if ind == 0:
            merged_data.rename(columns={'matchedseq': 'human_site', 'pvalue': 'pval_hg38'}, inplace=True)
            merged_data.to_csv(args.o, index = False, mode = 'w', header=True)
        else:
            merged_data.to_csv(args.o, index = False, mode = 'a', header=False)

    t1_stop = perf_counter()
    print("Elapsed time (seconds):", t1_stop-t1_start)


if __name__ == '__main__':
    main()
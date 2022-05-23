#!/usr/bin/env python3
import argparse
import glob
import pandas as pd

from Bio.SeqIO.FastaIO import SimpleFastaParser

def parse_args():
    parser = argparse.ArgumentParser(prog = 'concat-hitsum.py', conflict_handler = 'resolve')
    # parser.add_argument('-bl', type = str, required = True, help = '=> .txt with organism blacklist e.g. mm10')
    parser.add_argument('-fimodir', type = str, required = True, help = '=> path/to/fimo_directory')
    parser.add_argument('-alndir', type = str, required = False, 
                        help = '=> path/to/alignments_directory. ONLY if you want to list orgs w/o motif hits')
    parser.add_argument('-o', type = str, required = True, help = '=> path/to/outfile.csv')
    return(parser.parse_args())

def glob_files(path: str) -> list():
    return(glob.glob(f'{path}/*.tsv'))

def extract_maln(aln_dir: str, query_seqID: str, seq_sites: list()) -> list():
    with open(f'{aln_dir}/{query_seqID}.12taxa.fa') as aln_file:
        species_regions = []
        for title, sequence in SimpleFastaParser(aln_file):
            species_regions.append([f'{title.split("_")[-1]}: {sequence[position-1:position+7]}' for position in seq_sites])
    return(list(map(list, zip(*species_regions))))

def exclude_hits(hits_to_exclude: list(), all_hits: list()) -> list():
    nonhit_regions = []
    for hit_index, species in enumerate(hits_to_exclude):
        nonhit_regions.append(set(all_hits[hit_index]).symmetric_difference(species))
    return(nonhit_regions)

# pandas agg func rename
def sequenceID(series) -> str:
    return(series[0:1])

def start(series) -> int:
    return(series[0:1])

def concat_sites(series) -> tuple():
    return(tuple(series))

def pval_min(series) -> float:
    return(min(series))

def human_hit(series) -> str:
    if series.str.contains('hg38').any():
        return('Yes')
    else:
        return('No')

def main():
    """
    """
    args = parse_args()

    #Set files and columns to extract from
    infimo_files = glob_files(args.fimodir.rstrip('/'))
    infile_ind = [1, 2, 6, 8] # 'sequence name', 'start', 'p-value', 'matched sequence'

    #Set agg functions, formatted for desired colname outputs
    agg_func_text = {'seqIDs': [sequenceID],
                    'start': [start, 'count'],
                    'species_seqs': [concat_sites],
                    'pvalue': [pval_min],
                    'species': [human_hit]}

    for ind, file in enumerate(infimo_files):

        #Create dataframe with selected data from fimo file
        tsv_data = pd.read_csv(file, sep = '\t', usecols = infile_ind, names = ['seqname', 'start', 'pvalue', 'matchedseq'])
        tsv_data[['seqIDs', 'species']] = tsv_data.seqname.str.split('.12taxa.fa_', expand=True)
        tsv_data['species_seqs'] = tsv_data['species'].astype(str) + ': ' + tsv_data['matchedseq']

        #Retain unmerged data: hg38 matchedseq and pvalue data
        hg_data = tsv_data[tsv_data['species'] == 'hg38'].sort_values('start', axis = 0, ascending = True)

        #collapse tsv_data to one line per motif hit across orgs
        tsv_data = (tsv_data.iloc[1: , 1:]
                    .groupby(['seqIDs', 'start'], as_index = False)
                    .agg(agg_func_text))
        tsv_data.columns = [col[1] for col in tsv_data.columns.values] # replace colnames with subheader alone

        #merge tsv_data to retained hg38 data and export
        merged_data = pd.merge(tsv_data, hg_data[['start', 'matchedseq', 'pvalue']],on='start', how='left')

        #OPTIONAL: use seqID, start pt, and list of species hits to scrape sequences of orgs with no detectable motif
        if args.alndir:
            #collect species-relevant motif info
            aln_directory = args.alndir.rstrip('/')
            grp_seqID = tsv_data['sequenceID'][0]
            mstarts = tsv_data.start.astype(int) #motif start sites
            sp_hits_to_exclude = tsv_data.concat_sites

            #extract aln of each motif across all primates regardless of score
            sp_mregions = extract_maln(aln_directory, grp_seqID, mstarts)

            #exclude hits already examined
            nonhit_mregions = exclude_hits(sp_hits_to_exclude, sp_mregions)
            
            #create nonhit df to merge
            nonhit_df = pd.DataFrame(columns = ['start', 'Non_hits'])
            nonhit_df['Non_hits'] = nonhit_mregions
            nonhit_df['start'] = tsv_data.start

            #merge nonhit df to merged_data
            merged_data = pd.merge(merged_data, nonhit_df[['start', 'Non_hits']],on='start', how='left')

        #Create csv file if first glob file initiated, otherwise append to existing csv
        if ind == 0:
            merged_data.rename(columns={'matchedseq': 'human_site', 'pvalue': 'pval_hg38'}, inplace=True)
            merged_data.to_csv(args.o, index = False, mode = 'w', header=True)
        else:
            merged_data.to_csv(args.o, index = False, mode = 'a', header=False)


if __name__ == '__main__':
    main()
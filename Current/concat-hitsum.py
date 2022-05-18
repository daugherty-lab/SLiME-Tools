#!/usr/bin/env python3
import argparse
import glob
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(prog = 'concat-hitsum.py', conflict_handler = 'resolve')
    # parser.add_argument('-bl', type = str, required = True, help = '=> .txt with organism blacklist e.g. mm10')
    parser.add_argument('-fimodir', type = str, required = True, help = '=> path/to/fimo_directory')
    parser.add_argument('-o', type = str, required = True, help = '=> path/to/outfile.csv')
    return(parser.parse_args())

def glob_files(path: str) -> list():
    return(glob.glob(f'{path}/*.tsv'))

# pandas agg func rename
def sequenceID(series) -> str:
    return(series[0:1])

def start(series) -> int:
    return(series[0:1])

def species_detected(series) -> tuple():
    return(tuple(series))

def human_hit(series) -> str:
    if series.str.contains('hg38').any():
        return('Yes')
    else:
        return('No')

def pval_min(series) -> float:
    return(min(series))

def concat_sites(series) -> tuple():
    return(tuple(series))
    
def main():
    """
    """
    args = parse_args()

    infimo_files = glob_files(args.fimodir.rstrip('/'))
    infile_ind = [1, 2, 6, 8] # 'sequence name', 'start', 'p-value', 'matched sequence'
    agg_func_text = {'seqID': [sequenceID],
                    'start': [start, 'count'],
                    'species_seqs': [concat_sites],
                    'species': [human_hit],
                    'pvalue': [pval_min]}
    for ind, file in enumerate(infimo_files):
        tsv_data = pd.read_csv(file, sep = '\t', usecols = infile_ind, names = ['seqname', 'start', 'pvalue', 'matchedseq'])
        tsv_data[['seqID', 'species']] = tsv_data.seqname.str.split('.12taxa.fa_', expand=True)
        tsv_data['species_seqs'] = tsv_data['species'].astype(str) + ': ' + tsv_data['matchedseq']
        hg_data = tsv_data[tsv_data['species'] == 'hg38'].sort_values('start', axis = 0, ascending = True)
        tsv_data = (tsv_data.iloc[1: , 1:]
                    .groupby(['seqID', 'start'], as_index = False)
                    .agg(agg_func_text))
        tsv_data.columns = [col[1] for col in tsv_data.columns.values] # replace colnames with subheader alone
        merged_data = pd.merge(tsv_data, hg_data[['start', 'matchedseq', 'pvalue']],on='start', how='left')
        if ind == 0:
            merged_data.rename(columns={'matchedseq': 'human_site', 'pvalue': 'pval_hg38'}, inplace=True)
            merged_data.to_csv(args.o, index = False, mode = 'w', header=True)
        else:
            merged_data.to_csv(args.o, index = False, mode = 'a', header=False)


if __name__ == '__main__':
    main()
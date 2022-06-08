#!/usr/bin/env python3
import argparse
import configparser
import json
# import logging
import pandas as pd

# set logging
# logger=logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# formatter=logging.Formatter('[%(asctime)s:%(levelname)s:%(lineno)d %(message)s', datefmt='%H:%M:%S') #time:levelname:message:line#

# file_handler=logging.FileHandler('log/merge-to-db.log')
# # file_handler=logging.FileHandler('log/merge_db-error.log')
# # file_handler.setLevel(logging.ERROR)
# file_handler.setFormatter(formatter)

# stream_handler=logging.StreamHandler()
# stream_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)

def parse_args():
    parser=argparse.ArgumentParser(prog='concat-hitsum.py', conflict_handler='resolve')
    parser.add_argument('-i', type=str, required=False, help='=> path/to/infile.csv')
    parser.add_argument('-dbconfig', type=str, required=False, help='=> path/to/main_db.ini')
    parser.add_argument('-o', type=str, required=False, help='=> path/to/merged_outfile.csv')
    return(parser.parse_args())

def main():
    """
    Appends column-specific data from a db.csv file to a designated .csv file
    """
    args=parse_args()

    # Set main input df to merge file
    in_df=pd.read_csv(args.i)

    # Initiate and assign vals to config object
    config = configparser.ConfigParser()
    config.read(args.dbconfig)

    # Set main db file and columns to merge using config (.ini)
    db_df=pd.read_csv(config['db']['filepath'])
    keycol=config['db']['keycol']
    cols_order = json.loads(config.get('db', 'cols-order')) # Note: only "" are accepted for json

    # Re-order db_df and merge to input df on keycol val
    db_df=db_df.loc[:, cols_order]
    in_df=pd.merge(in_df, db_df[[*cols_order]],on=keycol, how='left')

    # Hard-coded, this order doesn't need to change
    final_cols_order = ['sequenceID', 'Gene_Sym', 'description', 'AA_seqlength', 'start', 'count', 'Num_Unique', 'concat_sites', 'org_pvals', 'Non_hits', 'best_pval', 'human_site', 'pval_hg38', 'FUBAR_PSRs', 'PC1', 'Omega', 'calc_AF', 'log_calc_AF', 'human_hit', 'Ifn_u2', 'Ifn_u5', 'Ifn_d2', 'Ifn_d5', 'GOBiologicalProcess', 'Pfam', 'Resource_Plate', 'Resource_Position', 'hORF_Length']
    in_df=in_df.loc[:, final_cols_order]
    in_df.to_csv(args.o, index=False, mode='w', header=True)


if __name__ == '__main__':
    main()
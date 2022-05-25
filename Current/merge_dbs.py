#!/usr/bin/env python3
import argparse
import glob
import logging
import pandas as pd

# set logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter('[%(asctime)s:%(levelname)s:%(lineno)d %(message)s', datefmt='%H:%M:%S') #time:levelname:message:line#

# file_handler = logging.FileHandler('log/merge_db-error.log')
# file_handler.setLevel(logging.ERROR)
# file_handler.setFormatter(formatter)

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)

def parse_args():
    parser = argparse.ArgumentParser(prog = 'concat-hitsum.py', conflict_handler = 'resolve')
    parser.add_argument('-i', type = str, required = True, help = '=> path/to/infile.csv')
    parser.add_argument('-db_dir', type = str, required = True, help = '=> path/to/database_directory')
    parser.add_argument('-o', type = str, required = True, help = '=> path/to/outfile.csv')
    return(parser.parse_args())

def glob_files(path: str) -> list():
    return(glob.glob(f'{path}/*'))

def main():
    """
    """
    args = parse_args()

    # Set files and columns to extract from
    in_csv = pd.read_csv(args.i)
    db_files = glob_files(args.db_dir.rstrip('/'))
    db_endpoint = len(db_files)-1
    
    for ind, file in enumerate(db_files):

        # Check to ensure seqID column is always FIRST (Make function for this later)
        # Check to ensure seqID formatting 'NM_number' is the same across both

        # Create dataframe with selected data from each compatible db files in loop
        db = pd.read_csv(file)
        seqID, *othercols = db.columns

        # Merge new db dataframe to existing csv
        in_csv = pd.merge(in_csv, db[[seqID, *othercols]],on=seqID, how='left')

        # Create csv file if list of db files is done
        if ind == db_endpoint:
            # logger.debug(in_csv.columns)
            in_csv.to_csv(args.o, index = False, mode = 'w', header=True)

if __name__ == '__main__':
    main()
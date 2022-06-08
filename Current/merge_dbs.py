#!/usr/bin/env python3
import argparse
import glob
import pandas as pd

def parse_args():
    parser=argparse.ArgumentParser(prog='merge-dbs.py', conflict_handler='resolve')
    parser.add_argument('-db', type=str, required=True, help='=> path/to/main_db.csv')
    parser.add_argument('-db_dir', type=str, required=True, help='=> path/to/database_directory')
    parser.add_argument('-o', type=str, required=True, help='=> path/to/merged_outfile.csv')
    return(parser.parse_args())

def glob_files(path: str) -> list[str]:
    return(glob.glob(f'{path}/*'))

def auto_merge(in_df: pd.DataFrame, glob_files: list[str]) -> tuple[pd.DataFrame, list[str]]:
    leftovers=[]
    for file in glob_files:
        # Create dataframe with selected data from each compatible db files in loop
        filename=file.split('/')[-1]
        db=pd.read_csv(file)
        cols=list(db)
        col_intersect=list(in_df.columns.intersection(db.columns)) # get key col, assume one

        # If shared key col exists, unpack to unique var, else skip/report file error
        if col_intersect:
            cols.insert(0, cols.pop(cols.index(col_intersect[0]))) # move intersected key col to the front
            db=db.loc[:, cols]
            sharedID, *othercols=db.columns
            print(f'{filename}: joined at {sharedID}')
        else:
            print(f'{filename}: Missing shared key column')
            leftovers.append(file)
            continue
        # Merge cleaned up dfs
        db.drop_duplicates(subset=sharedID, keep='first', inplace=True)
        in_df=pd.merge(in_df, db[[sharedID, *othercols]],on=sharedID, how='left')
    return(in_df, leftovers)


def main():
    """
    Appends column-specific data from other .csv files to a designated .csv file
    """
    args=parse_args()

    # Set main db file
    db_csv=pd.read_csv(args.db)

    # Set directory of db files to merge
    db_files=glob_files(args.db_dir.rstrip('/'))

    # Merge each db_file to in_csv by shared key col, record unmerged files
    db_csv, db_leftovers=auto_merge(db_csv, db_files)
    
    # Retry with unmerged files, if applicable, then export .csv
    if db_leftovers:
        db_csv, remaining_leftovers=auto_merge(db_csv, db_leftovers)
        db_csv.to_csv(args.o, index=False, mode='w', header=True)
        if remaining_leftovers:
            remaining_filenames=[file.split('/')[-1] for file in remaining_leftovers]
            print(f'Remaining un-merged files: {remaining_filenames}')
    else:
        db_csv.to_csv(args.o, index=False, mode='w', header=True)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import argparse
import sys
from Bio import SeqIO

def parse_args():
    parser = argparse.ArgumentParser(prog='PROG', conflict_handler='resolve')
    parser.add_argument('-bl', type = str, required = True, help = '=> .txt with organism blacklist e.g. mm10')
    parser.add_argument('-i', type = str, required = True, help = '=> original .fasta input')
    parser.add_argument('-o', type = str, required = True, help = '=> desired name for filtered .fasta output')
    return(parser.parse_args())

def list_ids(txtfile: str) -> set():
    """
    Return a set containing the identifiers presented in a file,
    line by line, starting with ">"
    """

    identifiers = set()

    with open(txtfile, 'r') as fi:
        for line in fi:
            line = line.strip()
            identifiers.add(str(line).replace(">", "")) #record.id excludes ">"

    return(identifiers)

def get_orgname(recIDstr: str) -> str:
    """
    Splits a faster header by \s and "_" to return orgname
    """
    orgname = recIDstr.split()[0].split("_")[1]
    return(orgname)

def main():
    """
    Writes a file containing only the sequences with identifiers NOT
    present in a set of identifiers
    """

    args = parse_args()

    exclude_ids = list_ids(args.bl)

    with open(args.i) as original_fasta, open(args.o, 'w') as corrected_fasta:
        records = SeqIO.parse(original_fasta, 'fasta')
        for record in records:
            orgname = get_orgname(record.id)
            #print(orgname)
            if orgname not in exclude_ids:
                SeqIO.write(record, corrected_fasta, 'fasta-2line')

if __name__ == '__main__':
    main()
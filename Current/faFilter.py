#!/usr/bin/env python3

import sys
from Bio import SeqIO

def list_ids(txtfile):
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

def get_orgName(recIDstr):
    return(recIDstr.split()[0].split("_")[1])

def filterby_org():
    """
    Writes a file containing only the sequences with identifiers NOT
    present in a set of identifiers
    """

    identifiers = list_ids(sys.argv[1])

    with open(sys.argv[2]) as original_fasta, open(sys.argv[3], 'w') as corrected_fasta:
        records = SeqIO.parse(original_fasta, 'fasta')
        for record in records:
            orgName = get_orgName(record.id)
            #print(orgName)
            if orgName not in identifiers:
                SeqIO.write(record, corrected_fasta, 'fasta-2line')

if __name__ == '__main__':
    filterby_org()
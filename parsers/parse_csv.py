# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 05/06/2017
"""
Generates a plot from a json file with a list of model states.
"""

import argparse
import re
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve information from a csv file from the commandline")
    parser.add_argument("path", type=str, help="The csv file path")
    parser.add_argument("command", type=str, choices=["maxrow", "header"])
    parser.add_argument("--delimiters", "-d", type=str, nargs='+', default=[";",","], help="csv field delimiters")
    parser.add_argument("--skip_header", "-s", type=int, default=0)
    parser.add_argument("--column", "-c", type=int, default=-1, help="Column to search. -1 for the last one")
    parser.add_argument("--field", "-f", type=str, default=None, help="Field to search. Only valid when no skip-header is set. Overrides column option.")
    args = parser.parse_args()

    if args.skip_header > 0 and args.field is not None:
        raise ValueError("Cannot skip header and filter by field at the same time")
    if args.skip_header > 0 and args.command == "header":
        raise ValueError("Cannot skip and return header")


    header_fields = []
    with open(args.path, 'r') as infile:
        lines = infile.read().rstrip().split('\n')
    if args.skip_header > 0:
        lines = lines[args.skip_header:]
    else:
        header_fields = re.split("|".join(args.delimiters), lines[0])
        lines = lines[1:]

    if args.command == "maxrow":
        column = []
        if args.field is not None:
            idx = header_fields.index(args.field)
        for l in lines:
            linesp = re.split("|".join(args.delimiters), l)
            if args.field is None:
                column.append(linesp[args.column])
            elif len(header_fields) > 0:
                column.append(linesp[idx])
              
        print(lines[np.argmax(column)])
    elif args.command == "header":
        print(";".join(header_fields))
                




        

# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 05/06/2017
"""
Generates a plot from a json file with a list of model states.
"""

import json
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('path', nargs='+', type=str,
                    help='paths where the files are located')
parser.add_argument('target_field', type=str,
                    help='key value')
parser.add_argument('--action', type=str, default='max',
                    help='report max/min value of the target field')
parser.add_argument('--output', type=str, default='report.csv',
                    help='output file')
parser.add_argument('--delimiter', type=str, default=';',
                    help='csv field delimiter')
parser.add_argument('--fields', nargs='+', type=str, default=None,
                    help='other fields to appear in the report. Defaults to all.')
args = parser.parse_args()

def better(a, b):
    """ Checks whether a is better than b given a criterion

    Args:
        a: integer or float
        b: integer or float

    Returns: boolean

    """
    if args.action == 'max':
        return a > b
    elif args.action == 'min':
        return a < b
    else:
        raise ValueError

output = open(args.output, 'w')

outer_buffer = []
for path in args.path:
    try:
        with open(path, 'r') as infile:
            data = json.load(infile)
    except Exception as e:
        print(e)
        print(path)
        continue

    if len(data) == 0:
        print('skipping empty ', path)
        continue
    best_line = data[0]
    for line in data[1:]:
        target = float(line[args.target_field])
        if better(target, float(best_line[args.target_field])):
            best_line = line

    inner_buffer = []
    for field in sorted(line.keys()):
        if args.fields is None or field in args.fields:
            inner_buffer.append(best_line[field])
    outer_buffer.append(';'.join([str(x) for x in inner_buffer]))

output.write('%s\n'%(';'.join(sorted(best_line.keys()))))
output.write('\n'.join(outer_buffer))

output.close()












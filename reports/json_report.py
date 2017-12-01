# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 05/06/2017
"""
Generates a plot from a json file with a list of model states.
"""

import json
import argparse
import numpy as np

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
parser.add_argument('--average', type=int, default=0, metavar="AVG",
                    help='merge AVG similar rows')
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

outer_buffer = {}
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

    index = 0
    while index < len(data) and args.target_field not in data[index]:
        index += 1

    if index == len(data):
        print('%s not found in %s' %(args.target_field, path))
        continue
    else:
        best_line = data[index]

    for line in data[index:]:
        target = float(line[args.target_field])
        if better(target, float(best_line[args.target_field])):
            best_line = line

    inner_buffer = []
    keys = filter(lambda x: x != args.target_field, best_line.keys())
    for field in sorted(keys):
        if args.fields is None or field in args.fields:
            inner_buffer.append(best_line[field])
    inner_buffer_str = ";".join([str(x) for x in inner_buffer])
    if inner_buffer_str not in outer_buffer:
        outer_buffer[inner_buffer_str] = [best_line[args.target_field]]
    else:
        outer_buffer[inner_buffer_str].append(best_line[args.target_field])

avg_outer_buffer = []
for line in outer_buffer:
    targets = outer_buffer[line]
    if args.average == 0:
        for t in targets:
            avg_outer_buffer.append(";".join([line, str(t)]))
    elif len(targets) >= args.average:
        avg_outer_buffer.append(";".join([line, str(np.mean(targets)), str(np.std(targets))]))
if args.average != 0:
    args.target_field = ";".join(["%s_mean" %args.target_field, "%s_std" %args.target_field])

if args.fields is None:
    keys = filter(lambda key: key != args.target_field, best_line.keys())
else:
    keys = args.fields

output.write('%s\n'%(';'.join(sorted(keys) + [args.target_field])))
output.write('\n'.join(avg_outer_buffer))

output.close()












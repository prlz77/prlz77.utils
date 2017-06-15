# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 05/06/2017
"""
Generates a plot from a json file with a list of model states.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsers.pad_state_dict import pad_state_dict
import argparse
import numpy as np
import pylab
import json
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument('path', type=str, nargs='+', help="json log path")
parser.add_argument('-x', type=str, help="x axis field name")
parser.add_argument('-y', type=str, help="y axis field name")
parser.add_argument('--list_fields', action='store_true', help="list log fields")
parser.add_argument('--title', '-t', type=str, default='', help="plot title")
parser.add_argument('--legend_fields', '-l', type=str, nargs='+', default=[],
        help='list of fields to show in the legend')

args = parser.parse_args()

pylab.figure()
pylab.hold(True)


data = []
max_y = []

for path in args.path:
    with open(path, 'r') as infile:
        parsed = json.load(infile)

    if len(parsed) == 0:
        print('skipping empty %s' %path)
        continue

    padded = pad_state_dict(parsed)

    if args.list_fields:
        print(padded.keys())
    else:
        d = {'x':padded[args.x], 'y':np.array(padded[args.y]), 'legend': None}
        max_y.append(np.max(padded[args.y]))
        if len(args.legend_fields) > 0:
            d['legend'] = ','.join([str(parsed[0][x]) for x in args.legend_fields])
        data.append(d)
            

indices = np.argsort(max_y)[::-1]
legend = []
for ind in indices:
    pylab.plot(data[ind]['x'], data[ind]['y'])
    legend.append(data[ind]['legend'])
    
pylab.title(args.title)
pylab.xlabel(args.x)
pylab.ylabel(args.y)
    
if len(args.legend_fields) > 0:
    pylab.legend(legend).draggable()

pylab.show()

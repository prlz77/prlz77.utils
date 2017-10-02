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
import glob
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument('path', type=str, nargs='+', help="json log path")
parser.add_argument('-x', type=str, help="x axis field name")
parser.add_argument('-y', type=str, help="y axis field name")
parser.add_argument('--list_fields', action='store_true', help="list log fields")
parser.add_argument('--title', '-t', type=str, default='', help="plot title")
parser.add_argument('--ignore_errors', action='store_true', help="will continue in case of erroneous log")
parser.add_argument('--legend_fields', '-l', type=str, nargs='+', default=[],
        help='list of fields to show in the legend')
parser.add_argument('--live', action='store_true', 
        help='update plot live')
parser.add_argument('--filter', action='append', type=str, default=[], 
        help='use in the following way: field [>|<][=] value. For instance: accuracy > 0.5')

args = parser.parse_args()

pylab.figure()

def read(verbose=False):
    padded = []
    for folded_path in args.path:
        for path in glob.glob(folded_path):
            if verbose:
                print(path)
            try:
                with open(path, 'r') as infile:
                    parsed = json.load(infile)
            except:
                if verbose:
                    print("Could not parse %s" %path)
                parsed = []

            if len(parsed) == 0:
                if verbose:
                    print('skipping empty %s' %path)
                continue

            padded.append(pad_state_dict(parsed))
    return padded

def parse(padded_list):
    data = []
    max_y = []
    for padded in padded_list:
        try:
            if len(args.filter) > 0:
                keys = padded.keys()
                skip = False
                for filt in args.filter:
                    tokens = filt.split(' ')
                    for token in tokens:
                        if token in padded:
                            filt = filt.replace(token, 'padded["%s"][idx]' %token)
                    length = len(padded[args.x])
                    for idx in range(length):
                        if not eval(filt):
                            skip = True
                            break
                    if skip:
                        break
                if skip:
                    continue

            d = {'x':padded[args.x], 'y':np.array(padded[args.y]), 'legend': None}
            max_y.append(np.max(padded[args.y]))
            if len(args.legend_fields) > 0:
                d['legend'] = ','.join([str(padded[x][0]) for x in args.legend_fields])
            data.append(d)
        except Exception as e:
            if args.ignore_errors:
                print(e)
            else:
                raise e

    return data, max_y

def plot(data, max_y):
    pylab.hold(True)
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

def main():
    padded = read(True)
    if args.list_fields:
        for p in padded:
            print(padded.keys())
    else:
        data, max_y = parse(padded)
        plot(data, max_y)
        while args.live:
            pylab.draw()
            pylab.pause(1)
            padded = read(False)
            data, max_y = parse(padded)
            pylab.clf()
            plot(data, max_y)
        pylab.show()


if __name__=='__main__':
    main()

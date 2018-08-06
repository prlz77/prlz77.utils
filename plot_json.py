# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 05/06/2017
"""
Generates a plot from a json file with a list of model states.
"""
import matplotlib
matplotlib.use('qt5agg')
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
parser.add_argument('path', type=str, nargs='+', 
        help="json log path")
parser.add_argument('-x', type=str, 
        help="x axis field name")
parser.add_argument('-y', type=str, action='append',
        help="y axis field name (x)")
parser.add_argument('--list_fields', action='store_true', 
        help="list log fields")
parser.add_argument('--title', '-t', type=str, default='', 
        help="plot title")
parser.add_argument('--ignore_errors', action='store_true', 
        help="will continue in case of erroneous log")
parser.add_argument('--legend_fields', '-l', type=str, nargs='+', default=[],
        help='list of fields to show in the legend')
parser.add_argument('--live', action='store_true', 
        help='update plot live')
parser.add_argument('--filter', action='append', type=str, default=[], 
        help='use in the following way: field [>|<][=] value. For instance: accuracy > 0.5')
parser.add_argument('--meanstd', action='store_true',  
        help='plot mean and std')

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
    ret = {'data':[], 'max_y':[]}
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
            d = {'x': padded[args.x], 'legend': ""}
            d.update({y: np.array(padded[y]) for y in args.y})
            if len(args.legend_fields) > 0:
                d['legend'] = ','.join([str(padded[x][0]) for x in args.legend_fields])
            ret['data'].append(d)
            ret['max_y'].append(np.nanmax(padded[args.y[0]]))

        except Exception as e:
            if args.ignore_errors:
                print(e)
            else:
                raise e

    return ret

def plot_data(data):
    pylab.hold(True)
    indices = np.argsort(data['max_y'])[::-1]
    legend = []
    for ind in indices:
        print(args.y)
        for y in args.y:
            pylab.plot(data['data'][ind]['x'], data['data'][ind][y])
            legend.append("%s. %s" %(y, data['data'][ind]['legend']))
        
    pylab.title(args.title)
    pylab.xlabel(args.x)
    pylab.ylabel(args.y[0])
    
    pylab.legend(legend).draggable()

def plot_error(data):
    pylab.hold(True)
    all_y = np.array([d['y'] for d in data['data']])

    pylab.errorbar(data['data'][0]['x'], np.nanmean(all_y, axis=0), np.nanstd(all_y, axis=0))
    pylab.plot(data['data'][0]['x'], np.nanmean(all_y, axis=0))
        
    pylab.title(args.title)
    pylab.xlabel(args.x)
    pylab.ylabel(args.y)

def main():
    padded = read(True)
    if args.meanstd:
        plot = plot_error
    else:
        plot = plot_data
    if args.list_fields:
        for p in padded:
            print(padded.keys())
    else:
        data = parse(padded)
        plot(data)
        while args.live:
            pylab.draw()
            pylab.pause(1)
            padded = read(False)
            data = parse(padded)
            pylab.clf()
            plot(data)
        pylab.show()


if __name__=='__main__':
    main()

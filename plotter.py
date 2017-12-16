# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 15/12/2017
import fire
import pylab
import seaborn
import os
from parsers import json_utils as jutils
import json
import glob
import logging
import numpy as np
import uuid
import sys
from copy import deepcopy as copy

data = []
def load(path):
    pathsp = path.split(" ")
    paths = []
    for p in pathsp:
        paths += glob.glob(p)
    global data
    for path in paths:
        try:
            with open(path, 'r') as infile:
                data.append(json.load(infile))
        except json.decoder.JSONDecodeError:
            logging.warning("Error decoding %s" %path)
        logging.info('load %s' %path)
    return data

def select_hyperparams(data, field, value):
    ret = []
    for document in data:
        cdoc = jutils.collapse(document)
        if cdoc[field] == value:
            ret.append(document)
    return ret

def select_hyperparams_2(data, filter):
    ret = []
    for document in data:
        cdoc = jutils.collapse(document)
        filt = filter[:]
        for key in cdoc.keys():
            filt = filt.replace(key, "cdoc['%s']" %key)
        if eval(filt):
            ret.append(document)
    return ret

def bulk_get_keys(data):
    keys = set([])
    for document in data:
        keys.update(jutils.get_all_keys(document))
    return sorted(list(keys))

def pad_docs(data, transpose=True):
    keys = bulk_get_keys(data)
    transposed = []
    for document in data:
        transposed.append(jutils.transpose(document))
    for key in keys:
        lengths = []
        for document in transposed:
            if key not in document:
                document[key] = []
            lengths.append(len(document[key]))
        max_length = np.max(lengths)
        for document in transposed:
            l = len(document[key])
            d = max_length - l
            if d > 0:
                document[key] += [float('nan')] * d
    if transpose:
        return transposed
    else:
        return jutils.transpose(transposed)


def reduce(data, src, function, dst, out=None):
    buff = pad_docs(data)
    if out is None:
        out = copy(buff[0])
    out[dst] = []
    for document in buff:
        out[dst].append(document[src])
    out[dst] = function(out[dst])
    return out

if __name__ == '__main__':
    fire.Fire()



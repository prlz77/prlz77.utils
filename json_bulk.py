# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 15/12/2017

import glob
import json
import logging
import fire
from copy import deepcopy as copy

import numpy as np
from parsers.json_utils import JsonDoc
from plot.plotter import Plotter


class JsonBulk(object):
    def __init__(self, path="", skip_header=0):
        self.data = []
        self.keys = []
        self.hyperparams = []
        self.iter_count = 0
        if path != "":
            self.load(path, skip_header=skip_header)

    def __add__(self, docs):
        ret = copy(self)
        if isinstance(docs, list):
            ret.data += docs
        elif isinstance(docs, JsonBulk):
            ret.data += docs.data
        elif isinstance(docs, JsonDoc):
            ret.data.append(docs)
        ret.__update_keys()
        ret.__pad_docs()
        return ret

    def __iadd__(self, docs):
        if isinstance(docs, JsonBulk):
            self.data += docs.data
        self.__update_keys()
        self.__pad_docs()

    def __iter__(self):
        self.iter_count = 0
        return self

    def __next__(self):
        if self.iter_count == len(self.data):
            raise StopIteration()
        ret = self.data[self.iter_count]
        self.iter_count += 1
        return ret

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.data[item]
        elif isinstance(item, str):
            ret = []
            for document in self.data:
                ret.append(document[item])
            return np.array(ret)
        else:
            raise ValueError("invalid key")

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.data[key] = value
        elif isinstance(key, str):
            for document, val in zip(self.data, value):
                document[key] = val

    def clear(self):
        self.data = []

    def load(self, path, append=True, skip_header=0):
        pathsp = path.split(" ")
        paths = []
        if append:
            ret = self
        else:
            ret = JsonBulk()
        for p in pathsp:
            paths += glob.glob(p)
        for path in paths:
            try:
                ret.data.append(JsonDoc(path, skip_header=skip_header))
            except json.decoder.JSONDecodeError:
                logging.warning("Error decoding %s" % path)
            except IOError as e:
                logging.warning(e)
            logging.info('load %s' % path)
        self.__update_keys()
        self.__pad_docs()
        return ret

    def add_doc(self, doc):
        self.data.append(doc)
        self.__update_keys()
        self.__pad_docs()

    def select_hyperparams(self, field, value):
        ret = JsonBulk()
        for document in self.data:
            if document.hyperparams[field] == value:
                ret.add_doc(document)
        return ret

    def filter(self, filter):
        ret = JsonBulk()
        for document in self.data:
            filt = filter[:]
            for key in document.keys:
                filt = filt.replace(key, "document['%s']" % key)
            if eval(filt):
                ret.add_doc(document)
        return ret

    def __update_keys(self):
        self.keys = set([])
        for document in self.data:
            self.keys.update(document.keys)
        self.keys = list(sorted(self.keys))

    def __pad_docs(self):
        for key in self.keys:
            lengths = []
            for document in self.data:
                if key not in document.keys:
                    document[key] = []
                lengths.append(len(document[key]))
            max_length = np.max(lengths)
            for document in self.data:
                l = len(document[key])
                d = max_length - l
                if d > 0:
                    document[key] += [float('nan')] * d

    def reduce(self, src, function, dst):
        ret = copy(self.data[0])
        for document in self.data:
            ret[dst].append(document[src])
        ret[dst] = function(ret[dst])
        return ret

    def plot_one_line(self, y_field, x_field="", legend="", score_f=np.nanmax, plotter=None):
        if legend == "":
            legend = y_field
        if plotter is None:
            plotter = Plotter()
        data = [d[y_field] for d in self.data]
        if x_field != "":
            x = [d[x_field] for d in self.data]
        else:
            x = None
        plotter.add_line(data, x=x, label=legend, score_f=score_f)
        return plotter

    def plot_hyperparam(self, hyperparam, target, legend="", score_f=np.nanmax, order="asc", plotter=None):
        hypervalues = set([])
        for document in self.data:
            hypervalues.update(filter(lambda x: not np.isnan(x), np.unique(document[hyperparam]).tolist()))

        hypervalues = list(sorted(hypervalues))
        if order == "desc":
            hypervalues = hypervalues[::-1]

        target_values = []
        for hypervalue in hypervalues:
            buffer = []
            docs = self.select_hyperparams(hyperparam, hypervalue)
            for doc in docs:
                buffer.append(score_f(doc[target]))
            target_values.append(score_f(buffer))
        if plotter is None:
            plotter = Plotter()
        plotter.add_line(target_values, hypervalues, legend, score_f)
        return plotter

if __name__ == '__main__':
    fire.Fire()
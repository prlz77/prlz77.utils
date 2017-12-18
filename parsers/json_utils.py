import numpy as np
import json


def get_all_keys(document):
    """

    Args:
        document:

    Returns:

    """
    keys = set(document[0].keys())
    for line in document:
        keys.update(line.keys())
    return sorted(list(keys))

def transpose(document):
    """

    Args:
        document:

    Returns:

    """
    if isinstance(document, list):
        document = pad_dict(document)
        keys = document[0].keys()
        data = {key: [] for key in keys}
        for line in document:
            for key in keys:
                data[key].append(line[key])

    elif isinstance(document, dict):
        data = []  # [{}, {}, {}]
        for key in document:
            for i in range(len(document[key])):
                if i >= len(data):
                    data.append({key: document[key][i]})
                else:
                    data[i][key] = document[key][i]

    return data


def collapse(document):
    """ Returns a one_line summary of the immutable values of the document

    Args:
        document: list of dicts
    """
    assert (isinstance(document, list))
    tdoc = transpose(document)
    ret = {}
    for key in tdoc:
        if np.unique(tdoc[key]).shape[0] == 1:
            ret[key] = tdoc[key][0]
    return ret


def pad_dict(document):
    assert (isinstance(document, list))
    keys = get_all_keys(document)
    ret = []
    for line in document:
        ret.append({})
        for key in keys:
            if key in line:
                ret[-1][key] = line[key]
            else:
                ret[-1][key] = float('nan')
    return ret

class JsonDoc(object):
    def __init__(self, path, skip_header=0):
        self.path = path
        with open(path, 'r') as infile:
            self.data = json.load(infile)
        if self.skip_header > 0:
            self.data = self.data[skip_header:]
        self.hyperparams = collapse(self.data)
        self.data = transpose(self.data)
        self.keys = self.data.keys()
        self.transposed = True

    def transpose(self):
        self.data = transpose(self.data)
        self.transposed = not self.transposed

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value
        if key not in self.keys:
            self.keys.append(key)


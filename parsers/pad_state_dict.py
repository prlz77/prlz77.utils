# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 05/06/2017
"""
Pads sequence missing values with NaN to allow comparisons with other sequences.
"""

def pad_state_dict(lines):
    """ The main method

    Args:
        lines (list of dict): list with the model status at each timestep.

    Returns: a list of dictionary with NaN at the missing values on each timestep.

    """
    data = {}
    for idx, parsed in enumerate(lines):
        for key in parsed.keys():
            if key in data:
                data[key].append(parsed[key])
            else:
                data[key] = [float('nan')]*idx
                data[key].append(parsed[key])
        for key in set(data.keys()).difference(set(parsed.keys())):
            data[key].append(float('nan'))
    return data

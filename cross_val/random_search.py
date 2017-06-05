# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Date: 05/06/2017 
"""
Generates random hyperparameter sets from given distributions.
"""

import numpy as np
import os
import json

class RandomSearch(object):
    """
    The main class
    """
    def __init__(self, load_from='./history.json', save_to='./history.json'):
        """ Constructor

        Args:
            load_from (str): List of previous generations to avoid repetition in multiple runs.
            save_to (str): Output file to save the generated hyperparameter sets.
        """
        self.params = {}
        self.history = []
        if os.path.isfile(load_from):
            self.load_history(load_from)

        self.save_to = save_to

    def load_history(self, path):
        """ Loads previous generations from a json file.

        Args:
            path (str): history file path.
        """
        with open(path, 'r') as infile:
            self.history = json.load(infile)

    def add_discrete(self, name, values):
        """ Sample a discrete or categorical hyperparameter using a uniform distribution.

        Args:
            name (str): the hyperparam name, e.g. --learning_rate.
            values (list): list of possible values. bools represent flags, e.g. --standarize, [True, False].
        """
        self.params[name] = lambda : values[np.random.randint(0, len(values))]

    def add_continuous_uniform(self, name, min, max):
        """ Sample real value from a uniform distribution.

        Args:
            name (str): the hyperparam name.
            min (float): min value.
            max (float): max value.
        """
        self.params[name] = lambda : np.random.uniform(min, max)

    def add_continuous_log(self, name, min, max, base=10):
        """ Sample from a log-space uniform distribution.

        Args:
            name (str): hyperparam name.
            min (float): min value.
            max (float): max value.
            base (float): log base.
        """
        self.params[name] = lambda : float(base)**(np.random.uniform(np.log(min) / np.log(base), np.log(max) / np.log(base)))

    def add_persistent(self, name, value):
        """ Fixed value. Always return the same result.

        Args:
            name (str): hyperparam name.
            value: value to return.
        """
        self.params[name] = lambda : value

    def connect(self, new, prev, f=(lambda x: x)):
        """ Make hyperparam to depend on a previously sampled one.

        Args:
            new (str): hyperparam name.
            prev (str): hyperparam to depend on.
            f (function): function to generate the new hyperparam from the prev one.
        """
        self.params[new] = (prev, f)

    def get_one(self):
        """ Sample one hyperparam set.

        Returns: A list of names and values. [param, value, --param, value, ...]

        """
        connect = []
        flags = []
        arg = {}
        for key in sorted(self.params.keys()):
            if isinstance(self.params[key], tuple):
                connect.append(key)
            else:
                value = self.params[key]()
                if isinstance(value, bool):
                    if value:
                        flags.append(key)
                else:
                    arg[key] = value

        for key in connect:
            b, f = self.params[key]
            arg[key] = f(arg[b])

        ret = []
        for key in arg:
            ret.append(key)
            ret.append(arg[key])

        for flag in flags:
            ret.append(flag)

        return ret

    def get_unique(self, max=100):
        """ Sample a unique hyperparam set.

        Args:
            max (int): max number of attemps until desist.

        Returns: A list of hyperparams or None if no unique hyperparams are left.

        """
        arg = self.get_one()
        counter = max
        while [str(x) for x in arg] in self.history and counter > 0:
            arg = self.get_one()
            counter -= 1

        if counter == 0:
            return None
        else:
            self.history.append([str(x) for x in arg])
            if self.save_to is not None:
                with open(self.save_to, 'w') as outfile:
                    json.dump(self.history, outfile)
            return arg

    def expand_arg(self, args, name, values):
        """ Given a list of hyperparams and a new one with n possible values, it generates n lists covering all of them.

        Args:
            args (list): original hyperparam list
            name (str): hyperparam name
            values (list): list of possible values.

        Returns: list of hyperparam lists

        """
        assert(isinstance(args, list))
        ret = []
        for v in values:
            ret.append(args[:])
            ret[-1].append(name)
            ret[-1].append(v)
        return ret

    def get_unique_string(self, max=100):
        """ Converts hyperparam list into string.

        Args:
            max (int): max number of attempts until desist.

        Returns: string or None

        """
        ret = self.get_unique(max=max)
        if ret is None:
            return None
        else:
            return " ".join([str(x) for x in ret])

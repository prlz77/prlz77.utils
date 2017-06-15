""" Harakiri helps models to kill themselves when they reach a plateau """
import sys


class Harakiri(object):
    """
    The main class
    """

    def __init__(self, initial_value=0):
        """ Constructor

        Args:
            initial_value: best value to compare with
        """
        self.best_value = initial_value
        self.buffer = []
        self.test = lambda: 1  # The test consists in two bits: plateau_length_exceeded current_value_is_best (2^1 2^0)
        self.message = "(Harakiri) Plateau reached."

    def set_max_plateau(self, plateau_length):
        """ Sets harakiri to look for max values.

        Args:
            plateau_length: length of the plateau until seppuku
        """
        assert (plateau_length >= 1)
        self.test = lambda: 1 * (self.best_value > self.buffer[-1]) + 2 * (len(self.buffer) >= plateau_length)

    def set_min_plateau(self, plateau_length):
        """ Sets harakiri to look for max values

        Args:
            plateau_length: length of the plateau until seppuku
        """
        assert (plateau_length >= 1)
        self.test = lambda: 1 * (self.best_value < self.buffer[-1]) + 2 * (len(self.buffer) >= plateau_length)

    def set_message(self, message):
        """ Set the process last words

        Args:
            message: the last string of words
        """
        self.message = message

    def update(self, value):
        """ Tests the plateau condition given a new value

        Args:
            value (int or float): value to test
        """
        self.buffer.append(value)
        test_v = self.test()
        if test_v == 3:
            print(self.message)
            sys.exit(0)
        elif test_v & 1 == 0:
            self.buffer = []
            self.best_value = value


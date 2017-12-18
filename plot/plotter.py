import numpy as np
import seaborn as sns
import pylab


class Plotter(object):
    def __init__(self):
        pylab.figure()
        self.legend = []
        self.scores = []
        self.x = []
        self.y = []

    def add_line(self, data, x=None, label="", score_f=np.nanmax):
        data = np.array(data)
        if x is None:
            x = np.arange(data.shape[-1])
        self.x.append(x)
        self.y.append(data)
        self.scores.append(score_f(data))
        self.legend.append(label)

    def plot(self, xlabel="", ylabel="", title=""):
        indices = np.argsort(self.scores)[::-1]
        colors = sns.color_palette("hls", len(indices))
        legend = []
        for i in indices:
            pylab.plot(self.x[i], np.array(self.y[i]), color=colors[i])
            legend.append(self.legend[i])
        pylab.legend(legend).draggable()
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        pylab.title(title)

    def tsplot(self, xlabel="", ylabel="", title=""):
        indices = np.argsort(self.scores)[::-1]
        colors = sns.color_palette("hls", len(indices))
        legend = []
        for i in indices:
            sns.tsplot(np.array(self.y[i]), color=colors[i])
            legend.append(self.legend[i])
        pylab.legend(legend).draggable()
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        pylab.title(title)

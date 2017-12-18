import numpy as np
import seaborn as sns
import pylab


class Plotter(object):
    legend = []
    scores = []
    x = []
    y = []

    @staticmethod
    def add_line(data, x=None, label="", score_f=np.max):
        data = np.array(data)
        if x is None:
            x = np.arange(data.shape[-1])
        Plotter.x.append(x)
        Plotter.y.append(data)
        Plotter.scores.append(score_f(data))
        Plotter.legend.append(label)

    @staticmethod
    def plot(xlabel="", ylabel="", title=""):
        pylab.figure()
        indices = np.argsort(Plotter.scores)[::-1]
        colors = sns.color_palette("hls", len(indices))
        legend = []
        for i in indices:
            pylab.plot(Plotter.x[i], np.array(Plotter.y[i]), color=colors[i])
            legend.append(Plotter.legend[i])
        pylab.legend(legend).draggable()
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        pylab.title(title)
        pylab.show()

    @staticmethod
    def tsplot(xlabel="", ylabel="", title=""):
        pylab.figure()
        indices = np.argsort(Plotter.scores)[::-1]
        colors = sns.color_palette("hls", len(indices))
        legend = []
        for i in indices:
            sns.tsplot(np.array(Plotter.y[i]), color=colors[i])
            legend.append(Plotter.legend[i])
        pylab.legend(legend).draggable()
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        pylab.title(title)
        pylab.show()

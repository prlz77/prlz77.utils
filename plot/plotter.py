import numpy as np
import seaborn as sns
import pylab

sns.set(font_scale=1.75)
sns.set_style("white")

class Plotter(object):
    def __init__(self):
        pylab.figure()
        self.legend = []
        self.scores = []
        self.x = []
        self.y = []

    def add_line(self, data, x=None, label="", score_f=np.nanmax):
        data = np.array(data, dtype=float)
        if x is None:
            x = np.arange(data.shape[-1])
        self.x.append(x)
        self.y.append(data)
        self.scores.append(score_f(data))
        self.legend.append(label)

    def plot(self, xlabel="", ylabel="", title=""):
        pylab.cla()
        indices = np.argsort(self.scores)[::-1]
        colors = sns.color_palette("deep", len(indices))
        legend = []
        color_lines = []
        for i in indices:
            pylab.plot(self.x[i], np.array(self.y[i]), color=colors[i])
            legend.append(self.legend[i])
            color_lines.append(pylab.Line2D([], [], color=colors[i]))
        pylab.legend(color_lines, legend, frameon=False, edgecolor='gray').draggable()
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        pylab.title(title)
        pylab.tight_layout()

    def tsplot(self, xlabel="", ylabel="", title=""):
        pylab.cla()
        indices = np.argsort(self.scores)[::-1]
        colors = sns.color_palette("deep", len(indices))
        legend = []
        color_lines = []
        for i in indices:
            mean = np.nanmean(self.y[i], 0)
            # min = np.nanmin(self.y[i], 0)
            # max = np.nanmax(self.y[i], 0)
            std = np.nanstd(self.y[i], 0)
            pylab.plot(self.x[i], mean, color=colors[i])
            pylab.fill_between(self.x[i], mean-std, mean + std,  color=colors[i], alpha=0.45)
            # pylab.fill_between(self.x[i], mean-min, mean + max,  color=colors[i], alpha=0.15)

            legend.append(self.legend[i])
            color_lines.append(pylab.Line2D([], [], color=colors[i]))
        pylab.legend(color_lines, legend, frameon=False, edgecolor='gray').draggable()
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        pylab.title(title)
        pylab.tight_layout()


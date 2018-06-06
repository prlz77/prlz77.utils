import matplotlib

matplotlib.use("qt5agg")
import argparse
import glob
import json
import os
import warnings
import pylab
import numpy as np
import pandas as pd


def filter_log(log, filter):
    filtersp = filter.split(" ")
    for w in filtersp:
        if w[0] == "$":
            filter = filter.replace(w, str(log[0][w[1:]]))
    return eval(filter)


def read_path(path_str, pre_fn=lambda x: x, filter=None):
    paths = glob.glob(path_str, recursive=True)
    logs = []
    for path in paths:
        if not os.path.isfile(path):
            warnings.warn("%s does not exist." % path)
        if path.split(".")[-1] == "json":
            with open(path, "r") as infile:
                log = json.load(infile)
                if filter is not None and not filter_log(log, filter):
                    pass
                else:
                    logs.append(pre_fn(log))
    return logs


def report(logs, target_field, output):
    idx = logs[target_field].replace(np.NaN, -1).groupby(level=0).idxmax()
    ret = pd.DataFrame(logs, index=idx)
    ret.to_csv(output)


def plot(logs, target_field, fields):
    fields = logs.keys() if fields is None else fields
    fields = list(set(fields) - set([target_field, "epoch"]))
    ret = logs.pivot_table(index="epoch", columns=fields, values=target_field).plot()
    pylab.gca().get_legend().draggable()
    pylab.show()


def main(args):
    if args.fields is not None:
        fields = set(args.fields)
        fields.add(args.target_field)
        fields.add("epoch")
        fields = list(fields)
    logs = read_path(args.paths, lambda data: pd.DataFrame(data=data, columns=fields), args.filter_hyperparam)
    logs = pd.concat(logs, keys=range(len(logs)))
    if args.command == "s" or args.command == "summarize":
        report(logs, args.target_field, args.summary_output)
    elif args.command == "p" or args.command == "plot":
        plot(logs, args.target_field, fields)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, choices=["summary", "s", "plot", "p"])
    parser.add_argument("paths", type=str, help="For instance, ./*.json")
    parser.add_argument("target_field", type=str, default="val_accuracy")
    parser.add_argument("--fields", type=str, nargs="*", default=None)
    parser.add_argument("--filter_hyperparam", type=str, nargs="?", default=[], help="$depth > 16")
    # Summary options
    parser.add_argument("--summary_output", "-so", type=str, default="report.csv")
    # Plot options
    parser.add_argument("--plot")

    args = parser.parse_args()

    main(args)

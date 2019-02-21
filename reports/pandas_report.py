import matplotlib

matplotlib.use('qt5agg')
import os
import sys

if "DISPLAY" not in os.environ:
    matplotlib.use("agg")
else:
    matplotlib.use('qt5agg')
import pandas as pd
import argparse
import glob
import json
import ndjson
import warnings
import pylab
import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x: x


def filter_log(log, filter):
    filtersp = filter.split(" ")
    for w in filtersp:
        if w[0] == "$":
            key = log[0][w[1:]]
            if isinstance(key, str):
                key = "'%s'" % key
            else:
                key = str(key)
            filter = filter.replace(w, key)
    return eval(filter)


def read_path(path_lst, pre_fn=lambda x: x, filter=None):
    paths = set([])
    for path in path_lst:
        paths.update(glob.glob(path, recursive=True))
    logs = []
    for path in tqdm(paths):
        if not os.path.isfile(path):
            warnings.warn("%s does not exist." % path)
        _, ext = os.path.splitext(path)
        if ext in [".json", ".ndjson"]:
            with open(path, "r") as infile:
                try:
                    if ext == ".json":
                        log = json.load(infile)
                    else:
                        log = ndjson.load(infile)
                except:
                    print("Error decoding %s" % path)

        if filter is not None and not filter_log(log, filter):
            pass
        else:
            log = pre_fn(log)
            if log is not None:
                logs.append(log)
    return logs


def print_empty(path_lst):
    for path in path_lst:
        for p in glob.glob(path):
            if not os.path.isfile(p):
                print(p)
            else:
                with open(p, 'r') as infile:
                    if len(infile.read()) <= 2:
                        print(p)

def convert_types(x):
    if not isinstance(x, int) and not isinstance(x, float):
        return str(x)
    elif np.isnan(x):
        return 'NaN'
    else:
        return x

def report(logs, target_field, columns, output, merge_op, x_axis):
    idx = logs[target_field].replace(np.NaN, -1).groupby(level=0).idxmax()
    ret = pd.DataFrame(logs, index=idx)

    if len(merge_op) > 0:
        ret = ret.applymap(convert_types)
        columns = list(columns)
        ret = ret.groupby(columns).agg(merge_op)

    ret.to_csv(output)


def plot_pandas(logs, target_field, columns, x_axis):
    columns = logs.keys() if columns is None else columns
    columns = list(set(columns) - set([target_field, x_axis]))
    logs = logs.applymap(lambda x: str(x) if isinstance(x, list) else x)
    ret = logs.pivot_table(index=x_axis, columns=columns, values=target_field, aggfunc=np.nanmean)
    ret.plot()
    pylab.gca().get_legend().draggable()
    pylab.show()


def plot_confidence(logs, target_field, columns, x_axis):
    columns = logs.keys() if columns is None else columns
    columns = list(set(columns) - set([target_field, x_axis]))
    logs = logs.applymap(lambda x: str(x) if isinstance(x, list) else x)
    # logs = pd.DataFrame(logs, index=logs[target_field].unstack().dropna(how='all').stack().index)
    ret = logs.pivot_table(index=x_axis, columns=columns, values=target_field,
                           aggfunc=[np.nanmin, np.nanmax, np.nanmean])
    ret_dict = ret.to_dict('list')
    new_dict = {}
    max_values = []
    max_keys = []
    for key in ret_dict:
        if key[0] == "nanmean":
            max_values.append(np.nanmax(ret_dict[key]))
            max_keys.append(key[1:])
        if key[1:] in new_dict:
            new_dict[key[1:]][key[0]] = ret_dict[key]
        else:
            new_dict[key[1:]] = {key[0]: ret_dict[key]}
    import seaborn as sns
    colors = sns.color_palette("deep", len(new_dict.keys()))
    styles = ["-", "--"]
    idx = np.argsort(max_values)[::-1]
    for i in range(len(idx)):
        key = max_keys[idx[i]]
        data = new_dict[key]
        amin = data['nanmin']
        amax = data['nanmax']
        mean = data['nanmean']
        pylab.fill_between(range(len(amin)), amin, amax, alpha=0.5, color=colors[i], )
        pylab.plot(range(len(amin)), mean, color=colors[i], linestyle=styles[i % len(styles)])
    pylab.xlabel(x_axis)
    pylab.ylabel(target_field)
    pylab.title("%s: %s" % (target_field, str(columns)))
    keys = [",".join([str(x) for x in max_keys[i]]) for i in idx]
    pylab.legend(keys, title=",".join(columns)).draggable()
    pylab.show()


def load_fn(data, filter_all=""):
    df = pd.DataFrame(data=data)  # , columns=columns)
    if filter_all != "":
        filtersp = filter_all.split("$")
        if len(filtersp) > 1:
            for f in filtersp:
                if f == '':
                    continue
                w = f.split(" ")[0]
                filter_all = filter_all.replace("$%s" % w, "df['%s']" % w)
        return df if eval(filter_all) else None
    else:
        return df

def auto_hyperparams(data, skip=[]):
    current_hyperparams = {}
    count = 0
    for _, log in data.groupby(level=0):
        count += 1
        cols = set(log.columns) - set(skip)
        for col in cols:
            if len(set(map(str, log[col].values))) == 1:
                if col in current_hyperparams:
                    current_hyperparams[col].append(str(log[col].values[0]))
                else:
                    current_hyperparams[col] = [str(log[col].values[0])]
    ret = []
    for k, v in current_hyperparams.items():
        l = len(set(map(str, v)))
        if l > 1 and l <= count * 0.8:
            ret.append(k)
    return ret




def main(args):
    if args.command in ["e", "empty"]:
        print_empty(args.paths)
        sys.exit()


    logs = read_path(args.paths, lambda x: load_fn(x, args.filter_all), args.filter_column)
    logs = pd.concat(logs, keys=range(len(logs)))

    if len(args.remove_columns) > 0:
        logs = logs.filter(items=(set(logs.columns) - set(args.remove_columns)))

    if args.auto:
        columns = auto_hyperparams(logs, [args.target_field, args.x_axis])
        print("Auto found params: ", columns)
    elif args.columns is not None:
        columns = set(args.columns)
        columns = list(columns)
    else:
        columns = []

    if len(columns) > 0 and not args.extended:
        logs = logs.filter(items=(columns + [args.target_field, args.x_axis]))


    if args.command == "s" or args.command == "summarize":
        merge_op = []
        if args.avg:
            merge_op.append("mean")
        elif args.med:
            merge_op.append("median")
        elif args.max:
            merge_op.append("max")
        if args.std:
            merge_op.append("std")

        report(logs, args.target_field, columns, args.summary_output, merge_op, args.x_axis)
    elif args.command == "p" or args.command == "plot":
        columns.append(args.target_field)
        columns.append(args.x_axis)
        if args.confidence:
            plot_confidence(logs, args.target_field, columns, args.x_axis)
        else:
            plot_pandas(logs, args.target_field, columns, args.x_axis)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, choices=["summary", "s", "plot", "p", "e", "empty"])
    parser.add_argument("paths", type=str, nargs="+", help="For instance, ./*.json")
    parser.add_argument("target_field", type=str)
    parser.add_argument("--auto", action="store_true", help="Automatically identifies hyperparameters")
    parser.add_argument("--multi", action="store_true", help="Interpret outer most folder as different experiments")
    parser.add_argument("--add_targets", type=str, default=[], nargs="+")
    parser.add_argument("--hyperparams", "-hp", type=str, nargs="*", default=None, help="Hyperparams to group")
    parser.add_argument("--columns", "-c", type=str, nargs="*", default=None, help="which columns to show")
    parser.add_argument("--remove_columns", '-rc', default=[], nargs="*", type=str)
    parser.add_argument("--filter_column", "-f", type=str, nargs="?", default=None, help="$depth > 16")
    parser.add_argument("--filter_all", type=str, default="", help="$accuracy > 0")
    parser.add_argument("--x_axis", type=str, default="epoch")
    # Summary options
    parser.add_argument("--extended", action="store_true", help="Show all fields")
    parser.add_argument("--summary_output", "-so", type=str, default="report.csv")
    parser.add_argument("--avg", action="store_true")
    parser.add_argument("--std", action="store_true", help="Appends standard deviation")
    parser.add_argument("--med", action="store_true", help="Use median.")
    parser.add_argument("--max", action="store_true", help="Use max")
    # Plot options
    parser.add_argument("--plot")
    parser.add_argument("--confidence", action="store_true")

    args = parser.parse_args()

    if args.multi:
        all = set([])
        for path in args.paths:
            all.update(glob.glob(path))
        expdirs = map(lambda x: x.split("/")[0], all)
        for expdir in set(expdirs):
            print(expdir)
            args.paths = list(filter(lambda x: x.split("/")[0] == expdir, all))
            args.summary_output = "report_%s.csv" %expdir
            main(args)
    else:
        main(args)

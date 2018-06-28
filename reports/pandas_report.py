import matplotlib
import os
if "DISPLAY" not in os.environ:
    matplotlib.use("agg")
else:
    matplotlib.use('qt5agg')
import pandas as pd
import argparse
import glob
import json
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
                key = "'%s'" %key
            else:
                key = str(key)
            filter = filter.replace(w, key)
    return eval(filter)


def read_path(path_lst, pre_fn=lambda x: x, filter=None):
    paths = set([])
    for path in path_lst:
        paths.update(glob.glob(path))
    logs = []
    for path in tqdm(paths):
        if not os.path.isfile(path):
            warnings.warn("%s does not exist." % path)
        if path.split(".")[-1] == "json":
            with open(path, "r") as infile:
                log = json.load(infile)
                if filter is not None and not filter_log(log, filter):
                    pass
                else:
                    log = pre_fn(log)
                    if log is not None:
                        logs.append(log)
    return logs


def report(logs, target_field, output, avg, x_axis):
    idx = logs[target_field].replace(np.NaN, -1).groupby(level=0).idxmax()
    ret = pd.DataFrame(logs, index=idx)
    if avg:
        ret = ret.applymap(lambda x: str(x) if isinstance(x, list) else x)
        columns = list(ret.columns)
        columns.remove(target_field)
        columns.remove(x_axis)
        ret = ret.groupby(columns).mean()

    ret.to_csv(output)


def plot_pandas(logs, target_field, columns, x_axis):
    columns = logs.keys() if columns is None else columns
    columns = list(set(columns) - set([target_field, x_axis]))
    ret = logs.pivot_table(index=x_axis, columns=columns, values=target_field)
    ret.plot()
    pylab.gca().get_legend().draggable()
    pylab.show()

def plot_confidence(logs, target_field, columns, x_axis):
    columns = logs.keys() if columns is None else columns
    columns = list(set(columns) - set([target_field, x_axis]))
    logs = logs.applymap(lambda x: str(x) if isinstance(x, list) else x)
   # logs = pd.DataFrame(logs, index=logs[target_field].unstack().dropna(how='all').stack().index)
    ret = logs.pivot_table(index=x_axis, columns=columns, values=target_field, aggfunc=[np.nanmin, np.nanmax, np.nanmean])
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
    pylab.title("%s: %s" %(target_field, str(columns)))
    keys = [",".join([str(x) for x in max_keys[i]]) for i in idx]
    pylab.legend(keys, title=",".join(columns)).draggable()
    pylab.show()


def load_fn(data, columns, filter_all=""):
    df = pd.DataFrame(data=data, columns=columns)
    if filter_all != "":
        filtersp = filter_all.split("$")
        if len(filtersp) > 1:
            for f in filtersp:
                w = f.split(" ")[0]
                filter_all = filter_all.replace("$%s" %w, "df['%s']" %w)
        return df if eval(filter_all) else None
    else:
        return df




def main(args):
    if args.columns is not None:
        columns = set(args.columns)
        columns.add(args.target_field)
        columns.add(args.x_axis)
        columns = list(columns)
    else:
        columns = None
    logs = read_path(args.paths, lambda x: load_fn(x, columns, args.filter_all), args.filter_column)
    logs = pd.concat(logs, keys=range(len(logs)))
    if args.command == "s" or args.command == "summarize":
        report(logs, args.target_field, args.summary_output, args.avg, args.x_axis)
    elif args.command == "p" or args.command == "plot":
        if args.confidence:
            plot_confidence(logs, args.target_field, columns, args.x_axis)
        else:
            plot_pandas(logs, args.target_field, columns, args.x_axis)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, choices=["summary", "s", "plot", "p"])
    parser.add_argument("paths", type=str, nargs="+", help="For instance, ./*.json")
    parser.add_argument("target_field", type=str )
    parser.add_argument("--columns", "-c", type=str, nargs="*", default=None)
    parser.add_argument("--filter_column", "-f", type=str, nargs="?", default=None, help="$depth > 16")
    parser.add_argument("--filter_all", type=str, default="", help="$accuracy > 0")
    parser.add_argument("--x_axis", type=str, default="epoch")
    # Summary options
    parser.add_argument("--summary_output", "-so", type=str, default="report.csv")
    parser.add_argument("--avg", action="store_true")
    # Plot options
    parser.add_argument("--plot")
    parser.add_argument("--confidence", action="store_true")

    args = parser.parse_args()

    main(args)

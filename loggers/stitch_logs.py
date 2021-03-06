import json
import ndjson
import argparse
import glob
import os
import warnings
import re

#path = '/Users/prlz77/Code/adaptron3000/results/psynbols2svhn_dynamic_retrain_policy/19910_4205_30636/log*json'

def read_file(path):
    print(path)
    with open(path, 'r') as f:
        if '.json' in path:
            return json.load(f)
        elif '.ndjson' in path:
            return ndjson.load(f)
        else:
            raise IOError('not a json file')

def stitch_logs(paths):
    ret = []
    for file in paths:
        data = read_file(file)
        counter = 0
        # Skipping headers
        while counter < len(data) and "epoch" not in data[counter]:
            counter += 1
        if counter == len(data):
            warnings.warn("Skipping header-only %s" %file)
            continue
        else:
            data = data[counter:]

        counter = 1
        if len(data) > 0:
            if len(ret) == 0:
                ret += data
                continue
            elif "retrain_iter" in ret[-counter]:
                while ret[-counter]["retrain_iter"] != data[0]["retrain_iter"]:
                    counter += 1
            if ret[-counter]["epoch"] + 1 >= data[0]["epoch"]:
                while ret[-counter]["epoch"] > data[0]["epoch"]:
                    counter += 1
                ret = ret[:-counter] + data
            elif ret[-counter]["epoch"] + 1 < data[0]["epoch"]:
                raise ValueError("Could not stitch logs on %s" %file)
    return ret

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=str,
                        help="root folder where experiments are located in subfolders. \
                              Works with infinite nesting.")
    parser.add_argument("--file_pattern", type=str, default="log_[0-9][0-9].ndjson")
    parser.add_argument("--silent", action="store_false")
    args = parser.parse_args()

    for root, dirs, files in os.walk(args.folder):
        matches = re.findall(args.file_pattern, ",".join(files))
        if len(matches) > 0:
            matches = [os.path.join(root, x) for x in sorted(matches)]
            stitched = stitch_logs(matches)
            if len(stitched) > 0:
                with open(os.path.join(os.path.dirname(matches[0]), 'log.ndjson'), 'w') as output:
                    print("Save: %s" %os.path.join(os.path.dirname(matches[0]), 'log.ndjson'))
                    ndjson.dump(stitched, output)
            else:
                if args.silent:
                    print("%s not processed" %str(matches))



if __name__ == "__main__":
    main()

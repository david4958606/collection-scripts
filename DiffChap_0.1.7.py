# coding=utf-8

import sys
if sys.version_info[:2] < (3, 6):
    print("The fxxx programmer is too lazy to check any support for Python 3.6-")
    input("Press ENTER to exit...")
    sys.exit(1)
import os
import re
import time
import multiprocessing as mp
from operator import methodcaller

HELP = """Differ Chapter 0.1.7
Drag an even number of OGM-format chapter files onto this script
The first half and the rest should come from different sources
Be careful about the file order when dragging
"""
TIME_THRESHOLD = 0.01
TIME_LINE_PATTERN = r"CHAPTER[0-9][0-9]=[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9][0-9][0-9]\n"
NAME_LINE_PATTERN = r"CHAPTER[0-9][0-9]NAME=.+\n"

def worker(fpath):
    try:
        with open(fpath[0], 'r') as fo1, open(fpath[1], 'r') as fo2:
            lines1 = fo1.readlines()
            lines2 = fo2.readlines()
    except:
        return ("Error in loading files",)
    if len(lines1) - len(lines2):
        return ("Error in comparing line numbers",)
    for line in lines1 + lines2:
        if not (re.match(TIME_LINE_PATTERN, line) or re.match(NAME_LINE_PATTERN, line)):
            return ("Error in checking file content %s" % line,)
    ret = []
    for i, line in enumerate(zip(lines1, lines2), start=1):
        line1 = line[0][:-1]
        line2 = line[1][:-1]
        if i % 2:
            hrs1 = int(line1.split(':')[0][-2:])
            min1 = int(line1.split(':')[1])
            sec1 = float(line1.split(':')[2])
            t1 = 3600 * hrs1 + 60 * min1 + sec1
            hrs2 = int(line2.split(':')[0][-2:])
            min2 = int(line2.split(':')[1])
            sec2 = float(line2.split(':')[2])
            t2 = 3600 * hrs2 + 60 * min2 + sec2
            if abs(t1 - t2) > TIME_THRESHOLD:
                ret.append(f"Time differs too much at line {i:2}: {line1} vs {line2}")
        else:
            line = line1 if "VCB-S" in fpath[0] else (line2 if "VCB-S" in fpath[1] else 0)
            if line and not re.match(r"Chapter [0-9][0-9]", line[14:]):
                ret.append(f"Recheck chapter name at line {i:2}: {line}")
    return ret if ret else ("Pass",)

if __name__ == "__main__":

    fpaths = sys.argv[1:]
    if len(fpaths) == 0:
        print(HELP)
        input("Press ENTER to exit...")
        sys.exit(1)
    if len(fpaths) % 2:
        print("File number should be multiples of two")
        input("Press ENTER to exit...")
        sys.exit(1)
    for fpath in fpaths:
        if os.path.isdir(fpath):
            print("Folders have not been supported yet")
            input("Press ENTER to exit...")
            sys.exit(1)
    rpath = f"{os.path.dirname(fpaths[0])}/result-{time.time()}.txt"

    pool = mp.Pool(processes=mp.cpu_count())
    num = len(fpaths) // 2
    result = [None] * num
    for i, fpath in enumerate(zip(fpaths[:num], fpaths[num:])):
        result[i] = pool.apply_async(func=worker, args=(fpath,))
    pool.close()
    pool.join()
    result = list(map(methodcaller("get"), result))

    with open(rpath, 'w') as fo:
        for fp1, fp2, r in zip(fpaths[:num], fpaths[num:], result):
            fo.write(f"{os.path.basename(fp1)} <==> {os.path.basename(fp2)}:\n")
            for l in r:
                fo.write(f"    {l}\n")

    print(f"Done and the result is at: {rpath}")
    time.sleep(3)
    sys.exit(0)

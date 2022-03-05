# coding=utf-8

import sys
if sys.version_info[:2] < (3, 6):
    print("The fxxx programmer is too lazy to check any support for Python 3.6-")
    input("Press ENTER to exit...")
    sys.exit(1)
import os
if os.name != 'nt':
    print("The fxxx programmer is too lazy to check any support for Linux and MacOS")
    input("Press ENTER to exit...")
    sys.exit(1)
import subprocess
try:
    subprocess.run('cwebp', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except FileNotFoundError:
    try:
        import PIL
        ver = PIL.__version__.split('.')
        if float(f"{ver[0]}.{ver[1]}") < 5.2:
            raise ImportError
    except ImportError:
        if os.system("pip install --upgrade pillow"):
            print("Necessary libraries have been installed/updated, please re-run this script")
            input("Press ENTER to exit...")
        else:
            print("Error in installing/updating necessary libraries")
            print("Please manually check 'pip install --upgrade pillow'")
            input("Press ENTER to exit...")
        sys.exit(1)
    else:
        TOOL = "pillow"
        from PIL import Image
else:
    TOOL = "cwebp"
import multiprocessing as mp
from operator import methodcaller
import time
import win32api
import win32con
import re

HELP = """Batch to Webp Converter 0.1.0
Drag any folders/files to the script in order to convert images under the 
Only certain extensions will be converted, controlled by 'EXTENSIONS'
Only certain presets will be used, controlled by this file's name and 'PRESETS'
"""
EXTENTIONS = (".BMP", ".PNG", ".TIF", ".TIFF")
PRESETS = {"cwebp": {"vcbs": "-q 90",
                     "lsls": "-z 9"},
           "pillow": {"vcbs": {"lossless": False, "quality": 90, "method": 6},
                      "lsls": {"lossless": True, "quality": 100, "method": 6}}}

FILENAME_PATTERN = r"ToWebp-[a-z]-[a-z][a-z][a-z][a-z]\.py"

def cwebp_worker(fpath, preset, keep):
    fbase = os.path.split(fpath)[1]
    rpath = f"{os.path.splitext(fpath)[0]}.webp"
    try:
        cmd = f"cwebp \"{fpath}\" {preset} -metadata all -o \"{rpath}\""
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        return f"{fpath} ==> webp\n    Error in converting"
    if not keep:
        try:
            os.remove(fpath)
        except:
            try:
                win32api.SetFileAttributes(fpath, win32con.FILE_ATTRIBUTE_NORMAL)
                os.remove(fpath)
            except:
                return f"{fpath} ==> webp\n    Succeeded but failed to delete {fbase}"
    return f"{fpath} ==> webp\n    Succeeded"

def pil_worker(fpath, preset, keep):
    try:
        im = Image.open(fpath)
    except:
        return f"{fpath}\n    Error in loading file"
    fbase = os.path.split(fpath)[1]
    rpath = f"{os.path.splitext(fpath)[0]}.webp"
    icc = im.info.get("icc_profile")
    try:  
        if icc:
            im.save(rpath, **preset, icc_procfile=icc)
        else:
            im.save(rpath, **preset)
    except:
        try:
            os.remove(rpath)
        except FileNotFoundError:
            pass
        except:
            return f"{fpath} ==> webp\n    Error in writing file and please manually remove the empty webp"
        return f"{fpath} ==> webp\n    Error in writing file"
    if not keep:
        try:
            os.remove(fpath)
        except:
            try:
                win32api.SetFileAttributes(fpath, win32con.FILE_ATTRIBUTE_NORMAL)
                os.remove(fpath)
            except:
                return f"{fpath} ==> webp\n    Succeeded but failed to delete {fbase}"
    return f"{fpath} ==> webp\n    Succeeded"

WORKER = {"cwebp": cwebp_worker, "pillow": pil_worker}

class RECURSIVE_CONVERTER():
    
    def __init__(self, worker, preset, keep):
        self.worker = worker
        self.preset = preset
        self.keep = keep

    def __call__(self, fpaths):
        self.ret = []
        self.pool = mp.Pool(processes=mp.cpu_count())
        self._recursive(fpaths)
        self.pool.close()
        self.pool.join()
        return list(map(methodcaller("get"), self.ret))

    def _recursive(self, fpaths):
        for fpath in fpaths:
            if os.path.isfile(fpath) and os.path.splitext(fpath)[1].upper() in EXTENTIONS:
                args = (fpath, self.preset, self.keep)
                self.ret.append(self.pool.apply_async(func=self.worker, args=args))
            elif os.path.isdir(fpath):
                self._recursive(f"{fpath}\\{i}" for i in os.listdir(fpath))

if __name__ == "__main__":

    name = os.path.split(sys.argv[0])[1]
    if not re.match(FILENAME_PATTERN, name):
        print(f"Invalid filename: '{name}'")
        input("Press ENTER to exit...")
        sys.exit(1)

    pname = name[-7:-3]
    if pname not in PRESETS[TOOL].keys():
        print(f"Invalid converter preset '{pname}'")
        input("Press ENTER to exit...")
        sys.exit(1)
    else:
        preset = PRESETS[TOOL][pname]
    print(f"Using {TOOL} with {preset}")

    kname = name[-9:-8]
    if kname == 'k':
        keep = True
        print("Keep source images")
    elif kname == 'n':
        keep = False
        print("Remove source images")
    else:
        print(f"Invalid indicator for keeping source: '{kname}'")
        input("Press ENTER to exit...")
        sys.exit(1)
        
    fpaths = sys.argv[1:]
    if len(fpaths) == 0:
        print(HELP)
        input("Press ENTER to exit...")
        sys.exit(1)

    print("working...\n")
    list(map(print, RECURSIVE_CONVERTER(WORKER[TOOL], preset, keep)(fpaths)))

    input("\nDone")
    sys.exit(0)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import os.path
import subprocess
import re
import numpy as np

if sys.version_info[0] < 3:
    input("Please use Python 3")
    sys.exit(1)


def get_path(exe):
    search_path = ['.'] + os.environ['PATH'].split(os.pathsep)
    path = ''
    for p in search_path:
        if os.path.isfile(os.path.join(p, exe)):
            path = os.path.join(p, exe)
            break
    if path == '':
        raise FileNotFoundError(
            'Please ensure `{}` is in your system!'.format(exe))
    return path


FFMPEG_EXECUTABLE = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
FFMPEG_PATH = get_path(FFMPEG_EXECUTABLE)

XCORR_RATIO = 3
MATH_BACKEND = 'scipy'
try:
    from scipy.signal import fftconvolve
except ImportError:
    MATH_BACKEND = 'numpy'
    print("Can not find `scipy`, using `numpy` instead.\nThis may cause lower performance.")

HELP_TEXT = """AUDIO DIFF Version 3.0
请把音频文件拖到本脚本身上
1、单文件时为输出自身的频谱图
2、多个文件时为将第按组对比（2n-1与2n）音频区别，再分别输出时间差、频谱图和指标
PS: 此处的第一个指拖动时鼠标下方的第一个，请尽量避免全角字符
"""

def read_wav(file):
    command = [FFMPEG_PATH,
               '-hide_banner',
               '-i', str(file),
               '-vn',
               '-ss', '00:00:15.00',
               '-t', '00:00:15.00',
               '-f', 'f32le',
               # '-ar', '2400',
               '-c:a', 'pcm_f32le',
               '-ac', '1',
               '-']
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8) as p:
        outs, errs = p.communicate()
        if p.returncode == 0:
            ptn = re.compile(r"Output #0.*\n(?:.*\n)+.*Stream #0:0.*?(\d+) Hz")
            sr = int(ptn.search(errs.decode('utf-8')).group(1))
            return (np.frombuffer(outs, dtype=np.float32), sr)
        else:
            raise ChildProcessError("ffmpeg has returned `{}` with following message:\n{}".format(
                p.returncode, errs.decode('utf-8')))


def get_offset(input_file):
    if not isinstance(input_file, tuple):
        raise TypeError()
    elif not len(input_file) == 2:
        raise ValueError()

    audio1 = read_wav(input_file[0])
    audio2 = read_wav(input_file[1])

    if audio1[1] != audio2[1]:
        raise ValueError('Sample rate of input files are inconsistent:\n{}: {}Hz\n{}: {}Hz'.format(
            input_file[0], audio1[1], input_file[1], audio2[1]))
    audio_array = (audio1[0], audio2[0])

    shorter_clip = audio_array[0] if len(audio_array[0]) < len(
        audio_array[1]) else audio_array[1]

    if MATH_BACKEND == 'scipy':
        xcorr = fftconvolve(audio_array[0], audio_array[1][::-1])
    else:
        xcorr = np.correlate(audio_array[0], audio_array[1], 'full')
    idx = np.argmax(xcorr)

    if XCORR_RATIO * xcorr[idx] > sum(shorter_clip ** 2):
        idx = idx - len(audio_array[1]) + 1
        starts = (abs(min(0, idx)), max(0, idx))
    else:
        starts = (0, 0)
    return starts


def draw_spectrumpic(input_file):
    filter_command = '[0:a1]aformat=sample_fmts=s16p:channel_layouts=mono,asplit=2[aout1][aout2];' \
        '[aout1]showspectrumpic=s=hd720[gout];' \
        '[aout2]astats[tout]'

    output_file = '{}.png'.format(os.path.splitext(input_file)[0])
    if os.path.exists(output_file):
        ans = input(
            "Output file `{}` already exists!\nContinue anyway? [y/N] ".format(output_file))
        if not (ans == 'y' or ans == 'Y'):
            return
    command = [FFMPEG_PATH,
               '-hide_banner',
               '-y',
               '-i', input_file,
               '-filter_complex', filter_command,
               '-map', '[gout]',
               output_file,
               '-map', '[tout]',
               '-f', 'null',
               '-'
               ]
    with subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, bufsize=10**8) as p:
        _, errs = p.communicate()
        if p.returncode == 0:
            ptn = re.compile(r'^\[Parsed_astats.*\] (.*)$', re.M)
            stats = re.findall(ptn, errs.decode('utf-8'))
            stats = stats[:next(
                i for i, s in enumerate(stats) if 'Overall' in s)]
            print('\n'.join(stats))
        else:
            raise ChildProcessError("ffmpeg has returned `{}` with following message:\n{}".format(
                p.returncode, errs.decode('utf-8')))


def draw_sub_spectrumpic(input_files, offset=(0, 0)):
    filter_command = '[0:a:0]pan=mono|c0=c0,adelay={}S,aformat=sample_fmts=s16p:channel_layouts=mono[am1];' \
        '[1:a:0]pan=mono|c0=c0,adelay={}S,aformat=sample_fmts=s16p:channel_layouts=mono[am2];' \
        '[am1][am2]amerge=inputs=2,pan=mono|c0=c0-c1,asplit=2[aout][aout2];' \
        '[aout]showspectrumpic=s=hd720[gout];' \
        '[aout2]astats[tout]' \
        .format(offset[0], offset[1])
    output_file = '{}.png'.format(os.path.splitext(input_files[0])[0])
    if os.path.exists(output_file):
        ans = input(
            "Output file `{}` already exists!\nContinue anyway? [y/N] ".format(output_file))
        if not (ans == 'y' or ans == 'Y'):
            return
    command = [FFMPEG_PATH,
               '-hide_banner',
               '-y',
               '-i', input_files[0],
               '-i', input_files[1],
               '-filter_complex', filter_command,
               '-map', '[gout]',
               output_file,
               '-map', '[tout]',
               '-f', 'null',
               '-'
               ]
    with subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, bufsize=10**8) as p:
        _, errs = p.communicate()
        if p.returncode == 0:
            ptn = re.compile(r'^\[Parsed_astats.*\] (.*)$', re.M)
            stats = re.findall(ptn, errs.decode('utf-8'))
            stats = stats[:next(
                i for i, s in enumerate(stats) if 'Overall' in s)]
            print('\n'.join(stats))
        else:
            raise ChildProcessError("ffmpeg has returned `{}` with following message:\n{}".format(
                p.returncode, errs.decode('utf-8')))


def main(file_list):
    for files in file_list:
        print("Ref: {}".format(files[0]))
        print("Cmp: {}".format(files[1]))
        offset = get_offset(files)
        if offset[0] > 0:
            print("The track is {} samples later than the reference.".format(offset[0]))
        elif offset[1] > 0:
            print("The track is {} samples earlier than the reference.".format(offset[1]))
        else:
            print("There is no delay between the two tracks.")
        draw_sub_spectrumpic(files, offset)
        # draw_sub_spectrumpic(files)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        draw_spectrumpic(os.path.realpath(sys.argv[1]))
    elif len(sys.argv) > 1 and len(sys.argv) % 2 == 1:
        files = list(map(os.path.realpath, sys.argv[1:]))
        main(
            list(zip(files[:int(len(files) / 2)], files[int(len(files) / 2):])))
        input("All finished!\nPlease press any key to exit!")
    else:
        print(HELP_TEXT)
    

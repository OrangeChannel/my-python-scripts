#!/usr/bin/python
"""OGM chapter timings generator that opens into toolnix GUI"""
import shlex
import subprocess
from fractions import Fraction

path_to_mkvtoolnix_gui = 'mkvtoolnix-gui'

frame_no = input('Enter STARTING frame number(s) (0-indexed)  (\'34 7004 13451\'): ')

frames = list(map(int, frame_no.split()))

names = shlex.split(input('Enter names as strings separated by spaces \'part a\' \'part b\' \'ED\': '))

fps = input('FPS (n/d) (blank for 23.976): ')

if fps is not '':
    n, d = fps.split('/')
    n = int(n)
    d = int(d)
else:
    n = 24000
    d = 1001

ts = []
for v in frames:
    t = round(10 ** 3 * v * Fraction(d, n))
    s = t / 10 ** 3
    m = s // 60
    s %= 60
    h = m // 60
    m %= 60

    ts.append('{:02.0f}:{:02.0f}:{:06.3f}'.format(h, m, s))

lines = []
for i in range(len(ts)):
    lines.append('CHAPTER{:02d}={}'.format(i, ts[i]))
    lines.append('CHAPTER{:02d}NAME={}'.format(i, names[i]))

text_file = open('chapters.txt', 'w')
for i in lines:
    text_file.write(i + '\n')
text_file.close()

gui = input('Open the MKVToolNix GUI? (Y/n): ')

if gui == 'Y':
    cmd = '{} --edit-chapters "chapters.txt"'
    args = shlex.split(cmd.format(path_to_mkvtoolnix_gui))
    subprocess.Popen(args)

else:
    exit()

#!/usr/bin/python
"""
Chapter timings generator
"""
from fractions import Fraction

frame_no = input('Frame number(s) (\'34 7004 13451\'): ')

frames = list(map(int, frame_no.split()))

fps = input('FPS (n/d) (blank for 23.976): ')

if fps:
    n, d = [*map(int, fps.split('/'))]
else:
    n, d = 24000, 1001

for v in frames:
    t = round(10 ** 9 * v * Fraction(d, n))
    s = t / 10 ** 9
    m = s // 60
    s %= 60
    h = m // 60
    m %= 60

    print('{:02.0f}:{:02.0f}:{:012.9f}'.format(h, m, s))

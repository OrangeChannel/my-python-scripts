#!/usr/bin/python
"""
Dependencies:
    which
    mv
    fd :      https://www.archlinux.org/packages/community/x86_64/fd/ OR `cargo install fd-find`
    rhash :   https://www.archlinux.org/packages/extra/x86_64/rhash/
    rnr :     https://aur.archlinux.org/packages/rnr/ OR `cargo install rnr`
    xdelta3 : https://www.archlinux.org/packages/community/x86_64/xdelta3/
    7z :      https://www.archlinux.org/packages/extra/x86_64/p7zip/
"""
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '6 February 2020'
import argparse
import re
import shlex
import subprocess
from sys import version_info
from typing import List
from shutil import which

if version_info[0] != 3 or version_info[1] < 8:
    raise SystemError("Python version 3.8+ required!")


def _check_dependencies(depends: List[str]):
    paths = {}

    for i in depends:
        if path := which(i): paths[i] = path
        else: raise OSError('{} not found in PATH'.format(i))

    return paths


def renamer(group_name: str, title: str, src: str, resolution: str):
    """Renames files from `ep##.mkv` to `[Group] Title - ## (SRC RESp)`."""
    paths = _check_dependencies(['fd', 'rnr'])

    cmd = '{} -e mkv -X {} -f --no-dump '.format(paths['fd'], paths['rnr']) + r'"(ep)(?P<num>\d+)" ' + '"[{}] {} - '.format(group_name, title) + r'$num ' + '({} {}p)"'.format(src, resolution)
    args = shlex.split(cmd)
    proc = subprocess.run(args, stdout=subprocess.PIPE, text=True)

    print('{} files have been renamed:\n'.format(len(proc.stdout.splitlines())))
    print(proc.stdout)


def hasher():
    """Appends CRC32 to filenames."""
    paths = _check_dependencies(['fd', 'rhash'])

    cmd = '{} -e mkv -X {} --embed-crc'.format(paths['fd'], paths['rhash'])
    args = shlex.split(cmd)

    proc = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    if x := proc.stderr:
        for i in x.splitlines(): print(i)

    filenum = 0
    for i in (lines := proc.stdout.splitlines()):
        if i[0] != r';': filenum += 1

    print('{} files have been renamed:\n'.format(filenum))
    for line in lines:
        if line[0] != r';': print(line[:-9])


def remover():
    """Removes CRC32 hash from filenames. Removes whitespace if needed."""
    paths = _check_dependencies(['fd', 'rnr'])

    cmd = '{} -e mkv -X {} -f --no-dump '.format(paths['fd'], paths['rnr']) + r'"(?P<hash>\s?\[\S{8}\].)" ' + r'"."'
    args = shlex.split(cmd)
    proc = subprocess.run(args, stdout=subprocess.PIPE, text=True)

    print('{} files have been renamed:\n'.format(len(proc.stdout.splitlines())))
    print(proc.stdout)


def checker():
    """Verifies CRC32 hashes in filenames."""
    paths = _check_dependencies(['fd', 'rhash'])

    cmd = '{} -e mkv -X {} -k'.format(paths['fd'], paths['rhash'])
    args = shlex.split(cmd)
    subprocess.run(args, text=True)


def cleaner():
    """Renames files based on unique one-two digit number found in original filename."""
    group_name = input('Group name: ')
    title = input('Show title: ')
    src = input('Source (TV, WEB, BD, DVD): ')
    resolution = input('Resolution (1080, 720...): ')
    paths = _check_dependencies(['fd', 'mv'])
    cmd = '{} -e mkv'.format(paths['fd'])
    args = shlex.split(cmd)
    orig_names = subprocess.Popen(args, stdout=subprocess.PIPE).stdout.read().decode().splitlines()
    orig_names = [i.rstrip() for i in orig_names]
    for k, name in enumerate(orig_names):
        m = re.search(r'(\s|_)(?P<num>\d{1,2})\D', name)
        if m:
            cmd = '{} "{}" "[{}] {} - {:02d} ({} {}p).mkv"'.format(paths['mv'], name, group_name, title, int(m.group('num')), src, resolution)
            args = shlex.split(cmd)
            subprocess.Popen(args)


def diff(numbers: List[int]):
    """TODO"""
    print(numbers)


parser = argparse.ArgumentParser(description='Utility functions for fansubbing.', epilog=r'More information on GitHub: https://github.com/OrangeChannel/my-python-scripts/blob/master/Fansubbing/README.md', prog='fansub_utils.py')
subparsers = parser.add_subparsers(help='Full command-line version of --renamer')
parser_renamer = subparsers.add_parser('renamer')
parser_renamer.add_argument('renamer', type=str, nargs=4, metavar='"str"', help='"group" "title" "src" "RES" - Batch renames "ep##.mkv" to "[group] title - ## (src RESp).mkv"')
parser.add_argument('-H', '--hasher', dest='hasher', action='store_true', default=False, help='Appends a CRC32 hash to the filenames: "file.mkv" -> "file [ABCD1234].mkv"')
parser.add_argument('-K', '--checker', dest='checker', action='store_true', default=False, help='Verifies CRC32 hashes in filenames')
parser.add_argument('-X', '--remover', dest='remover', action='store_true', default=False, help='Removes a CRC32 hash from filenames: "file [ABCD1234].mkv" -> "file.mkv"')
parser.add_argument('-R', '--renamer', dest='Prenamer', action='store_true', default=False, help='Useful for batch renaming "ep##.mkv" to "[Group] Title - ## (SRC RESp).mkv"')
parser.add_argument('-C', '--cleaner', dest='cleaner', action='store_true', default=False, help=r'Similar to renamer but works with any original filename format containing "_##"/" ##" or "_#"/" #"')
parser.add_argument('-D', '--diff', dest='diff', metavar='int', type=int, nargs='+', default=None, help='Creates an xdelta3 patch archive for one or more v2\'s specified by episode number(s)')


def _run():
    args = parser.parse_args()
    if hasattr(args, 'renamer'):
        renamer(*args.renamer)

    else:

        if args.Prenamer:
            renamer(input('Group name: '), input('Show title: '), input('Source (TV, WEB, BD, DVD): '), input('Resolution (1080, 720...): '))
        elif args.hasher:
            hasher()
        elif args.remover:
            remover()
        elif args.checker:
            checker()
        elif args.cleaner:
            cleaner()
        elif args.diff:
            diff([*map(int, args.diff)])
        else:
            print('Specify a function to run. Use `-h` for help.')


if __name__ == '__main__':
    _run()

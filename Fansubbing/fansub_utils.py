#!/usr/bin/python
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '6 February 2020'
from typing import List
import shlex
import subprocess
from sys import version_info
import argparse
import re

if version_info[0] != 3 or version_info[1] < 8:
    raise SystemError("Python version 3.8+ required!")


def _check_dependencies(depends: List[str]):
    paths = {}
    for i in depends:
        cmd = 'which ' + i
        args = shlex.split(cmd)
        if ' no {}'.format(i) in (path := subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().decode().rstrip()):
            raise OSError('{} not found in PATH'.format(i))
        else:
            paths[i] = path

    return paths


def renamer(group_name: str, title: str, src: str, resolution: int):
    """
    Renames files from `ep##.mkv` to `[Group] Title - ## (SRC RESp)`.

    :param group_name: name to be placed in brackets
    :param title: title of the show
    :param src: source (TV, WEB, BD, DVD...)
    :param resolution: 720, 1080, 840...
    """
    paths = _check_dependencies(['fd', 'rnr'])
    cmd = '{} -e mkv -X {} -f --no-dump '.format(paths['fd'], paths['rnr']) + r'"(ep)(?P<num>\d+)" ' + '"[{}] {} - '.format(group_name, title) + r'$num ' + '({} {}p)"'.format(src, resolution)
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    filenum = len(proc.stdout.read().decode().splitlines())
    proc.kill()
    print('{} files have been renamed.'.format(filenum))


def hasher():
    """Appends CRC32 to filenames."""
    paths = _check_dependencies(['fd', 'rhash'])
    cmd = '{} -e mkv -X {} --embed-crc'.format(paths['fd'], paths['rhash'])
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)

    filenum = 0
    for i in proc.stdout.read().decode().splitlines():
        if i[0] != r';': filenum += 1

    proc.kill()
    print('{} files have been renamed.'.format(filenum))


def remover():
    """Removes CRC32 hash from filenames. Removes whitespace if needed."""
    paths = _check_dependencies(['fd', 'rnr'])
    cmd = '{} -e mkv -X {} -f --no-dump '.format(paths['fd'], paths['rnr']) + r'"(?P<hash>\s?\[\S{8}\].)" ' + r'"."'
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    filenum = len(proc.stdout.read().decode().splitlines())
    proc.kill()
    print('{} files have been renamed.'.format(filenum))


def checker():
    """Verifies CRC32 hashes in filenames."""
    paths = _check_dependencies(['fd', 'rhash'])
    cmd = '{} -e mkv -X {} -k'.format(paths['fd'], paths['rhash'])
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE).stdout.read().decode()
    print(proc)


def cleaner():
    group_name = input('Group name: ')
    title = input('Show title: ')
    src = input('Source (TV, WEB, BD, DVD): ')
    resolution = int(input('Resolution (1080, 720...): '))
    paths = _check_dependencies(['fd', 'mv'])
    cmd = '{} -e mkv'.format(paths['fd'])
    args = shlex.split(cmd)
    orig_names = subprocess.Popen(args, stdout=subprocess.PIPE).stdout.read().decode().splitlines()
    orig_names = [i.rstrip() for i in orig_names]
    for k, name in enumerate(orig_names):
        m = re.search(r'\s(?P<num>\d{1,2})', name)
        if m:
            cmd = '{} "{}" "[{}] {} - {:02d} ({} {}p).mkv"'.format(paths['mv'], name, group_name, title, int(m.group('num')), src, resolution)
            args = shlex.split(cmd)
            subprocess.Popen(args)





parser = argparse.ArgumentParser(description='Utility functions for fansubbing.', epilog=r'Issue tracker on GitHub: https://github.com/OrangeChannel', prog='fansub_utils.py', usage='%(prog)s [mode]')
parser.add_argument('-H', '--hasher', dest='hasher', action='store_true', default=False, help='Appends a CRC32 hash to the filenames: "file.mkv" -> "file [ABCD1234].mkv"')
parser.add_argument('-K', '--checker', dest='checker', action='store_true', default=False, help='Verifies CRC32 hashes in filenames')
parser.add_argument('-X', '--remover', dest='remover', action='store_true', default=False, help='Removes a CRC32 hash from filenames: "file [ABCD1234].mkv" -> "file.mkv"')
parser.add_argument('-R', '--renamer', dest='renamer', action='store_true', default=False, help=r'Useful for batch renaming "ep##.mkv" to "[Group] Title - ## (SRC RESp).mkv"')
parser.add_argument('-C', '--cleaner', dest='cleaner', action='store_true', default=False, help=r'Similar to renamer but works with any original filename format containing " ##" or " #"')


def _run():
    args = parser.parse_args()

    if args.renamer:
        renamer(input('Group name: '), input('Show title: '), input('Source (TV, WEB, BD, DVD): '), int(input('Resolution (1080, 720...): ')))
    elif args.hasher:
        hasher()
    elif args.remover:
        remover()
    elif args.checker:
        checker()
    elif args.cleaner:
        cleaner()

    else:
        print('Specify a function to run. Use `-h` for help.')


if __name__ == '__main__':
    _run()

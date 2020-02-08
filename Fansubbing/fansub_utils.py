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
import re
import shlex
import subprocess
from sys import version_info
from typing import List
from shutil import which
import click

if version_info[0] != 3 or version_info[1] < 8:
    raise SystemError("Python version 3.8+ required!")


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Fansubbing utility functions. Meant to be ran inside of a folder with .mkv files.

\b
More information on GitHub:
https://github.com/OrangeChannel/my-python-scripts/blob/master/Fansubbing/README.md
    """


def _check_dependencies(depends: List[str]):
    paths = {}

    for i in depends:
        if path := which(i): paths[i] = path
        else: raise OSError('{} not found in PATH'.format(i))

    return paths


@cli.command()
@click.option('-q', '--quiet', is_flag=True, help='Supress output.')
@click.option('-v', '--verbose', is_flag=True, help='Prints new filenames.')
def hasher(quiet, verbose):
    """Appends CRC32 hash to filenames."""
    paths = _check_dependencies(['fd', 'rhash'])

    cmd = '{} -e mkv -X {} --embed-crc'.format(paths['fd'], paths['rhash'])
    args = shlex.split(cmd)

    proc = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    if err := proc.stderr:
        for i in err.splitlines(): print(i)

    filenum = 0
    for i in (lines := proc.stdout.splitlines()):
        if i[0] != r';': filenum += 1

    if not quiet:
        if verbose:
            print('{} files have been renamed:\n'.format(filenum))
            for line in lines:
                if line[0] != r';': print(line[:-9])
        else: print('{} files have been renamed.'.format(filenum))


@cli.command()
@click.option('-q', '--quiet', is_flag=True, help='Supress output.')
@click.option('-v', '--verbose', is_flag=True, help='Prints new filenames.')
def remover(quiet, verbose):
    """Removes CRC32 hash from filenames. Removes whitespace if needed."""
    paths = _check_dependencies(['fd', 'rnr'])

    cmd = '{} -e mkv -X {} -f --no-dump '.format(paths['fd'], paths['rnr']) + r'"(?P<hash>\s?\[\S{8}\].)" ' + r'"."'
    args = shlex.split(cmd)
    proc = subprocess.run(args, stdout=subprocess.PIPE, text=True)

    filenum = len(proc.stdout.splitlines())

    if not quiet:
        if verbose:
            print('{} files have been renamed:\n'.format(filenum))
            print(proc.stdout)
        else: print('{} files have been renamed.'.format(filenum))


@cli.command()
def checker():
    """Verifies CRC32 hashes in filenames."""
    paths = _check_dependencies(['fd', 'rhash'])
    cmd = '{} -e mkv -X {} -k'.format(paths['fd'], paths['rhash'])
    args = shlex.split(cmd)
    subprocess.run(args, text=True)


@cli.group()
def renamer():
    """Batch renames files."""


@renamer.command('simple')
@click.option('-G', '--group', prompt='Group name', metavar=r'"Group"')
@click.option('-T', '--title', prompt='Show title', metavar=r'"Title')
@click.option('-S', '--src', prompt='Source', type=click.Choice(['BD', 'DVD', 'TV', 'WEB'], case_sensitive=False))
@click.option('-R', '--res', prompt='Resolution <int>', metavar='<int>')
@click.option('-q', '--quiet', is_flag=True, help='Supress output.')
@click.option('-v', '--verbose', is_flag=True, help='Prints new filenames.')
def simple_renamer(group: str, title: str, src: str, res: str, quiet, verbose):
    """Renames from `ep##.mkv` to `[Group] Title - ## (SRC RESp).mkv`."""
    paths = _check_dependencies(['fd', 'rnr'])

    cmd = '{} -e mkv -X {} -f --no-dump '.format(paths['fd'], paths['rnr']) + r'"(ep)(?P<num>\d+)" ' + '"[{}] {} - '.format(group, title) + r'$num ' + '({} {}p)"'.format(src.upper(), res)
    args = shlex.split(cmd)
    proc = subprocess.run(args, stdout=subprocess.PIPE, text=True)

    filenum = len(proc.stdout.splitlines())

    if not quiet:
        if verbose:
            print('{} files have been renamed:\n'.format(filenum))
            print(proc.stdout)
        else:
            print('{} files have been renamed.'.format(filenum))


@renamer.command('cleaner')
@click.option('-G', '--group', prompt='Group name', metavar=r'"Group"')
@click.option('-T', '--title', prompt='Show title', metavar=r'"Title')
@click.option('-S', '--src', prompt='Source', type=click.Choice(['BD', 'DVD', 'TV', 'WEB'], case_sensitive=False))
@click.option('-R', '--res', prompt='Resolution <int>', metavar='<int>')
@click.option('-D', '--dryrun', is_flag=True, help='Prints new filenames without modifying them.')
def cleaner(group: str, title: str, src: str, res: str, dryrun):
    """Renames files based on unique 1-2 digit number found in original filename.

Will find episode number from a '_#'/' #' or '_##'/' ##' sub-string in filename.

WARNING: if same number is found in multiple filenames,
files will be overwritten with one file. This is NOT reversible.

Run with `--dryrun` to make sure your files have unique episode numbers.

\b
Files that are OK:
    `re:zero 06v3.mkv` --> 06
    `[Trash] rezero s2 episode 12[ABCD1234].mkv` --> 12
    `[Trash] Re:Zero2_5.mkv` --> 05
    `[Garbage *$ s1 ReZERO 1.mkv` --> 01

\b
Files that are NOT unique:
    `re:zero season 2 06v3.mkv` --> 02
    `[Trash] rezero s_2 episode 12[ABCD1234].mkv` --> 02
    `[Trash] Re:Zero 2_5.mkv` --> 02
    `[Garbage *$ s1 ReZERO 02.mkv` --> 02
"""
    paths = _check_dependencies(['fd', 'mv'])

    cmd = '{} -e mkv'.format(paths['fd'])
    args = shlex.split(cmd)
    orig_names = subprocess.run(args, stdout=subprocess.PIPE, text=True).stdout.splitlines()
    orig_names = [i.rstrip() for i in orig_names]
    new_names = []

    for k, name in enumerate(orig_names):
        m = re.search(r'(\s|_)(?P<num>\d{1,2})\D', name)
        if m:
            if dryrun:
                print('"{}"'.format(name))

                new_name = '\t--> "[{}] {} - {:02d} ({} {}p).mkv"'.format(group, title, int(m.group('num')), src.upper(), res)
                if new_name in new_names:
                    click.secho(new_name + '\tERR', fg='bright_red', bold=True, blink=True)
                else:
                    print(new_name)
                    new_names.append(new_name)
            else:
                cmd = '{} "{}" "[{}] {} - {:02d} ({} {}p).mkv"'.format(paths['mv'], name, group, title, int(m.group('num')), src.upper(), res)
                args = shlex.split(cmd)
                subprocess.Popen(args)


def diff(numbers: List[int]):
    """TODO"""
    print(numbers)


if __name__ == '__main__':
    cli()

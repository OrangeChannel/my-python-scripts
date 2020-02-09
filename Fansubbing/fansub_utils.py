#!/usr/bin/python
"""
Dependencies:
    which
    mkdir
    mv
    fd :      https://www.archlinux.org/packages/community/x86_64/fd/ OR `cargo install fd-find`
    rhash :   https://www.archlinux.org/packages/extra/x86_64/rhash/
    rnr :     https://aur.archlinux.org/packages/rnr/ OR `cargo install rnr`
    xdelta3 : https://www.archlinux.org/packages/community/x86_64/xdelta3/
    7z :      https://www.archlinux.org/packages/extra/x86_64/p7zip/
"""
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '8 February 2020'

from re import search
from shlex import split as ssplit
from shutil import which
from subprocess import PIPE, run, STDOUT
from sys import exit
from typing import List

import click

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
    args = ssplit(cmd)

    proc = run(args, stderr=PIPE, stdout=PIPE, text=True)
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
    args = ssplit(cmd)
    proc = run(args, stdout=PIPE, text=True)

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
    args = ssplit(cmd)
    run(args, text=True)


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
    args = ssplit(cmd)
    proc = run(args, stdout=PIPE, text=True)

    filenum = len(proc.stdout.splitlines())

    if not quiet:
        if verbose:
            print('{} files have been renamed:\n'.format(filenum))
            print(proc.stdout)
        else:
            print('{} files have been renamed.'.format(filenum))


@renamer.command()
@click.option('-D', '--dryrun', is_flag=True, help='Prints new filenames without modifying them.')
@click.option('-G', '--group', prompt='Group name', metavar=r'"Group"')
@click.option('-T', '--title', prompt='Show title', metavar=r'"Title')
@click.option('-S', '--src', prompt='Source', type=click.Choice(['BD', 'DVD', 'TV', 'WEB'], case_sensitive=False))
@click.option('-R', '--res', prompt='Resolution <int>', metavar='<int>')
def cleaner(dryrun, group: str, title: str, src: str, res: str):
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
    args = ssplit(cmd)
    orig_names = run(args, stdout=PIPE, text=True).stdout.splitlines()
    orig_names = [i.rstrip() for i in orig_names]
    new_names = []

    for k, name in enumerate(orig_names):
        m = search(r'(\s|_)(?P<num>\d{1,2})\D', name)
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
                args = ssplit(cmd)
                run(args)


@cli.command()
@click.option('-D', '--dryrun', is_flag=True, help='Prints detected v2 files without creating patches.')
@click.option('-v', '--verbose', is_flag=True, help='Prints all operations\' outputs.')
def diff(dryrun, verbose):
    """Creates xdelta3 patches for v2 files.

Packs patches, a README, and Windows / Linux auto-patch scripts into a .7z archive called "patches.7z".

Should be used on files cleaned/renamed with renamer in the following format:


    [Group] Title - ## (SRC RESp) [CRC32CRC].mkv

    \b
i.e.
[ChannelOrange] Re:Zero Season 5 - 01 (BD 1080p) [468A23FD].mkv
[ChannelOrange] Re:Zero Season 5 - 02 (BD 1080p) [BACB9212].mkv
[ChannelOrange] Re:Zero Season 5 - 02v2 (BD 1080p) [E9F7A497].mkv
[ChannelOrange] Re:Zero Season 5 - 03 (BD 1080p) [FBE791AF].mkv
[ChannelOrange] Re:Zero Season 5 - 03v2 (BD 1080p) [CEDA7D89].mkv

    Will create patches for episodes 2 and 3 only.

Run with `--dryrun` to see what episode patches will be created.
"""
    paths = _check_dependencies(['fd', 'xdelta3', '7z', 'mkdir', 'rm'])

    cmd = '{} -e mkv'.format(paths['fd'])
    args = ssplit(cmd)
    orig_names = run(args, stdout=PIPE, text=True).stdout.splitlines()
    orig_names = [i.rstrip() for i in orig_names]

    episodes, old_names, new_names = {}, {}, {}

    for name in orig_names:
        m = search(r'- (?P<epnum>\d{2})v?(?P<version>\d)?', name)
        if m:
            episodes.setdefault(int(m.group('epnum')), []).append(name)

            if verbose:
                if m.group('version'):
                    print('Episode {} version {} detected.'.format(m.group('epnum'), m.group('version')))

    for num in episodes:
        if len(episodes[num]) > 2:
            raise ValueError('Episode {} has more than 2 versions!'.format(num))
        if len(episodes[num]) < 2:
            episodes[num] = None

    for num in episodes:
        if episodes[num]:
            old_names[num] = episodes[num][0]
            new_names[num] = episodes[num][1]

    if verbose or dryrun:
        for num in old_names:
            click.secho('{}'.format(old_names[num]), fg='green')
            click.secho('\t--> {}'.format(new_names[num]), fg='bright_blue')

    if not dryrun:
        dirargs = ssplit('{} patches'.format(paths['mkdir']))
        mkdir = run(dirargs, stdout=PIPE, stderr=STDOUT, text=True)
        if mkdir.stdout:
            click.secho('ERR: ' + mkdir.stdout.rstrip(), fg='bright_red')
            exit()

        dirargs = ssplit('{} patches/vcdiff'.format(paths['mkdir']))
        mkdir = run(dirargs, stdout=PIPE, stderr=STDOUT, text=True)
        if mkdir.stdout:
            click.secho('ERR: ' + mkdir.stdout.rstrip(), fg='bright_red')
            exit()

        for num in old_names:
            cmd = '{} -q -e -s "{}" "{}" "patches/vcdiff/{:02d}.vcdiff"'.format(paths['xdelta3'], old_names[num], new_names[num], num)
            args = ssplit(cmd)
            run(args)

        readme = """Windows:
1. Extract the patches.7z (containing this file and a vcdiff folder) into your folder containing the original episode .mkv files.
2. Double click the _Apply-Patch_windows.bat file and the patching will start automatically.
3. When finished, the new file will appear in this folder and the original will be moved to a folder called 'old'.
4. Delete the vcdiff folder along with this file and the Apply-Patch files.

Linux:
1. Extract the patches.7z (containing this file and a vcdiff folder) into your folder containing the original episode .mkv files.
2. Run _Apply-Patch_unix.sh.
3. When finished, the new file will appear in this folder and the original will be moved to a folder called 'old'.
4. You will be prompted to auto-delete the patch files."""

        linux_patch = '` #!/bin/sh`\n` mkdir old`'

        for num in old_names:
            linux_patch += '\n` xdelta3 -v -d -s "{}" "vcdiff/{:02}.vcdiff" "{}"`'.format(old_names[num], num, new_names[num])
            linux_patch += '\n` mv "{}" old`'.format(old_names[num])

        linux_patch += '\n` rm -i -r vcdiff`'
        linux_patch += '\n` rm -i "_README.txt" "_Apply-Patch_windows.bat"`\n'

        windows_patch = '@echo off\nmkdir old'

        for num in old_names:
            windows_patch += '\n.\\xdelta3.exe -v -d -s "{}" "vcdiff/{:02}.vcdiff" "{}"`'.format(old_names[num], num, new_names[num])
            windows_patch += '\nmove "{}" old'.format(old_names[num])

        windows_patch += '\necho Patching complete.'
        windows_patch += '\n@pause\n'

        readme_file = open('patches/_README.txt', 'w')
        readme_file.write(readme)
        readme_file.close()

        linux_file = open('patches/_Apply-Patch_unix.sh', 'w')
        linux_file.write(linux_patch)
        linux_file.close()

        windows_file = open('patches/_Apply-Patch_windows.bat', 'w')
        windows_file.write(windows_patch)
        windows_file.close()

        cmd = '7z a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on patches.7z patches'
        args = ssplit(cmd)
        archive_proc = run(args, stdout=PIPE, stderr=PIPE, text=True)
        if archive_proc.stderr:
            click.secho('ERR: ' + archive_proc.stderr.rstrip(), fg='bright_red')
            exit()
        else:
            if verbose:
                print(archive_proc.stdout)

        rm_cmd = '{} -i -r patches'.format(paths['rm'])
        args = ssplit(rm_cmd)
        run(args, text=True)


if __name__ == '__main__':
    cli()

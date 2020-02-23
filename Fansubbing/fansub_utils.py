#!/usr/bin/python
"""
Dependencies:
    which
    cp
    mkdir
    mv
    rm
    fd :      https://www.archlinux.org/packages/community/x86_64/fd/ OR `cargo install fd-find`
    rhash :   https://www.archlinux.org/packages/extra/x86_64/rhash/
    rnr :     https://aur.archlinux.org/packages/rnr/ OR `cargo install rnr`
    xdelta3 : https://www.archlinux.org/packages/community/x86_64/xdelta3/
    7z :      https://www.archlinux.org/packages/extra/x86_64/p7zip/
"""
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '22 February 2020'

from re import search
from shutil import which
from subprocess import PIPE, run, STDOUT
from sys import exit
from typing import List

import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Fansubbing utility functions. Batch processing functions meant to be ran inside of a folder with .mkv files.

\b
More information on GitHub:
https://github.com/OrangeChannel/my-python-scripts/blob/master/Fansubbing
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
def hasher(quiet: bool, verbose: bool):
    """Appends CRC32 hash to filenames."""
    paths = _check_dependencies(['fd', 'rhash'])

    args = [paths['fd'], '-e', 'mkv', '-X', paths['rhash'], '--embed-crc']
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
def remover(quiet: bool, verbose: bool):
    """Removes CRC32 hash from filenames. Removes whitespace if needed."""
    paths = _check_dependencies(['fd', 'rnr'])

    args = [paths['fd'], '-e', 'mkv', '-X', paths['rnr'], '-f', '--no-dump', r'\s*\[\S{8}\]\s*\.', '.']
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

    run([paths['fd'], '-e', 'mkv', '-X', paths['rhash'], '-k'], text=True)


@cli.group()
def renamer():
    """Batch renames files."""


@renamer.command('simple')
@click.option('-G', '--group', prompt='Group name', metavar=r'"Group"')
@click.option('-T', '--title', prompt='Show title', metavar=r'"Title')
@click.option('-S', '--src', prompt='Source', type=click.Choice(['BD', 'DVD', 'TV', 'WEB'], case_sensitive=False))
@click.option('-R', '--res', prompt='Resolution <int>', metavar='INT', type=click.IntRange(72, 2160))
@click.option('-q', '--quiet', is_flag=True, help='Supress output.')
@click.option('-v', '--verbose', is_flag=True, help='Prints new filenames.')
def simple_renamer(group: str, title: str, src: str, res: int, quiet: bool, verbose: bool):
    """Renames from `ep##.mkv` to `[Group] Title - ## (SRC RESp).mkv`."""
    paths = _check_dependencies(['fd', 'rnr'])

    args = [paths['fd'], '-e', 'mkv', '-X', paths['rnr'], '-f', '--no-dump', r'ep(?P<num>\d+)', f'[{group}] {title} - $num ({src.upper()} {res}p)']
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
@click.option('-R', '--res', prompt='Resolution <int>', metavar='INT', type=click.IntRange(72, 2160))
def cleaner(dryrun: bool, group: str, title: str, src: str, res: int):
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

    orig_names = run([paths['fd'], '-e', 'mkv'], stdout=PIPE, text=True).stdout.splitlines()
    orig_names = [i.rstrip() for i in orig_names]
    new_names = []

    for k, name in enumerate(orig_names):
        m = search(r'[\s_](?P<num>\d{1,2})\D', name)
        if m:
            if dryrun:
                print(f'"{name}"')

                new_name = '\t--> "[{}] {} - {:02d} ({} {}p).mkv"'.format(group, title, int(m.group('num')), src.upper(), res)
                if new_name in new_names:
                    click.secho(new_name + '\tERR', fg='bright_red', bold=True, blink=True)
                else:
                    print(new_name)
                    new_names.append(new_name)
            else:
                args = [paths['mv'], name, '[{}] {} - {:02d} ({} {}p).mkv'.format(group, title, int(m.group('num')), src.upper(), res)]
                run(args)


@cli.command()
@click.option('-D', '--dryrun', is_flag=True, help='Prints detected v2 files without creating patches.')
@click.option('-W', '--windows', is_flag=True, default=False, help='Creates patch script for Windows users (requires xdelta3.exe in folder).')
@click.option('-v', '--verbose', is_flag=True, help='Prints all operations\' outputs.')
def diff(dryrun: bool, windows: bool, verbose: bool):
    """Creates xdelta3 patches for v2 files.

Packs patches, a README, and Windows / Linux auto-patch scripts into a .7z archive called "patches.7z".

If running in --windows mode, you must have an xdelta3.exe binary in the same folder as the .mkv files.
The exe can be downloaded from here: https://github.com/jmacd/xdelta-gpl/releases and needs to be renamed
to `xdelta3.exe`.

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
    paths = _check_dependencies(['fd', 'xdelta3', '7z', 'mkdir', 'rm', 'mv', 'cp'])

    orig_names = run([paths['fd'], '-e', 'mkv'], stdout=PIPE, text=True).stdout.splitlines()
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
        patch_mkdir_proc = run([paths['mkdir'], 'patches'], stdout=PIPE, stderr=STDOUT, text=True)
        if patch_mkdir_proc.stdout:
            click.secho('ERR: ' + patch_mkdir_proc.stdout.rstrip(), fg='bright_red')
            exit()

        if windows:
            mvx = run([paths['mv'], 'xdelta3.exe', 'patches'], stdout=PIPE, stderr=STDOUT, text=True)
            if mvx.stdout:
                click.secho('ERR: ' + mvx.stdout.rstrip(), fg='bright_red')
                click.secho('Running with --windows requires an xdelta3.exe file in the folder.', fg='bright_red')
                run([paths['rm'], '-r', 'patches'])
                exit()

        vcdiff_mkdir_proc = run([paths['mkdir'], 'patches/vcdiff'], stdout=PIPE, stderr=STDOUT, text=True)
        if vcdiff_mkdir_proc.stdout:
            click.secho('ERR: ' + vcdiff_mkdir_proc.stdout.rstrip(), fg='bright_red')
            exit()

        for num in old_names:
            run([paths['xdelta3'], '-q', '-e', '-s', old_names[num], new_names[num], f'patches/vcdiff/{num:02d}.vcdiff'])

        readme = """Linux:
1. Extract the patches.7z (containing this file and a vcdiff folder) into your folder containing the original episode .mkv files.
2. Run _Apply-Patch_unix.sh.
3. When finished, the new file will appear in this folder and the original will be moved to a folder called 'old'.
4. You will be prompted to auto-delete the patch files.\n\n"""

        if windows:
            readme += """Windows:
1. Extract the patches.7z (containing this file and a vcdiff folder) into your folder containing the original episode .mkv files.
2. Double click the _Apply-Patch_windows.bat file and the patching will start automatically.
3. When finished, the new file will appear in this folder and the original will be moved to a folder called 'old'.
4. Delete the vcdiff folder along with this file and the Apply-Patch files."""

        linux_patch = '` #!/bin/sh`\n` mkdir old`'

        for num in old_names:
            linux_patch += '\n` xdelta3 -v -d -s "{}" "vcdiff/{:02d}.vcdiff" "{}"`'.format(old_names[num], num, new_names[num])
            linux_patch += '\n` mv "{}" old`'.format(old_names[num])

        linux_patch += '\n` rm -i -r vcdiff`'
        linux_patch += '\n` rm -i "_README.txt" "_Apply-Patch_windows.bat"`'
        if windows:
            linux_patch += '\n` rm -i "xdelta3.exe"`\n'

        windows_patch = '@echo off\nmkdir old'

        for num in old_names:
            windows_patch += '\n.\\xdelta3.exe -v -d -s "{}" "vcdiff/{:02d}.vcdiff" "{}"`'.format(old_names[num], num, new_names[num])
            windows_patch += '\nmove "{}" old'.format(old_names[num])

        windows_patch += '\necho Patching complete.'
        windows_patch += '\n@pause\n'

        readme_file = open('patches/_README.txt', 'w')
        readme_file.write(readme)
        readme_file.close()

        linux_file = open('patches/_Apply-Patch_unix.sh', 'w')
        linux_file.write(linux_patch)
        linux_file.close()

        linux_xdelta3_lib = run([paths['cp'], paths['xdelta3'], 'patches/xdelta3'], stdout=PIPE, stderr=STDOUT, text=True)
        if linux_xdelta3_lib.stdout:
            click.secho('ERR: ' + linux_xdelta3_lib.stdout.rstrip(), fg='bright_red')
            exit()

        if windows:
            windows_file = open('patches/_Apply-Patch_windows.bat', 'w')
            windows_file.write(windows_patch)
            windows_file.close()

        args = [paths['7z'], 'a', '-t7z', '-m0=lzma', '-mx=9', '-mfb=6', '-md=32m', '-ms=on', 'patches.7z', 'patches']
        archive_proc = run(args, stdout=PIPE, stderr=PIPE, text=True)
        if archive_proc.stderr:
            click.secho('ERR: ' + archive_proc.stderr.rstrip(), fg='bright_red')
            exit()
        else:
            if verbose:
                print(archive_proc.stdout)

        run([paths['rm'], '-i', '-r', 'patches'], text=True)


@cli.command('bitrate')
@click.option('-S', '--size', type=click.FLOAT, help='Filesize (number only).', prompt=True)
@click.option('-U', '--unit', type=click.Choice(['TB', 'GB', 'MB', 'kB', 'TiB', 'GiB', 'MiB', 'KiB'], case_sensitive=False), prompt=True)
@click.option('-T', '--time', type=click.FLOAT, help='Time (in seconds) of clip.', default=0)
@click.option('-F', '--frames', type=click.INT, help='Number of frames in clip.', default=0)
@click.option('-R', '--framerate', default=24000/1001, type=click.FLOAT, help='Framerate (in fps) of clip. (23.976 by default)')
def bitrate_(size: float, unit: str, time: float, frames: int, framerate: float):
    """Converts a desired filesize into average bitrate in kbps.

If specifying --time, you do not need to specify --frames and vice versa. Units will be prompted for if not specified.

\b
Examples:
    \b
    For a 950 MiB file that is 24 minutes long:
    $ python fansub_utils.py bitrate -S 950 -U mib -T 1440
    > Bitrate should be 5,534 kbps.
....
    For a 2 GB file that is 34720 frames long:
    $ python fansub_utils.py bitrate --size 2 -F 34720
    > Unit (TB, GB, MB, kB, TiB, GiB, MiB, KiB): gb
    > Bitrate should be 11,049 kbps."""
    if not time and not frames:
        click.secho('ERR: --time or --frames must be specified.', fg='bright_red')
        exit()

    decimal = {'k': 1000,
               'm': 1000 ** 2,
               'g': 1000 ** 3,
               't': 1000 ** 4}

    binary = {'k': 1024,
              'm': 1024 ** 2,
              'g': 1024 ** 3,
              't': 1024 ** 4}

    if frames:
        time = (framerate ** -1) * frames

    if 'i' in unit:
        bytes_ = binary[unit.lower()[0]] * size
    else:
        bytes_ = decimal[unit.lower()[0]] * size

    bits = bytes_ * 8

    rate = round((bits / 1000) / time)
    print('Bitrate should be {:,} kbps.'.format(rate))


@cli.command()
@click.option('-B', '--bitrate', type=click.INT, help='Average bitrate in kbps.', prompt=True)
@click.option('-T', '--time', type=click.FLOAT, help='Time (in seconds) of clip.', default=0)
@click.option('-F', '--frames', type=click.INT, help='Number of frames in clip.', default=0)
@click.option('-R', '--framerate', default=24000/1001, type=click.FLOAT, help='Framerate (in fps) of clip. (23.976 by default)')
def filesize(bitrate: int, time: float, frames: int, framerate: float):
    """Estimates filesize based on average bitrate in kbps.

\b
Examples:
    \b
    At 7,774 kbps for 32,000 frames:
    $ python fansub_utils.py filesize -B 7774 -F 32000
    > Estimated filesize is 1.21 GiB or 1.30 GB.
....
    At 5,736 kbps for 24 minutes:
    $ python fansub_utils.py filesize -B 5736 -T 1440
    > Estimated filesize is 984.65 MiB or 1.03 GB."""
    if not time and not frames:
        click.secho('ERR: --time or --frames must be specified.', fg='bright_red')
        exit()

    if frames:
        time = (framerate ** -1) * frames

    bits = bitrate * 1000 * time
    bytes_ = bits / 8

    if (bsize := bytes_ / 1024 ** 4) >= 1: binary = 'Ti'
    elif (bsize := bytes_ / 1024 ** 3) >= 1: binary = 'Gi'
    elif (bsize := bytes_ / 1024 ** 2) >= 1: binary = 'Mi'
    elif (bsize := bytes_ / 1024) >= 1: binary = 'Ki'
    else:
        click.secho('ERR: resulting filesize too small', fg='bright_red')
        exit()

    if (dsize := bytes_ / 1000 ** 4) >= 1: decimal = 'T'
    elif (dsize := bytes_ / 1000 ** 3) >= 1: decimal = 'G'
    elif (dsize := bytes_ / 1000 ** 2) >= 1: decimal = 'M'
    elif (dsize := bytes_ / 1000) >= 1: decimal = 'k'
    else:
        click.secho('ERR: resulting filesize too small', fg='bright_red')
        exit()

    print('Estimated filesize is {:.2f} {}B or {:.2f} {}B.'.format(bsize, binary, dsize, decimal))


if __name__ == '__main__':
    cli()

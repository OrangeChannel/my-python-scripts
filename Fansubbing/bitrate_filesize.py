"""Bitrate and filesize calculator."""
__all__ = ['bitrate', 'filesize']
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '30 November 2019'

from string import ascii_uppercase


def bitrate(size: str, seconds: int = None, frames: int = None,
            framerate: float = 24000 / 1001):
    """Converts a desired filesize into average bitrate in kbps.

    >>> bitrate('118.5 MB', seconds=1050)  # 118.5 megabytes
    bitrate should be 903 kbps
    >>> bitrate('24 g', frames=46500)  # 24 gigabits
    bitrate should be 12,375 kbps
    >>> bitrate('24 gi', frames=46500)  # 24 gibibits
    bitrate should be 13,287 kbps

    :param size: desired size i.e. '4.7 GiB'
        size is in the format '<float> <unit>' where unit can take any
        of the following forms:
        T=TB,   Ti=TiB,   t=tb,   ti=tib
        G=GB,   Gi=GiB,   g=gb,   gi=gib
        M=MB,   Mi=MiB,   m=mb,   mi=mib
        K=KB,   Ki=KiB,   k=kb,   ki=kib

        an 'i' indicates a binary system (2**30 = GiB)
        otherwise uses a decimal system (1E9 = GB)

        capital 'T, G, M, K' indicates the size is in bytes
        lowercase 't, g, m, k' indicates the size is in bits

    :param seconds: number of seconds in clip (Default value = None)
    :param frames: number of frames in clip (Default value = None)
    :param framerate: clip fps used with `frames`
                      (Default value = 23.976)
    """
    if not seconds and not frames: raise ValueError('find_bitrate: either seconds or frames must be specified')
    if frames: seconds = frames / framerate

    number, prefix = size.split()
    number = float(number)

    size = number * 8 if prefix[0] in ascii_uppercase else number

    if 'i' in prefix:
        ter = 2 ** 40
        gig = 2 ** 30
        meg = 2 ** 20
        kil = 2 ** 10
        conv = 2 ** 10 / 1E3
    else:
        ter = 1E12
        gig = 1E9
        meg = 1E6
        kil = 1E3
        conv = 1

    if prefix[0] in ['T', 't']:
        size = size * (ter / kil) * conv
    if prefix[0] in ['G', 'g']:
        size = size * (gig / kil) * conv
    elif prefix[0] in ['M', 'm']:
        size = size * (meg / kil) * conv
    elif prefix[0] in ['K', 'k']:
        size = size * conv
    else:
        raise ValueError('find_bitrate: size unit is unexpected')

    kbps = round(size / seconds)
    print('bitrate should be {:,} kbps'.format(kbps))


def filesize(brate: int, seconds: int = None, frames: int = None,
             framerate: float = 24000 / 1001):
    """Estimates filesize based on average bitrate in kbps.

    >>> filesize(4800, seconds=60*24)  # 4,800 kbps for 24 minutes
    estimated filesize is 823.97 MiB or 864.00 MB
    >>> filesize(8710, frames=840)  # 8,710 kbps for 840 frames
    estimated filesize is 36.38 MiB or 38.14 MB
    >>> filesize(12375, frames=46500)  # 12,375 kbps for 46500 frames
    estimated filesize is 2.79 GiB or 3.00 GB

    :param brate: must be specified in kilobits per second (kbps)
    :param seconds: number of seconds in clip (Default value = None)
    :param frames: number of frames in clip (Default value = None)
    :param framerate: clip fps used with `frames`
                      (Default value = 23.976)
    """
    if not seconds and not frames: raise ValueError('find_filesize: either seconds or frames must be specified')

    if frames: seconds = frames / framerate

    size = brate * 1000 * seconds
    size /= 8

    if size > 2 ** 40:
        a = size / 2 ** 40
        binary = 'Ti'
    elif size > 2 ** 30:
        a = size / 2 ** 30
        binary = 'Gi'
    elif size > 2 ** 20:
        a = size / 2 ** 20
        binary = 'Mi'
    elif size > 2 ** 10:
        a = size / 2 ** 10
        binary = 'Ki'
    else:
        raise ValueError('find_filesize: resulting size too small')

    if size > 1E12:
        b = size / 1E12
        decimal = 'T'
    elif size > 1E9:
        b = size / 1E9
        decimal = 'G'
    elif size > 1E6:
        b = size / 1E6
        decimal = 'M'
    elif size > 1E3:
        b = size / 1E3
        decimal = 'K'
    else:
        raise ValueError('find_filesize: resulting size too small')

    print('estimated filesize is {:.2f} {bin}B or {:.2f} {dec}B'.format(a, b, bin=binary, dec=decimal))


find_bitrate = bitrate
find_filesize = filesize

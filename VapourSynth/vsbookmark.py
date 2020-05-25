"""VSEdit bookmark generator."""
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '25 May 2020'

import os
import re
from pathlib import Path
from typing import Union

import vapoursynth as vs

core = vs.core


def generate(clip: vs.VideoNode, /, script_path: Union[Path, str]):
    """
    Generates keyframe bookmark file from `clip`.

    Some of this stolen from kageru's generate_keyframes
    (https://github.com/Irrational-Encoding-Wizardry/kagefunc)

    :param clip:
        :bit depth: ANY
        :color family: ANY
        :float precision: ANY
        :sample type: ANY
        :subsampling: ANY

    :param script_path: path to active VSEdit script (can be input simply as `__file__`)
    """
    if not Path(script_path).exists():
        raise ValueError('generate: script path not found')
    if os.path.splitext(script_path)[1] != '.vpy':
        raise ValueError('generate: active script must be first saved as a `.vpy` file')
    bookmarks_path = str(script_path) + '.bookmarks'

    if Path(bookmarks_path).exists():
        print('generate: bookmark file already exists')
        return  # not super helpful as this doesn't print in the VSEdit log but prevents re-generating the bookmarks on second preview

    # speed up the analysis by resizing first
    clip = core.resize.Point(clip, 640, 360, format=clip.format.replace(bits_per_sample=8))
    clip = core.wwxd.WWXD(clip)
    kf = '0'
    for i in range(1, clip.num_frames):
        if clip.get_frame(i).props.Scenechange == 1:
            kf += f', {i}'

    text_file = open(bookmarks_path, 'w')
    text_file.write(kf)
    text_file.close()


def convert(keyframe_path: Union[Path, str], script_path: Union[Path, str]):
    """
    Converts standard keyframe file to VSEdit bookmark format.
    Accepts WWXD qp-files and (SC)XviD keyframe files.

    :param keyframe_path: `'/path/to/keyframes.txt'`
    :param script_path: path to active VSEdit script (can be input simply as `__file__`)
    """
    if os.path.splitext(script_path)[1] != '.vpy':
        raise ValueError('generate: active script must be first saved as a `.vpy` file.')
    bookmarks_path = str(script_path) + '.bookmarks'

    if (keyframe_path := Path(keyframe_path)).exists():
        lines = [line.rstrip() for line in keyframe_path.open()]
        lines = list(filter(None, lines))

        if 'WWXD' in lines[0]:
            kf = '0'
            for i in range(2, len(lines)):
                match = re.search(r'\d+', lines[i])
                if match:
                    kf += (', ' + match[0])
        elif 'XviD' in lines[0]:
            count = 0
            kf = ''
            for i in range(len(lines)):
                if lines[i][0] == 'i':
                    kf += (str(count) + ', ')
                    count += 1
                elif lines[i][0] == 'p' or lines[i][0] == 'b':
                    count += 1
            kf = kf[:-2]

        else:
            raise IOError('convert: keyframe file format could not be read')
    else:
        raise ValueError('convert: keyframe_path needs to be specified')

    text_file = open(bookmarks_path, 'w')
    text_file.write(kf)
    text_file.close()

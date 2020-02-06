"""VSEdit bookmark generator."""
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '6 February 2020'

import re

import vapoursynth as vs

core = vs.core


def generate(clip: vs.VideoNode, script_name: str = None):
    """
    Generates keyframe bookmark file from clip.

    Some of this stolen from kageru's generate_keyframes
    (https://github.com/Irrational-Encoding-Wizardry/kagefunc)

    :param clip:
        :bit depth: ANY
        :color family: ANY
        :float precision: ANY
        :sample type: ANY
        :subsampling: ANY

    :param script_name: name of VSEdit script with no extension
    """
    if script_name is not None:
        script_name += '.vpy.bookmarks'
    else:
        raise ValueError('generate: script_name needs to be specified')

    # speed up the analysis by resizing first
    clip = core.resize.Bilinear(clip, 640, 360)
    clip = core.wwxd.WWXD(clip)
    kf = '0'
    for i in range(1, clip.num_frames):
        if clip.get_frame(i).props.Scenechange == 1:
            kf += ", %d" % i

    text_file = open(script_name, "w")
    text_file.write(kf)
    text_file.close()


def convert(file_path: str = None, script_name: str = None):
    """
    Converts standard keyframe file to VSEdit bookmark format.
    Accepts WWXD qp-files and (SC)XviD keyframe files.

    :param file_path: `'/path/to/keyframes.txt'`
    :param script_name: name of VSEdit script with no extension
    """
    if script_name is not None:
        script_name += '.vpy.bookmarks'
    else:
        raise ValueError('convert: script_name needs to be specified')

    if file_path is not None:
        lines = [line.rstrip('\n') for line in open(file_path, 'r')]
        lines = list(filter(None, lines))

        if 'WWXD' in lines[0]:
            kf = '0'
            for i in range(2, len(lines)):
                match = re.search(r'\d+', lines[i])
                match = match[0] if match else ''
                if match is not '':
                    kf += (', ' + match)
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
        raise ValueError('convert: file_path needs to be specified')

    text_file = open(script_name, 'w')
    text_file.write(kf)
    text_file.close()

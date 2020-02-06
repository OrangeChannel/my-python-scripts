"""Creates easy frame comparisons between multiple VapourSynth clips."""
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '6 February 2020'

import os
from contextlib import contextmanager
from functools import partial
from math import floor, sqrt
from random import randint, sample
from typing import List, Union

import vapoursynth as vs
from vsutil import get_depth, get_subsampling  # https://github.com/Irrational-Encoding-Wizardry/vsutil

core = vs.core  # requires fmtc:  https://github.com/EleonoreMizo/fmtconv


def prep(*clips: vs.VideoNode, w: int = 1280, h: int = 720, dith: bool = True, yuv444: bool = True, static: bool = True) \
        -> Union[vs.VideoNode, List[vs.VideoNode]]:
    """Prepares multiple clips of diff sizes/bit-depths to be compared.

    Can optionally be used as a simplified resize/ftmc wrapper for one
    clip. Clips MUST be either YUV420 or YUV444.

    Transforms all planes to w x h using Bicubic:
        Hermite 0,0 for downscale / Mitchell 1/3,1/3 for upscale.

    :param clips: clip(s) to process
        :bit depth: ANY
        :color family: YUV
        :float precision: ANY
        :sample type: ANY
        :subsampling: 420, 444

    :param w: target width in px

    :param h: target height in px

    :param dith: whether or not to dither clips down to 8-bit (Default value = True)

    :param yuv444: whether or not to convert all clips to 444 chroma subsampling (Default value = True)

    :param static: changes dither mode based on clip usage (Default value = True)
        True will use Floyd-Steinberg error diffusion (good for static screenshots)
        False will use Sierra's Filter Lite error diffusion (faster)

    :returns: processed clip(s)
    """
    outclips = []
    for clip in clips:
        if get_subsampling(clip) == '444':
            if clip.height > h: clip_scaled = core.resize.Bicubic(clip, w, h, filter_param_a=0, filter_param_b=0)
            elif clip.height < h: clip_scaled = core.resize.Bicubic(clip, w, h, filter_param_a=0.33, filter_param_b=0.33)
            else: clip_scaled = clip

        elif get_subsampling(clip) == '420' and yuv444:
            if clip.height > h:
                if clip.height >= (2 * h):
                    # this downscales chroma with Hermite instead of Mitchell
                    clip_scaled = core.resize.Bicubic(clip, w, h, filter_param_a=0, filter_param_b=0, filter_param_a_uv=0,
                                                      filter_param_b_uv=0, format=clip.format.replace(subsampling_w=0, subsampling_h=0))
                else:
                    clip_scaled = core.resize.Bicubic(clip, w, h, filter_param_a=0, filter_param_b=0, filter_param_a_uv=0.33,
                                                      filter_param_b_uv=0.33, format=clip.format.replace(subsampling_w=0, subsampling_h=0))
            elif clip.height < h:
                clip_scaled = core.resize.Bicubic(clip, w, h, filter_param_a=0.33, filter_param_b=0.33,
                                                  format=clip.format.replace(subsampling_w=0, subsampling_h=0))
            else:
                clip_scaled = core.resize.Bicubic(clip, filter_param_a=0.33, filter_param_b=0.33,
                                                  format=clip.format.replace(subsampling_w=0, subsampling_h=0))

        else:
            if clip.height > h:
                clip_scaled = core.resize.Bicubic(clip, w, h, filter_param_a=0, filter_param_b=0)
            elif clip.height < h:
                clip_scaled = core.resize.Bicubic(clip, w, h, filter_param_a=0.33, filter_param_b=0.33)
            else:
                clip_scaled = clip

        if get_depth(clip_scaled) > 8:
            if dith:
                if static:
                    # Floyd-Steinberg error diffusion
                    clip_dith = core.fmtc.bitdepth(clip_scaled, bits=8, dmode=6)
                else:
                    # Sierra-2-4A "Filter Lite" error diffusion
                    clip_dith = core.fmtc.bitdepth(clip_scaled, bits=8, dmode=3)
            else:
                # No dither, round to the closest value
                clip_dith = core.fmtc.bitdepth(clip_scaled, bits=8, dmode=1)
        else:
            clip_dith = clip_scaled

        outclips.append(clip_dith)

    if len(outclips) == 1:
        return clip_dith

    return outclips


def save(*frames: int, rand: int = 0, folder: bool = False, zoom: int = 1, **clips: vs.VideoNode):
    """
    Writes frames as named PNG files for easy upload to slowpics.org.

    Running "save(17, 24, rand=2, folder=True, zoom=3, BD=bd, TV=tv)"
    will save four 3x-point-upscaled frames (17, 24, and 2 randoms) in folders named 'BD' and 'TV'.

    :param frames: frame number(s) to save

    :param rand: number of random frames to extract (Default value = 0)

    :param folder: saves images into named sub-folders (Default value = False)
        If True, saving will not prefix image files with clip name.

    :param zoom: zoom factor (Default value = 1)

    :param clips: comma separated pairs of name=clip to save frames from
        :bit depth: ANY
        :color family: ANY
        :float precision: ANY
        :sample type: ANY
        :subsampling: ANY
    """
    frames = list(frames)
    if len(frames) == 0 and rand < 1: rand = 1

    if rand > 0:
        max_frame = min(clip.num_frames for name, clip in clips.items()) - 1
        if rand == 1: frames.append(randint(0, max_frame))
        else: frames = frames + sample(range(max_frame), rand)

    if folder:
        for name, clip in clips.items():
            os.makedirs(str(name), exist_ok=True)
            with _cd(str(name)):
                for f in frames:
                    out = core.imwri.Write(clip[f].resize.Point(width=(zoom * clip.width), height=(zoom * clip.height),
                                                                format=vs.RGB24, matrix_in_s='709', range=0, range_in=0),
                                           'PNG', '%05d.png', firstnum=f)
                    out.get_frame(0)
    else:
        for name, clip in clips.items():
            for f in frames:
                out = core.imwri.Write(clip[f].resize.Point(width=(zoom * clip.width), height=(zoom * clip.height),
                                                            format=vs.RGB24, matrix_in_s='709', range=0, range_in=0),
                                       'PNG', f"{name}%05d.png", firstnum=f)
                out.get_frame(0)


def comp(*frames: int, rand: int = 0, slicing: bool = False, slices: List[str] = None, full: bool = False, label: bool = True,
         label_size: int = 30, label_alignment: int = 7, stack_type: str = 'clip', **in_clips: vs.VideoNode) -> vs.VideoNode:
    """
    All-encompassing comparison tool for VapourSynth preview.

    Allows an infinite number of clips to be compared.
    Can compare entire clips, frames, or slices.
    Visually arranges clips in five ways:
        continuous clip (A0 B0 A1 B1)
        vertical stacking
        horizontal stacking
        mosaic
        split (A | B [| C])

    :param frames: frame number(s) to be compared
        Can be left blank.

    :param rand: number of random frames to compare from all clips (Default value = 0)
        Can be left blank.

    :param slicing: changes output to slicing mode (Default value = False)
        Overrides 'frames' and 'rand'.

    :param slices: Python slices of all clips to be compared (Default value = None)
        Does not accept advanced / combined slicing.
        Example: '[":16","200:400","570:"]' for frames 0-15,200-399,570+
        Can be left blank is slicing is False.

    :param full: whether or not to compare full length of clips (Default value = False)
        Overrides 'frames', 'rand', and 'slicing'/'slices'

    :param label: labels clips with their name (Default value = True)

    :param label_size: <int> fontsize for 'label' (Default value = 30)

    :param label_alignment: numpad alignment of 'label' (Default value = 7)

    :param stack_type: type of comparison to output (Default value = 'clip')
        Accepts 'clip', 'vertical', 'horizontal', 'mosaic', 'split'.
        'split' allows only 2 or 3 clips and overrides 'label_alignment'

    :param in_clips: comma separated pairs of name=clip
        :bit depth: ANY
        :color family: ANY
        :float precision: ANY
        :sample type: ANY
        :subsampling: ANY

    :returns: processed clip
    """

    def _markclips(clips, names, label_size, label_alignment) -> List[vs.VideoNode]:
        style = f'sans-serif,{label_size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,1,' \
                f'{label_alignment},10,10,10,1'
        margins = [10, 0, 10, 0]
        markedclips = []

        if type(clips) == vs.VideoNode:
            return core.sub.Subtitle(clips, str(names), style=style, margins=margins)
        else:
            for name, clip in zip(names, clips):
                markedclip = core.sub.Subtitle(clip, str(name), style=style, margins=margins)
                markedclips.append(markedclip)

        return markedclips

    def _cutclips(clips, frames, rand) -> List[vs.VideoNode]:
        if slicing:
            cut_clips = []
            for i, clip in enumerate(clips):
                cut_clips.append(core.std.BlankClip(clip, length=1))
                for s in slices:
                    a, b = s.split(':')
                    if a == '': cut_clips[i] += clip[:int(b)]
                    elif b == '': cut_clips[i] += clip[int(a):]
                    else: cut_clips[i] += clip[int(a):int(b)]

        else:
            if len(frames) == 0 and rand < 1: rand = 1
            if rand > 0:
                max_frame = min(clip.num_frames for clip in clips) - 1
                if rand == 1: frames.append(randint(0, max_frame))
                else: frames = frames + sample(range(max_frame), rand)

            cut_clips = []
            for i, clip in enumerate(clips):
                cut_clips.append(core.std.BlankClip(clip, length=1))
                for f in frames: cut_clips[i] += clip[f]

        for i in range(len(cut_clips)): cut_clips[i] = cut_clips[i][1:]

        return cut_clips

    def _assemble(markedclips: List[vs.VideoNode], stack_type: str) -> vs.VideoNode:

        def _stack2d(clips, size):
            rows = []
            for i in range(0, size):
                min_s = (i * size)
                max_s = ((i + 1) * size)
                if i == 0:
                    row_clips = clips[:max_s]
                    rows.append(core.std.StackHorizontal(row_clips))
                else:
                    row_clips = clips[min_s:max_s]
                    rows.append(core.std.StackHorizontal(row_clips))

            return core.std.StackVertical(rows)

        def _root_check(clips):

            def _blank_create(clips, size):
                blank_clips = []
                blank_number = (size ** 2) - len(clips)
                for _ in range(0, blank_number): blank_clips.append(core.std.BlankClip(clips[0], length=1))
                added_clips = clips + blank_clips

                return _stack2d(added_clips, size)

            root = sqrt(len(clips))
            size = floor(root) + 1

            if int(root + 0.5) ** 2 != len(clips):
                return _blank_create(clips, size)
            else:
                return _stack2d(clips, int(root))

        def _split(clips):
            width = clips[0].width
            if len(clips) == 2:
                clip_left = _markclips(clips[0], names[0], label_size, 7)
                clip_right = _markclips(clips[1], names[1], label_size, 9)

                clip_left = core.std.Crop(clip_left, 0, width / 2, 0, 0)
                clip_right = core.std.Crop(clip_right, width / 2, 0, 0, 0)

                clips_list = clip_left, clip_right

                return core.std.StackHorizontal(clips_list)

            if len(clips) == 3:
                width = floor(width / 3)
                dwidth = 2 * width

                clip_left = _markclips(clips[0], names[0], label_size, 7)
                clip_middle = _markclips(clips[1], names[1], label_size, 8)
                clip_right = _markclips(clips[2], names[2], label_size, 9)

                clip_left = core.std.Crop(clip_left, 0, dwidth, 0, 0)
                clip_middle = core.std.Crop(clip_middle, width, width, 0, 0)
                clip_right = core.std.Crop(clip_right, dwidth, 0, 0, 0)

                clips_list = clip_left, clip_middle, clip_right

                return core.std.StackHorizontal(clips_list)

        if stack_type == 'vertical':
            return core.std.StackVertical(markedclips)
        elif stack_type == 'horizontal' or (stack_type == 'mosaic' and len(markedclips) < 3):
            return core.std.StackHorizontal(markedclips)
        elif stack_type == 'mosaic':
            return _root_check(markedclips)
        elif stack_type == 'split' and (len(clips) < 2 or len(clips) > 3):
            raise ValueError('comp: \'split\' stack_type only allows 2 or 3 clips')
        elif stack_type == 'split':
            return _split(clips)
        else:
            return core.std.Interleave(markedclips)

    names = list(in_clips.keys())
    clips = list(in_clips.values())

    for i in range(1, len(clips)):
        if clips[i - 1].width != clips[i].width:
            raise ValueError("comp: the width of all clips must be the same")
        if clips[i - 1].height != clips[i].height:
            raise ValueError("comp: the height of all clips must be the same")
        if clips[i - 1].format != clips[i].format:
            raise ValueError("comp: the format of all clips must be the same")

    if not full:
        frames = list(frames)
        clips = _cutclips(clips, frames, rand)

    if label: markedclips = _markclips(clips, names, label_size, label_alignment)
    else: markedclips = clips

    return _assemble(markedclips, stack_type)


# Vertical comparison alias
vcomp = partial(comp, stack_type='vertical')

# Horizontal comparison alias
hcomp = partial(comp, stack_type='horizontal')

# Full clip comparison alias
ccomp = partial(comp, full=True, stack_type='clip')

# Mosaic comparison alias
mcomp = partial(comp, stack_type='mosaic')

# Split comparison alias
scomp = partial(comp, stack_type='split')


@contextmanager
def _cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try: yield
    finally: os.chdir(prevdir)

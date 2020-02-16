## vscompare.py - saving screenshots from VapourSynth

`prep(*clips, w, h, dith, yuv444, static)` and
`save(*frames, rand, folder, zoom, **clips)`
can be used to make comparisons on [slowpics][]
or for uploading to the [guide.encode.moe][guide] guide.

Example: uploading screenshots from a YUV420 source to the guide.

```py
import vapoursynth as vs
import vscompare
core = vs.core

clip1 = core.ffms2.Source(r'clip1.mkv')
clip2 = core.ffms2.Source(r'clip2.mkv')

... # in the filterchain, clip1 and clip2 become 16-bit

# converts to 8-bit YUV444 with Floyd-Steinberg error diffusion
clip1, clip2 = vscompare.prep(clip1, clip2, w=1920, h=1080, dith=True, yuv444=True, static=True)

# saves frames 107, 814, and 2 randoms named properly as RGB24 PNG files (uncompressed) for easy drag-n-drop to slowpics.
vscompare.save(107, 814, rand=2, folder=False, bluray=clip1, tv=clip2)
```

[slowpics]: https://slow.pics/
[guide]: https://guide.encode.moe/

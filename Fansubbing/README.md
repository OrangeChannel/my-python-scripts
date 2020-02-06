# `fansub_utils.py`: batch-processing functions

**This is designed to be ran inside of a (release) folder containing `.mkv` files.**

```sh
# Prints possible options:
python fansub_utils.py -h

# Runs the renaming function
python fansub_utils.py --renamer
```

# Current Functions:

## hasher (`-H`)
Appends a CRC32 hash to the filenames in the folder.

Before: `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p).mkv`

After: `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p) [ABCD1234].mkv`

## checker (`-C`)
Verifies CRC32 hases in filenames.

## remover (`-X`)
Removes CRC32 hashes from the end of filenames (can handle whitespace before the hash).

Before:  `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p) [ABCD1234].mkv`

After:  `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p).mkv`

## renamer (`-R`)
Batch renames files `ep01.mkv`, `ep02.mkv`, ...`ep13.mkv` to `[Group] Title - ## (SRC RESp).mkv`
- i.e. `ep05.mkv` --> `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p).mkv`

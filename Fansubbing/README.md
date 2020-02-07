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

## checker (`-K`)
Verifies CRC32 hases in filenames.

## remover (`-X`)
Removes CRC32 hashes from the end of filenames (can handle whitespace before the hash).

Before:  `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p) [ABCD1234].mkv`

After:  `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p).mkv`

## renamer (`-R`)
Batch renames files `ep01.mkv`, `ep02.mkv`, ...`ep13.mkv` to `[Group] Title - ## (SRC RESp).mkv`
- i.e. `ep05.mkv` --> `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p).mkv`

## cleaner (`-C`)
Reformats arbitrary filenames to `[Group] Title - ## (SRC RESp).mkv` based only on episode number found in original
 title.
 
##### Before

- `re:zero 06.mkv`
- `[Trash] rezero episode 12[ABCD1234].mkv`
- `[Trash] Re:Zero 5.mkv`
- `[Garbage *$ ReZERO 1.mkv`

#### After

- `[ChannelOrange] Re:Zero Season 3 - 01 (WEB 720p).mkv`
- `[ChannelOrange] Re:Zero Season 3 - 05 (WEB 720p).mkv`
- `[ChannelOrange] Re:Zero Season 3 - 06 (WEB 720p).mkv`
- `[ChannelOrange] Re:Zero Season 3 - 12 (WEB 720p).mkv`

*Note: only will find episode numbers with a space before them (`_##` or `_#`).*

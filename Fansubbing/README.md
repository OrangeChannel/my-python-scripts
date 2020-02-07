# `fansub_utils.py`: batch-processing functions

**This is designed to be ran inside of a (release) folder containing `.mkv` files.**

```sh
# Prints possible options:
python fansub_utils.py -h

# Runs the renaming function
python fansub_utils.py --renamer
```

# Current Functions:

## hasher `-H`
Appends a CRC32 hash to the filenames in the folder.

Before: `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p).mkv`

After: `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p) [ABCD1234].mkv`

## checker `-K`
Verifies CRC32 hases in filenames.

## remover `-X`
Removes CRC32 hashes from the end of filenames (can handle whitespace before the hash).

Before:  `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p) [ABCD1234].mkv`

After:  `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p).mkv`

## renamer `-R`
Batch renames files `ep01.mkv`, `ep02.mkv`, ...`ep13.mkv` to `[Group] Title - ## (SRC RESp).mkv`
- i.e. `ep05.mkv` --> `[ChannelOrange] Watashi ni ga Maiorita! - 05 (BD 720p).mkv`

## cleaner `-C`
Reformats arbitrary filenames to `[Group] Title - ## (SRC RESp).mkv` based only on episode number found in original
 title.
 
##### Before

- `re:zero 06v3.mkv`
- `[Trash] rezero s2 episode 12[ABCD1234].mkv`
- `[Trash] Re:Zero2_5.mkv`
- `[Garbage *$ s1 ReZERO 1.mkv`

#### After

- `[ChannelOrange] Re:Zero - 01 (WEB 720p).mkv`
- `[ChannelOrange] Re:Zero - 05 (WEB 720p).mkv`
- `[ChannelOrange] Re:Zero - 06 (WEB 720p).mkv`
- `[ChannelOrange] Re:Zero - 12 (WEB 720p).mkv`

*Note: only will find episode numbers with a space (or underscore) before them (`_##` or `_#`).*

*WARNING: files like `[ChannelOrange] Re:Zero Season 3 - 12 (WEB 720p).mkv` containing a season number will all be
 overwritten with the same name into one file. This is **NOT** reversible so make sure the episodes all have a
  __single unique__ one-two digit number in them.*

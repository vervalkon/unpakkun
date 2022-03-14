# unpakkun.py
A file decompressor/dumper for Sutte Hakkun (all versions)

## a few things to know
* You _must_ edit the `outputpath` and `rompath` variables on rows `6` and  `7` before running the script
* Will refuse to work if you recalculated the ROM checksum yourself after hacking
* Never tested on a non-macOS environment
* Not tested for all edge cases so who knows what kind of problems there might be

## faq
1. why are there two versions of `BS Sutte Hakkun 2`? Isn't the other one just a bad dump?
   * no, the other version they broadcast was actually a legitimate bugfix. There are level changes and the huffman tree and TOC are different.
~~2. why can't you run it straight from the command line with arguments and options and all that jazz?~~
   * ~~i don't know how to program that~~
3. how to recompress?
   * see above

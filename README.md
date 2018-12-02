# `manhuagui`

A cmdline comic downloader for [manhuagui.com](https://tw.manhuagui.com/).
(Modifed from chazeon/manhuagui.py)

## Features
- Multiple connections (multi-volumes at the same time)
- Auto archive (as .zip) each volume(chapter)
- Auto detect completed volume
- Auto sort volume list
- Progress report

## Usage
    python3 ./src/main.py <comic number> [chapter# started from]

## Example
to download https://tw.manhuagui.com/comic/19430/

    python3 ./src/main.py 19430    # fetch entirely
    python3 ./src/main.py 19430 20 # start from chapter 21


# TODO
- save history for comics already downloaded.
- auto update all comics that have new volumes.

# Known issue
- some volume may hit download failure on final pages

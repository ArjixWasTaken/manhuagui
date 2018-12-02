# `manhuagui`

A comic downloader for [manhuagui.com](https://tw.manhuagui.com/).
(Modifed from chazeon/manhuagui.py)

## usage:
    python3 ./src/main.py <comic number> [chapter# started from]

## example:
to download https://tw.manhuagui.com/comic/19430/

    python3 ./src/main.py 19430    # fetch entirely
    python3 ./src/main.py 19430 20 # start from chapter 21


# TODO
- save history for comics already downloaded.
- auto update all comics that have new volumes.

# Known issue
- some volume may hit download failure on final pages

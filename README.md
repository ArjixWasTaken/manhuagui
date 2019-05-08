# `manhuagui`

A cmdline comic downloader for [manhuagui.com](https://tw.manhuagui.com/).
(Forked from chazeon/manhuagui.py)

## Features
- Multiple connections (multi-pages at the same time)
- Auto archive (as .zip) each volume(chapter)
- Auto detect completed volume
- Auto sort volume list
- Progress report
- Auto save download progress of each comic
- Auto download all comics saved locally

## Usage
````
python3 ./src/main.py -h
````

## Example
1. download https://tw.manhuagui.com/comic/19430/
````
python3 ./src/main.py -i 19430        # fetch all chapter/albums
python3 ./src/main.py -i 19430 -c 20  # start from chapter 21
````

1. check and download new comics recorded from local config
````
python3 ./src/main.py -a
````

# Known issue


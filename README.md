# `manhuagui`

A cmdline comic downloader for [manhuagui.com](https://tw.manhuagui.com/).
(Forked from chazeon/manhuagui.py)

## Features

- Multiple connections (multi-pages at the same time)
- Auto archive (as .zip) each volume(chapter)
- Auto detect completed volume
- Auto sort volume list
- Progress report
- Auto save download progress(chapters) of each comic
- Auto update all comics saved locally
- Auto fetch available proxies
- Auto remove dead proxy

## Installation

- If you do not already have Node.js, install it and add to path, such as

```bash
sudo apt-get install nodejs
```

- Change any setting you desire by creating `config.json` file. For example, set your own destination for storing comics. (See config.example)

> Be careful when change settings like 'backoff_factor', 'sleep', 'connections'. You might be probably got banned by website if too aggressive.

## Usage

- Run with

```bash
python3 ./src/main.py -h
```

## Basic example

- would like to download comics in <https://tw.manhuagui.com/comic/19430/>

```bash
python3 ./src/main.py -i 19430        # fetch all chapter/albums
python3 ./src/main.py -i 19430 -c 20  # start from chapter 21
```

- check and download new comics recorded in local config file

```bash
python3 ./src/main.py -a
```

- fetch available proxies and save to config file

```bash
python3 ./src/main.py -u
```

## Known issue

- Exception occurs during another exception. This might be triggered when multiple downloads through proxy are failed. [Not affect the download process]

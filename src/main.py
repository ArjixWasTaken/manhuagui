#!/usr/bin/env python3
import json
from client import MHGClient
from mhg import MHGComic, MHGVolume
import multiprocessing.pool


def retrieve(target):
    target.retrieve()

if __name__ == '__main__':
    with open('config.json', encoding='utf8') as f:
        opts = json.load(f)
    # comic_uri = input('Please input comic album url: ')
    comic = MHGComic('https://tw.manhuagui.com/comic/4070/', opts=opts)
    pool = multiprocessing.pool.Pool(opts.connections)
    pool.map(retrieve, comic.volumes)

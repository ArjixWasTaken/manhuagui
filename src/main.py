#!/usr/bin/env python3
import json
import sys
from client import MHGClient
from mhg import MHGComic, MHGVolume
import multiprocessing.pool



def retrieve(target):
    target.retrieve()

if __name__ == '__main__':
    comic_start_from = 1
    with open('config.json', encoding='utf8') as f:
        opts = json.load(f)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        comic_id = sys.argv[1]
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            comic_start_from = sys.argv[2]
    else:
        comic_id = input('Please input comic ID of manhuagui.com: ')
    try:
        comic = MHGComic(comic_id, start_from=comic_start_from, opts=opts)
        pool = multiprocessing.pool.Pool(opts['connections'])
        pool.map(retrieve, comic.volumes, chunksize=1)
    except KeyboardInterrupt:
        sys.exit()

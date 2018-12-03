#!/usr/bin/env python3
import json
import sys
from mhg import MHGComic
import multiprocessing.pool
import signal
import os


def retrieve(target):
    target.retrieve()


def fetch_comic(comic_id, comic_start_from=1):
    try:
        comic = MHGComic(comic_id, start_from=comic_start_from, opts=opts)
        original_sigint_handler = signal.signal(
            signal.SIGINT, signal.SIG_IGN)  # ignore SIGINT in child process
        pool = multiprocessing.pool.Pool(opts['connections'])
        signal.signal(signal.SIGINT, original_sigint_handler)
        r = pool.map_async(retrieve, comic.volumes, chunksize=1)
        r.wait()
    except KeyboardInterrupt:
        pool.terminate()


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

    if comic_id:
        fetch_comic(comic_id, comic_start_from)
    elif os.path.exists(opts['record_conf']):
        with open(opts['record_conf']) as f:
            records = json.load(f)
            comic_ids = records.keys()
        print(comic_ids)
        for id in comic_ids:
            fetch_comic(id)

#!/usr/bin/env python3
import json
import sys
from mhg import MHGComic
import multiprocessing.pool
import signal
import os
from argparse import ArgumentParser
# from pprint import pprint


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
        print("[Up to date]")
    except KeyboardInterrupt:
        pool.terminate()


if __name__ == '__main__':
    with open('config.json', encoding='utf8') as f:
        opts = json.load(f)

    parser = ArgumentParser(prog=sys.argv[0])
    parser.add_argument("-i", "--id", type=int, help="Comic ID of manguagui.com")
    parser.add_argument("-c", "--chapter", type=int, help="Which chapter# to start with")
    parser.add_argument("-a", "--auto", action="store_true", help="Resume/recheck ALL downloads by the records of history file")
    args = parser.parse_args()

    if args.auto:
        if os.path.exists(opts['record_conf']):
            with open(opts['record_conf']) as f:
                records = json.load(f)
                comic_ids = records.keys()
            for id in comic_ids:
                fetch_comic(id, records[id]["number"])
        else:
            print("No history records found.({})".format(opts['record_conf']))
    elif args.id is not None:
        if args.chapter is not None:
            fetch_comic(args.id, args.chapter)
        else:
            fetch_comic(args.id)
    else:
        parser.print_help()

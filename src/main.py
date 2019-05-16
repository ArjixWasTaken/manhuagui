#!/usr/bin/env python3
import json
import sys
from mhg import MHGComic
import os
from argparse import ArgumentParser
# from pprint import pprint

from proxy import MGHProxy

global VERBOSE
VERBOSE = False
__version__ = '3.1.1'


def vprint(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


def fetch_comic(opts, comic_id, comic_start_from=1):
    try:
        comic = MHGComic(opts, comic_id, start_from=comic_start_from)
        comic.retrieve()
        vprint("[Up to date]")
    except KeyboardInterrupt:
        print("Caught Ctrl-C interrupt. Stop process.")
        sys.exit()


if __name__ == '__main__':
    with open('config.json', encoding='utf8') as f:
        opts = json.load(f)

    parser = ArgumentParser(prog=sys.argv[0])
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ver:' + __version__)
    parser.add_argument("-i", "--id", type=int, nargs="+",
                        help="Comic ID of manguagui.com")
    parser.add_argument("-c", "--chapter", type=int,
                        help="Which chapter# to start with")
    parser.add_argument("-a", "--auto", action="store_true",
                        help="Resume/recheck ALL downloads by the records of history file")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="verbose output")
    args = parser.parse_args()

    if args.debug:
        VERBOSE = True
        opts['debug'] = True

    # init proxy
    MGHProxy(opts)

    if args.auto:
        if os.path.exists(opts['record_conf']):
            with open(opts['record_conf']) as f:
                records = json.load(f)
                comic_ids = records.keys()
            for id in comic_ids:
                fetch_comic(opts, id, records[id]["number"])
        else:
            print("No history records found.({})".format(opts['record_conf']))
    elif args.id is not None:
        if isinstance(args.id, list):
            ids = args.id
        else:
            ids = [args.id]
        for id in ids:
            if args.chapter is not None:    # do check from the last chapter we downloaded
                fetch_comic(opts, id, args.chapter)
            else:
                fetch_comic(opts, id)
    else:
        parser.print_help()
    print()

import random
import time
import sys

import bs4
import requests

from proxy import MGHProxy
from retry import requests_retry_session
from retry2 import retry2

# import logging


class MHGClient():
    def __init__(self, opts):
        self.opts = opts
        self.session = requests.Session()
        if 'backoff_factor' in opts.keys():
            self.session = requests_retry_session(
                retries=opts['retry'],
                session=self.session,
                backoff_factor=opts['backoff_factor'])
        self.session.headers.update({
            'User-Agent': opts['user_agent']
        })
        if 'retry_page' in opts.keys():
            self.retry_page = opts['retry_page']
        else:
            self.retry_page = 0

        self.chunk_size = opts['chunk_size'] if opts['chunk_size'] else 512
        # logging.basicConfig()
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

    def get(self, uri: str, use_proxy=True, **kwargs):
        res = self._get(uri, use_proxy=use_proxy, **kwargs)
        if 'sleep' in self.opts.keys():
            self.sleep()
        return res

    def get_soup(self, uri: str, use_proxy=True, ** kwargs):
        res = self.get(uri, use_proxy=use_proxy, ** kwargs)
        return bs4.BeautifulSoup(res.text, 'html.parser')

    def retrieve(self, uri: str, dst: str, **kwargs):
        res = self._get(uri, stream=True, **kwargs)
        with open(dst, 'wb') as f:
            for chunk in res.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    f.write(chunk)
        if 'sleep' in self.opts.keys():
            self.sleep()

    def _get(self, uri: str, use_proxy=True, stream=False, **kwargs):
        retry = self.retry_page
        while(retry >= 0):
            try:
                proxy = MGHProxy().get() if use_proxy else None
                res = retry2(
                    lambda: self.session.get(
                        uri, proxies=proxy, timeout=self.opts['timeout'], stream=stream, **kwargs),
                    max_retry=self.opts['retry'],
                    backoff_factor=self.opts['backoff_factor']
                )
                break
            except Exception as err:
                MGHProxy().remove(proxy)
                if retry > 0:
                    retry -= 1
                else:
                    print("\n> Failed to fetch [", uri, "].", "\r",
                          file=sys.stderr, flush=True)
                    raise err from None
        return res

    def sleep(self):
        time.sleep(random.randrange(*self.opts['sleep']) / 1000)

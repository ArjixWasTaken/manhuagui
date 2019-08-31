import random
import time
import bs4
import requests

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

        self.chunk_size = opts['chunk_size'] if opts['chunk_size'] else 512
        # logging.basicConfig()
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

    def get(self, uri: str, proxy=None, **kwargs):
        try:
            res = retry2(
                lambda: self.session.get(uri, proxies=proxy, **kwargs)
            )
            if 'sleep' in self.opts.keys():
                self.sleep()
        except Exception as err:
            print(err, ", proxy=", proxy)
            raise err

        return res

    def get_soup(self, uri: str, proxy=None, **kwargs):
        res = self.get(uri, proxy, **kwargs)
        return bs4.BeautifulSoup(res.text, 'html.parser')

    def retrieve(self, uri: str, dst: str, proxy: dict, **kwargs):
        res = retry2(
            lambda: self.session.get(
                uri, stream=True, proxies=proxy, timeout=self.opts['timeout'], **kwargs),
            max_retry=self.opts['retry'],
            backoff_factor=self.opts['backoff_factor']
        )
        with open(dst, 'wb') as f:
            for chunk in res.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    f.write(chunk)
        if 'sleep' in self.opts.keys():
            self.sleep()

    def sleep(self):
        time.sleep(random.randrange(*self.opts['sleep']) / 1000)

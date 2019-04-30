import random
import time
import bs4
import requests

from retry import requests_retry_session
from retry2 import retry2

# import logging


class MHGClient:
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
        if 'proxy' in opts.keys():
            self.retry_proxy = opts['retry-proxy']
        else:
            self.retry_proxy = 0

        self.chunk_size = opts['chunk_size'] if opts['chunk_size'] else 512
        # logging.basicConfig()
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

    @property
    def proxy(self):
        if 'proxy' in self.opts.keys():
            if type(self.opts['proxy']) is list:
                rp = random.choice(self.opts['proxy'])
            else:
                rp = self.opts['proxy']
            # print(">> proxy:", rp)
            return {
                'https': rp
            }
        else:
            return None

    def get(self, uri: str, **kwargs):
        try:
            pp = self.proxy
            res = retry2(
                lambda: self.session.get(uri, proxies=None, **kwargs)
            )
            if 'sleep' in self.opts.keys():
                self.sleep()
        except Exception as err:
            print(err, ", proxy=", pp)
            raise err

        return res

    def get_soup(self, uri: str, **kwargs):
        res = self.get(uri, **kwargs)
        return bs4.BeautifulSoup(res.text, 'html.parser')

    def retrieve(self, uri: str, dst: str, **kwargs):
        try:
            pp = self.proxy
            res = retry2(
                lambda: self.session.get(
                    uri, stream=True, proxies=pp, timeout=30, **kwargs),
                max_retry=self.opts['retry'],
                backoff_factor=self.opts['backoff_factor']
            )
            with open(dst, 'wb') as f:
                for chunk in res.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
            if 'sleep' in self.opts.keys():
                self.sleep()
        except Exception as err:
            print(err, "\tproxy=", pp)
            if self.retry_proxy > 0:
                self.retry_proxy -= 1
                print("> Use another proxy to retry again ...", uri, "retry=", self.retry_proxy)
                self.retrieve(uri, dst, **kwargs)
            else:
                raise err

    def sleep(self):
        time.sleep(random.randrange(*self.opts['sleep']) / 1000)

import functools
import json
import threading
from io import open
from itertools import cycle
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

lock = threading.Lock()


def synchronized(lock):
    """ Synchronization decorator """
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock:
                return f(*args, **kw)
        return inner_wrapper
    return wrapper


class Singleton(type):
    _instances = {}

    @synchronized(lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MGHProxy(metaclass=Singleton):
    def __init__(self, opts):
        self.max_proxy = opts['max_proxy']
        if len(opts['proxy']) > 0:
            self.proxy_set = set(opts['proxy'])
            self.proxy_cycle = cycle(opts['proxy'])
        else:
            self.proxy_set = None
            self.proxy_cycle = None

    @synchronized(lock)
    def get(self):
        if self.proxy_cycle is None:
            return None
        return {
            'https': 'https://' + next(self.proxy_cycle)
        }

    @synchronized(lock)
    def remove(self, e):
        try:
            self.proxy_set.remove(e['https'][8:])  # remove 'https://'
            if len(self.proxy_set) == 0:
                self.update_all()
            else:
                self.proxy_cycle = cycle(self.proxy_set)
                self.save_to_file()
        except (ValueError, KeyError):
            pass

    def update_all(self):
        ua = UserAgent()  # From here we generate a random user agent
        pp = set()  # Will contain proxies [ip, port]

        if self.proxy_set is None:
            self.proxy_set = set()
        # Retrieve latest proxies
        proxies_req = Request('https://www.sslproxies.org/')
        proxies_req.add_header('User-Agent', ua.random)
        proxies_doc = urlopen(proxies_req).read().decode('utf8')
        soup = BeautifulSoup(proxies_doc, 'html.parser')
        proxies_table = soup.find(id='proxylisttable')

        # Save proxies in the array
        for row in proxies_table.tbody.find_all('tr'):
            # sample:
            # [<td>179.125.178.154</td>,
            #  <td>8080</td>,
            #  <td>BR</td>,
            #  <td class="hm">Brazil</td>,
            #  <td>elite proxy</td>,
            #  <td class="hm">no</td>,
            #  <td class="hx">yes</td>,
            #  <td class="hm">7 seconds ago</td>]
            if row.find_all('td')[6].string != "yes":  # enforce ssl proxy
                continue
            pp.add("{}:{}".format(row.find_all('td')[
                0].string, row.find_all('td')[1].string))
            if len(pp) >= self.max_proxy:
                break

        # merge with the exsting items
        self.proxy_set |= pp
        self.proxy_cycle = cycle(self.proxy_set)
        # save back to config file
        self.save_to_file()
        print('Proxy list is updated.')

    def save_to_file(self):
        with open('config.json', 'r+', encoding='utf8') as f:
            data = json.load(f)
            data['proxy'] = list(self.proxy_set)
            f.truncate(0)
            f.seek(0)
            json.dump(data, f, indent=4)

import threading
import functools
from itertools import cycle

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
        if 'proxy' in opts.keys():
            self.raw_proxies = opts['proxy']
            self.proxies = cycle(opts['proxy'])
        else:
            self.proxies = None

    @synchronized(lock)
    def get(self):
        if self.proxies is None:
            return None
        return {
            'https': next(self.proxies)
        }

    @synchronized(lock)
    def remove(self, e):
        try:
            self.raw_proxies.remove(e['https'])
            self.proxies = cycle(self.raw_proxies)
        except ValueError:
            return

            # if 'proxy' in self.opts.keys():
            #     if type(self.opts['proxy']) is list:
            #         random.seed(datetime.now())
            #         rp = random.choice(self.opts['proxy'])
            #     else:
            #         rp = self.opts['proxy']
            #     # print(">> proxy:", rp)
            #     return {
            #         'https': rp
            #     }
            # else:
            #     return None

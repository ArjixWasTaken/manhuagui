import requests
from client import MHGClient
import urllib
import re
import lzstring
import json
import node
import copy
import os
import re
import shutil

class MHGComic:
    def __init__(self, comic_id: str, start_from: int = 1, client: MHGClient = None, opts = None):
        self.client = client if client else MHGClient(opts)
        self.uri = self.client.opts['base_url'] + comic_id + '/'
        self.volumes = list(self.get_volumes(start_from))
    def get_volumes(self, start_from):
        comic_soup = self.client.get_soup(self.uri)
        title = comic_soup.select_one('.book-detail > .book-title > h1').text
        anchors = comic_soup.select('.chapter-list > ul > li > a')
        print("Fetching volume list ...")
        for anchor in anchors:
            link = anchor.get('href')
            volume_name = anchor.get('title')
            volume_number = re.search(r"\d+", volume_name)
            if volume_number and int(volume_number[0]) < int(start_from):
                continue
            # volume_name = str(next(anchor.select_one('span').children))
            volume = MHGVolume(urllib.parse.urljoin(self.uri, link), title, volume_name, self.client)
            print(volume)
            yield volume

class MHGVolume:
    def __init__(self, uri: str, title: str, volume_name: str, client: MHGClient):
        self.uri = uri
        self.title = title
        self.volume_name = volume_name
        self.client = client
    def __repr__(self):
        return '< [{title} - {volume_name}] >'.format(
            title=self.title,
            volume_name=self.volume_name,
            uri=self.uri
        )
    def get_pages_opts(self):
        res = self.client.get(self.uri)
        raw_content = res.text
        res = re.search(r'<script type="text\/javascript">window\["\\x65\\x76\\x61\\x6c"\](.*\)) <\/script>', raw_content).group(1)
        lz_encoded = re.search(r"'([A-Za-z0-9+/=]+)'\['\\x73\\x70\\x6c\\x69\\x63'\]\('\\x7c'\)", res).group(1)
        lz_decoded = lzstring.LZString().decompressFromBase64(lz_encoded)
        res = re.sub(r"'([A-Za-z0-9+/=]+)'\['\\x73\\x70\\x6c\\x69\\x63'\]\('\\x7c'\)", "'%s'.split('|')"%(lz_decoded), res)
        code = node.get_node_output(res)
        pages_opts = json.loads(re.search(r'^SMH.imgData\((.*)\)\.preInit\(\);$', code).group(1))
        return pages_opts
    def get_pages(self):
        for i, f in enumerate(self.pages_opts['files']):
            page_opts = copy.deepcopy(self.pages_opts)
            del page_opts['files']
            page_opts['page_num'] = i + 1
            page_opts['file'] = f
            page_opts['referer'] = self.uri
            page_opts['title'] = self.title
            page_opts['volume_name'] = self.volume_name
            yield MHGPage(page_opts, self.client)
    def retrieve(self):
        self.pages_opts = self.get_pages_opts()
        self.pages = list(self.get_pages())
        volume_skipped = True
        for idx, page in enumerate(self.pages):
            if page.retrieve():
                print("Downloading Volume - {:>30s}\t[{:2.2f}%] : {}\r".format(
                    self.volume_name, idx/len(self.pages)*100, page.storage_file_name), end="", flush=True)
                volume_skipped = False
        if volume_skipped:
            print("Volume - {:>30s} [Failed] !".format(self.volume_name))
            return
        print("Volume - {:>30s} [Completed].".format(self.volume_name))
        # zip current volume
        volume_path = os.path.join(self.client.opts['download_dir'], self.title, self.volume_name)
        shutil.make_archive(volume_path,
                            "zip",
                            os.path.join(self.client.opts['download_dir'], self.title),
                            self.volume_name)
        shutil.rmtree(volume_path)


class MHGPage:
    def __init__(self, opts, client: MHGClient):
        self.opts = opts
        self.client = client
    @property
    def uri(self):
        return urllib.parse.urljoin(
            self.client.opts['image_base'],
            urllib.parse.quote(
                self.opts['path'] + self.opts['file'],
                encoding='utf8'
            )
        )
    @property
    def dir_name(self):
        return os.path.join(self.opts['title'], self.opts['volume_name'])
    @property
    def storage_file_name(self):
        return '{page_num}-{file_name}'.format(
            page_num='%03d' % self.opts['page_num'],
            file_name=self.opts['file'][-15:]
        )
    def retrieve(self):
        dir_path = os.path.join(self.client.opts['download_dir'], self.dir_name)
        file_path = os.path.join(dir_path, self.storage_file_name)
        if os.path.exists(file_path): return False
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.client.retrieve(
            self.uri,
            file_path,
            params={
                'cid': self.opts['cid'],
                'md5': self.opts['sl']['md5']
            },
            headers={
                'Referer': self.opts['referer']
            }
        )
        return True




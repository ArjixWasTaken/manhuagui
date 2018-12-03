from client import MHGClient
import urllib
import re
import lzstring
import bs4
import json
import node
import copy
import os
import shutil
import logging
import pprint
import requests

logger = logging.getLogger('manguagui')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
pp = pprint.PrettyPrinter(indent=4)


class MHGComic:
    def __init__(self, comic_id: str, start_from=1, client: MHGClient = None, opts=None):
        self.client = client if client else MHGClient(opts)
        self.uri = self.client.opts['base_url'] + comic_id + '/'
        self.volumes = list(self.get_volumes(start_from))

    def get_volumes(self, start_from):
        comic_soup = self.client.get_soup(self.uri)
        title = comic_soup.select_one('.book-detail > .book-title > h1').text
        anchors = comic_soup.select('.chapter-list > ul > li > a')
        if not anchors:  # for adult only pages, decrypt the chapters
            soup = lzstring.LZString().decompressFromBase64(
                comic_soup.find('input', id='__VIEWSTATE')['value'])
            anchors = bs4.BeautifulSoup(soup, 'html.parser').select(
                '.chapter-list > ul > li > a')
        logger.debug('soup=' + str(comic_soup))
        logger.debug('title=' + title)
        logger.debug('anchors=' + str(anchors))
        print("Fetching volume list ...")

        sorted_volume = []
        for anchor in anchors:
            vol = {}
            vol['link'] = anchor.get('href')
            vol['name'] = anchor.get('title')
            result = re.search(r"\d+", vol['name'])
            vol['number'] = float(result[0]) if result else 0
            sorted_volume.append(vol)
        sorted_volume.sort(key=lambda x: x['number'])

        for vol in sorted_volume:
            if vol['number'] <= float(start_from):
                continue
            volume = MHGVolume(urllib.parse.urljoin(
                self.uri, vol['link']), title, vol['name'], self.client)
            print(volume)
            yield volume


class MHGVolume:
    def __init__(self, uri: str, title: str, volume_name: str, client: MHGClient):
        self.uri = uri
        self.title = title
        self.volume_name = volume_name
        self.client = client

    def __repr__(self):
        return '- [{title} : {volume_name}]'.format(
            title=self.title,
            volume_name=self.volume_name,
            uri=self.uri
        )

    def get_pages_opts(self):
        res = self.client.get(self.uri)
        raw_content = res.text
        res = re.search(
            r'<script type="text\/javascript">window\["\\x65\\x76\\x61\\x6c"\](.*\)) <\/script>', raw_content).group(1)
        lz_encoded = re.search(
            r"'([A-Za-z0-9+/=]+)'\['\\x73\\x70\\x6c\\x69\\x63'\]\('\\x7c'\)", res).group(1)
        lz_decoded = lzstring.LZString().decompressFromBase64(lz_encoded)
        res = re.sub(r"'([A-Za-z0-9+/=]+)'\['\\x73\\x70\\x6c\\x69\\x63'\]\('\\x7c'\)",
                     "'%s'.split('|')" % (lz_decoded), res)
        code = node.get_node_output(res)
        pages_opts = json.loads(
            re.search(r'^SMH.imgData\((.*)\)\.preInit\(\);$', code).group(1))
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
        volume_path = os.path.join(
            self.client.opts['download_dir'], self.title, self.volume_name)

        # skip this volume if .zip already exists
        if os.path.isfile(volume_path + '.zip'):
            print("  >> {:30s} [Skipped]".format(self.volume_name))
            return

        self.pages_opts = self.get_pages_opts()
        self.pages = list(self.get_pages())
        for idx, page in enumerate(self.pages):
            try:
                page.retrieve()
                print("Fetch: {:30s}\t[{:2.2f}%]: {}\r"
                      .format(self.volume_name, (idx + 1) / len(self.pages) * 100, page.storage_file_name),
                      end='',
                      flush=True)
            except requests.exceptions.RetryError:
                print("  >> {:>30s} [Failed] !!!".format(
                    self.volume_name), flush=True)
                return

        print("  >> {:30s} [Completed]".format(self.volume_name), flush=True)
        # zip current volume
        shutil.make_archive(volume_path,
                            "zip",
                            os.path.join(
                                self.client.opts['download_dir'], self.title),
                            self.volume_name)
        shutil.rmtree(volume_path)


class MHGPage:
    def __init__(self, opts, client: MHGClient):
        self.opts = opts
        self.client = client

    @property
    def uri(self):
        # HACK
        # don't encode filename as url, especially '(' and ')'
        # the remote server has tricky bug on those url (cause 500)
        url = urllib.parse.urljoin(
            self.client.opts['image_base'],
            urllib.parse.quote(
                self.opts['path'],
                encoding='utf8'
            )
        )
        return url + self.opts['file']

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
        dir_path = os.path.join(
            self.client.opts['download_dir'], self.dir_name)
        file_path = os.path.join(dir_path, self.storage_file_name)
        # if os.path.exists(file_path):
        #     return False
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # print('==', self.uri, file_path)
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

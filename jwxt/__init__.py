import requests
import json
import re
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from jwxt.config import Config
from jwxt.viewstate import ViewState, LoginVS, SearchVS, Course

class Jwxt(requests.Session):
    def __init__(self):
        super().__init__()
        self.headers.update(Config.HEADERS)
        self.root = self.best_root()

    def __repr__(self):
        return '<Jwxt cookies="{}", root="{}">'.format(self.cookies, self.root)

    @staticmethod
    def best_root():
        for root in Config.JWXT_ROOTS:
            res = requests.get(root)
            if res.status_code == 200:
                return root

    def login(self, username, password):
        res = self.get(self.root + Config.JWXT_VALIDCODE)
        img = Image.open(BytesIO(res.content))
        img.show()
        validation = input('[-] Please enter validcode > ')
        vs = LoginVS(self)
        vs.fill(username, password, validation)
        self.post(self.root + Config.JWXT_LOGIN, data=vs.data)

    def search(self, **kwargs):
        url = self.root + Config.JWXT_XK
        vs = SearchVS(self)
        vs.fill(**kwargs)
        res = self.post(url, data=vs.data)
        return SearchResult(self, res.text)


class SearchResult(object):
    def __init__(self, jwxt, html):
        self.courses = []
        dict_dataA = ViewState.extract(html)
        
        BS1 = BeautifulSoup(html, 'html.parser')
        tags = BS1.find_all('tr',
            attrs={'class': re.compile(Config.XK_COURSE_PATTERN)})
        for tag in tags:
            E = list(tag.children)
            K = Course(jwxt)

            K.magic = re.search(
                    Config.XK_MAGIC_PATTERN,
                    E[1].a.get('href')
                ).group(0)

            dict_dataA['__EVENTTARGET'] = K.magic
            resA = jwxt.post(
                jwxt.root + Config.JWXT_XK,
                data=ViewState.encode(dict_dataA))

            # the form is ready, just take it.
            dict_dataB = {}
            BS = BeautifulSoup(resA.text, 'html.parser')
            for i in BS.form.find_all('input'):
                dict_dataB[i.get('name')] = i.get('value')
            dict_dataB.pop('btnReturnX')
            K._data = dict_dataB

            K.class_number = E[2].string
            K.order_number = E[3].string
            K.name = E[4].string
            self.courses.append(K)

    def __repr__(self):
        return '<SearchResult courses=%s>' % repr(self.courses)

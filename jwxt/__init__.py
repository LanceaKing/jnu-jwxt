import requests
import json
import re
from io import BytesIO
from PIL import Image
from config import Config, FORM_DATA
from jwxt.funcs import bsfilter, urlequal
from jwxt.viewstate import JwxtLoginVS
from jwxt.models import XKCenter, Course, SearchResult

class Jwxt(requests.Session):
    urls = Config.JWXT_URLS
    __is_logined = False

    @property
    def netloc(self):
        return self.urls['root']

    @property
    def is_logined(self):
        return self.__is_logined

    def __init__(self):
        requests.Session.__init__(self)
        self.headers.update(Config.HEADERS)

    def __repr__(self):
        return '<Jwxt cookies={}, netloc={}>'.format(
            repr(self.cookies), self.netloc)

    def login(self, username, password):
        validcode = self.get(self.urls['validcode'])
        img = Image.open(BytesIO(validcode.content))
        img.show()
        validation = input('[-] Please enter validcode > ')
        login = self.get(self.netloc)
        loginvs = JwxtLoginVS(self, login)
        loginvs.fill(username, password, validation)
        loginvs.submit()
        self.__is_logined = True

    def get_xkcenter(self):
        return XKCenter(self)

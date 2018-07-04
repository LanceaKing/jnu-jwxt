from urllib.parse import urlencode
from bs4 import BeautifulSoup
from jwxt.config import Config
from copy import copy
import requests
import json
import re

formdata = json.load(open(Config.FORM_DATA, 'rb'))

class ViewState(object):
    _data = {}

    def __init__(self, jwxt):
        self.sess = jwxt

    @staticmethod
    def extract(html):
        data = {}
        BS = BeautifulSoup(html, 'html.parser')
        for tag in BS.find_all('input', type='hidden'):
            data[tag.get('name')] = tag.get('value')
        return data

    @staticmethod
    def encode(d):
        return urlencode(d, encoding=Config.JWXT_ENCODING)

    @property
    def data(self):
        return self.encode(self._data)
    
    @data.setter
    def data(self, D):
        if isinstance(D, dict):
            self._data = D
        else:
            raise TypeError('dict required.')



class LoginVS(ViewState):
    def __init__(self, jwxt):
        super().__init__(jwxt)
        self.url = self.sess.root
        self._data = self.extract(self.sess.get(self.url).text)

    def fill(self, username, password, validcode):
        form = copy(formdata['login'])
        form['txtYHBS'] = username
        form['txtYHMM'] = password
        form['txtFJM'] = validcode
        self._data.update(form)

class XKCenterVS(ViewState):
    choice = 'btnKkLb'

    def __init__(self, jwxt):
        super().__init__(jwxt)
        self.url = self.sess.root + Config.JWXT_XK
        self._data = self.get_xk_form()

    def get_xk_form(self):
        rooturl = self.sess.root
        menu = formdata['xkcenter']

        resA = self.sess.get(rooturl + Config.JWXT_XK_README, allow_redirects=False)
        if resA.status_code != 302:
            dataB = self.extract(resA.text)
            dataB.update(formdata['readme'])
            resB = self.sess.post(rooturl + Config.JWXT_XK_README, data=self.encode(dataB))
        else:
            resB = self.sess.get(self.url)

        dataB = self.extract(resB.text)
        dataB.update({self.choice: menu[self.choice]})

        resC = self.sess.post(self.url, data=self.encode(dataB))
        dataC = self.extract(resC.text)
        return dataC


class SearchVS(XKCenterVS):
    choice = 'btnKkLb'

    def fill(self, name='', class_number='', order_number='',
             teacher='', credit='', grade='', location='', comment=''):
        form = copy(formdata['search'])
        form['txtXf'] = credit
        form['txtKcmc'] = name
        form['txtNj'] = grade
        form['txtKcbh'] = class_number
        form['txtSkDz'] = location
        form['txtPkbh'] = order_number
        form['txtBzxx'] = comment
        form['txtZjjs'] = teacher
        self._data.update(form)


class Course(ViewState):
    magic = ''
    class_number = ''
    order_number = ''
    name = ''

    def __repr__(self):
        return '<Course name={} class_number={} order_number={}>'.format(
            self.name, self.class_number, self.order_number)

    def select(self):
        res = self.sess.post(self.sess.root + Config.JWXT_XK, data=self.data)
        return re.search(Config.XK_MSG_PATTERN, res.text).group(1)

class CourseException(Exception):
    pass

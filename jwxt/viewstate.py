from urllib.parse import urlencode
from config import Config, FORM_DATA
from jwxt.funcs import bsfilter, urlequal


class ViewState(dict):
    url = action = None
    form = None

    def __init__(self, session, response):
        if self.url:
            assert urlequal(self.url, response.url)
        else:
            self.url = response.url

        self.session = session

        dict.__init__(self)
        self.update(ViewState.extract(response.text))
        if self.form:
            self.update(self.form)

        for k, v in self.items():
            self[k] = v or ''

    @staticmethod
    def urlencode(d):
        return urlencode(d, encoding=Config.JWXT_ENCODING)

    @property
    def urldata(self):
        return ViewState.urlencode(self)

    def submit(self, action=None):
        action = action or self.action or self.url
        assert action != None
        return self.session.post(action, data=self.urldata)

    @staticmethod
    def extract(html):
        rel = {}
        tags = bsfilter(html, name='input',attrs={
            'name': Config.VIEWSTATE_PATTERN,
            'type': 'hidden'})
        for tag in tags:
            rel[tag.get('name')] = tag.get('value')
        return rel


class JwxtLoginVS(ViewState):
    url = Config.JWXT_URLS['root']
    action = Config.JWXT_URLS['login']
    form = FORM_DATA['login'].copy()

    def fill(self, username, password, validcode):
        self['txtYHBS'] = username
        self['txtYHMM'] = password
        self['txtFJM'] = validcode


class JwxtSearchVS(ViewState):
    url = Config.JWXT_URLS['xkcenter']
    form = FORM_DATA['search'].copy()

    def fill(self, name='', class_number='', order_number='',
             teacher='', credit='', grade='', location='', comment=''):
        self['txtXf'] = credit
        self['txtKcmc'] = name
        self['txtNj'] = grade
        self['txtKcbh'] = class_number
        self['txtSkDz'] = location
        self['txtPkbh'] = order_number
        self['txtBzxx'] = comment
        self['txtZjjs'] = teacher


class JwxtXKCenterVS(ViewState):
    url = Config.JWXT_URLS['xkcenter']
    selection = FORM_DATA['xkcenter']
    targets = {
        JwxtSearchVS: 'btnKkLb'
    }

    def go(self, target):
        assert target in self.targets

        name = self.targets[target]
        self[name] = self.selection[name]

        response = self.submit()

        self.pop(name)
        return target(self.session, response)

from urllib.parse import urlencode
from config import Config, FORM_DATA
from jwxt.funcs import bsfilter, urlequal


class ViewState(dict):
    url = None
    #action = None
    form = {}

    def __init__(self, session, response):
        self.session = session
        if self.url:
            assert urlequal(self.url, response.url)
        else:
            self.url = response.url

        dict.__init__(self)

        self.update(self.extract(response.text))
        if self.form:
            self.form = self.form.copy()
            for k, v in self.form.items():
                self.form[k] = v or ''
            self.update(self.form)

    @staticmethod
    def urlencode(d):
        return urlencode(d, encoding=Config.JWXT_ENCODING)

    @property
    def urldata(self):
        return ViewState.urlencode(self)

    def submit(self, action=None):
        action = action or self.url
        assert action != None
        result = self.session.post(action, data=self.urldata)
        assert result.ok
        return result

    @staticmethod
    def extract(html):
        ret = {}
        tags = bsfilter(html, name='input',attrs={
            'name': Config.VIEWSTATE_PATTERN,
            'type': 'hidden'})
        for tag in tags:
            ret[tag.get('name')] = tag.get('value')
        return ret

    def __repr__(self):
        return '<{} url={}, {}>'.format(
            type(self).__name__,
            repr(self.url),
            dict.__repr__(self))


class JwxtLoginVS(ViewState):
    url = Config.JWXT_URLS['login']
    form = FORM_DATA['login']

    def fill(self, id, password, validcode):
        self['txtYHBS'] = id
        self['txtYHMM'] = password
        self['txtFJM'] = validcode


class JwxtSearchVS(ViewState):
    url = Config.JWXT_URLS['xkcenter']
    form = FORM_DATA['search']

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

        del self[name]
        return target(self.session, response)

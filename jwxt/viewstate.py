import re

from config import FORM_DATA, Config
from lib.viewstate import ViewState


class LoginVS(ViewState):
    encoding = Config.JWXT_ENCODING
    url = Config.JWXT_URLS['login']
    form = FORM_DATA['login']

    def fill(self, id, password, validcode):
        self['txtYHBS'] = id
        self['txtYHMM'] = password
        self['txtFJM'] = validcode


class SearchInitVS(ViewState):
    encoding = Config.JWXT_ENCODING
    url = Config.JWXT_URLS['xkcenter']
    form = FORM_DATA['search']

    def fill(self, limit=None, type='', name='', class_id='', order_id='',
             teacher='', credit='', grade='', location='', comment=''):
        if not limit:
            limit = self['dlstSsfw'][4]
        else:
            assert limit in self['dlstSsfw']

        assert type in self['dlstKclb']

        self['dlstSsfw'] = limit
        self['dlstKclb'] = type
        self['txtXf'] = credit
        self['txtKcmc'] = name
        self['txtNj'] = grade
        self['txtKcbh'] = class_id
        self['txtSkDz'] = location
        self['txtPkbh'] = order_id
        self['txtBzxx'] = comment
        self['txtZjjs'] = teacher



class SearchVS(ViewState):
    encoding = Config.JWXT_ENCODING
    url = Config.JWXT_URLS['xkcenter']
    form = FORM_DATA['search2']

    def __init__(self, session, html, rows=None):
        ViewState.__init__(self, session, html)

        pattern = Config.RE_ROW_COUNT
        found = re.search(pattern, html)
        N = found.group(1)
        self.result_count = int(N)
        self.rows = rows or N

    @property
    def rows(self):
        return self['txtRows']

    @rows.setter
    def rows(self, N):
        if isinstance(N, int):
            self['txtRows'] = str(N)
        else:
            self['txtRows'] = N


class XKCenterVS(ViewState):
    encoding = Config.JWXT_ENCODING
    url = Config.JWXT_URLS['xkcenter']

    selections = FORM_DATA['xkcenter']
    targets = {
        SearchInitVS: 'btnKkLb'
    }

    def get(self, target):
        assert target in self.targets

        name = self.targets[target]
        self[name] = self.selections[name]

        response = self.submit()

        del self[name]
        return target(self.session, response.text)

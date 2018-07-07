import re
from urllib.parse import urlencode

from requests import Response, Session

from lib.funcs import bsfilter, urlequal


class ViewState(dict):
    url = ''
    form = {}
    pattern = {
        'name': re.compile(r"__[A-Z]+"),
        'type': 'hidden'
    }
    encoding = None

    def __init__(self, session: Session, html='', url=''):
        self.session = session
        self.url = self.url or url

        dict.__init__(self)

        if html:
            self.update(ViewState.extract(html))

        if self.form:
            self.form = self.form.copy()
            for k, v in self.form.items():
                self.form[k] = v or ''
            self.update(self.form)

    @property
    def urldata(self) -> str:
        return urlencode(self, encoding=self.encoding)

    def submit(self, action=None) -> Response:
        action = action or self.url
        assert action != None
        result = self.session.post(action, data=self.urldata)
        assert result.ok
        return result

    @staticmethod
    def urlencode(d: dict) -> str:
        return urlencode(d, encoding=ViewState.encoding)

    @staticmethod
    def extract(html: str) -> dict:
        ret = {}
        tags = bsfilter(html, name='input',
                        attrs=ViewState.pattern)
        for tag in tags:
            ret[tag.get('name')] = tag.get('value')
        return ret

    def copy(self):
        new_vs = type(self)(self.session, url=self.url)
        new_vs.url = self.url
        new_vs.form = self.form
        new_vs.encoding = self.encoding
        new_vs.update(dict.copy(self))
        return new_vs

    def __repr__(self):
        return '<{} url={}, {}>'.format(
            type(self).__name__,
            repr(self.url),
            dict.__repr__(self))

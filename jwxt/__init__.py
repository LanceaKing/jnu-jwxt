from io import BytesIO
from time import sleep

from PIL import Image
from requests import Session

from config import FORM_DATA, Config
from jwxt.course import CourseJar
from jwxt.errors import LoginError, TooQuickError
from jwxt.viewstate import LoginVS, SearchInitVS, SearchVS, XKCenterVS
from lib.funcs import find_alert_msg
from lib.viewstate import ViewState


class Jwxt(Session):
    urls = Config.JWXT_URLS
    id = None
    __logined = False

    @property
    def netloc(self):
        return self.urls['root']

    @property
    def logined(self):
        return self.__logined

    def __init__(self):
        Session.__init__(self)
        self.headers.update(Config.HEADERS)

    def __repr__(self):
        return '<Jwxt netloc={}, id={}, logined={}>'.format(
            repr(self.netloc),
            repr(self.id),
            repr(self.logined))

    def get_validcode_img(self) -> Image.Image:
        validcode = self.get(self.urls['validcode'])
        assert validcode.ok
        return Image.open(BytesIO(validcode.content))

    def login(self, id, password, validation):
        assert not self.logined
        login = self.get(self.urls['login'])
        loginvs = LoginVS(self, login.text)
        loginvs.fill(id, password, validation)
        result = loginvs.submit()
        if result.url != self.urls['index']:
            login_mistake = find_alert_msg(result.text)
            raise LoginError(login_mistake)
        self.id = id
        self.__logined = True
        return result

    def logout(self):
        assert self.logined
        logout_url = self.urls['logout']
        logout = self.get(logout_url)
        logoutvs = ViewState(self, logout.text, logout_url)
        logoutvs.update(FORM_DATA['logout'])
        result = logoutvs.submit()
        assert "window.open('Login.aspx','_parent')" in result.text
        self.id = None
        self.__logined = False

    def get_xkcenter(self):
        return XKCenter(self)


class XKCenter(object):
    url = ''
    session = None
    viewstate = None
    __readmed = False
    targets = {
        SearchVS: 'btnKkLb'
    }

    def __init__(self, session: Jwxt):
        assert session.logined
        self.session = session
        xkcenter_res = self.get_response()
        self.viewstate = XKCenterVS(session, xkcenter_res.text)

    def get_response(self):
        if not self.__readmed:
            readme_url = self.session.urls['xkreadme']
            self.url = self.session.urls['xkcenter']

            readme_res = self.session.get(readme_url, allow_redirects=False)
            if readme_res.status_code != 302:
                readme_vs = ViewState(self.session, readme_res.text, readme_url)
                readme_vs.url = readme_url
                readme_vs.update(FORM_DATA['xkreadme'])
                xkcenter_res = readme_vs.submit()
            else:
                xkcenter_res = self.session.get(self.url)

            self.__readmed = True
            return xkcenter_res
        else:
            return self.session.get(self.url)

    def search(self, rows=None, **kwargs):
        search = Searcher(self, rows, **kwargs)
        sleep(2)
        return search.go()

    @property
    def readmed(self):
        return self.__readmed

    def __repr__(self):
        return '<JwxtXKCenter session={}, readmed={}, url={}>'.format(
            repr(self.session),
            repr(self.readmed),
            repr(self.url))


class Searcher(object):
    def __init__(self, xkcenter: XKCenter, rows=None, **kwargs):
        assert xkcenter.readmed
        
        self.session = xkcenter.session
        self.conditions = kwargs

        init_vs = xkcenter.viewstate.get(SearchInitVS)
        init_vs.fill(**kwargs)
        response = init_vs.submit()

        self.viewstate = SearchVS(self.session, response.text, rows=rows)

    def go(self):
        response = self.viewstate.submit()
        too_quick = find_alert_msg(response.text)
        if too_quick:
            TooQuickError(too_quick)
        return CourseJar(self.session, response.text)

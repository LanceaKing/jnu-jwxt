from requests import Session
from io import BytesIO
from PIL import Image
from config import Config, FORM_DATA
from jwxt.viewstate import ViewState, LoginVS, XKCenterVS, SearchVS
from jwxt.course import CourseJar
from jwxt.errors import LoginError
from jwxt.funcs import find_msg

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
            self.netloc,
            self.id,
            self.logined)

    def get_validcode_img(self):
        validcode = self.get(self.urls['validcode'])
        assert validcode.ok
        return Image.open(BytesIO(validcode.content))

    def login(self, id, password, validation):
        assert not self.logined
        login = self.get(self.urls['login'])
        loginvs = LoginVS(self, login)
        loginvs.fill(id, password, validation)
        result = loginvs.submit()
        if result.url != self.urls['index']:
            login_mistake = find_msg(result.text)
            raise LoginError(login_mistake)
        self.id = id
        self.__logined = True
        return result

    def logout(self):
        assert self.logined
        logout = self.get(self.urls['logout'])
        logoutvs = ViewState(self, logout)
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

    def __init__(self, session):
        assert session.logined
        self.session = session
        xkcenter = self.get_response()
        self.viewstate = XKCenterVS(session, xkcenter)

    def get_response(self):
        if not self.__readmed:
            readme_url = self.session.urls['xkreadme']
            self.url = self.session.urls['xkcenter']

            readme = self.session.get(readme_url, allow_redirects=False)
            if readme.status_code != 302:
                readmevs = ViewState(self.session, readme)
                readmevs.update(FORM_DATA['xkreadme'])
                xkcenter = readmevs.submit()
            else:
                xkcenter = self.session.get(self.url)

            self.__readmed = True
            return xkcenter
        else:
            return self.session.get(self.url)

    def search(self, **kwargs):
        searchvs = self.viewstate.go(SearchVS)
        searchvs.fill(**kwargs)
        result = searchvs.submit()
        return CourseJar(self.session, result)

    @property
    def readmed(self):
        return self.__readmed

    def __repr__(self):
        return '<JwxtXKCenter session={}, readmed={}, url={}>'.format(
            repr(self.session),
            repr(self.readmed),
            repr(self.url))

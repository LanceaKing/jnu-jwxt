from requests import Session
from io import BytesIO
from PIL import Image
from config import Config, FORM_DATA
from jwxt.viewstate import ViewState, JwxtLoginVS
from jwxt.models import JwxtXKCenter

class Jwxt(Session):
    urls = Config.JWXT_URLS
    id = None
    __is_logined = False

    @property
    def netloc(self):
        return self.urls['root']

    @property
    def is_logined(self):
        return self.__is_logined

    def __init__(self):
        Session.__init__(self)
        self.headers.update(Config.HEADERS)

    def __repr__(self):
        return '<Jwxt netloc={}, id={}, is_logined={}>'.format(
            self.netloc,
            self.id,
            self.is_logined)

    def get_validcode_img(self):
        validcode = self.get(self.urls['validcode'])
        assert validcode.ok
        return Image.open(BytesIO(validcode.content))

    def login(self, id, password, validation):
        assert not self.is_logined
        login = self.get(self.urls['login'])
        loginvs = JwxtLoginVS(self, login)
        loginvs.fill(id, password, validation)
        result = loginvs.submit()
        assert result.ok
        assert result.url == self.urls['index']
        self.id = id
        self.__is_logined = True
        return result

    def logout(self):
        assert self.is_logined
        logout = self.get(self.urls['logout'])
        logoutvs = ViewState(self, logout)
        logoutvs.update(FORM_DATA['logout'])
        result = logoutvs.submit()
        assert result.ok
        assert "window.open('Login.aspx','_parent')" in result.text
        self.id = None
        self.__is_logined = False
        return result

    def get_xkcenter(self):
        return JwxtXKCenter(self)

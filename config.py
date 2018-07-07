import json
import re
from os.path import dirname, join
from urllib.parse import urljoin


class Config(object):
    FORM_DATA_PATH = join(dirname(__file__), 'jwxt', 'forms.json')
    HEADERS = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    JWXT = 'http://202.116.0.172:8083/'
    JWXT_URLS = {
        'root': JWXT,
        'index': urljoin(JWXT, 'IndexPage.aspx'),
        'login': urljoin(JWXT, 'Login.aspx'),
        'logout': urljoin(JWXT, 'areaTopLogo.aspx'),
        'validcode': urljoin(JWXT, 'ValidateCode.aspx'),
        'xkcenter': urljoin(JWXT, 'Secure/PaiKeXuanKe/wfrm_XK_XuanKe.aspx'),
        'xkrule': urljoin(JWXT, 'Secure/PaiKeXuanKe/wfrm_XK_Rule.aspx'),
        'xkreadme': urljoin(JWXT, 'Secure/PaiKeXuanKe/wfrm_Xk_ReadMeCn.aspx')
    }
    JWXT_ENCODING = 'gbk'
    JWXT_SLEEP = 2

    RE_XK_MAGIC = re.compile(r"dgrdPk\$ctl\d+\$ctl\d+")
    BS_XK_COURSE = {'class': ['DGItemStyle', 'DGAlternatingItemStyle']}
    RE_ROW_COUNT = re.compile(r"共\d+页(\d+)行")


FORM_DATA = json.load(open(Config.FORM_DATA_PATH, 'rb'))

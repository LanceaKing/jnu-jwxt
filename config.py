import json
import re
from os.path import join, dirname
from urllib.parse import urljoin

class Config(object):
    FORM_DATA_PATH = join(dirname(__file__), 'jwxt', 'forms.json')
    HEADERS = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    JWXT = 'http://202.116.0.172:8083/'
    JWXT_URLS = {
        'root': JWXT,
        'login': urljoin(JWXT, '/Login.aspx'),
        'validcode': urljoin(JWXT, '/ValidateCode.aspx'),
        'xkcenter': urljoin(JWXT, '/Secure/PaiKeXuanKe/wfrm_XK_XuanKe.aspx'),
        'xkrule': urljoin(JWXT, '/Secure/PaiKeXuanKe/wfrm_XK_Rule.aspx'),
        'xkreadme': urljoin(JWXT, '/Secure/PaiKeXuanKe/wfrm_Xk_ReadMeCn.aspx')
    }
    JWXT_ENCODING = 'gbk'

    VIEWSTATE_PATTERN = re.compile(r'__[A-Z]+')
    XK_COURSE_PATTERN = re.compile(r'DG(?!Header)\w+Style')
    XK_MAGIC_PATTERN = re.compile(r'dgrdPk\$ctl\d+\$ctl\d+')
    XK_MSG_PATTERN = re.compile(r'alert\(\'(.*?)\'\)')

FORM_DATA = json.load(open(Config.FORM_DATA_PATH, 'rb'))
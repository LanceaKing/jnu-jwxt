from bs4 import BeautifulSoup
from config import Config
import re

def urlequal(A, B):
    return A.rstrip('/') == B.rstrip('/')

def bsfilter(html, **kwargs):
    BS = BeautifulSoup(html, 'html.parser')
    return BS.find_all(**kwargs)

def find_msg(html):
        result = re.search(Config.XK_MSG_PATTERN, html)
        return result and result.group(1)

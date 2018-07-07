import re

from bs4 import BeautifulSoup


def urlequal(A, B):
    return A.rstrip('/') == B.rstrip('/')

def bsfilter(html, **kwargs):
    BS = BeautifulSoup(html, 'html.parser')
    return BS.find_all(**kwargs)

def find_alert_msg(html, pattern=None):
    pattern = pattern or re.compile(r"alert\('(.*?)'\)")
    result = re.search(pattern, html)
    return result and result.group(1)

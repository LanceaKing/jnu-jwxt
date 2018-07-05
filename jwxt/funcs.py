from bs4 import BeautifulSoup

def urlequal(A, B):
    return A.rstrip('/') == B.rstrip('/')

def bsfilter(html, **kwargs):
    BS = BeautifulSoup(html, 'html.parser')
    return BS.find_all(**kwargs)
from jwxt.viewstate import ViewState, JwxtXKCenterVS, JwxtSearchVS
from jwxt.funcs import bsfilter, urlequal
from config import Config, FORM_DATA
import re


class XKCenter(object):
    session = None
    viewstate = None
    __already_readme = False

    @property
    def already_readme(self):
        return self.__already_readme

    def __init__(self, session):
        assert session.is_logined
        self.session = session
        xkcenter = self.pass_readme()
        self.viewstate = JwxtXKCenterVS(session, xkcenter)

    def pass_readme(self):
        if not self.__already_readme:
            readme_url = self.session.urls['xkreadme']
            xkcenter_url = self.session.urls['xkcenter']

            readme = self.session.get(readme_url, allow_redirects=False)
            if readme.status_code != 302:
                readmevs = ViewState(self.session, readme)
                readmevs.update(FORM_DATA['xkreadme'])
                xkcenter = readmevs.submit()
            else:
                xkcenter = self.session.get(xkcenter_url)

            self.__already_readme = True
            return xkcenter
        else:
            return self.session.get(xkcenter_url)

    def search(self, **kwargs):
        search = self.viewstate.go(JwxtSearchVS)
        search.fill(**kwargs)
        result = search.submit()
        return SearchResult(self.session, result)

class Course(ViewState):
    url = Config.JWXT_URLS['xkcenter']
    magic = ''
    name = ''
    class_number = ''
    order_number = ''

    def __init__(self, session, response):
        if self.url:
            assert urlequal(self.url, response.url)
        else:
            self.url = response.url

        self.session = session

        dict.__init__(self)
        tags = bsfilter(response.text, name='input')
        for i in tags:
            self[i.get('name')] = i.get('value')
        self.pop('btnReturnX')

        if self.form:
            self.update(self.form)

        for k, v in self.items():
            self[k] = v or ''

    def select(self):
        res = self.submit()
        return Course.find_msg(res.text)
    
    @staticmethod
    def find_msg(html):
        return re.search(Config.XK_MSG_PATTERN, html).group(1)

    def __repr__(self):
        return '<Course name={} class_number={} order_number={}>'.format(
            self.name, self.class_number, self.order_number)


class SearchResult(list):
    def __init__(self, session, response):
        list.__init__(self)
        course_checker = ViewState(session, response)
        assert urlequal(course_checker.url, session.urls['xkcenter'])
        
        tags = bsfilter(response.text, name='tr',
            attrs={'class': Config.XK_COURSE_PATTERN})
        for tag in tags:
            E = list(tag.children)
            magic = re.search(
                    Config.XK_MAGIC_PATTERN,
                    E[1].a.get('href')
                ).group(0)

            course_checker['__EVENTTARGET'] = magic
            final = course_checker.submit()

            new_course = Course(session, final)

            new_course.class_number = E[2].string
            new_course.order_number = E[3].string
            new_course.name = E[4].string
            self.append(new_course)

    def __repr__(self):
        return '<SearchResult%s>' % list.__repr__(self)

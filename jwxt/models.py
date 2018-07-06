from jwxt.viewstate import ViewState, JwxtXKCenterVS, JwxtSearchVS
from jwxt.funcs import bsfilter, urlequal, find_msg
from jwxt.errors import CourseError
from config import Config, FORM_DATA
import re


class JwxtXKCenter(object):
    url = ''
    session = None
    viewstate = None
    __readmed = False

    def __init__(self, session):
        assert session.logined
        self.session = session
        xkcenter = self.get_response()
        self.viewstate = JwxtXKCenterVS(session, xkcenter)

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
        searchvs = self.viewstate.go(JwxtSearchVS)
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
            repr(self.url)
        )


class Course(ViewState):
    url = Config.JWXT_URLS['xkcenter']
    magic = ''
    name = ''
    class_number = ''
    order_number = ''

    @staticmethod
    def extract(html):
        # all fields is in the course page, just take it
        ret = {}
        tags = bsfilter(html, name='input')
        for tag in tags:
            ret[tag.get('name')] = tag.get('value')
        ret.pop('btnReturnX') # don't return
        return ret

    def select(self):
        result = self.submit()
        course_mistake = find_msg(result.text)
        if course_mistake:
            raise CourseError(course_mistake)

    def __repr__(self):
        return 'Course(name={}, class_number={}, order_number={})'.format(
            repr(self.name),
            repr(self.class_number),
            repr(self.order_number))


class CourseJar(list):
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

            not_enter_course = find_msg(final.text)
            if not_enter_course:
                raise CourseError(not_enter_course)

            new_course = Course(session, final)

            new_course.class_number = E[2].string
            new_course.order_number = E[3].string
            new_course.name = E[4].string
            self.append(new_course)

    def __repr__(self):
        return '<CourseJar{}>'.format(list.__repr__(self))

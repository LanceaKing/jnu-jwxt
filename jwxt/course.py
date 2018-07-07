import re

from requests import Response, Session

from config import Config
from jwxt.errors import CourseError
from lib.funcs import bsfilter, find_alert_msg, urlequal
from lib.viewstate import ViewState


class Course(object):
    encoding = Config.JWXT_ENCODING
    url = Config.JWXT_URLS['xkcenter']

    magic = ''

    class_id = ''
    order_id = ''
    name = ''
    credit = ''
    type = ''
    schedule = ''
    teacher = ''
    location = ''
    comment = ''
    exam_date = ''
    language = ''

    def __init__(self, viewstate: ViewState):
        self.viewstate = viewstate

    def select(self) -> Response:
        confirmer = CourseConfirmer(self)
        return confirmer.confirm()


    def __repr__(self):
        return 'Course(name={})'.format(repr(self.name))


class CourseConfirmer(ViewState):
    url = Config.JWXT_URLS['xkcenter']

    source = None

    def __init__(self, course: Course):
        self.source = course
        viewstate = course.viewstate.copy()
        viewstate.url = self.url
        viewstate['__EVENTTARGET'] = course.magic
        confirm_res = viewstate.submit()

        course_mistake = find_alert_msg(confirm_res.text)
        if course_mistake:
            raise CourseError(course_mistake)
    
        ViewState.__init__(self, course.session, confirm_res)

    @staticmethod
    def extract(html):
        # all fields is in the course page, just take it
        ret = {}
        tags = bsfilter(html, name='input')
        for tag in tags:
            ret[tag.get('name')] = tag.get('value')
        ret.pop('btnReturnX') # don't return
        return ret

    def confirm(self):
        result = self.submit()
        confirm_mistake = find_alert_msg(result.text)
        if confirm_mistake:
            raise CourseError(confirm_mistake)
        return result


class CourseJar(list):
    def __init__(self, session: Session, html: str):
        list.__init__(self)
        attrs = Config.BS_XK_COURSE
        pattern = Config.RE_XK_MAGIC

        xk_url = session.urls['xkcenter']
        course_checker = ViewState(session, html, xk_url)
        tags = bsfilter(html, attrs=attrs)
        for tag in tags:
            E = list(tag.children)
            magic = re.search(pattern, E[1].a.get('href')).group(0)

            course = Course(course_checker)
            course.magic = magic

            course.class_id = E[2].text.strip()
            course.order_id = E[3].text.strip()
            course.name = E[4].text.strip()
            course.credit = E[5].text.strip()
            course.type = E[6].text.strip()
            course.schedule = E[7].text.strip()
            course.teacher = E[8].text.strip()
            course.location = E[9].text.strip()
            course.comment = E[10].text.strip()
            course.exam_date = E[11].text.strip()
            course.language = E[12].text.strip()

            self.append(course)

    def __repr__(self):
        return '<CourseJar{}>'.format(list.__repr__(self))

from jwxt.viewstate import ViewState
from jwxt.errors import CourseError
from jwxt.funcs import bsfilter, urlequal, find_msg
from config import Config
import re


class Course(ViewState):
    url = Config.JWXT_URLS['xkcenter']
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

    @property
    def magic(self):
        return self['__EVENTTARGET']

    @magic.setter
    def magic(self, magic):
        self['__EVENTTARGET'] = magic

    def select(self):
        commiter = CourseCommiter(self)
        result = commiter.commit()

        confirm_mistake = find_msg(result.text)
        if confirm_mistake:
            raise CourseError(confirm_mistake)

    def __repr__(self):
        return 'Course(name={}, class_id={}, order_id={})'.format(
            repr(self.name),
            repr(self.class_id),
            repr(self.order_id))


class CourseCommiter(ViewState):
    url = Config.JWXT_URLS['xkcenter']
    source = None

    def __init__(self, course):
        self.source = course
        commit = course.submit()

        course_mistake = find_msg(commit.text)
        if course_mistake:
            raise CourseError(course_mistake)
    
        ViewState.__init__(self, course.session, commit)

    @staticmethod
    def extract(html):
        # all fields is in the course page, just take it
        ret = {}
        tags = bsfilter(html, name='input')
        for tag in tags:
            ret[tag.get('name')] = tag.get('value')
        ret.pop('btnReturnX') # don't return
        return ret

    def commit(self):
        self.submit()


class CourseJar(list):
    def __init__(self, session, response):
        list.__init__(self)
        xkchecker = ViewState(session, response)
        assert urlequal(xkchecker.url, session.urls['xkcenter'])
        
        tags = bsfilter(response.text, name='tr',
            attrs=Config.XK_COURSE_PATTERN)
        for tag in tags:
            E = list(tag.children)
            magic = re.search(
                    Config.XK_MAGIC_PATTERN,
                    E[1].a.get('href')
                ).group(0)

            course = Course(session, response)
            course.magic = magic

            course.class_id = E[2].text
            course.order_id = E[3].text
            course.name = E[4].text
            course.credit = E[5].text
            course.type = E[6].text
            course.schedule = E[7].text
            course.teacher = E[8].text
            course.location = E[9].text
            course.comment = E[10].text
            course.exam_date = E[11].text
            course.language = E[12].text

            self.append(course)

    def __repr__(self):
        return '<CourseJar{}>'.format(list.__repr__(self))

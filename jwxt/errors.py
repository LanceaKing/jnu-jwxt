

class JwxtException(Exception):
    msg = []
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class LoginError(JwxtException):
    pass


class CourseError(JwxtException):
    pass

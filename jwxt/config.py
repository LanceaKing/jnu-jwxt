from os.path import join, dirname

class Config(object):
    FORM_DATA = 'forms.json'
    HEADERS = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    JWXT_ENCODING = 'gbk'
    JWXT_ROOTS = [
        'http://202.116.0.172:8083',
        'https://jwxt.jnu.edu.cn'
    ]
    JWXT_LOGIN = '/Login.aspx'
    JWXT_VALIDCODE = '/ValidateCode.aspx'
    JWXT_XK = '/Secure/PaiKeXuanKe/wfrm_XK_XuanKe.aspx'
    JWXT_XK_RULE = '/Secure/PaiKeXuanKe/wfrm_XK_Rule.aspx'
    JWXT_XK_README = '/Secure/PaiKeXuanKe/wfrm_Xk_ReadMeCn.aspx'
    XK_COURSE_PATTERN = r'DG(?!Header)\w+Style'
    XK_MAGIC_PATTERN = r'dgrdPk\$ctl\d+\$ctl\d+'
    XK_MSG_PATTERN = r'alert\(\'(.*?)\'\)'

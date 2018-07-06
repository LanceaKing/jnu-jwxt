from jwxt import Jwxt
from getpass import getpass

app = Jwxt()

userid = input('[-] User ID > ')
password = getpass('[-] Password > ')
validcode = ''
while not validcode:
    validcode_img = app.get_validcode_img()
    validcode_img.show()
    validcode = input('[-] Validcode > ')

app.login(userid, password, validcode)

xk = app.get_xkcenter()
print(xk)
rel = xk.search()
print(rel)

print(rel[1])
msg = rel[1].select()
print(msg)

app.logout()

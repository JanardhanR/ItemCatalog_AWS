import sys

sys.path.insert(0, '/var/www/html/')



from itemcatalog import app as application
from itemcatalog import SetupDB
application.secret_key = 'x+\xcd9.\xcf\xcb\xf1}\xeep\xc7\xb6\x05\x93\x96\xe3r\xc1\x97\x97\xd9\xdc'
application.static_foler = 'static'
SetupDB()


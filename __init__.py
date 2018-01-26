from html import itemcatalog
from html import catalogDB

if __name__ == '__main__':
    app.secret_key = 'x+\xcd9.\xcf\xcb\xf1}\xeep\xc7\xb6\x05\x93\x96\xe3r\xc1\x97\x97\xd9\xdc'
    app.debug = True
    app.static_folder = 'static'
    print 'setting up Itemcatalog db'
    SetupDB()
    app.run(host='0.0.0.0', port=8080)


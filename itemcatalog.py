'''module for item catalog'''
import random
import string
import json
import requests
from flask import Flask, flash, redirect, \
    render_template, request, \
    make_response, jsonify, session as login_session
from oauth2client import client
import httplib2
from catalogDB import SetupDB, getCatalog, \
    GetLatestItems, GetUserID, CreateUser, \
    AddItem, GetItemsByCat, \
    GetItemById, GetCatalogItems, EditItem, \
    DeleteItem

app = Flask(__name__)

def IsUserLoggedIn():
    '''check if user is already logged in
    setup session if not logged in'''

    if 'username' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
                for x in xrange(32))
        login_session['state'] = state
        return False
    else:
        return True


@app.route('/', methods=['GET'])
@app.route('/catalog', methods=['GET'])
def CatalogHander():
    '''Show all categories and items
    http://localhost:8000/
    http://localhost:8000/ (logged in)'''

    catalog = getCatalog()
    catalogitems = GetLatestItems()
    IsUserLoggedIn()
    return render_template("catalog.html", catalogitems=catalogitems , \
        catalog=catalog, \
        session=login_session)

@app.route('/catalog/<string:catagoryname>/items', methods=['GET'])
def CatalogItemsHander(catagoryname):
    '''Show items in selected category
    http://localhost:8000/catalog/Snowboarding/items'''

    catalog = getCatalog()
    catalogitems = GetItemsByCat(catagoryname)
    IsUserLoggedIn()
    return render_template("catalogitems.html", \
        category=catagoryname, \
        catalog=catalog, \
        catalogitems=catalogitems, \
        session=login_session)

@app.route('/catalog/<string:catagoryname>/<int:itemid>', methods=['GET'])
def ShowItemHander(catagoryname, itemid):
    '''Show individual item in particular category - unlogged/logged users
    http://localhost:8000/catalog/Snowboarding/Snowboard'''

    catitem = GetItemById(itemid)
    print 'Item Id %s ' % itemid
    if catitem:
        return render_template("showitem.html", \
            catagoryname=catagoryname, \
            itemname=catitem.item_name, \
            itemid=catitem.item_id, \
            itemdesc=catitem.description)
    else:
        print "error getting catitem for id %s" % itemid
        redirect("/")


@app.route('/catalog/<int:itemid>/edit', methods=['GET', 'POST'])
def EditItemHandler(itemid):
    '''Edit individual item - logged users
    http://localhost:8000/catalog/Snowboard/edit (logged in)'''

    if not IsUserLoggedIn():
        return redirect('/catalog')
    else:
        print 'reached edit here..'
        if request.method == 'GET':
            catitem = GetItemById(itemid)
            if catitem:
                catalog = getCatalog()
                return render_template("edititem.html", \
                    catalog=catalog, catitem=catitem)
            else:
                #though it is not possible to reach here,
                # just in case handle it
                return redirect('/catalog')
        else:
            #for now redirect to root..
            item_name = request.form['ItemName']
            item_desc = request.form['ItemDesc']
            cat_id = request.form['ItemCat']
            EditItem(itemid, item_name, item_desc, cat_id)
            return redirect('/catalog')


@app.route('/catalog/Add', methods=['GET', 'POST'])
def AddItemHandler():
    '''Add new item
    http://localhost:8000/catalog/Snowboard/Add (logged in)'''
    if not IsUserLoggedIn():
        return redirect('/catalog')
    else:
        print 'reached here..'
        if request.method == 'GET':
            catalog = getCatalog()
            return render_template("additem.html", catalog=catalog)
        else:
            item_name = request.form['ItemName']
            item_desc = request.form['ItemDesc']
            cat_id = request.form['ItemCat']
            AddItem(item_name, item_desc, cat_id)
            return redirect('/catalog')


@app.route('/catalog/<int:itemid>/delete', methods=['POST'])
def DeleteItemHander(itemid):
    '''Delete a item  - logged users only
    http://localhost:8000/catalog/Snowboard/delete (logged in)'''

    print "Delete item %s" % itemid

    if not IsUserLoggedIn():
        return redirect('/catalog')
    else:
        if DeleteItem(itemid):
            print 'reached delete here..'
        else:
            print 'failed to delete item with id %s..' % itemid
    return redirect('/catalog')

@app.route('/catalog.json', methods=['GET'])
def GetCatalogItemJson():
    '''Catalog JSON - public
    http://localhost:8000/catalog.json'''

    items = GetCatalogItems()
    return jsonify(json_list=[i.serialize for i in items])


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''Google sigin metohd
    (Receive auth_code by HTTPS POST)'''

    #Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print 'failed to get state'
        return response
    # Obtain authorization code
    auth_code = request.data

    # If this request does not have `X-Requested-With` header, this could be a CSRF
    if not request.headers.get('X-Requested-With'):
        app.abort(403)

    # Set path to the Web application client_secret_*.json file you downloaded from the
    # Google API Console: https://console.developers.google.com/apis/credentials
    clientSecretFile = 'client_secret.json'

    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
        clientSecretFile,
        ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
        auth_code)

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['credentials'] = credentials

    # Get profile info from ID token
    login_session['userid'] = credentials.id_token['sub']
    login_session['email'] = credentials.id_token['email']
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']

    user = GetUserID(login_session['email'])
    if user is None:
        CreateUser(login_session)
    else:
        print user

    flash("you are now logged in as %s" % login_session['username'])
    print "signed in %s" % login_session['username']
    response = make_response(json.dumps("Logged in"), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/gdisconnect', methods=['GET'])
def gdisconnect():
    '''google signout
    (Receive auth_code by HTTPS POST)'''

    print 'staring to disconnect'
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("current user not connected"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print 'staring to disconnect'
    access_token = credentials.access_token
    print access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    httpreq = httplib2.Http()
    # result = httpreq.request(url, 'GET')[0]
    # print 'Google revoke access returned %s ' % result['status']
    result, response = httpreq.request(url, 'GET')
    print 'Google revoke access returned %s ' % result['status']
    print result
    print response

    print 'start delete of session values. '
    del login_session['credentials']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['userid']
    print 'Delete session values complete..'
    # irrespective of what hte status was, we'll remove the entries from our records
    if result['status'] == '200':
        print 'successfully disconnected'
        response = make_response(json.dumps('successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        print 'Disconnected! \n'
        return response
    else:
        print 'Failed to disconnect'
        response = make_response(json.dumps('Failed to disconnect'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'x+\xcd9.\xcf\xcb\xf1}\xeep\xc7\xb6\x05\x93\x96\xe3r\xc1\x97\x97\xd9\xdc'
    app.debug = True
    app.static_folder = 'static'
    print 'setting up Itemcatalog db'
    SetupDB()
    app.run(host='0.0.0.0', port=8080)



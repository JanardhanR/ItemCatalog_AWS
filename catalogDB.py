'''module for item catalog db handlers'''
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Catalog, Base, CatalogItem, User

db_session = None

def SetupDB():
    '''setup Item catalog db session'''

    engine = create_engine('postgresql+psycopg2://catalog:catalog@localhost/ItemCatalog.db')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    global db_session
    db_session = DBSession()
    if db_session:
        print "session created"


def getCatalog():
    '''Get List of all categories'''

    catalog = db_session.query(Catalog).all()
    return catalog

def GetLatestItems():
    '''Get latest items, so makes sense to show
    same number of items to make it look good.'''

    count = db_session.query(Catalog).count()
    catitems = db_session.query(CatalogItem) \
                .order_by(CatalogItem.last_updated.desc()) \
                .limit(count)
    return catitems

def GetCatalogItems():
    '''Get all CatalogItems'''

    catalogitems = db_session.query(CatalogItem).all()
    return catalogitems

def AddItem(item_name, item_desc, cat_id):
    '''Add new CatalogItem'''

    catitem = CatalogItem()
    catitem.item_name = item_name
    catitem.description = item_desc
    catitem.cat_id = cat_id
    catitem.user_id = login_session['userid']
    db_session.add(catitem)
    db_session.commit()

def GetItemsByCat(cat_name):
    '''Get items by cateogory'''

    catitems = db_session.query(CatalogItem). \
    join(CatalogItem.catalog). \
    filter(Catalog.cat_name == cat_name)
    return catitems

def GetItemById(item_id):
    '''Get Item By Item Id'''

    catitem = db_session.query(CatalogItem). \
    filter(CatalogItem.item_id == item_id).one()
    return catitem

def CreateUser(login_session_arg):
    '''Create  new User'''

    newUser = User(name=login_session_arg['username'], \
                   email=login_session_arg['email'], \
                   picture=login_session_arg['picture'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User) \
           .filter_by(email=login_session_arg['email']).one()
    return user.id

def EditItem(item_id, item_name, item_desc, cat_id):
    '''Edit a catalog item'''

    try:
        catitem = GetItemById(item_id)
        catitem.item_name = item_name
        catitem.description = item_desc
        catitem.cat_id = cat_id
        db_session.commit()
    except:
        return False
    return True

def DeleteItem(item_id):
    '''Delete a catalog item'''

    try:
        catitem = GetItemById(item_id)
        db_session.delete(catitem)
        db_session.commit()
    except:
        return False
    return True


def GetUserID(email):
    '''get user Id from email id'''

    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

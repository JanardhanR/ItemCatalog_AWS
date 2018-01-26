from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, CatalogItem, User

engine = create_engine('postgresql://catalog:catalog@localhost:5432/ItemCatalog.db')
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
session = DBSession()

session.query(User).delete()
session.query(Catalog).delete()
session.query(CatalogItem).delete()
session.commit()

user1 = User(name="Janardhan", email="jana.dhana@gmail.com")
session.add(user1)
session.commit()

cat1 = Catalog(cat_name="Soccer",user_id=user1.id)
session.add(cat1)
session.commit()

cat2 = Catalog(cat_name="Tennis",user_id=user1.id)
session.add(cat2)
session.commit()

cat3 = Catalog(cat_name="Badminton",user_id=user1.id)
session.add(cat3)
session.commit()

cat4 = Catalog(cat_name="Cycling",user_id=user1.id)
session.add(cat4)
session.commit()

catalogitem = CatalogItem(item_name="Football", \
                          description="Football for small kids and professional players", \
                          cat_id=cat1.cat_id, user_id=user1.id)

catalogitem1 = CatalogItem(item_name="Shoes", \
                          description="Football shoes", \
                          cat_id=cat1.cat_id, user_id=user1.id)
catalogitem2 = CatalogItem(item_name="Glows", \
                          description="Football Glows", \
                          cat_id=cat1.cat_id, user_id=user1.id)
catalogitem3 = CatalogItem(item_name="Socks", \
                          description="Football Socks", \
                          cat_id=cat1.cat_id, user_id=user1.id)

session.add(catalogitem)
session.add(catalogitem1)
session.add(catalogitem2)
session.add(catalogitem3)

catalogitem4 = CatalogItem(item_name="Racket", \
                          description="Tennis Racket", \
                          cat_id=cat2.cat_id, user_id=user1.id)

catalogitem5 = CatalogItem(item_name="Shoes", \
                          description="Tennis shoes", \
                          cat_id=cat2.cat_id, user_id=user1.id)
catalogitem6 = CatalogItem(item_name="Ball", \
                          description="Tennis Glows", \
                          cat_id=cat2.cat_id, user_id=user1.id)
catalogitem7 = CatalogItem(item_name="Socks", \
                          description="Tennis Socks", \
                          cat_id=cat2.cat_id, user_id=user1.id)

session.add(catalogitem4)
session.add(catalogitem5)
session.add(catalogitem6)
session.add(catalogitem7)

catalogitem8 = CatalogItem(item_name="Cycle", \
                          description="Cycle for kids and professions", \
                          cat_id=cat4.cat_id, user_id=user1.id)

catalogitem9 = CatalogItem(item_name="Cycling Shoes", \
                          description="Cycling shoes", \
                          cat_id=cat4.cat_id, user_id=user1.id)
session.add(catalogitem8)
session.add(catalogitem9)
session.commit()

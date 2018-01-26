import sys
import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy  import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=True)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id':self.id,
            'email':self.email,
            'picture':self.picture
        }


class Catalog(Base):
    __tablename__ = 'catalog'

    cat_id = Column(Integer, primary_key=True)
    cat_name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    @property
    def serialize(self):
        return {
            'cat_name': self.cat_name,
            'cat_id':self.cat_id,
            'user_id':self.user_id
        }


class CatalogItem(Base):
    __tablename__ = 'cat_item'

    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(80), nullable=False)
    description = Column(String(250))
    catalog = relationship(Catalog)
    cat_id = Column(Integer, ForeignKey('catalog.cat_id'))
    user = relationship(User)
    user_id = Column(Integer, ForeignKey('user.id'))
    last_updated = Column(DateTime, nullable=False, \
                          default=datetime.datetime.now, \
                          onupdate=datetime.datetime.now)

    @property
    def serialize(self):
        return {
            'item_id':self.item_id,
            'item_name': self.item_name,
            'description':self.description,
            'cat_id':self.cat_id,
            'user_id':self.user_id
        }

engine = create_engine(
    'postgresql://catalog:catalog@localhost:5432/ItemCatalog.db'
)
Base.metadata.create_all(engine)

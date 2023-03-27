from __future__ import annotations
from sqlalchemy import create_engine, DateTime, func, Boolean, Float, PickleType, desc
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref, Query, Mapped, mapped_column, \
    DeclarativeBase
from typing import List
from sqlalchemy import or_, and_
import psycopg2

Base = declarative_base()


class Product(Base):
    __tablename__ = 'product_table'
    id = mapped_column(Integer, primary_key=True)
    children = relationship("Attribute", back_populates="parent")
    category = Column(String)
    name = Column(String)
    photo = Column(String)
    description = Column(String)
    price = Column(String)

    def __init__(self, category, name, photo, description, price):
        self.category = category
        self.name = name
        self.photo = photo
        self.description = description
        self.price = price


class Attribute(Base):
    __tablename__ = 'place_attribute'
    id = mapped_column(Integer, primary_key=True)
    product_id = mapped_column(ForeignKey("product_table.id"))
    parent = relationship("Product", back_populates="children")
    name = Column(String)
    value_type = Column(String)
    value = Column(String)
    value_description = Column(String)

    def __init__(self, product_id, name, value_type, value, value_description):
        self.product_id = product_id
        self.name = name
        self.value_type = value_type
        self.value = value
        self.value_description = value_description


class User(Base):
    __tablename__ = 'user_table'
    id = mapped_column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class Rate(Base):
    __tablename__ = 'rate_table'
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey("user_table.id"))
    product_id = mapped_column(ForeignKey("product_table.id"))
    rate = Column(Integer)

    def __init__(self, user_id, product_id, rate):
        self.user_id = user_id
        self.product_id = product_id
        self.rate = rate


class ObjectHandler(object):

    def __init__(self):
        self.meta = MetaData()
        self.engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/recomapi')
        Base.metadata.create_all(self.engine)

    def add_product(self, category, name, photo, description, price):
        session = sessionmaker(bind=self.engine)()
        prod = Product(category, name, photo, description, price)
        p_id = prod.id
        session.add(prod)
        session.commit()
        session.close()
        return p_id

    def add_attribute(self, product_id, name, value_type, value, value_description):
        session = sessionmaker(bind=self.engine)()
        attribute = Attribute(product_id, name, value_type, value, value_description)
        session.add(attribute)
        session.commit()
        session.close()


if __name__ == "__main__":
    q = ObjectHandler()

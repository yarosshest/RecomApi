from __future__ import annotations
from sqlalchemy import create_engine, DateTime, func, Boolean, Float, PickleType, desc
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref, Query, Mapped, mapped_column, \
    DeclarativeBase
from typing import List
from sqlalchemy import or_, and_
import psycopg2
from tqdm import tqdm

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


class Distance(Base):
    __tablename__ = 'distance_table'
    id = mapped_column(Integer, primary_key=True)
    product_f_id = mapped_column(ForeignKey("product_table.id"))
    product_s_id = mapped_column(ForeignKey("product_table.id"))
    distance = Column(Float)

    def __init__(self, product_f_id, product_s_id, distance):
        self.product_f_id = product_f_id
        self.product_s_id = product_s_id
        self.distance = distance


class Attribute(Base):
    __tablename__ = 'attribute_table'
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


def Session(fun):
    def wrapper(self, *args):
        session = sessionmaker(bind=self.engine)()
        result = fun(self, session, *args)
        session.close()
        return result

    return wrapper


class ObjectHandler(object):

    def __init__(self):
        self.meta = MetaData()
        self.engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/recomapi')
        Base.metadata.create_all(self.engine)

    @Session
    def add_product(self, session, category, name, photo, description, price):
        prod = Product(category, name, photo, description, price)
        session.add(prod)
        session.commit()
        p_id = prod.id
        return p_id

    @Session
    def add_attribute(self, session, product_id, name, value_type, value, value_description):
        attribute = Attribute(product_id, name, value_type, value, value_description)
        session.add(attribute)
        session.commit()

    @Session
    def add_distance(self, session, product_f_id, product_s_id, distance):
        # dist = session.query(Distance).filter(or_(
        #     and_(Distance.product_f_id == product_f_id, Distance.product_s_id == product_s_id),
        #     and_(Distance.product_s_id == product_f_id, Distance.product_f_id == product_s_id))).first()
        # if dist is not None:
        #     session.delete(dist)
        #     session.commit()

        dist = Distance(product_f_id, product_s_id, distance)
        session.add(dist)
        session.commit()

    @Session
    def add_some_distances(self, session, distances):
        for i in distances:
            dist = Distance(i[0], i[1], i[2])
            session.add(dist)
        session.commit()

    @Session
    def get_all_description(self, session):
        products = session.query(Product).all()
        res = []
        for prod in products:
            if prod.description != '':
                res.append([prod.id, prod.description])
        return res


if __name__ == "__main__":
    q = ObjectHandler()

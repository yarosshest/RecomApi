from __future__ import annotations
from sqlalchemy import ForeignKey, PickleType
from sqlalchemy import Column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List

BDCONNECTION = "postgresql+asyncpg://postgres:postgres@localhost:5432/recomapi_as"


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = 'product_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    distance: Mapped[List[Distance]] = relationship()
    attribute: Mapped[List[Attribute]] = relationship()
    vector: Mapped[Vector] = relationship(back_populates="product")
    lemma: Mapped[Lemma] = relationship(back_populates="product")
    rates: Mapped[List[Rate]] = relationship(back_populates="product")
    name: Mapped[str]
    photo: Mapped[str]
    description: Mapped[str]

    def __init__(self, name, photo, description):
        self.name = name
        self.photo = photo
        self.description = description


class Distance(Base):
    __tablename__ = 'distance_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_f_id: Mapped[int] = mapped_column(ForeignKey("product_table.id"))
    product_s_id: Mapped[int]
    distance: Mapped[float]

    def __init__(self, product_f_id, product_s_id, distance):
        self.product_f_id = product_f_id
        self.product_s_id = product_s_id
        self.distance = distance


class Vector(Base):
    __tablename__ = 'vector_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product_table.id"))
    product: Mapped[Product] = relationship(back_populates="vector")
    vector = Column(PickleType)

    def __init__(self, product_id, vector):
        self.product_id = product_id
        self.vector = vector


class Lemma(Base):
    __tablename__ = 'lemma_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product_table.id"))
    product: Mapped[Product] = relationship(back_populates="lemma")
    lemma: Mapped[str]

    def __init__(self, product_id, lemma):
        self.product_id = product_id
        self.lemma = lemma


class Attribute(Base):
    __tablename__ = 'attribute_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product_table.id"))
    name: Mapped[str]
    value_type: Mapped[str] = mapped_column(nullable=True)
    value: Mapped[str]
    value_description: Mapped[str] = mapped_column(nullable=True)

    def __init__(self, product_id, name, value_type, value, value_description):
        self.product_id = product_id
        self.name = name
        self.value_type = value_type
        self.value = value
        self.value_description = value_description


class User(Base):
    __tablename__ = 'user_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    rates: Mapped[List[Rate]] = relationship(back_populates="user")
    name: Mapped[str]
    password: Mapped[str]

    def __init__(self, name, password):
        self.name = name
        self.password = password


class Rate(Base):
    __tablename__ = "rate_table"
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product_table.id"), primary_key=True)
    rate: Mapped[bool]
    product: Mapped[Product] = relationship(back_populates="rates")
    user: Mapped[User] = relationship(back_populates="rates")

    def __init__(self, user_id, product_id, rate):
        self.user_id = user_id
        self.product_id = product_id
        self.rate = rate


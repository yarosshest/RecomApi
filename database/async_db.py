from __future__ import annotations
import tracemalloc
import asyncio
import datetime
import time
import pickle

import numpy as np
from typing import List

from sqlalchemy import ForeignKey, or_, and_, NullPool, PickleType
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload
from tqdm import tqdm


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = 'product_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    distance: Mapped[List[Distance]] = relationship()
    attribute: Mapped[List[Attribute]] = relationship()
    vector: Mapped[Vector] = relationship(back_populates="product")
    rates: Mapped[List[Rate]] = relationship(back_populates="product")
    category: Mapped[str]
    name: Mapped[str]
    photo: Mapped[str]
    description: Mapped[str]
    price: Mapped[str]

    def __init__(self, category, name, photo, description, price):
        self.category = category
        self.name = name
        self.photo = photo
        self.description = description
        self.price = price


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


class Attribute(Base):
    __tablename__ = 'attribute_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product_table.id"))
    name: Mapped[str]
    value_type: Mapped[str]
    value: Mapped[str]
    value_description: Mapped[str]

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
    right_id: Mapped[int] = mapped_column(ForeignKey("product_table.id"), primary_key=True)
    rate: Mapped[bool]
    product: Mapped[Product] = relationship(back_populates="rates")
    user: Mapped[User] = relationship(back_populates="rates")

    def __init__(self, user_id, product_id, rate):
        self.user_id = user_id
        self.product_id = product_id
        self.rate = rate


def async_to_tread(fun):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(fun(*args, **kwargs))
        loop.close()

    return wrapper


def Session(fun):
    async def wrapper(self, *args):
        engine = create_async_engine(
            "postgresql+asyncpg://postgres:postgres@localhost:5433/recomapi_as",
            echo=False,
            poolclass=NullPool,
        )
        async with async_sessionmaker(engine, expire_on_commit=True)() as session:
            async with session.begin():
                result = await fun(self, session, *args)
                await session.commit()
        return result

    return wrapper

class asyncHandler:
    # def __init__(self):
    #     self.engine = create_async_engine(
    #         "postgresql+asyncpg://postgres:postgres@localhost:5433/recomapi_as",
    #         echo=False,
    #         poolclass=NullPool,
    #     )
    #     self.async_sessionmaker = async_sessionmaker(self.engine, expire_on_commit=True)

    async def init_db(self):
        engine = create_async_engine(
            "postgresql+asyncpg://postgres:postgres@localhost:5433/recomapi_as",
            echo=False,
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()

    @Session
    async def add_product(self, session, product, attributes) -> None:
        prod = Product(product[0], product[1], product[2], product[3], product[4])
        session.add(prod)
        await session.flush()
        p_id = prod.id
        for i in attributes:
            attribute = Attribute(p_id, i[0], i[1], i[2], i[3])
            session.add(attribute)

    @Session
    async def add_some_products(self, session, products) -> None:
        for i in tqdm(products):
            prod = Product(i[0][0], i[0][1], i[0][2], i[0][3], i[0][4])
            session.add(prod)
            await session.flush()
            p_id = prod.id
            for j in i[1]:
                attribute = Attribute(p_id, j[0], j[1], j[2], j[3])
                session.add(attribute)

    @Session
    async def add_attribute(self, session, product_id, name, value_type, value, value_description) -> None:
        attribute = Attribute(product_id, name, value_type, value, value_description)
        session.add(attribute)

    @Session
    async def add_distance(self, session, product_f_id, product_s_id, distance) -> None:
        dist = Distance(product_f_id, product_s_id, distance)
        session.add(dist)

    @Session
    async def add_some_distances(self, session, distances):
        for i in distances:
            dist = Distance(i[0], i[1], i[2])
            session.add(dist)

    @Session
    async def get_all_vectors(self, session):
        result = await session.execute(select(Product))
        vectors = result.scalars().all()
        res = []

        for i in vectors:
            res.append(pickle.loads(i.vector))

        return res

    @Session
    async def add_some_vectors(self, session, vectors):
        for i in vectors:
            vector = Vector(i[0], pickle.dumps(i[1]))
            session.add(vector)

    @Session
    async def get_all_description(self, session) -> list:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        res = []
        for prod in tqdm(products):
            if prod.description != '':
                res.append([prod.id, prod.description])
        return res

    @Session
    async def add_user(self, session, name, password):
        user = User(name, password)
        session.add(user)

    @Session
    async def rate_product(self, session, user_id, product_id, rate):
        rate = Rate(user_id, product_id, rate)
        session.add(rate)

    @Session
    async def get_nearest_for_user_by_median(self, session, user_id) -> int:


        q = session.query(Vector, Product, User, Rate).filter(Rate.user.id == user_id).filter(Rate.rate == True).all()
        query_vectors = await session.execute(q)
        vectors_t = []
        for i in query_vectors:
            vectors_t.append(pickle.loads(i.vector))

        q = session.query(Vector, Product, User, Rate).filter(Rate.user.id == user_id).filter(Rate.rate == False).all()
        query_vectors = await session.execute(q)
        vectors_f = []


        for i in query_vectors:
            vectors_f.append(pickle.loads(i.vector))

        vectors_t = np.array(vectors_t)
        vectors_f = np.array(vectors_f)

        vectors = np.array(await self.get_all_vectors())

        median_t = np.median(vectors_t, axis=0)
        dist_t = np.inner(median_t, vectors[1])

        median_f = np.median(vectors_f, axis=0)
        dist_f = np.inner(median_f, vectors[1])

        dist = vectors_t - vectors_f
        id = vectors[np.argmax(dist)]
        return id


if __name__ == "__main__":
    tracemalloc.start()
    a = asyncHandler()
    asyncio.run(a.init_db())

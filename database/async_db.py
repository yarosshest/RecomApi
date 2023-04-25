from __future__ import annotations
import tracemalloc
import asyncio
import datetime
import time
import pickle

import numpy as np
from numpy import dot, median
from numpy.linalg import norm
from typing import List, Any

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
from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from tqdm import tqdm

from random import choice

BDCONNECTION = "postgresql+asyncpg://postgres:postgres@localhost:5432/recomapi_as"


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = 'product_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    distance: Mapped[List[Distance]] = relationship()
    attribute: Mapped[List[Attribute]] = relationship()
    vector: Mapped[Vector] = relationship(back_populates="product")
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
            BDCONNECTION,
            echo=False,
            poolclass=NullPool,
        )
        async with async_sessionmaker(engine, expire_on_commit=True)() as session:
            async with session.begin():
                result = await fun(self, session, *args)
                await session.commit()
        return result

    return wrapper


async def calculate_median_distance(vect_f, vect_s: np.array) -> np.array:
    median = np.median(vect_f, axis=0)
    dist = np.inner(median, vect_s)
    return dist


def cos_sim(a, b):
    return dot(a, b) / (norm(a) * norm(b))


class asyncHandler:
    async def init_db(self):
        engine = create_async_engine(
            BDCONNECTION,
            echo=False,
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()

    @Session
    async def add_product(self, session, product, attributes) -> None:
        prod = Product(product[0], product[1], product[2])
        session.add(prod)
        await session.flush()
        p_id = prod.id
        for i in attributes:
            attribute = Attribute(p_id, i[0], None, str(i[1]), None)
            session.add(attribute)

    @Session
    async def add_some_products(self, session, products) -> None:
        print("adding products in db")
        for i in tqdm(products):
            prod = Product(i[0][0], i[0][1], i[0][2])
            session.add(prod)
            await session.flush()
            for j in i[1]:
                attribute = Attribute(prod.id, j[0], None, str(j[1]), None)
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
        result = await session.execute(select(Vector))
        vectors = result.scalars().all()
        res = [[], []]

        for i in vectors:
            res[0].append(i.id)
            res[1].append(pickle.loads(i.vector))

        return res

    @Session
    async def get_vectors_without(self, session, ids):
        result = await session.execute(select(Vector))
        vectors = result.scalars().all()
        res = [[], []]

        for i in vectors:
            if i.id not in ids:
                res[0].append(i.id)
                res[1].append(pickle.loads(i.vector))

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
        result = await session.execute(select(User).filter(User.name == name))
        result = result.scalars().all()
        if result:
            return False
        else:
            user = User(name, password)
            session.add(user)
            return True

    @Session
    async def get_user(self, session, name, password):
        result = await session.execute(select(User).filter(User.name == name))
        result = result.scalars().all()
        if result:
            if result[0].password == password:
                return result[0].__dict__
            else:
                return False
        else:
            return False

    @Session
    async def rate_product(self, session, user_id: int, product_id: int, u_rate: bool):
        rates = await session.execute(select(Rate).filter(and_(Rate.user_id == user_id, Rate.product_id == product_id)))
        rates = rates.scalars().all()
        if rates:
            return False
        else:
            rate = Rate(user_id, product_id, u_rate)
            session.add(rate)

    @Session
    async def get_user_vectors(self, session, user_id: int, rtype: bool, rated: list) -> list:
        q = select(Vector, Rate).filter(and_(Rate.user_id == user_id, Vector.product_id == Rate.product_id)
                                        ).filter(Rate.rate == rtype)
        query_vectors = await session.execute(q)
        query_vectors = query_vectors.scalars().all()
        vectors = []
        for i in query_vectors:
            rated.append(i.product_id)
            vectors.append(pickle.loads(i.vector))

        return vectors

    async def get_nearest_for_user_by_median(self, user_id) -> list:
        rated = []

        vectors_t = np.array(await self.get_user_vectors(user_id, True, rated))

        vectors_f = np.array(await self.get_user_vectors(user_id, False, rated))

        vectors = await self.get_vectors_without(rated)
        vectors_id = vectors[0]
        vectors_all = np.array(vectors[1])

        dist_f = None
        if vectors_f:
            dist_f = calculate_median_distance(vectors_f, vectors_all)

        dist_t = calculate_median_distance(vectors_t, vectors_all)

        if dist_f is None:
            dist = dist_t
        else:
            dist = dist_t - dist_f

        films = np.argsort(dist)
        ids = [vectors_id[i] for i in films[:5]]
        return ids

    async def get_nearest_for_user_by_cos_sim(self, user_id) -> list:
        rated = []

        vector_t = median(np.array(await self.get_user_vectors(user_id, True, rated)), axis=0)

        vector_f = median(np.array(await self.get_user_vectors(user_id, False, rated)), axis=0)

        vectors = await self.get_vectors_without(rated)
        vectors_id = vectors[0]
        vectors_all = np.array(vectors[1])

        dist_f = None
        if np.isfinite(vector_f):
            dist_f = [cos_sim(vector_f, i) for i in vectors_all]

        dist_t = [cos_sim(vector_t, i) for i in vectors_all]

        if dist_f is None:
            dist = dist_t
        else:
            dist = [dist_t[i] - dist_f[i] for i in range(vectors_all.shape[0])]

        dist = np.array(dist)

        films = np.argsort(dist)
        ids = [vectors_id[i] for i in films[-5:]][::-1]

        return ids

    @Session
    async def get_random_product(self, session) -> Product:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        res = choice(products).__dict__
        return res

    @Session
    async def get_product_by_req(self, session, param):
        result = await session.execute(select(Product))
        products = result.scalars().all()
        res = []
        for i in products:
            if param in i.name:
                res.append(i)
        if len(res) == 0:
            return None
        else:
            res = [i.__dict__ for i in res]
            return res

    @Session
    async def get_product_by_id(self, session, product_id: int) -> dict | None:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
        if product is None:
            return None
        else:
            return product.__dict__

    async def get_recommendation(self, user_id: int):
        ids = await self.get_nearest_for_user_by_cos_sim(user_id)
        ret = []
        for i in ids:
            ret.append(await self.get_product_by_id(i))
        return ret


if __name__ == "__main__":
    tracemalloc.start()
    a = asyncHandler()
    asyncio.run(a.init_db())

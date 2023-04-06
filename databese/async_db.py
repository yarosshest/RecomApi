from __future__ import annotations
import tracemalloc
import asyncio
import datetime
import time
from typing import List

from sqlalchemy import ForeignKey, or_, and_, NullPool
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
    rate: Mapped[List[Rate]] = relationship()
    name: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class Rate(Base):
    __tablename__ = "rate_table"
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey("product_table.id"), primary_key=True)
    rate: Mapped[str]
    child: Mapped["Product"] = relationship()

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
            "postgresql+asyncpg://postgres:postgres@localhost:5432/recomapi_as",
            echo=False,
        )
        async with async_sessionmaker(engine, expire_on_commit=True)() as session:
            async with session.begin():
                result = await fun(self, session, *args)
                await session.commit()
                await engine.dispose()
        return result

    return wrapper


class asyncHandler:
    # def __init__(self):
    #     self.engine = create_async_engine(
    #         "postgresql+asyncpg://postgres:postgres@localhost:5432/recomapi_as",
    #         echo=False,
    #     )
    #     self.async_sessionmaker = async_sessionmaker(self.engine, expire_on_commit=True)

    async def init_db(self):
        engine = create_async_engine(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/recomapi_as",
            echo=False,
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
    async def get_all_description(self, session) -> list:
        result = await session.execute(select(Product))
        products = result.all()
        res = []
        for prod in products:
            if prod.description != '':
                res.append([prod.id, prod.description])
        return res


if __name__ == "__main__":
    tracemalloc.start()
    a = asyncHandler()
    asyncio.run(a.init_db())

from __future__ import annotations
import tracemalloc
import asyncio
import pickle

from sqlalchemy import ForeignKey, or_, and_, NullPool, PickleType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import and_
from tqdm import tqdm

from random import choice

from database.recomindation_alg import get_nearest_for_user_by_cos_sim
from database.Db_objects import Product, Attribute, Distance, Base, BDCONNECTION, Vector, Rate, User


def async_to_tread(fun):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(fun(*args, **kwargs))
        loop.close()

    return wrapper


def Session(fun):
    async def wrapper(*args):
        engine = create_async_engine(
            BDCONNECTION,
            echo=False,
            poolclass=NullPool,
        )
        async with async_sessionmaker(engine, expire_on_commit=True)() as session:
            async with session.begin():
                result = await fun(session, *args)
                await session.commit()
        return result

    return wrapper


class asyncHandler:
    @staticmethod
    async def init_db():
        engine = create_async_engine(
            BDCONNECTION,
            echo=False,
            poolclass=NullPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()

    @staticmethod
    @Session
    async def add_product(session, product, attributes) -> None:
        prod = Product(product[0], product[1], product[2])
        session.add(prod)
        await session.flush()
        p_id = prod.id
        for i in attributes:
            attribute = Attribute(p_id, i[0], None, str(i[1]), None)
            session.add(attribute)

    @staticmethod
    @Session
    async def add_some_products(session, products) -> None:
        print("adding products in db")
        for i in tqdm(products):
            prod = Product(i[0][0], i[0][1], i[0][2])
            session.add(prod)
            await session.flush()
            for j in i[1]:
                attribute = Attribute(prod.id, j[0], None, str(j[1]), None)
                session.add(attribute)

    @staticmethod
    @Session
    async def add_attribute(session, product_id, name, value_type, value, value_description) -> None:
        attribute = Attribute(product_id, name, value_type, value, value_description)
        session.add(attribute)

    @staticmethod
    @Session
    async def add_distance(session, product_f_id, product_s_id, distance) -> None:
        dist = Distance(product_f_id, product_s_id, distance)
        session.add(dist)

    @staticmethod
    @Session
    async def add_some_distances(session, distances):
        for i in distances:
            dist = Distance(i[0], i[1], i[2])
            session.add(dist)

    @staticmethod
    @Session
    async def get_all_vectors(session):
        result = await session.execute(select(Vector))
        vectors = result.scalars().all()
        res = [[], []]

        for i in vectors:
            res[0].append(i.id)
            res[1].append(pickle.loads(i.vector))

        return res

    @staticmethod
    @Session
    async def get_vectors_without(session, ids):
        result = await session.execute(select(Vector))
        vectors = result.scalars().all()
        res = [[], []]

        for i in vectors:
            if i.id not in ids:
                res[0].append(i.id)
                res[1].append(pickle.loads(i.vector))

        return res

    @staticmethod
    @Session
    async def add_some_vectors(session, vectors):
        for i in vectors:
            vector = Vector(i[0], pickle.dumps(i[1]))
            session.add(vector)

    @staticmethod
    @Session
    async def get_all_description(session) -> list:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        res = []
        for prod in tqdm(products):
            if prod.description != '':
                res.append([prod.id, prod.description])
        return res

    @staticmethod
    @Session
    async def add_user(session, name, password) -> bool | int:
        result = await session.execute(select(User).filter(User.name == name))
        result = result.scalars().all()
        if result:
            return False
        else:
            user = User(name, password)
            session.add(user)
            await session.flush()
            return user.id

    @staticmethod
    @Session
    async def get_user(session, name, password) -> bool | dict:
        result = await session.execute(select(User).filter(User.name == name))
        result = result.scalars().all()
        if result:
            if result[0].password == password:
                return result[0].__dict__
            else:
                return False
        else:
            return False

    @staticmethod
    @Session
    async def rate_product(session, user_id: int, product_id: int, u_rate: bool):
        rates = await session.execute(select(Rate).filter(and_(Rate.user_id == user_id, Rate.product_id == product_id)))
        rates = rates.scalars().all()
        if rates:
            return False
        else:
            rate = Rate(user_id, product_id, u_rate)
            session.add(rate)

    @staticmethod
    @Session
    async def get_user_vectors(session, user_id: int, rtype: bool, rated: list) -> list:
        q = select(Vector, Rate).filter(and_(Rate.user_id == user_id, Vector.product_id == Rate.product_id)
                                        ).filter(Rate.rate == rtype)
        query_vectors = await session.execute(q)
        query_vectors = query_vectors.scalars().all()
        vectors = []
        for i in query_vectors:
            rated.append(i.product_id)
            vectors.append(pickle.loads(i.vector))

        return vectors

    @staticmethod
    @Session
    async def get_random_product(session) -> Product:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        res = choice(products).__dict__
        return res

    @staticmethod
    @Session
    async def get_product_by_req(session, param) -> list[dict] | None:
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

    @staticmethod
    @Session
    async def get_product_by_id(session, product_id: int) -> dict | None:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
        if product is None:
            return None
        else:
            return product.__dict__

    @staticmethod
    async def get_recommendation(user_id: int):
        rated = []

        vector_t = await asyncHandler.get_user_vectors(user_id, True, rated)
        vector_f = await asyncHandler.get_user_vectors(user_id, False, rated)
        clear_vectors = await asyncHandler.get_vectors_without(rated)

        ids = await get_nearest_for_user_by_cos_sim(clear_vectors, vector_t, vector_f)
        ret = []
        for i in ids:
            ret.append(await asyncHandler.get_product_by_id(i))
        return ret


if __name__ == "__main__":
    tracemalloc.start()
    asyncio.run(asyncHandler.init_db())

from __future__ import annotations
import tracemalloc
import asyncio
import pickle

import numpy as np
import pandas as pd
from sqlalchemy import ForeignKey, or_, and_, NullPool, PickleType, delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import and_
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from tqdm import tqdm

from random import choice
from sklearn.preprocessing import MultiLabelBinarizer

from database.recomindation_alg import get_cat_recommed
from database.Db_objects import Product, Attribute, Distance, Base, Vector, Rate, User, Lemma

import database.config as config


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
            config.bd_connection,
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
    async def init_db() -> None:
        engine = create_async_engine(
            config.bd_connection,
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
    async def add_some_lemma(session, lemmas):
        for i in lemmas:
            dist = Lemma(i[0], i[1])
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
    async def get_all_short_description(session) -> list:
        q = select(Product). \
            join(Attribute,
                 and_(Attribute.product_id == Product.id, Attribute.name == "short_desription")). \
            options(contains_eager(Product.attribute))

        result = await session.execute(q)

        products = result.scalars().unique().all()
        res = []
        for prod in tqdm(products):
            res.append([prod.id, prod.attribute[0].value])
        return res

    @staticmethod
    @Session
    async def get_gen_enc(session) -> MultiLabelBinarizer:
        q_genres = select(Attribute).filter(Attribute.name == 'genres').distinct()
        genres = await session.execute(q_genres)
        gen = genres.scalars().all()

        enc = MultiLabelBinarizer()
        g = []
        for i in gen:
            g.append(i.value.split(' '))

        enc.fit(g)
        return enc

    @staticmethod
    @Session
    async def get_cat_data_by_id(session, p_id) -> list:
        enc = await asyncHandler.get_gen_enc()

        q = select(Product).filter(Product.id == p_id). \
            join(Attribute, Attribute.product_id == Product.id). \
            join(Vector, Vector.id == Product.id). \
            options(contains_eager(Product.attribute), contains_eager(Product.vector))

        result = await session.execute(q)

        prod = result.scalars().unique().first()
        select_attr = ['rating_imdb', 'rating_imdb_vote_count', 'rating_film_critics', 'rating_kinopoisk',
                       'rating_kinopoisk_vote_count', 'year', 'rating_age_limit', 'film_length']

        atrebutes = []
        for attr in prod.attribute:
            if attr.name in select_attr:
                if attr.value != 'None':
                    atrebutes.append(attr.value)
                else:
                    atrebutes.append(0)
            if attr.name == 'genres':
                gen = enc.transform([attr.value.split(' ')])[0]
                atrebutes.append(np.array(gen))
        res = [pickle.loads(prod.vector.vector)]
        res += atrebutes
        return res

    @staticmethod
    @Session
    async def get_all_cat_data(session) -> dict:
        enc = await asyncHandler.get_gen_enc()

        otv = {}
        q = select(Product). \
            join(Attribute, Attribute.product_id == Product.id). \
            join(Vector, Vector.id == Product.id). \
            options(contains_eager(Product.attribute), contains_eager(Product.vector))

        result = await session.execute(q)

        prod = result.scalars().unique().all()
        select_attr = ['rating_imdb', 'rating_imdb_vote_count', 'rating_film_critics', 'rating_kinopoisk',
                       'rating_kinopoisk_vote_count', 'year', 'rating_age_limit', 'film_length']

        for p in tqdm(prod):
            atrebutes = ["0.0", "0", "0.0", "0.0", "0", "0", "0", "0"]
            for attr in p.attribute:
                if attr.name in select_attr and attr.value != 'None':
                    atrebutes[select_attr.index(attr.name)] = attr.value
                if attr.name == 'genres':
                    gen = enc.transform([attr.value.split(' ')])[0]
                    atrebutes.append(np.array(gen))
            res = [pickle.loads(p.vector.vector)]
            res += atrebutes
            otv.update({p.id: res})
        return otv

    @staticmethod
    @Session
    async def get_cat_data_by_list_id(session, p_ids) -> list:
        enc = await asyncHandler.get_gen_enc()
        otv = []
        for p_id in p_ids:
            q = select(Product).filter(Product.id == p_id). \
                join(Attribute, Attribute.product_id == Product.id). \
                join(Vector, Vector.id == Product.id). \
                options(contains_eager(Product.attribute), contains_eager(Product.vector))

            result = await session.execute(q)

            prod = result.scalars().unique().first()
            select_attr = ['rating_imdb', 'rating_imdb_vote_count', 'rating_film_critics', 'rating_kinopoisk',
                           'rating_kinopoisk_vote_count', 'year', 'rating_age_limits', 'film_length']

            atrebutes = ["0.0", "0", "0.0", "0.0", "0", "0", "0", "0"]
            for attr in prod.attribute:
                if attr.name in select_attr and attr.value != 'None':
                    atrebutes[select_attr.index(attr.name)] = attr.value
                if attr.name == 'genres':
                    gen = enc.transform([attr.value.split(' ')])[0]
                    atrebutes.append(np.array(gen))
            res = [pickle.loads(prod.vector.vector)]
            res += atrebutes
            otv.append(res)
        return otv

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
    async def get_vector_by_p_id(session, p_id) -> bool | list:
        result = await session.execute(select(Vector).filter(Vector.product_id == p_id))
        result = result.scalars().first()
        if result:
            return pickle.loads(result.vector)
        else:
            return False

    @staticmethod
    @Session
    async def get_lemma_by_p_id(session, p_id) -> bool | list:
        result = await session.execute(select(Lemma).filter(Lemma.product_id == p_id))
        result = result.scalars().first()
        if result:
            return result.lemma
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
    async def get_user_rate_id(session, user_id: int, rtype: bool) -> list:
        q = select(Rate).filter(and_(Rate.user_id == user_id, Rate.rate == rtype))
        query_vectors = await session.execute(q)
        query_vectors = query_vectors.scalars().all()
        ids = []
        for i in query_vectors:
            ids.append(i.product_id)

        return ids

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

    # @staticmethod
    # async def get_recommendation(user_id: int):
    #     rated = []
    #
    #     vector_t = await asyncHandler.get_user_vectors(user_id, True, rated)
    #     vector_f = await asyncHandler.get_user_vectors(user_id, False, rated)
    #     clear_vectors = await asyncHandler.get_vectors_without(rated)
    #
    #     ids = await get_neareses_by_max_pooling(clear_vectors, vector_t, vector_f)
    #     ret = []
    #     for i in ids:
    #         ret.append(await asyncHandler.get_product_by_id(i))
    #     return ret

    @staticmethod
    async def get_recommend_cat(user_id: int) -> list[dict] | str:
        t_id = await asyncHandler.get_user_rate_id(user_id, True)
        f_id = await asyncHandler.get_user_rate_id(user_id, False)
        if len(t_id) < 2:
            return 'less 2 positive rates'
        if len(f_id) < 2:
            return 'less 2 negative rates'
        all_cat = await asyncHandler.get_all_cat_data()
        print("data loaded")
        ids = await get_cat_recommed(all_cat, t_id, f_id)
        ret = []
        for i in ids:
            ret.append(await asyncHandler.get_product_by_id(i))
        return ret

    @staticmethod
    @Session
    async def clear_products_without_short_description(session):
        statement = delete(Product).where(
            and_(Attribute.name == "short_desription", Attribute.value == "None"))
        # toDel = await session.execute(select(Product).join(Attribute).where(
        #     and_(Attribute.name == "short_desription", Attribute.value != "None")))
        await session.execute(statement)

        # for i in tqdm(products):
        #         await session.delete(i)


if __name__ == "__main__":
    tracemalloc.start()
    asyncio.run(asyncHandler.init_db())

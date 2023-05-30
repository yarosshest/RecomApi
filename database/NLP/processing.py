import tracemalloc
import asyncio
import numpy as np
from tqdm.asyncio import trange, tqdm
from database.async_db import asyncHandler
from multiprocessing import Pool
from sentence_transformers import SentenceTransformer
from database.NLP.lemmatization import lemmatize_many
from nltk import download
from nltk.corpus import stopwords


async def calc_distance(distances: list, id_f, id_s: int, vec_f, vec_s: np.array) -> None:
    distances.append([id_f, id_s, np.dot(vec_f, vec_s)])


async def get_data():
    ids = []
    des = []

    data = await asyncHandler.get_all_short_description()
    for i in data:
        ids.append(i[0])
        des.append(i[1])

    return [ids, des]


def embed(input):
    mod = 'uaritm/multilingual_en_ru_uk'
    model = SentenceTransformer(mod)
    return model.encode(input, show_progress_bar=False)


async def calc_dist():
    dt = await get_data()
    dt = dt[:100]
    print("descriptions load from bd")
    ids = dt[0]
    des = dt[1]
    print("processing descriptions start")
    dist = embed(des)
    print("processing descriptions end")

    distances = []

    # create pool of 8 tasks and run them in parallel with 8 workers
    with Pool(32) as p:
        async for i in trange(len(ids)):
            async for j in trange(len(ids)):
                p.map_async(calc_distance, [distances, ids[i], ids[j], dist[i], dist[j]])
        p.close()
        p.join()
    await asyncHandler.add_some_distances(distances)


async def calc_vectors():
    dt = await get_data()
    print("descriptions load from bd")
    ids = dt[0]
    print("lemmatization")
    des = lemmatize_many(dt[1])
    lemmas = []
    async for i in trange(len(ids)):
        lemmas.append([ids[i], des[i]])
    await asyncHandler.add_some_lemma(lemmas)
    print("processing descriptions start")
    vec = embed(des)
    print("processing descriptions end")
    vectors = []
    async for i in trange(len(ids)):
        vectors.append([ids[i], vec[i]])
    await asyncHandler.add_some_vectors(vectors)


if __name__ == "__main__":
    tracemalloc.start()
    asyncio.run(calc_vectors())
    print("done")

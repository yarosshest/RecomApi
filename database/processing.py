import tracemalloc
import tensorflow_text
from absl import logging
from tensorflow.python.client import device_lib
import tensorflow as tf
import asyncio
import tensorflow_hub as hub
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import seaborn as sns
from tqdm.asyncio import trange, tqdm
# from db import ObjectHandler
from async_db import asyncHandler
import tensorflow as tf
from multiprocessing import Pool


async def calc_distance(distances: list, id_f, id_s: int, vec_f, vec_s: np.array) -> None:
    distances.append([id_f, id_s, np.dot(vec_f, vec_s)])


async def get_data(h):
    ids = []
    des = []

    data = await h.get_all_description()
    for i in data:
        ids.append(i[0])
        des.append(i[1])

    return [ids, des]


def embed(input):
    module_url = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
    model = hub.load(module_url)
    print("module %s loaded" % module_url)
    return model(input)


async def calc_dist(h):
    dt = await get_data(h)
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
    await h.add_some_distances(distances)


async def calc_vectors(h):
    dt = await get_data(h)
    dt = dt[:2]
    print("descriptions load from bd")
    ids = dt[0]
    des = dt[1]
    print("processing descriptions start")
    vec = embed(des)
    print("processing descriptions end")
    vectors = []
    async for i in trange(len(ids)):
        vectors.append([ids[i], vec[i]])
    await h.add_some_vectors(vectors)


if __name__ == "__main__":
    tracemalloc.start()
    h = asyncHandler()
    asyncio.run(calc_vectors(h))
    # asyncio.run(calc_dist(h))

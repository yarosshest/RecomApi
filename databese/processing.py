from absl import logging

import tensorflow as tf
import asyncio
import tensorflow_hub as hub
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import seaborn as sns
from tqdm import tqdm
from db import ObjectHandler


def get_data(h):
    ids = []
    des = []

    data = h.get_all_description()
    for i in data:
        ids.append(i[0])
        des.append(i[1])

    return [ids, des]


def embed(input):
    module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
    model = hub.load(module_url)
    print("module %s loaded" % module_url)
    return model(input)


def calc_dist(h):
    dt = get_data(h)
    ids = dt[0]
    des = dt[1]
    print("processing descriptions start")
    dist = embed(des)
    print("processing descriptions end")

    print("collecting distances")
    corr = np.inner(dist, dist)

    for i in tqdm(range(len(des))):
        distances = []
        for j in range(len(des)):
            if i > j:
                distances.append([ids[i], ids[j], corr[i][j].item()])
        h.add_some_distances(distances)


if __name__ == "__main__":
    h = ObjectHandler()
    calc_dist(h)

# for i in tqdm(range(len(des))):
#     distances = []
#     for j in range(len(des)):
#         if i > j:
#             distances.append([ids[i], ids[j], corr[i][j].item()])
#     hand.add_some_distances(distances)

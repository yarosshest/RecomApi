from absl import logging

import tensorflow as tf

import tensorflow_hub as hub
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import seaborn as sns
from tqdm import tqdm
from db import ObjectHandler

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)
print ("module %s loaded" % module_url)
def embed(input):
  return model(input)

ids = []
des = []

hand = ObjectHandler()

for i in hand.get_all_description():
    ids.append(i[0])
    des.append(i[1])
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
    hand.add_some_distances(distances)

import asyncio
from typing import Tuple, Any

import numpy as np
from numpy import dot, median
from numpy.linalg import norm
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from random import shuffle

from database.async_db import asyncHandler as db
from database.recomindation_alg import get_nearest_for_user_by_cos_sim,\
    get_nearest_for_user_by_median,\
    get_neareses_by_max_pooling


def split_data(data, kof=0.2) -> tuple[Any, Any]:
    shuffle(data)
    return data[:int(len(data) * kof)], data[int(len(data) * kof):]


class System:
    obj_t = {}
    obj_f = {}
    obj = {}

    def __init__(self, id_t, id_f, filt):
        vectors = asyncio.run(db.get_all_vectors())

        for i in range(len(vectors[0])):
            if vectors[0][i] in id_t:
                self.obj_t.update({vectors[0][i]: vectors[1][i]})
            elif vectors[0][i] in id_f:
                self.obj_f.update({vectors[0][i]: vectors[1][i]})
            elif vectors[0][i] in filt:
                self.obj.update({vectors[0][i]: vectors[1][i]})

    def set_rate(self, id: int, rate: bool):
        ob = self.obj.pop(id)
        if rate:
            self.obj_t.update({id: ob})
        else:
            self.obj_f.update({id: ob})

    def get_predict(self):
        ids = asyncio.run(get_neareses_by_max_pooling(
            [list(self.obj.keys()), list(self.obj.values())],
            list(self.obj_t.values()),
            list(self.obj_f.values())))

        return ids[0]


class User:
    obj_t = {}
    obj_f = {}

    def __init__(self, id_t, id_f):
        vectors = asyncio.run(db.get_all_vectors())

        for i in range(len(vectors[0])):
            if vectors[0][i] in id_t:
                self.obj_t.update({vectors[0][i]: vectors[1][i]})
            elif vectors[0][i] in id_f:
                self.obj_f.update({vectors[0][i]: vectors[1][i]})

    def feed(self, sys: System):
        id_pred = sys.get_predict()
        if id_pred in self.obj_t.keys():
            sys.set_rate(id_pred, True)
            return True
        if id_pred in self.obj_f.keys():
            sys.set_rate(id_pred, False)
            return False


def test_1():
    id_t = [14135, 2475, 504, 2297, 64650, 2345, 6688, 8554, 25481, 57750, 62418, 180, 63776, 7525, 2812, 2658]
    id_f = [514, 519, 544, 863, 926, 945, 951, 864, 876, 958, 1063, 1089, 1108, 1157, 5714, 61481, 1184, 65934, 66666,
            6674,
            66315, 66006, 1087, 1927, 1300, 65946, 7380, 295, 66023, 1268, 27624, 10360, 16299, 65960, 5, 4366, 589,
            60668, 386, 30355,
            1258, 66210, 1808]

    k = 0.8

    X_train, X_test = split_data(id_t, k)

    y_train, y_test = split_data(id_f, k)

    user = User(id_t, id_f)
    id_all = id_t + id_f
    sys = System(X_train, y_train, id_all)

    col = 0
    true_col = 0
    items = []
    while len(sys.obj_t) != len(user.obj_t):
        col += 1
        res = user.feed(sys)
        if res:
            true_col += 1
        items.append(true_col / col)

    fig, ax = plt.subplots()
    ax.set_title(f'k_steps={col/(len(id_t)-len(X_train))}  k_split={k}')
    ax.plot(items)
    plt.show()


if __name__ == '__main__':
    test_1()

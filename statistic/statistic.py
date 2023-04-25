import asyncio
import numpy as np
from numpy import dot, median
from numpy.linalg import norm
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from random import shuffle

from database.async_db import asyncHandler


def cos_sim(a, b):
    return dot(a, b) / (norm(a) * norm(b))


class System:
    obj_t = {}
    obj_f = {}
    obj = {}

    def __init__(self, id_t, id_f, filt):
        self.db = asyncHandler()
        vectors = asyncio.run(self.db.get_all_vectors())

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
        buf = self.obj_t.values()
        vector_t = median(np.array(list(self.obj_t.values())), axis=0)

        vector_f = median(np.array(list(self.obj_f.values())), axis=0)

        vectors_id = list(self.obj.keys())
        vectors_all = np.array(list(self.obj.values()))

        dist_f = None
        if np.isfinite(vector_f.any()):
            dist_f = [cos_sim(vector_f, i) for i in vectors_all]

        dist_t = [cos_sim(vector_t, i) for i in vectors_all]

        if dist_f is None:
            dist = dist_t
        else:
            dist = [dist_t[i] - dist_f[i] for i in range(vectors_all.shape[0])]

        dist = np.array(dist)

        films = np.argsort(dist)
        ids = [vectors_id[i] for i in films[-5:]][::-1]

        return ids[0]


class User:
    obj_t = {}
    obj_f = {}

    def __init__(self, id_t, id_f):
        self.db = asyncHandler()
        vectors = asyncio.run(self.db.get_all_vectors())

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
    id_t = [14135, 2475, 504, 2297, 64650, 2345, 6688, 8554, 25481, 57750, 62418, 180, 63776, 7525]  # 14
    id_f = [514, 519, 544, 863, 926, 945, 951, 864, 876, 958, 1063, 1089, 1108, 1157]  # 14

    X_train, X_test, y_train, y_test = train_test_split(id_t, id_f, test_size=0.9, random_state=42)

    user = User(id_t, id_f)
    id_all = id_t + id_f
    sys = System(X_train, y_train, id_all)

    col = 0
    true_col = 0
    items = []
    for i in range(len(X_test)):
        col += 1
        res = user.feed(sys)
        if res:
            true_col += 1
        items.append(true_col / col)

    plt.plot(items)
    plt.show()


if __name__ == '__main__':
    test_1()

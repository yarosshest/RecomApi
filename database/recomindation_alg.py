import numpy as np
from numpy import dot, median
from numpy.linalg import norm


async def calculate_median_distance(vect_f, vect_s: np.array) -> np.array:
    med = np.median(vect_f, axis=0)
    dist = np.inner(med, vect_s)
    return dist


def cos_sim(a, b):
    return dot(a, b) / (norm(a) * norm(b))


async def get_nearest_for_user_by_median(clear_vectors, vectors_t, vectors_f) -> list:
    vectors_id = clear_vectors[0]
    vectors_all = np.array(clear_vectors[1])

    dist_f = None
    if vectors_f:
        dist_f = await calculate_median_distance(vectors_f, vectors_all)

    dist_t = await calculate_median_distance(vectors_t, vectors_all)

    if dist_f is None:
        dist = dist_t
    else:
        dist = dist_t - dist_f

    films = np.argsort(dist)
    ids = [vectors_id[i] for i in films[:5]]
    return ids


async def get_nearest_for_user_by_cos_sim(clear_vectors, vectors_t, vectors_f) -> list:
    vectors_t = median(np.array(vectors_t), axis=0)
    vectors_f = median(np.array(vectors_f), axis=0)

    vectors_id = clear_vectors[0]
    vectors_all = np.array(clear_vectors[1])

    dist_f = None
    if np.isfinite(vectors_f):
        dist_f = [cos_sim(vectors_f, i) for i in vectors_all]

    dist_t = [cos_sim(vectors_t, i) for i in vectors_all]

    if dist_f is None:
        dist = dist_t
    else:
        dist = [dist_t[i] - dist_f[i] for i in range(vectors_all.shape[0])]

    dist = np.array(dist)

    films = np.argsort(dist)
    ids = [vectors_id[i] for i in films[-5:]][::-1]

    return ids
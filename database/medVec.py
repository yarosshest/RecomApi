import numpy as np


def returnNearest(user_vectors_t, user_vectors_f, vectors):
    median_t = np.median(user_vectors_t, axis=0)
    dist_t = np.inner(median_t, vectors[1])

    median_f = np.median(user_vectors_f, axis=0)
    dist_f = np.inner(median_f, vectors[1])

    dist = dist_t - dist_f
    id = vectors[np.argmax(dist)]
    return id

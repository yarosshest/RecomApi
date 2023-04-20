from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm
from numpy import dot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def cos_sim(a, b):
    return dot(a, b) / (norm(a) * norm(b))


def embed(input):
    mod = 'uaritm/multilingual_en_ru_uk'
    model = SentenceTransformer(mod)
    print("module %s loaded" % mod)
    return model.encode(input, show_progress_bar=True)


def create_heatmap(similarity, labels, cmap="YlGnBu"):
    df = pd.DataFrame(similarity)
    df.columns = labels
    df.index = labels
    plt.imshow(df, cmap='hot', interpolation='nearest')
    sns.heatmap(df, cmap=cmap)
    plt.show()


sent = [
    "Сегодня была хорошая погода",
    "Сегодня весть день светило сонце и было тепло, замечательно",
    "Сегодня был дождь и отвратная вьюга",
    "Стас борецкий съел бульдога и залез на лестницу"
]
emb = embed(sent)
similarity = []
for i in range(len(emb)):
    row = []
    for j in range(len(emb)):
        row.append(cos_sim(emb[i], emb[j]))
    similarity.append(row)
create_heatmap(similarity, sent)


dist = np.inner(emb, emb)
create_heatmap(dist, sent)

import math
import re

import nltk
import numpy as np
from nltk import download
from nltk.corpus import stopwords
from navec import Navec
from collections import Counter
from pymystem3 import Mystem

from database.recomindation_alg import cos_sim
from database.processing import embed

WORD = re.compile(r"\w+")
download('stopwords')
path = 'hudlit_v1_12B_500K_300d_100q.tar'
navec = Navec.load(path)

m = Mystem()


def wordMdistance(doc1, doc2):
    '''
        return the word mover distance between two documents

        -- input:
                        doc1: the first document as list of words
                        doc2: the second document as list of words
        -- output:
                        Word Mover's Distance score
    '''
    sum_dist = 0
    i = 0
    for word in doc1:
        mindist = 1000.0
        for word2 in doc2:
            try:
                j = np.copy(navec.get(word))
                t = np.copy(navec.get(word2))
                dista = np.sqrt(sum((j - t) ** 2))
                if dista < mindist:
                    mindist = dista
            except:
                continue
        sum_dist += mindist
        i += 1
    return sum_dist / i


def process_text(text: str) -> list:
    text = text.split()
    stopw = stopwords.words('russian')
    signs = ['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '«', '»', '№']
    stopw.extend(signs)

    text = [w for w in text if w not in stopw]

    for i in signs:
        text = [w.replace(i, '') for w in text]

    text = ' '.join(text)

    text = ''.join(m.lemmatize(text))

    return text.split()


sentence_a = 'История первого сражения Великой Отечественной войны. Гиперреалистичная телеверсия фильма «Брестская крепость»'
sentence_b = 'Иван Грозный отвечает на телефон, пока его тезка-пенсионер сидит на троне. Советский хит о липовом государе'
sentence_c = 'Масштабный документальный проект, снятый к 65-летию Победы. Реконструкция сражений и уникальная 3D-графика'

sentence_a = process_text(sentence_a)
sentence_b = process_text(sentence_b)
sentence_c = process_text(sentence_c)

print(wordMdistance(sentence_a, sentence_b))
print(wordMdistance(sentence_a, sentence_c))
print(wordMdistance(sentence_b, sentence_c))

sentence_a = embed(' '.join(sentence_a))
sentence_b = embed(' '.join(sentence_b))
sentence_c = embed(' '.join(sentence_c))

print(cos_sim(sentence_a, sentence_b))
print(cos_sim(sentence_a, sentence_c))
print(cos_sim(sentence_b, sentence_c))

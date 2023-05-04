from nltk import download
from nltk.corpus import stopwords
from navec import Navec
from pymystem3 import Mystem


def fast_lem(texts: list[str]) -> list[str]:
    m = Mystem()
    b = ''
    for i in texts:
        b += i + 'br'
    m.lemmatize(b)

    return b.split('br')


def lemmatize_many(texts: list[str]) -> list:
    stopw = stopwords.words('russian')
    download('stopwords')
    signs = ['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '«', '»', '№']
    stopw.extend(signs)

    otv = []

    for t in texts:
        t = t.lower()
        t = t.split()
        t = [w for w in t if w not in stopw]
        for i in signs:
            t = [w.replace(i, '') for w in t]
        t = ' '.join(t)
        otv.append(t)

    otv = fast_lem(otv)

    return otv

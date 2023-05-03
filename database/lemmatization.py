import sys
import requests
from pymystem3 import Mystem


def tag_mystem(
        text="Текст нужно передать функции в виде строки!", mapping=None, postags=True
):
    # если частеречные тэги не нужны (например, их нет в модели), выставьте postags=False
    # в этом случае на выход будут поданы только леммы
    m = Mystem()

    processed = m.analyze(text)
    tagged = []
    for w in processed:
        print(w)
        try:
            if w["text"] == "br":
                tagged.append("br")
            if not w['analysis']:
                continue
            lemma = w["analysis"][0]["lex"].lower().strip()
            pos = w["analysis"][0]["gr"].split(",")[0]
            pos = pos.split("=")[0].strip()
            if mapping:
                if pos in mapping:
                    pos = mapping[pos]  # здесь мы конвертируем тэги
                else:
                    pos = "X"  # на случай, если попадется тэг, которого нет в маппинге
            tagged.append(lemma.lower() + "_" + pos)
        except KeyError:
            continue  # я здесь пропускаю знаки препинания, но вы можете поступить по-другому
    if not postags:
        tagged = [t.split("_")[0] for t in tagged]
    return tagged


def lemmatize(text) -> str:
    otv = ''
    # Таблица преобразования частеречных тэгов Mystem в тэги UPoS:
    mapping_url = "https://raw.githubusercontent.com/akutuzov/universal-pos-tags" \
                  "/4653e8a9154e93fe2f417c7fdb7a357b7d6ce333/ru-rnc.map"

    mystem2upos = {}
    r = requests.get(mapping_url, stream=True)
    for pair in r.text.split("\n"):
        pair = pair.split()
        if len(pair) > 1:
            mystem2upos[pair[0]] = pair[1]

    res = text.strip()
    output = tag_mystem(text=res, mapping=mystem2upos)
    otv = " ".join(output)

    return otv

def lemmatize_mass(text : list) -> list:

    line = ''
    for i in text:
        line += i + ' br '
    # Таблица преобразования частеречных тэгов Mystem в тэги UPoS:
    mapping_url = "https://raw.githubusercontent.com/akutuzov/universal-pos-tags" \
                  "/4653e8a9154e93fe2f417c7fdb7a357b7d6ce333/ru-rnc.map"

    mystem2upos = {}
    r = requests.get(mapping_url, stream=True)
    for pair in r.text.split("\n"):
        pair = pair.split()
        if len(pair) > 1:
            mystem2upos[pair[0]] = pair[1]

    res = line.strip()
    output = tag_mystem(text=res, mapping=mystem2upos)
    one_piece = " ".join(output)
    otv = one_piece.split("br")

    return otv

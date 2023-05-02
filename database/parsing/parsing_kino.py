import asyncio
import json
import tracemalloc
from threading import Thread
from threading import Semaphore
from tqdm import tqdm

# from db import ObjectHandler
from database.async_db import asyncHandler, async_to_tread


def parse_object(x):
    if x['short_desription'] is not None and 'name_ru' in x and 'poster_url' in x and 'description' in x:
        product = [x['name_ru'], x['poster_url'], x['description']]
        del x['name_ru']
        del x['poster_url']
        del x['description']
        attributes = list(x.items())
        return [product, attributes]
    else:
        return None


async def parse_data(dt):
    objects = []
    print("parsing json")
    for i in tqdm(dt):
        ob = parse_object(i)
        if ob is not None:
            objects.append(ob)

    print("adding products in db")
    await asyncHandler.add_some_products(objects)


if __name__ == '__main__':
    tracemalloc.start()
    f = open('KinopoiskDumb.json', encoding='utf-8')
    data = json.load(f)
    asyncio.run(parse_data(data))

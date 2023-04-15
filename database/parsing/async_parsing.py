import asyncio
import json
import tracemalloc
from threading import Thread
from threading import Semaphore
from tqdm import tqdm

# from db import ObjectHandler
from async_db import asyncHandler, async_to_tread


def parse_object(x):
    if x['images'] and x['description'] != '':
        attributes = []
        for i in x['product_details']:
            pairs = list(i.items())[0]
            attributes.append([pairs[0], "", pairs[1], ""])
        product = [x['category'], x['title'], x['images'][0], x['description'], x['actual_price']]
        return [product, attributes]


async def parse_data(dt):
    data = []

    for i in tqdm(dt):
        x = parse_object(i)
        if x is not None:
            data.append(parse_object(i))

    h = asyncHandler()

    await h.add_some_products(data)


if __name__ == '__main__':
    tracemalloc.start()
    f = open('flipkart_fashion_products_dataset.json')
    data = json.load(f)
    asyncio.run(parse_data(data))

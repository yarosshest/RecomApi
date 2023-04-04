import asyncio
import json
import tracemalloc
from threading import Thread
from threading import Semaphore
from tqdm import tqdm

# from db import ObjectHandler
from async_db import asyncHandler, async_to_tread


@async_to_tread
async def parse_object(semaphore, x):
    with semaphore:
        oh = asyncHandler()
        # id_ob = "Err"
        # try:
        #     id_ob = await oh.add_product(x['category'], x['title'], x['images'][0], x['description'], x['actual_price'])
        #     for i in x['product_details']:
        #         pairs = list(i.items())[0]
        #         await oh.add_attribute(id_ob, pairs[0], "", pairs[1], "")
        # except IndexError:
        #     return
        # finally:
        #     print(id_ob)
        if x['images']:
            attributes = []
            for i in x['product_details']:
                pairs = list(i.items())[0]
                attributes.append([pairs[0], "", pairs[1], ""])
            product = [x['category'], x['title'], x['images'][0], x['description'], x['actual_price']]
            await oh.add_product(product, attributes)


def parse_data(dt):
    semaphore = Semaphore(2)

    for i in tqdm(dt):
        worker = Thread(target=parse_object, args=(semaphore, i))
        worker.start()


if __name__ == '__main__':
    tracemalloc.start()
    f = open('flipkart_fashion_products_dataset.json')
    data = json.load(f)
    parse_data(data)

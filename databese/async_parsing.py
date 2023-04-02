import asyncio
import json
import tracemalloc

from tqdm import tqdm

# from db import ObjectHandler
from async_db import asyncHandler


async def parse_object(semaphore, x):
    async with semaphore:
        oh = asyncHandler()
        id_ob = "Err"
        try:
            id_ob = await oh.add_product(x['category'], x['title'], x['images'][0], x['description'], x['actual_price'])
            for i in x['product_details']:
                pairs = list(i.items())[0]
                await oh.add_attribute(id_ob, pairs[0], "", pairs[1], "")
        except IndexError:
            return
        finally:
            print(id_ob)


async def parse_data(dt):
    semaphore = asyncio.Semaphore(10)

    coroutines = [parse_object(semaphore, i) for i in dt]

    await asyncio.gather(*coroutines)

if __name__ == '__main__':
    tracemalloc.start()
    f = open('flipkart_fashion_products_dataset.json')
    data = json.load(f)
    asyncio.run(parse_data(data))

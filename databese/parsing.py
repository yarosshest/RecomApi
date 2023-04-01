import json
from db import ObjectHandler

def parse_object(x):
    oh = ObjectHandler()
    try:
        id_ob = oh.add_product(category=x['category'],
                               name=x['title'],
                               photo=x['images'][0],
                               description=x['description'],
                               price=x['actual_price'])
        for i in x['product_details']:
            pairs = list(i.items())[0]
            oh.add_attribute(id_ob, pairs[0], "", pairs[1], "")
    except:
        print(x['title'])
        return


if __name__ == '__main__':
    f = open('flipkart_fashion_products_dataset.json')
    data = json.load(f)
    for i in data:
        parse_object(i)

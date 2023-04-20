import asyncio
import json
from async_db import asyncHandler


h = asyncHandler()
products = asyncio.run(h.get_all_description())

res = []
for product in products:
    res.append({
        'id': product[0],
        'description': product[1]
    })

with open('data.json', 'w') as f:
    json.dump(res, f)

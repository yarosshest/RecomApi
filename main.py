n = 5
from databese.db import ObjectHandler

def fn(i, j):
    return str(i) + str(j)


Matrix = [[fn(i, j) for j in range(n)] for i in range(n)]

for i in range(n):
    print(Matrix[i])

for i in range(n):
    for j in range(n):
        if i > j:
            print(Matrix[i][j])


hand = ObjectHandler
ids, des = [[x, y] for x, y in hand.get_all_description()]
print(ids)
print(des)
import psycopg2


class DataBase:
    def __init__(self):
        self.conn = psycopg2.connect(dbname='RecomApi', user='postgres',
                                            password='postgres', host='localhost',
                                            port=5433)

    def AddType(self, name, parent):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO ObjectType (name, parent) VALUES (%s, %s)", (name, parent))
        self.conn.commit()
        cur.close()

    def AddObj(self, name, description, price, image, type):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO Object (name, description, price, image, type) VALUES (%s, %s, %s, %s, %s)",
                    (name, description, price, image, type))
        self.conn.commit()
        cur.close()

    def GetObj(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Object WHERE id = %s", (id,))
        obj = cur.fetchone()
        cur.close()
        return obj





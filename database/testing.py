import tracemalloc
import unittest
from asyncio import run

from database.NLP.processing import calc_vectors
from database.async_db import asyncHandler as db
from database.parsing.parsing_kino import start
import configparser
import pathlib

p = pathlib.Path(__file__).parent.parent.joinpath('config.ini')

config = configparser.ConfigParser()
config.read(p)


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        tracemalloc.start()
        test = config['TEST']['testing'] == 'True'
        if test:
            run(db.drop_all())

            run(db.init_db())

            p = pathlib.Path(__file__).parent.joinpath('parsing').joinpath(str(config['DEFAULT']["DATAJSON"]))
            start(p)

            run(calc_vectors())

    def test_parsing(self):
        films = run(db.get_all_films())
        self.assertEqual(11875, len(films))

    def test_vectorization(self):
        vec = run(db.get_all_vectors())
        self.assertEqual(11875, len(vec[0]))

    def test_get_all_cat_data(self):
        cat = run(db.get_all_cat_data())
        self.assertEqual(11875, len(cat))


if __name__ == '__main__':
    unittest.main()

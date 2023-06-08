import tracemalloc
import unittest
import configparser
import pathlib
from asyncio import run

from fastapi.openapi.models import Response

from database.async_db import asyncHandler as db
from database.parsing.parsing_kino import start
from database.NLP.processing import calc_vectors

from api import login, register
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

            p = pathlib.Path(__file__).parent.parent.joinpath('database').joinpath('parsing').joinpath(str(config['DEFAULT']["DATAJSON"]))
            start(p)

            run(calc_vectors())


    # def test_login_register(self):
    #     res = Response()
    #     register(res, 'test', 'test')
    #     id = login(res, 'test', 'test')
    #     self.assertEqual(type(id), type(0))


if __name__ == '__main__':
    unittest.main()

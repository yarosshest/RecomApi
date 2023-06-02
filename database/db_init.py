from database.async_db import asyncHandler as db
from database.parsing.parsing_kino import start
from database.NLP.processing import calc_vectors
from asyncio import get_event_loop
import configparser
import pathlib


def db_init():
    p = pathlib.Path(__file__).parent.parent.joinpath('config.ini')
    config = configparser.ConfigParser()
    config.read(p)
    loop = get_event_loop()
    loop.run_until_complete(db.init_db())

    if config['DEFAULT']['PARSING']:
        print("parsing start")
        p = pathlib.Path(__file__).parent.joinpath('parsing').joinpath(str(config['DEFAULT']["DATAJSON"]))
        start(p)

        print("vectorization start")
        loop.run_until_complete(calc_vectors())

        config['DEFAULT']["PARSING"] = 'False'
        with open('../config.ini', 'w') as configfile:  # save
            config.write(configfile)

    print("db init end")


if __name__ == '__main__':
    db_init()

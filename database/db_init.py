from database.async_db import asyncHandler as db
from database.parsing.parsing_kino import start
from database.NLP.processing import calc_vectors
from asyncio import run
import database.config as config


def db_init():
    run(db.init_db())

    if config.parsing:
        print("parsing start")
        start("database/parsing/" + config.datajson)

        print("vectorization start")
        run(calc_vectors())

        config.parsing = False

    print("db init end")


if __name__ == '__main__':
    db_init()

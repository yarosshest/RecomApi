from database.async_db import asyncHandler as db
from database.parsing.parsing_kino import start
from database.NLP.processing import calc_vectors
from asyncio import get_event_loop
import database.config as config


def db_init():
    print(config.parsing)
    loop = get_event_loop()
    loop.run_until_complete(db.init_db())

    if config.parsing:
        print("parsing start")
        start("database/parsing/" + config.datajson)

        print("vectorization start")
        loop.run_until_complete(calc_vectors())

        config.parsing = False

    print("db init end")


if __name__ == '__main__':
    db_init()

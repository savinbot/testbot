# -*- coding: utf-8 -*-

from vedis import Vedis
from vedisdb import config


# Get current user's state from db.
def get_current_state(user_id, db_name):
    with Vedis(db_name) as db:
        try:
            return db[user_id]
        except KeyError:
            # Вот тут подумать что возвращать.
            return config.States.S_USE_MENU.value


# Save current user's state into db.
def set_state(user_id, value, db_name):
    with Vedis(db_name) as db:
        try:
            db[user_id] = value

            return True
        except NameError:
            return False


# Delete current ad status from db.
def delete(chat_id, db_name):
    with Vedis(db_name) as db:
        try:
            del db[chat_id]

            return True
        except KeyError:
            return False

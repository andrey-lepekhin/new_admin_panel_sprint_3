"""Functions to get state from SQLite and error handlers."""
import datetime
import logging
import sqlite3
import sys
import traceback
from contextlib import contextmanager

import psycopg2
from db_queries import (CREATE_TABLE, DELETE_OLD_STATES,
                        SELECT_LAST_SUCCESSFUL_LOAD_TIME,
                        UPSERT_LAST_SUCCESSFUL_LOAD_TIME)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@contextmanager
def sqlite_connection_context(db_path: str):
    connection = sqlite3.connect(db_path)
    yield connection
    connection.commit()
    connection.close()


def db_error_handler(func):
    def inner_function(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except sqlite3.Error as err:
            logger.error('SQLite error: {0}'.format((' '.join(err.args))))
            logger.error('Exception class is: ', err.__class__)
            logger.error('SQLite traceback: ')
            logger.error(traceback.format_exception(*sys.exc_info()))
        except psycopg2.Error as err:
            logger.error('Postgres error: {0}'.format(err.pgcode))
            logger.error(err)
        return result

    return inner_function


@db_error_handler
def get_lsl_from_sqlite(sqlite_db_path):
    """
    Get last successful load time from SQlite.
    """
    with sqlite_connection_context(sqlite_db_path) as sqlite_connection:
        sqlite_cursor = sqlite_connection.cursor()
        sqlite_cursor.execute(CREATE_TABLE)
        sqlite_cursor.execute(DELETE_OLD_STATES)
        last_successful_load = sqlite_cursor.execute(SELECT_LAST_SUCCESSFUL_LOAD_TIME).fetchone()
        if last_successful_load is None:
            last_successful_load = [datetime.datetime(1970, 1, 1).isoformat(timespec='seconds')]
            logger.debug('No saved LSL found. Defaulting to 1 Jan 1970.')
    return last_successful_load[0]


@db_error_handler
def save_lsl_to_sqlite(lsl, successful, sqlite_db_path):
    """
    Save last successful load time to SQlite.
    """
    with sqlite_connection_context(sqlite_db_path) as sqlite_connection:
        sqlite_cursor = sqlite_connection.cursor()
        now = datetime.datetime.now().isoformat(timespec='seconds')
        sqlite_cursor.execute(
            UPSERT_LAST_SUCCESSFUL_LOAD_TIME.format(lsl.isoformat(timespec='seconds'), successful, now),
        )
    return None

"""Main ETL module for transferring Filmworks from PG to ES."""
import datetime
import logging
import os
import time

import psycopg2
from backoff import NoFilmworks, backoff
from db_config import PG_CONNECTION_CREDENTIALS
from db_queries import SELECT_ONE_FILMWORK
from db_sqlite_functions import get_lsl_from_sqlite, save_lsl_to_sqlite
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from es import ES_INDEX_NAME, es_create_index, generate_actions
from psycopg2.extras import RealDictCursor
from run_once import get_lock
from psycopg2.extensions import connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@backoff()
def main(pg_connection: psycopg2.extensions.connection, es_client: Elasticsearch, sqlite_db_path: str, frequency=60):
    """
    Main ETL function. Extracts movie data from PG, transforms it and pushes to ES index.

    Searches PG for any movie-related entities that have changed since last cycle.
    If any found, transforms them and loads into ES.
    """

    # Get last successful load time from SQLite.
    logger.info('New cycle. Loading last successful load time...')
    # Django uses UTC to store changed_at, we should use UTC too.
    last_successful_load = datetime.datetime.fromisoformat(get_lsl_from_sqlite(sqlite_db_path)).replace(
        tzinfo=datetime.timezone.utc)
    logger.info('Last successful load = {0}'.format(last_successful_load))

    time_since_lsl = (datetime.datetime.now(datetime.timezone.utc) - last_successful_load).total_seconds()
    if time_since_lsl < frequency:
        logger.info('Last poll was less than {0} seconds ago. Waiting for {1} seconds.'.format(
            frequency,
            frequency - time_since_lsl,
        ))
        time.sleep(frequency - time_since_lsl)

    start_time = datetime.datetime.now(datetime.timezone.utc)
    logger.info('Starting new extraction.')
    etl_successful = False
    save_lsl_to_sqlite(start_time, etl_successful, sqlite_db_path)

    logger.info('Reading data from PG.')
    with pg_connection:
        # Check that DB is not empty
        pg_cursor = pg_connection.cursor()
        pg_cursor.execute(SELECT_ONE_FILMWORK)
        if pg_cursor.fetchone() is None:
            logger.info('No filmworks in DB, skipping ETL cycle.')
            logger.info('=======================================')
            raise NoFilmworks('No filmworks in DB')
        else:  # DB is not empty
            # Naming our cursor creates it serverside.
            # That allows using a generator to read results and not load everything in memory.
            pg_cursor = pg_connection.cursor(name='ETL_cursor')
            # The number of rows that the client will pull down at a time from the server side cursor.
            pg_cursor.itersize = 100

            logger.info('Creating ES index if not already present.')
            es_create_index(es_client)

            # Updating ES index
            logger.info('Updating ES index...')
            i = 0
            streaming_blk = streaming_bulk(
                client=es_client,
                index=ES_INDEX_NAME,
                actions=generate_actions(pg_cursor, last_successful_load),
                max_retries=100,
                initial_backoff=0.1,
                max_backoff=10,
            )
            for ok, response in streaming_blk:
                if not ok:
                    logger.error('Error while creating/updating index in ES.')
                logger.debug(response)
                i += 1
            etl_successful = True



    if etl_successful:
        logger.info('Done updating ES index. Updated {0} entries'.format(i))
        logger.info('==========================================')
    save_lsl_to_sqlite(start_time, etl_successful, sqlite_db_path)

@backoff()
def etl_cycle():
    """
    Launches ETL cycle and manages PG and ES connections.
    """
    es_client = Elasticsearch(hosts=os.environ.get('ES_HOST', 'http://127.0.0.1:9200'))
    pg_connection = psycopg2.connect(**PG_CONNECTION_CREDENTIALS, cursor_factory=RealDictCursor)
    try:
        while True:
            main(
                pg_connection=pg_connection,
                es_client=es_client,
                sqlite_db_path=os.environ.get('SQLITE_DB_PATH', 'etl_state/db.sqlite'),
                frequency=os.environ.get('ETL_CYCLE_SEC', 6),
            )
    finally:
        logger.info("Closing PG and ES connections.")
        es_client.transport.close()
        pg_connection.close()  # `with` doesn't close the PG connection, we have to do it manually

if __name__ == '__main__':
    # Ensure only one copy is running
    get_lock('etl')
    logger.info("Got the lock. We're the only ETL process running. Launching polling cycle.")

    # Start the ETL cycle
    etl_cycle()
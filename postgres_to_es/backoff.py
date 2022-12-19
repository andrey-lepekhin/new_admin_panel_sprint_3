"""Backoff decorator that will back off if PG/ES is unavailable."""

import logging
import time
from functools import wraps

import elasticsearch
import psycopg2

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class NoFilmworks(Exception):
    pass

def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=5, stop_at_border=False):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка PG или ES.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param stop_at_border: если True, остановит выполнение повторов при достижении border_sleep_time
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            number_of_retries = 0
            time_to_wait = 0
            while time_to_wait <= border_sleep_time or not stop_at_border:
                try:
                    return func(*args, **kwargs)
                except (psycopg2.InterfaceError, psycopg2.OperationalError, elasticsearch.ConnectionError, NoFilmworks) as e:
                    logger.error('Connection Error')
                    logger.error('{0}'.format(e))
                    logger.error('Waiting for {0} seconds before retrying.'.format(time_to_wait))
                    time.sleep(time_to_wait)
                    number_of_retries += 1
                    if time_to_wait < border_sleep_time:
                        time_to_wait = start_sleep_time * (factor ** number_of_retries)
                    else:
                        time_to_wait = border_sleep_time
                        if stop_at_border:
                            logger.critical('Reached max retries time. Stopping retires.')
                            break

        return inner
    return func_wrapper

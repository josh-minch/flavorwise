import functools
import time
import json


class Algorithm:
    BEST_MATCH = 0
    COMMON = 1
    UNIQUE = 2


def get_json(filename):
    with open(filename, encoding='utf8') as f:
        return json.load(f)


def write_json(data, filename, mode):
    with open(filename, mode, encoding='utf8') as f:
        return json.dump(data, f)


def timer(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        time_start = time.perf_counter()
        value = func(*args, **kwargs)
        time_end = time.perf_counter()
        elapsed_time = time_end - time_start

        print(f"{func.__name__} elapsed time: {elapsed_time:0.4f} seconds")
        return value
    return wrap

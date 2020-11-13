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

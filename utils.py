import contextlib


def to_float(value):
    with contextlib.suppress(ValueError):
        return float(value)
    return 0


def binarize(value, threshold):
    value = to_float(value)
    return (value, int(value >= threshold))


def get_item(data, item, tostr=True):
    if '.' in item:
        (name, rest) = item.split('.', maxsplit=1)
        return get_item(data.get(name, {}), rest, tostr)

    result = data.get(item, '')
    return str(result) if tostr else result


def get_items(data, items):
    return list(map(lambda item: get_item(data, item), items))

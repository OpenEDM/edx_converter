import contextlib


def get_item(data, item, *, type_=str):
    if '.' in item:
        (name, rest) = item.split('.', maxsplit=1)
        return get_item(data.get(name, {}), rest, type_=type_)

    return type_(data.get(item, type_()))


def get_items(data, items, *, type_=str):
    return list(map(lambda item: get_item(data, item, type_=type_), items))


class NonEmptyDict(dict):
    def __setitem__(self, key, value):
        if value or (key not in self):
            super().__setitem__(key, value)

import abc
import contextlib
import csv
import logging
import operator


__all__ = ['process_all_csvs']


class BaseCSV(metaclass=abc.ABCMeta):
    COLUMNS = []

    def __init__(self, prefix, index, encoding):
        self._file = open('{}{}.csv'.format(prefix, index),
                          'w', encoding=encoding)
        self._csv = csv.writer(self._file, delimiter=';')
        self._csv.writerow(map(operator.itemgetter(0), self.COLUMNS))

    def write(self, *items):
        row = tuple(map(str, items))
        for (item, (name, checker)) in zip(row, self.COLUMNS):
            if not checker(item):
                logging.warning('Invalid item "%s" in %s. Skip', name, row)
                return
        self._csv.writerow(row)

    def writeiter(self, iterable):
        for item in iterable:
            self.write(*item)

    @abc.abstractmethod
    def process(self, logs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self._file.close()


class Checkers:
    @staticmethod
    def nonempty(value):
        return bool(value)

    @staticmethod
    def zero_or_one(value):
        return str(value) in ('0', '1')

    @staticmethod
    def positive_int(value):
        with contextlib.suppress(ValueError):
            return int(value) > 0
        return False

    @staticmethod
    def nonnegative_int(value):
        with contextlib.suppress(ValueError):
            return int(value) >= 0
        return False


class Items:
    USER_ID = ('user_id', Checkers.nonempty)
    REVIEWER_ID = ('reviewer_id', Checkers.nonempty)

    ITEM_ID = ('item_id', Checkers.nonempty)
    ITEM_TYPE = ('item_type', Checkers.nonempty)
    ITEM_NAME = ('item_name', Checkers.nonempty)

    CONTENT_ID = ('content_piece_id', Checkers.nonempty)
    CONTENT_TYPE = ('content_piece_type', Checkers.nonempty)
    CONTENT_NAME = ('content_piece_name', Checkers.nonempty)

    MODULE_ID = ('module_id', Checkers.nonempty)
    MODULE_ORDER = ('module_order', Checkers.positive_int)
    MODULE_NAME = ('module_name', Checkers.nonempty)

    SCORE = ('score', Checkers.nonnegative_int)
    MAX_SCORE = ('max_score', Checkers.positive_int)

    CORRECT = ('correct', Checkers.zero_or_one)
    VIEWED = ('viewed', Checkers.zero_or_one)
    TIME = ('time', Checkers.nonempty)


class CSV1(BaseCSV):
    COLUMNS = [
        Items.USER_ID, Items.ITEM_ID, Items.CORRECT, Items.TIME]

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 1, encoding)

    def process(self, logs):
        self.writeiter(logs.get_student_solutions())


class CSV2(BaseCSV):
    COLUMNS = [
        Items.ITEM_ID, Items.ITEM_TYPE, Items.ITEM_NAME,
        Items.MODULE_ID, Items.MODULE_ORDER, Items.MODULE_NAME]

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 2, encoding)

    def process(self, logs):
        self.writeiter(logs.get_tasks())


class CSV3(BaseCSV):
    COLUMNS = [Items.USER_ID, Items.CONTENT_ID, Items.VIEWED]

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 3, encoding)

    def process(self, logs):
        self.writeiter(logs.get_student_content())


class CSV4(BaseCSV):
    COLUMNS = [
        Items.CONTENT_ID, Items.CONTENT_TYPE, Items.CONTENT_NAME,
        Items.MODULE_ID, Items.MODULE_ORDER, Items.MODULE_NAME]

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 4, encoding)

    def process(self, logs):
        self.writeiter(logs.get_content())


class CSV5(BaseCSV):
    COLUMNS = [
        Items.USER_ID, Items.ITEM_ID, Items.REVIEWER_ID,
        Items.SCORE, Items.MAX_SCORE]

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 5, encoding)

    def process(self, logs):
        self.writeiter(logs.get_assessments())


def process_all_csvs(prefix, encoding, logs):
    for processor in (CSV1, CSV2, CSV3, CSV4, CSV5):
        with processor(prefix, encoding) as p:
            p.process(logs)

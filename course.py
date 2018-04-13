import collections
import csv
import logging

from utils import get_id


__all__ = ['CourseParser']


class CourseParser:
    TYPES = ('type@problem', 'type@openassessment', 'type@video')

    def __init__(self, course):
        self.modules = collections.OrderedDict()
        self.content = {}
        self._parse(course)

    def _parse(self, course):
        for (i, item) in enumerate(csv.reader(course, delimiter=';')):
            if len(item) < 2:
                logging.warning('Invalid line %d in course structure file', i)
                continue

            (chapter, *middle, name) = item
            module_id = get_id(chapter)
            self.modules[module_id] = name.strip()

            for item in middle:
                if any(map(lambda type_: type_ in item, self.TYPES)):
                    self.content[item] = module_id

import csv
import logging

import utils


__all__ = ['CourseParser', 'CoursesParser']


class CoursesParser:
    def __init__(self, courses):
        self.names = {}
        self.roo_ids = {}
        self._parse(courses)

    def _parse(self, courses):
        for (i, item) in enumerate(csv.reader(courses, delimiter=';')):
            if len(item) < 2:
                logging.warning('Invalid line %d in course names file', i)
                continue

            course_id = item[0]
            course_name = item[1]
            if len(item) >= 3:
                roo_id = item[2]
                self.roo_ids[course_id] = roo_id
            self.roo_ids[course_id] = course_name

    def get_name(self, course_id):
        return self.names.get(course_id, course_id)

    def get_ro_id(self, course_id):
        return self.roo_ids.get(course_id, course_id)


class CourseParser:
    TYPES = ('type@problem', 'type@openassessment', 'type@video')

    def __init__(self, course):
        self.modules = utils.NonEmptyOrderedDict()
        self.content = {}
        self._parse(course)

    def _parse(self, course):
        for (i, item) in enumerate(csv.reader(course, delimiter=';')):
            if len(item) < 2:
                logging.warning('Invalid line %d in course structure file', i)
                continue

            (chapter, *middle, name) = item
            module_id = utils.get_id(chapter)
            self.modules[module_id] = name.strip()

            for item in middle:
                if any(map(lambda type_: type_ in item, self.TYPES)):
                    self.content[item] = module_id

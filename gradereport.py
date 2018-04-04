import collections
import csv
import operator

from utils import binarize, get_items


__all__ = ['GradeReportParser']


class GradeReportParser:
    FILTERED = ('', 'Not Attempted', 'Not Available')

    def __init__(self, file, threshold):
        self._id2user = {}
        self._user2id = {}
        self._grades = {}
        if file is not None:
            self._parse(file, threshold)

    @staticmethod
    def get_task_columns(fields):
        start = fields.index('Grade') + 1
        if fields[start] == 'Grade Percent':
            start += 1

        for (i, name) in enumerate(fields[start:]):
            if name in ('Cohort Name', 'Experiment Group', 'Team Name',
                        'Enrollment Track', 'Verification Status'):
                end = start + i
                break
        else:
            raise ValueError('Invalid grade report: missing end')

        return [(i, fields[i]) for i in range(start, end)
                if '(Avg)' not in fields[i]]

    def _parse(self, file, threshold):
        reader = csv.DictReader(file, delimiter=',')
        fields = self.get_task_columns(reader.fieldnames)
        self._tasks = tuple(map(operator.itemgetter(1), fields))

        for item in reader:
            (student_id, username) = get_items(
                item, ['Student ID', 'Username'])
            self._id2user[student_id] = username
            self._user2id[username] = student_id

            self._grades[student_id] = collections.OrderedDict(
                (name, binarize(item[name], threshold))
                for (_, name) in fields
                if item.get(name, '') not in GradeReportParser.FILTERED)

    def get_username(self, student_id):
        return self._id2user.get(student_id, '')

    def get_studentid(self, username):
        return self._user2id.get(username, '')

    def get_tasks(self):
        return self._tasks

    def get_grades(self, student_id):
        return self._grades.get(student_id, {})

    def get_userids(self):
        return self._id2user.keys()

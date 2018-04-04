import collections
import csv
import re

from utils import get_items


__all__ = ['ORAParser']


class ORAParser:
    SCORER = re.compile(r'scorer_id:\s+(\w+)')
    Item = collections.namedtuple(
        'Item', ('submission', 'student_id', 'reviewers',
                 'date_time', 'score', 'max_score'))

    def __init__(self, file):
        self._submissions = {}
        if file is not None:
            self._parse(file)

    def _parse(self, file):
        reader = csv.DictReader(file, delimiter=',')
        for item in reader:
            (submission_id, anon_student_id, submit_time,
             score, max_score, details) = get_items(
                 item, ['Submission ID', 'Anonymized Student ID',
                        'Date/Time Response Submitted',
                        'Final Score Points Earned',
                        'Final Score Points Possible',
                        'Assessment Details'])
            reviewers = tuple(self.SCORER.findall(details))
            self._submissions[submission_id] = ORAParser.Item(
                submission_id, anon_student_id, reviewers, submit_time,
                int(score or 0), int(max_score or 0))

    def __iter__(self):
        return iter(self._submissions.keys())

    def __getitem__(self, submission_id):
        return self._submissions.get(submission_id, None)

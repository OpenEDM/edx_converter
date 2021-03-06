import csv
import logging


__all__ = ['AnswersParser']


class AnswersParser:
    def __init__(self, answers):
        self.answers = []
        self._parse(answers)

    def _parse(self, answers):
        reader = csv.reader(answers, delimiter=';')
        for (i, item) in enumerate(reader):
            if len(item) < 10:
                logging.warning('Invalid line %d in student answers file', i)
                continue

            (_, _, problemid, taskid, userid, _,
             time, correct, *_, question, _) = item
            if question == 'NULL':
                question = ''
            self.answers.append(
                (problemid, taskid, question, userid, time, correct))

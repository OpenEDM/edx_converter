import abc
import collections
import csv


__all__ = ['process_all_csvs']


class Indexer:
    def __init__(self):
        self._ids = collections.defaultdict(dict)

    def get(self, kind, key, index=False):
        if key not in self._ids[kind]:
            self._ids[kind][key] = len(self._ids[kind]) + 1
        if index:
            return self._ids[kind][key]
        return '{}_{}'.format(kind, self._ids[kind][key])


class BaseCSV(metaclass=abc.ABCMeta):
    COLUMNS = []

    def __init__(self, prefix, index, encoding):
        self._file = open('{}{}.csv'.format(prefix, index),
                          'w', encoding=encoding)
        self._csv = csv.writer(self._file, delimiter=';')
        self._csv.writerow(self.COLUMNS)

    def write(self, *items):
        self._csv.writerow(map(str, items))

    @abc.abstractmethod
    def process(self, indexer, grade_report, logs, ora):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self._file.close()


class CSV1(BaseCSV):
    COLUMNS = ['user_id', 'item_id', 'correct', 'time']

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 1, encoding)

    def process(self, indexer, grade_report, logs, ora):
        for (userid, tasks) in logs.submits.items():
            # print(tasks.items())
            for (taskid, tries) in tasks.items():
                if 'type@problem' not in taskid:
                    continue
                for (_, correct, time) in tries:
                    self.write(userid, indexer.get('task', taskid),
                               correct, time)


class CSV2(BaseCSV):
    COLUMNS = ['item_id', 'item_type', 'item_name', 'module_id',
               'module_order', 'module_name']

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 2, encoding)

    @staticmethod
    def task_type(taskid):
        if 'type@problem' in taskid:
            return 'MCQ'
        return 'PR'

    def process(self, indexer, grade_report, logs, ora):
        for (taskid, (taskname, moduleid)) in logs.problems.items():
            self.write(
                indexer.get('task', taskid), self.task_type(taskid),
                taskname, indexer.get('module', moduleid),
                indexer.get('module', moduleid, True), moduleid)


class CSV3(BaseCSV):
    COLUMNS = ['user_id', 'content_piece_id', 'viewed']

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 3, encoding)

    def process(self, indexer, grade_report, logs, ora):
        for userid in grade_report.get_userids():
            viewed = logs.viewed_content['video'].get(userid, set())
            for videoid in logs.videos:
                self.write(userid, indexer.get('video', videoid),
                           int(videoid in viewed))


class CSV4(BaseCSV):
    COLUMNS = ['content_piece_id', 'content_piece_type', 'content_piece_name',
               'module_id', 'module_order', 'module_name']

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 4, encoding)

    def process(self, indexer, grade_report, logs, ora):
        for (videoid, moduleid) in logs.videos.items():
            self.write(
                indexer.get('video', videoid), 'video', videoid,
                indexer.get('module', moduleid),
                indexer.get('module', moduleid, True), moduleid)


class CSV5(BaseCSV):
    COLUMNS = ['user_id', 'item_id', 'reviewer_id', 'score', 'max_score']

    def __init__(self, prefix, encoding):
        super().__init__(prefix, 5, encoding)

    def process(self, indexer, grade_report, logs, ora):
        for (submission_id, (userid, taskid)) in logs.submissions.items():
            if submission_id not in logs.assessors:
                continue
            (reviewerid, score, maxscore) = logs.assessors[submission_id]
            self.write(userid, indexer.get('task', taskid), reviewerid,
                       score, maxscore)


def process_all_csvs(prefix, encoding, grade_report, logs, ora):
    indexer = Indexer()

    for processor in (CSV1, CSV2, CSV3, CSV4, CSV5):
        with processor(prefix, encoding) as p:
            p.process(indexer, grade_report, logs, ora)

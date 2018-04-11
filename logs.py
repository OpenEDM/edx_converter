import collections
import json
import logging
import re
from datetime import datetime

import utils
from utils import get_item, get_items


__all__ = ['LogParser']


MODULE_URL = re.compile(r'([^#?]*/)')


def convert_datetime(timestr):
    return datetime.strptime(
        timestr.split('.')[0],
        '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y %H:%M:%S')


def normalize_module_url(url):
    return (MODULE_URL.findall(url) or [''])[0]


def iscollection(type_):
    return isinstance(type_, (tuple, list, set, frozenset))


def last_nonempty(data):
    for item in reversed(data):
        if item:
            return item


class Registry:
    _NULL = object()

    def __init__(self):
        self.processors = []
        self.default = lambda obj, item: None

    def add(self, **kwargs):
        def wrapper(func):
            if kwargs:
                self.processors.append(({
                    key: (value if iscollection(value) else [value])
                    for (key, value) in kwargs.items()
                }, func))
            else:
                self.default = func
            return func
        return wrapper

    @staticmethod
    def check_item(item, kwargs):
        for (key, values) in kwargs.items():
            if item.get(key, Registry._NULL) not in values:
                return False
        return True

    def __call__(self, obj, item):
        for (kwargs, func) in self.processors:
            if Registry.check_item(item, kwargs):
                return func(obj, item)
        return self.default(obj, item)


class Users:
    def __init__(self):
        self.times = collections.defaultdict(
            lambda: collections.defaultdict(list))
        self.submits = collections.defaultdict(
            lambda: collections.defaultdict(list))
        self.pr_submits = {}
        self.assessments = collections.defaultdict(list)
        self.viewed_content = collections.defaultdict(set)

    def post_solution(self, user_id, problem_id, time):
        self.times[user_id][problem_id].append(time)

    def score_task(self, user_id, problem_id, subtask_id, correct):
        time = (self.times[user_id][problem_id] or [None])[-1]
        self.submits[user_id][subtask_id].append((time, int(correct)))

    def create_submission(self, submission_id, user_id, problem_id):
        self.pr_submits[submission_id] = (user_id, problem_id)

    def assess(self, submission_id, reviewer, score, max_score):
        self.assessments[submission_id].append((reviewer, score, max_score))

    def view_content(self, user_id, content_id):
        self.viewed_content[user_id].add(content_id)


class Tasks:
    def __init__(self):
        self.tasks = collections.defaultdict(set)
        self.subtask_text = utils.NonEmptyDict()
        self.subtask_type = utils.NonEmptyDict()
        self.assessments = utils.NonEmptyDict()

    def add_task(self, problem_id, subtask_id, text, type_):
        self.tasks[problem_id].add(subtask_id)
        self.subtask_text[subtask_id] = text
        self.subtask_type[subtask_id] = type_

    def add_assessment(self, problem_id, name):
        self.assessments[problem_id] = name


class Modules:
    def __init__(self):
        self.modules = utils.NonEmptyDict()
        self.tasks = utils.NonEmptyDict()
        self.content = utils.NonEmptyDict()

    def add_module(self, link, name):
        link = normalize_module_url(link)
        if link not in self.modules:
            self.modules[link] = name

    def add_task(self, link, problem_id):
        link = normalize_module_url(link)
        self.tasks[problem_id] = link

    def add_content(self, link, content_id):
        link = normalize_module_url(link)
        self.content[content_id] = link

    def create_index(self):
        used = sorted(set(self.tasks.values()) | set(self.content.values()))
        for (index, link) in enumerate(used):
            name = self.modules.get(link)
            moduleid = last_nonempty(link.split('/'))
            self.modules[link] = (moduleid, index + 1, name)


class Content:
    def __init__(self):
        self.content = collections.defaultdict(set)

    def add_content(self, content_type, content_id):
        self.content[content_type].add(content_id)


class LogParser:
    handler = Registry()

    @handler.add(event_type='edx.ui.lms.outline.selected')
    def _outline_selected(self, item):
        event = json.loads(get_item(item, 'event'))
        (url, name) = get_items(event, ['target_url', 'target_name'])
        self.modules.add_module(url, name)

    @handler.add(event_type=['load_video', 'edx.video.loaded'])
    def _load_video(self, item):
        video_id = get_item(json.loads(get_item(item, 'event')), 'id')
        page = get_item(item, 'page')
        self.content.add_content('video', video_id)
        self.modules.add_content(page, video_id)

    @handler.add(event_type=['play_video', 'edx.video.played'])
    def _play_video(self, item):
        user_id = get_item(item, 'context.user_id')
        video_id = get_item(json.loads(get_item(item, 'event')), 'id')
        self.users.view_content(user_id, video_id)

    @handler.add(event_type='problem_check', event_source='server')
    def _problem_check_server(self, item):
        (problem_id, user_id) = get_items(
            item, ['event.problem_id', 'context.user_id'])
        subtasks = get_item(item, 'event.submission', type_=dict)
        for (subtask_id, subtask) in subtasks.items():
            (question, task_type) = get_items(
                subtask, ['question', 'response_type'])
            correct = get_item(subtask, 'correct', type_=bool)
            self.tasks.add_task(problem_id, subtask_id, question, task_type)
            self.users.score_task(user_id, problem_id, subtask_id, correct)

    @handler.add(event_type='edx.grades.problem.submitted')
    def _problem_submitted(self, item):
        (user_id, problem_id, page, time) = get_items(
            item, ['context.user_id', 'event.problem_id', 'referer', 'time'])
        self.modules.add_task(page, problem_id)
        self.users.post_solution(user_id, problem_id, convert_datetime(time))

    @handler.add(event_type='openassessmentblock.create_submission')
    def _create_submission(self, item):
        (submission_id, task_id, user_id, name, page) = get_items(
            item, ['event.submission_uuid', 'context.module.usage_key',
                   'context.user_id', 'context.module.display_name',
                   'referer'])
        self.users.create_submission(submission_id, user_id, task_id)
        self.modules.add_task(page, task_id)
        self.tasks.add_assessment(task_id, name)

    @handler.add(event_type=['openassessmentblock.self_assess',
                             'openassessmentblock.peer_assess',
                             'openassessmentblock.staff_assess'])
    def _assess_submission(self, item):
        (submission_id, user_id) = get_items(
            item, ['event.submission_uuid', 'context.user_id'])
        scores = get_item(item, 'event.parts', type_=list)
        points = sum(
            get_item(score, 'option.points', type_=int) for score in scores)
        max_points = sum(
            get_item(score, 'criterion.points_possible', type_=int)
            for score in scores)
        self.users.assess(submission_id, user_id, points, max_points)

    def __init__(self, file):
        self.users = Users()
        self.tasks = Tasks()
        self.modules = Modules()
        self.content = Content()

        self._parse(file)
        self.modules.create_index()

    def _parse(self, file):
        for (i, line) in enumerate(file):
            try:
                item = json.loads(line.split(':', maxsplit=1)[-1])
                LogParser.handler(self, item)
            except Exception as e:
                logging.warning('Error on process entry, line %d: %s', i, e)

    def get_student_solutions(self, user_id=None):
        if user_id is None:
            for userid in self.users.submits:
                yield from self.get_student_solutions(userid)
        else:
            submits = self.users.submits[user_id]
            for (taskid, tries) in submits.items():
                for (time, correct) in tries:
                    yield (user_id, taskid, correct, time)

    def get_student_content(self, user_id=None):
        if user_id is None:
            for userid in self.users.viewed_content:
                yield from self.get_student_content(userid)
        else:
            viewed = self.users.viewed_content[user_id]
            for (_, content) in self.content.content.items():
                for content_id in content:
                    yield (user_id, content_id, int(content_id in viewed))

    def get_assessments(self):
        for submission_id in self.users.pr_submits:
            (user_id, problem_id) = self.users.pr_submits[submission_id]
            problem_id = problem_id.split('@')[-1]
            assessments = self.users.assessments[submission_id]
            for (reviewer, score, max_score) in assessments:
                yield (user_id, problem_id, reviewer, score, max_score)

    def get_tasks(self, task_id=None):
        if task_id is None:
            task_ids = set(self.tasks.tasks) | set(self.tasks.assessments)
            for taskid in task_ids:
                yield from self.get_tasks(taskid)
        else:
            module = self.modules.modules[self.modules.tasks[task_id]]
            if task_id in self.tasks.tasks:
                for subtask in self.tasks.tasks[task_id]:
                    text = self.tasks.subtask_text.get(subtask) or 'NA'
                    yield (subtask, self.tasks.subtask_type[subtask],
                           text, *module)
            if task_id in self.tasks.assessments:
                name = self.tasks.assessments[task_id]
                yield (task_id.split('@')[-1], 'openassessment', name, *module)

    def get_content(self):
        for (content_type, content) in self.content.content.items():
            for contentid in content:
                module = self.modules.modules[self.modules.content[contentid]]
                yield (contentid, content_type, 'NA', *module)

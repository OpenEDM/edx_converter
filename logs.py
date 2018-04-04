import collections
import json
import logging
import re
from datetime import datetime

from utils import binarize, get_item, get_items


__all__ = ['LogParser']


MODULE_RE = re.compile(r'/courseware/(\w+)')


def try_parse_json(idx, line):
    try:
        return json.loads(line)
    except Exception as e:
        logging.warning('Error on parse json, line %d: %s', idx, e)
        return {}


def calc_score(score, max_score):
    try:
        return float(score)/float(max_score)
    except ValueError:
        return 0


def convert_datetime(timestr):
    timestr = timestr.split('.')[0]
    return datetime.strptime(
        timestr, '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y %H:%M:%S')


def parse_module_id(page):
    match = MODULE_RE.findall(page)
    return match[0] if match else ''


class LogParser:
    def _load_video(self, item):
        video_id = get_item(json.loads(get_item(item, 'event')), 'id')
        page = get_item(item, 'page')
        self.videos[video_id] = parse_module_id(page)

    def _play_video(self, item):
        user_id = str(get_item(item, 'context.user_id'))
        video_id = json.loads(get_item(item, 'event')).get('id', '')
        self.viewed_content['video'][user_id].add(video_id)

    def _problem_submit(self, item):
        (user_id, page, task_name, task_id,
         score, max_score, time) = get_items(
            item, ['event.user_id', 'referer', 'context.module.display_name',
                   'event.problem_id', 'event.weighted_earned',
                   'event.weighted_possible', 'time'])
        if task_name:
            self.problems[task_id] = (task_name, parse_module_id(page))
        self.submits[user_id][task_id].append(
            (*binarize(calc_score(score, max_score), self._threshold),
             convert_datetime(time)))

    def _create_submission(self, item):
        (submission_id, task_id, user_id) = get_items(
            item, ['event.submission_uuid', 'context.module.usage_key',
                   'context.user_id'])
        self.submissions[submission_id] = (user_id, task_id)

    def _assess_submission(self, item):
        (submission_id, user_id) = get_items(
            item, ['event.submission_uuid', 'context.user_id'])
        scores = get_item(item, 'event.parts', False) or {}
        points = sum(int(get_item(score, 'option.points'))
                     for score in scores)
        max_points = sum(int(get_item(score, 'criterion.points_possible'))
                         for score in scores)
        self.assessors[submission_id] = (user_id, points, max_points)

    def _default_subparser(self, item):
        pass

    def __init__(self, file, threshold):
        # video_id -> module_id
        self.videos = {}
        self.viewed_content = {
            # user_id -> {video_ids}
            'video': collections.defaultdict(set)
        }

        # task_id -> (task_name, module_id)
        self.problems = {}
        # user_id -> {task_id:[(score,correct,time)]}
        self.submits = collections.defaultdict(
            lambda: collections.defaultdict(list))

        # submission_id -> (user_id, task_id)
        self.submissions = {}

        # submission_id -> (user_id, score, max_score)
        self.assessors = {}

        self._subparsers = {
            'load_video': self._load_video,
            'edx.video.loaded': self._load_video,
            'play_video': self._play_video,
            'edx.video.played': self._play_video,
            'edx.grades.problem.submitted': self._problem_submit,
            'openassessmentblock.create_submission': self._create_submission,
            'openassessmentblock.self_assess': self._assess_submission,
            'openassessmentblock.peer_assess': self._assess_submission,
            'openassessmentblock.staff_assess': self._assess_submission,
        }

        self._threshold = threshold
        self._parse(file)

    def _parse(self, file):
        for (i, line) in enumerate(file):
            item = try_parse_json(i, line.split(':', maxsplit=1)[-1])
            parser = (self._subparsers.get(item.get('event_type', '')) or
                      self._default_subparser)
            try:
                parser(item)
            except Exception as e:
                logging.warning('Error on process entry, line %d: %s', i, e)

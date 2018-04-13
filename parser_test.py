import unittest

from logs import LogParser


class LogsTest(unittest.TestCase):
    LOG = r"""1:{"event_type": "edx.ui.lms.outline.selected", "event": "{\"target_url\": \"https://pages.local/1/0/\", \"target_name\": \"m1\"}"}
2:{"event_type": "load_video", "event": "{\"id\": \"v1\"}", "page": "https://pages.local/1/0/?opt"}
3:{"event_type": "play_video", "event": "{\"id\": \"v1\"}", "context": {"user_id": "uu"}}
4:{"event_type": "edx.ui.lms.outline.selected", "event": "{\"target_url\": \"https://pages.local/2/0/\", \"target_name\": \"m2\"}"}
5:{"event_type": "edx.grades.problem.submitted", "referer": "https://pages.local/2/0/", "time": "2018-01-02T09:30:00.000000", "context": {"user_id": "15"}, "event": {"problem_id": "pp"}}
6:{"event_type": "problem_check", "event_source": "server", "event": {"problem_id": "pp", "submission": {"t1": {"question": "", "response_type": "type", "correct": false}}}, "context": {"user_id": "15"}}
7:{"event_type": "edx.grades.problem.submitted", "referer": "https://pages.local/2/0/#qq", "time": "2018-01-02T10:00:00.000000", "context": {"user_id": "15"}, "event": {"problem_id": "pp"}}
8:{"event_type": "problem_check", "event_source": "server", "event": {"problem_id": "pp", "submission": {"t1": {"question": "QQ", "response_type": "type", "correct": true}}}, "context": {"user_id": "15"}}
9:{"event_type": "openassessmentblock.create_submission", "context": {"user_id": "uu", "module": {"usage_key": "block-v1:a+b+type@openassessment+block@bb", "display_name": "aa"}}, "event": {"submission_uuid": "ps1"}, "referer": "https://pages.local/2/0/"}
10:{"event_type": "openassessmentblock.peer_assess", "context": {"user_id": "u2"}, "event": {"submission_uuid": "ps1", "parts": [{"option": {"points": 2}, "criterion": {"points_possible": 3}}, {"option": {"points": 1}, "criterion": {"points_possible": 2}}]}}""".split('\n')

    COURSE = r"""type@chapter+block@1;type@problem;module 1
type@chapter+block@2;type@openassessment;module 2
type@chapter+block@3;type@video;module 3""".split('\n')

    def test_parse(self):
        report = LogParser(self.LOG, self.COURSE)

        self.assertSetEqual(
            set(report.get_student_solutions()),
            {('15', 't1', 0, '02.01.2018 09:30:00'),
             ('15', 't1', 1, '02.01.2018 10:00:00')})
        self.assertSetEqual(
            set(report.get_tasks()),
            {('t1', 'type', 'QQ', '2', 2, 'module 2'),
             ('bb', 'openassessment', 'aa',
              '2', 2, 'module 2')})
        self.assertSetEqual(
            set(report.get_student_content()),
            {('uu', 'v1', 1)})
        self.assertSetEqual(
            set(report.get_content()),
            {('v1', 'video', 'NA', '1', 1, 'module 1')})
        self.assertSetEqual(
            set(report.get_assessments()),
            {('uu', 'bb', 'u2', 3, 5)})


if __name__ == '__main__':
    unittest.main()

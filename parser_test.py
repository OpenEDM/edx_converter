import unittest

from gradereport import GradeReportParser
from ora import ORAParser
from logs import LogParser


class GradeReportTest(unittest.TestCase):
    DATA = """Student ID,Email,Username,Last Name,First Name,Grade,Test 1,Test 2,Test 3,Final Test,Cohort Name
1,a@a.a,AA,BB,0.5,0.1,0.8,0.7,0.4,N/A
2,b@a.a,AB,BB,Not Attempted,Not Attempted,Not Attempted,0.2,0.4,N/A
3,c@a.a,AC,BB,0.6,0.1,Not Available,0.9,0.4,N/A
4,d@a.a,AD,BB,0.7,Not Available,Not Attempted,0.2,0.4,N/A
5,e@a.a,AE,BB,0.8,0.7,Not Attempted,0.2,0.4,N/A
""".split('\n')

    def test_parse(self):
        report = GradeReportParser(self.DATA, 0.7)
        self.assertTupleEqual(report.get_tasks(), ('Test 1', 'Test 2', 'Test 3', 'Final Test'))
        self.assertSetEqual(set(report.get_userids()), {'1', '2', '3', '4', '5'})
        self.assertDictEqual(
            report.get_grades('2'), {
                'Test 2': (0.2, 0),
                'Test 3': (0.4, 0),
                'Final Test': (0.0, 0)
            })
        self.assertDictEqual(
            report.get_grades('3'), {
                'Test 2': (0.9, 1),
                'Test 3': (0.4, 0),
                'Final Test': (0.0, 0)
            })


class ORATest(unittest.TestCase):
    DATA = """Submission ID,Item ID,Anonymized Student ID,Date/Time Response Submitted,Assessment Details,Final Score Points Earned,Final Score Points Possible
AA,1,aa,10:00,"-- scorer_id: a12\n-- scorer_id: b15",10,15
AB,2,aa,10:00,"scorer_id: a14",14,14
""".split('\n')

    def test_parse(self):
        report = ORAParser(self.DATA)
        self.assertSetEqual(set(report), {'AA', 'AB'})

        aa = report['AA']
        self.assertEqual(aa.student_id, 'aa')
        self.assertSetEqual(set(aa.reviewers), {'a12', 'b15'})
        self.assertEqual(aa.score, 10)
        self.assertEqual(aa.max_score, 15)


class LogsTest(unittest.TestCase):
    DATA = r"""1:{"event_type": "load_video", "event": "{\"id\": \"v1\"}", "page": "course-v1:a+b/courseware/aa/bb"}
2:{"event_type": "play_video", "event": "{\"id\": \"v1\"}", "context": {"user_id": "uu"}}
3:{"event_type": "edx.grades.problem.submitted", "referer": "course-v1:a+b/courseware/aa/c", "time": "2018-01-02T09:30:00.000000", "context": {"module": {"display_name": "Test 1"}}, "event": {"user_id": 15, "problem_id": "pp", "weighted_earned": 5, "weighted_possible": 10}}
4:{"event_type": "edx.grades.problem.submitted", "referer": "course-v1:a+b/courseware/aa/c", "time": "2018-01-02T10:00:00.000000", "context": {"module": {"display_name": "Test 1"}}, "event": {"user_id": 15, "problem_id": "pp", "weighted_earned": 8, "weighted_possible": 10}}
5:{"event_type": "openassessmentblock.create_submission", "context": {"user_id": "uu", "module": {"usage_key": "block-v1:a+b+type@openassessment+block@bb"}}, "event": {"submission_uuid": "ps1"}}
6:{"event_type": "openassessmentblock.peer_assess", "context": {"user_id": "u2"}, "event": {"submission_uuid": "ps1", "parts": [{"option": {"points": 2}, "criterion": {"points_possible": 3}}, {"option": {"points": 1}, "criterion": {"points_possible": 2}}]}}""".split('\n')

    def test_parse(self):
        report = LogParser(self.DATA, 0.7)
        self.assertDictEqual(report.videos, {'v1': 'aa'})
        self.assertDictEqual(report.viewed_content['video'], {'uu': {'v1'}})
        self.assertDictEqual(report.problems, {'pp': ('Test 1', 'aa')})
        self.assertDictEqual(report.submits['15'], {
            'pp': [(0.5, 0, '02.01.2018 09:30:00'),
                   (0.8, 1, '02.01.2018 10:00:00')]})
        self.assertDictEqual(report.submissions, {
            'ps1': ('uu', 'block-v1:a+b+type@openassessment+block@bb')})
        self.assertDictEqual(report.assessors, {'ps1': ('u2', 3, 5)})


if __name__ == '__main__':
    unittest.main()
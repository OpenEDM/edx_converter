from course import CourseParser, CoursesParser
from answers import AnswersParser
from logs import LogParser
from csv5 import process_all_csvs


def convert(course_file, answers_file, courses_file, logs_file,
            encoding, output):
    optional_data_source = [
        (course_file, CourseParser),
        (answers_file, AnswersParser),
        (courses_file, CoursesParser)]

    optional_source = []
    for (filename, parser) in optional_data_source:
        if filename:
            with open(filename, encoding=encoding) as file:
                optional_source.append(parser(file))
        else:
            optional_source.append(parser([]))

    with open(logs_file, encoding=encoding) as logfile:
        parser = LogParser(logfile, *optional_source)

    process_all_csvs(output, encoding, parser)

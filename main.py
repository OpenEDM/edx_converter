#!/usr/bin/env python3

import argparse
import sys

from gradereport import GradeReportParser
from ora import ORAParser
from logs import LogParser
from csv5 import process_all_csvs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--encoding', type=str, default='utf8', help='Files encoding')
    parser.add_argument(
        '--threshold', type=float, default=0.7, help='Score threshold')
    parser.add_argument('--logs', type=str, required=True, help='Log file')
    parser.add_argument('--grade', type=str, help='Grade report')
    parser.add_argument('--ora', type=str, help='ORA data')
    parser.add_argument('output', type=str, help='Output csv prefix')
    return parser.parse_args()


def main():
    params = parse_args()

    if params.grade:
        with open(params.grade, encoding=params.encoding) as f:
            grade_report = GradeReportParser(f, params.threshold)
    else:
        grade_report = GradeReportParser(None, params.threshold)

    if params.ora:
        with open(params.ora, encoding=params.encoding) as f:
            ora_report = ORAParser(f)
    else:
        ora_report = ORAParser(None)

    with open(params.logs, encoding=params.encoding) as f:
        logs = LogParser(f, params.threshold)

    process_all_csvs(params.output, params.encoding, grade_report, logs, ora_report)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3

import argparse
import os.path
import sys

from logs import LogParser
from csv5 import process_all_csvs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--encoding', type=str, default='utf8', help='Files encoding')
    parser.add_argument('--logs', type=str, required=True, help='Log file')
    parser.add_argument('output', type=str, help='Output csv prefix')
    return parser.parse_args()


def main():
    params = parse_args()

    with open(params.logs, encoding=params.encoding) as f:
        logs = LogParser(f)

    if os.path.isdir(params.output):
        params.output = os.path.join(params.output, 'csv')

    process_all_csvs(
        params.output, params.encoding, logs)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

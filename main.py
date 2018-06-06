#!/usr/bin/env python3

import argparse
import os.path
import sys

import converter


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--encoding', type=str, default='utf8', help='Files encoding')
    parser.add_argument(
        '-l', '--logs', type=str, required=True, help='Log file')
    parser.add_argument(
        '-c', '--course', type=str, help='Course structure file')
    parser.add_argument(
        '-a', '--answers', type=str, help='Student answers file')
    parser.add_argument(
        '-C', '--courses', type=str, help='Course names file')
    parser.add_argument('output', type=str, help='Output csv prefix')
    return parser.parse_args()


def main():
    params = parse_args()

    if os.path.isdir(params.output):
        params.output = os.path.join(params.output, 'csv')

    converter.convert(
        params.course, params.answers, params.courses, params.logs,
        params.encoding, params.output)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

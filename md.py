#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

import markdown


def parse_args() -> Namespace:
  parser = ArgumentParser()
  parser.add_argument("markdown")
  return parser.parse_args()


def main() -> None:
  args = parse_args()


try:
  main()
except KeyboardInterrupt:
  pass


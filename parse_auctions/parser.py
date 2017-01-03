#!/usr/bin/env python3


import re


class Parser(object):

  def __init__(self):
    pass

  def parse_auction(self, auction_message):
    """Parses an auction message and returns a list of items."""

  def split_line(self, line):
    """Parses text and returns a timestamp, character, and message."""
    # Lines like: [Sun Jan 01 13:45:35 2017] Toon auctions, 'WTS Root'
    split_regex = r"^\[[^ ]+ ([^]]+)] ([^ ]+) auctions, '(.+)'$"
    pattern = re.compile(split_regex)
    match = pattern.match(line)
    return match.group(1), match.group(2), match.group(3)

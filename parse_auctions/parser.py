#!/usr/bin/env python3


import re

import dateutil.parser


class Item(object):

  def __init__(self, item_id, is_selling, price):
    self.item_id = item_id
    self.is_selling = is_selling
    self.price = price


class Parser(object):

  def __init__(self, test_item_table=None):
    if test_item_table:
      self.items = test_item_table

  def split_line(self, line):
    """Parses text and returns a timestamp, character, and message."""
    # Lines like: [Sun Jan 01 13:45:35 2017] Toon auctions, 'WTS Root'
    split_regex = r"^\[[^ ]+ ([^]]+)] ([^ ]+) auctions, '(.+)'$"
    pattern = re.compile(split_regex)
    match = pattern.match(line)
    if match is None:
      return None, None, None
    return match.group(1), match.group(2), match.group(3)

  def parse_timestamp(self, timestamp_str):
    """Parses the timestamp_str and returns a datetime."""
    # TODO: support timezones
    timestamp = dateutil.parser.parse(timestamp_str)
    return timestamp

  def parse_auction(self, auction_message):
    """Parses an auction message and returns a list of items."""
    lowercase_message = auction_message.lower()
    if (lowercase_message.startswith('wtb') or
        lowercase_message.startswith('buying')):
      is_selling = False
    else:
      is_selling = True


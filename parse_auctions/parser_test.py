#!/usr/bin/env python3

import collections
import datetime
import unittest

from parse_auctions import parser


TEST_ITEM_TABLE = {
    'cloak of shadows': 13,
    'ale': 17,
}

AUCTION_TEST_CASES = collections.OrderedDict([
    # Messages without prices
    ('Ale', [parser.Item(17, True, None)]),
    ('Cloak of Shadows, Ale', [
      parser.Item(13, True, None), parser.Item(17, True, None)]),
    ('WTS Ale', [parser.Item(17, True, None)]),
    ('WTB Ale', [parser.Item(17, False, None)]),
    ('WTS Cloak of Shadows WTB Ale', [
      parser.Item(13, True, None), parser.Item(17, False, None)]),
    ('WTS Cloak of ShadowsAle', [
      parser.Item(13, True, None), parser.Item(17, True, None)]),
    ('WTB Cloak of ShadowsAle', [
      parser.Item(13, False, None), parser.Item(17, False, None)]),
    # Messages with prices
    ('Ale 123', [parser.Item(17, True, 123)]),
    ('Ale 123pp', [parser.Item(17, True, 123)]),
    ('Ale 1k', [parser.Item(17, True, 1000)]),
    ('Ale 1.2', [parser.Item(17, True, 1200)]),
    ('Ale 1.2k', [parser.Item(17, True, 1200)]),
    ('Ale 1.2k Cloak of Shadows', [
      parser.Item(17, True, 1200), parser.Item(13, True, None)]),
    ('Ale 1.2k Cloak of Shadows 375', [
      parser.Item(17, True, 1200), parser.Item(13, True, 375)]),
    # Messages with fancy punctuation
    ('*=WTB=* Ale 123', [parser.Item(17, False, 123)]),
    ('=Ale 123', [parser.Item(17, True, 123)]),
    ('=Ale=Cloak of Shadows',
      [parser.Item(17, True, None), parser.Item(13, True, None)]),
    ('Ale: 123', [parser.Item(17, True, 123)]),
    ('Ale- 123', [parser.Item(17, True, 123)]),
    ('Ale << 123', [parser.Item(17, True, 123)]),
    ('Ale (123)', [parser.Item(17, True, 123)]),
    ('Ale: 123|Cloak of Shadows',
      [parser.Item(17, True, 123), parser.Item(13, True, None)]),
])


class ParserTest(unittest.TestCase):

  def setUp(self):
    self.parser = parser.Parser(test_item_table=TEST_ITEM_TABLE)

  def test_split_line(self):
    line = "[Sun Jan 01 13:45:35 2017] Toon auctions, 'WTS Ale'"
    timestamp, seller, auction = parser.split_line(line)
    self.assertEqual(timestamp, 'Jan 01 13:45:35 2017')
    self.assertEqual(seller, 'Toon')
    self.assertEqual(auction, 'WTS Ale')

  def test_split_line_complicated(self):
    message = "[]::''WTS Ale"
    line = "[Sun Jan 01 13:45:35 2017] Toon auctions, '{}'".format(message)
    timestamp, seller, auction = parser.split_line(line)
    self.assertEqual(timestamp, 'Jan 01 13:45:35 2017')
    self.assertEqual(seller, 'Toon')
    self.assertEqual(auction, message)

  def test_split_line_fails_gracefully(self):
    line = 'not a good log  message'
    timestamp, seller, auction = parser.split_line(line)
    self.assertEqual(timestamp, None)
    self.assertEqual(seller, None)
    self.assertEqual(auction, None)

  def test_parse_timestamp(self):
    timestamp_str = 'Jan 02 13:45:35 2017'
    expected = datetime.datetime(2017, 1, 2, 13, 45, 35)
    actual = parser.parse_timestamp(timestamp_str)
    self.assertEqual(actual, expected)

  def test_parse_timestamp_normalized(self):
    timestamp_str = 'Jan 02 13:45:35 2017'
    server_time = datetime.datetime(2017, 1, 2, 15, 1, 0)
    client_time = datetime.datetime(2017, 1, 2, 14, 00, 30)
    # The server is 1 hour and 30 seconds ahead of the client.
    offset = server_time - client_time
    expected = datetime.datetime(2017, 1, 2, 14, 46, 5)
    actual = parser.parse_timestamp_normalized(timestamp_str, offset)
    self.assertEqual(actual, expected)

  def test_parse_auction(self):
    for auction_message, expected_output in AUCTION_TEST_CASES.items():
      actual_output = self.parser.parse_auction(auction_message)
      self.assertEqual(
          actual_output, expected_output,
          msg='Auction: {}, Expected: {}, Actual:{}'.format(
            auction_message, expected_output, actual_output))


if __name__ == '__main__':
  unittest.main()

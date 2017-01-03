#!/usr/bin/env python3

import unittest

import parse_auctions.parser

class ParserTest(unittest.TestCase):

  def test_split_line(self):
    line = "[Sun Jan 01 13:45:35 2017] Toon auctions, 'WTS Root'"
    parser = parse_auctions.parser.Parser()
    timestamp, seller, auction = parser.split_line(line)
    self.assertEqual(timestamp, 'Jan 01 13:45:35 2017')
    self.assertEqual(seller, 'Toon')
    self.assertEqual(auction, 'WTS Root')

  def test_split_line_complicated(self):
    message = "[]::''WTS Root"
    line = "[Sun Jan 01 13:45:35 2017] Toon auctions, '{}'".format(message)
    parser = parse_auctions.parser.Parser()
    timestamp, seller, auction = parser.split_line(line)
    self.assertEqual(timestamp, 'Jan 01 13:45:35 2017')
    self.assertEqual(seller, 'Toon')
    self.assertEqual(auction, message)

  def test_split_line_fails_gracefully(self):
    line = 'not a good log  message'
    parser = parse_auctions.parser.Parser()
    timestamp, seller, auction = parser.split_line(line)
    self.assertEqual(timestamp, None)
    self.assertEqual(seller, None)
    self.assertEqual(auction, None)


if __name__ == '__main__':
  unittest.main()

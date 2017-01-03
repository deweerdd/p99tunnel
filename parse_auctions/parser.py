#!/usr/bin/env python3


import re

import dateutil.parser
import pytrie


IS_SELLING_TRIE = pytrie.StringTrie(
    wts=True, selling=True, wtb=False, buying=False)
PRICE_REGEX = re.compile(r'^\s*(\d*\.?\d*)(k|p|pp)?$')

DEBUG = True


def debug_print(message):
  if DEBUG:
    print(message)


def split_line(line):
  """Parses text and returns a timestamp, character, and message."""
  # Lines like: [Sun Jan 01 13:45:35 2017] Toon auctions, 'WTS Ale'
  split_regex = r"^\[[^ ]+ ([^]]+)] ([^ ]+) auctions, '(.+)'$"
  pattern = re.compile(split_regex)
  match = pattern.match(line)
  if match is None:
    return None, None, None
  return match.group(1), match.group(2), match.group(3)


def parse_timestamp(timestamp_str):
  """Parses the timestamp_str and returns a datetime."""
  # TODO: support timezones
  timestamp = dateutil.parser.parse(timestamp_str)
  return timestamp


def is_price(s):
  return PRICE_REGEX.match(s)


def parse_price(price_str):
  match = PRICE_REGEX.match(price_str)
  amount = match.group(1)
  if len(amount) == 0:
    return None
  denomination = match.group(2)
  if denomination == 'p' or denomination == 'pp':
    factor = 1
  elif denomination == 'k':
    factor = 1000
  # If someone says "WTS GEB 1.8" they probably mean 1.8k
  elif '.' in amount and not amount.endswith('.'):
    factor = 1000
  # If someone says "WTS Ale 15" they probably mean 15pp
  else:
    factor = 1
  if '.' in amount:
    return int(float(amount) * factor)
  else:
    return int(amount) * factor


class Item(object):

  def __init__(self, item_id, is_selling, price=None):
    self.item_id = item_id
    self.is_selling = is_selling
    self.price = price

  def __eq__(self, other):
    if self.item_id != other.item_id:
      return False
    if self.is_selling != other.is_selling:
      return False
    if self.price != other.price:
      return False
    return True

  def __repr__(self):
    message = ''
    if self.is_selling:
      message += 'WTS '
    else:
      message += 'WTB '
    message += 'Item {}'.format(self.item_id)
    if self.price != None:
      message += ' {}pp'.format(self.price)
    return message


class Parser(object):

  def __init__(self, test_item_table=None):
    if test_item_table:
      self.items = pytrie.StringTrie(**test_item_table)

  def parse_auction(self, auction_message):
    """Parses an auction message and returns a list of items.

    Parsing strategy:
    - Go one character at a time.
    - Start in WTS mode (since some people just say /auc Ale)
    - If we see WTB or "Buying" then switch to buying mode
    - If we see WTS or "Selling" then switch to selling mode
    - After consuming each character, check the items trie to see if anything
      matches
    - If the current characters aren't a prefix for anything, then throw away
      the current characters and start processing again.
    - If the current characters are a full match for an item, then register that
      item.
    - After finding an item, try to process the next characters as a price.
    """
    all_items = []
    lowercase_message = auction_message.lower()
    is_selling = True
    item = None
    # Find the items
    message_so_far = ''
    # TODO: below is complicated.  Figure out a way to refactor it.
    for c in lowercase_message:
      message_so_far += c
      message_so_far = message_so_far.lstrip()
      debug_print(message_so_far)
      is_selling_matches = IS_SELLING_TRIE.items(prefix=message_so_far)
      matches = self.items.items(prefix=message_so_far)
      # If one item is done, finish it.
      if item and item.price and not is_price(message_so_far):
        debug_print('Finish item with price')
        item = None
        message_so_far = c
      elif item and not is_price(message_so_far):
        debug_print('Finish item without price')
        item = None
      # Try to find the price of the previous item or the next item.
      if item and is_price(message_so_far):
        debug_print('Update price')
        item.price = parse_price(message_so_far)
      elif not matches and not is_selling_matches:
        debug_print('No match')
        message_so_far = ''
        item = None
      elif (len(is_selling_matches) == 1 and
            is_selling_matches[0][0] == message_so_far):
        debug_print('is selling match')
        is_selling = is_selling_matches[0][1]
        message_so_far = ''
        item = None
      elif (len(matches) == 1 and matches[0][0] == message_so_far):
        debug_print('item match')
        item = Item(matches[0][1], is_selling)
        all_items.append(item)
        message_so_far = ''
    return all_items

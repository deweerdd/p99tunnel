#!/usr/bin/env python3

import datetime
import http
import io
import os
import pickle
import re
import time

import dateutil.parser
import requests


API_ENDPOINT = 'https://p99tunnel.com/upload_log'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_LINES_PATH = os.path.join(SCRIPT_DIR, '.processed-lines')
CACHED_LOG_DIR_PATH = os.path.join(SCRIPT_DIR, '.log-dir')

LOG_NAMES_REGEX = re.compile(r'eqlog_(.*)_project1999.txt')
TIMESTAMP_REGEX = re.compile(r'^\[[^ ]+ ([^]]+)]')
MY_AUCTION_REGEX = re.compile(r"^\[[^ ]+ [^]]+] You auction, '.+'$")
OTHER_AUCTION_REGEX = re.compile(r"^\[[^ ]+ [^]]+] [^ ]+ auctions, '.+'$")

UTF8_HEADER = {'Content-Encoding': 'utf-8'}

class NamedStream(object):

  def __init__(self, name, stream):
    self.name = name
    self.stream = stream

  def __repr__(self):
    return self.name

  def readline(self):
    return self.stream.readline()

  def tell(self):
    return self.stream.tell()

  def seek(self, offset):
    return self.stream.seek(offset)


class ProcessedLines(object):

  def __init__(self, path=PROCESSED_LINES_PATH):
    self.already_processed = {}
    if os.path.isfile(path):
      with open(path, 'rb') as f:
        self.already_processed = pickle.load(f)
        print('Starting at these lines for these characters:')
        print(str(self.already_processed))

  def update_in_memory(self, stream, last_line):
    self.already_processed[stream.name] = last_line

  def save_to_disk(self, path=PROCESSED_LINES_PATH):
    with open(path, 'wb') as f:
      pickle.dump(self.already_processed, f, protocol=0)

  def get(self, stream_name):
    return self.already_processed.get(stream_name)


def get_log_directory():
  print('Getting log directory...')
  if os.path.isfile(CACHED_LOG_DIR_PATH):
    with open(CACHED_LOG_DIR_PATH, 'r') as f:
      path = f.read().strip()
      print('  Log directory: ' + path)
      return path
  path = input('Please paste in the path to your log directory: ').strip()
  path = os.path.expanduser(path)
  assert os.path.isdir(path)
  with open(CACHED_LOG_DIR_PATH, 'w') as f:
    print('  Caching log directory...')
    f.write(path)
    return path


def get_log_streams(log_dir):
  print('Opening up log streams...')
  names = os.listdir(log_dir)
  streams = []
  for name in names:
    match = LOG_NAMES_REGEX.match(name)
    if match:
      print('  Opening a stream for: ' + name)
      character_name = match.group(1)
      path = os.path.join(log_dir, name)
      streams.append(NamedStream(name=character_name, stream=io.open(path)))
    else:
      print('  Not a p99 log: ' + name)
  return streams


def get_time(log_line):
  match = TIMESTAMP_REGEX.match(log_line)
  timestamp_str = match.group(1)
  return dateutil.parser.parse(timestamp_str)


def consume_up_to(stream, last_line):
  print('Getting to the new stuff in stream: ' + stream.name)
  if last_line is None:
    return
  last_time = get_time(last_line)
  last_old_offset = stream.tell()
  while True:
    line = stream.readline()
    # We got to the end of the file without finding a time after the last line
    if not line:
      return
    time = get_time(line)
    if time > last_time:
      stream.seek(last_old_offset)
      return
    last_old_offset = stream.tell()


def get_local_time_str():
  return datetime.datetime.now().replace(microsecond=0).isoformat()


def upload_auction(auction):
  now_str = get_local_time_str()
  post_body = '{} {}'.format(now_str, auction).encode('utf-8')
  response = requests.post(API_ENDPOINT, data=post_body, headers=UTF8_HEADER)
  if response.status_code != 200:
    print('Bad response: ', response)


def consume_log_output(stream, last_line):
  while True:
    line = stream.readline()
    # The stream doesn't have any more output for us to consume
    if not line:
      return last_line
    last_line = line
    # I auctioned something, which means I need to reformat the line to look
    # like a generic auction
    match = MY_AUCTION_REGEX.match(line)
    if match:
      line = line.replace(
        ' You auction, ', ' {} auctions, '.format(stream.name))
    # The line is a valid auction
    match = OTHER_AUCTION_REGEX.match(line)
    if match:
      upload_auction(line)


def main():
  log_dir = get_log_directory()
  log_streams = get_log_streams(log_dir)
  processed_lines = ProcessedLines()
  for stream in log_streams:
    consume_up_to(stream, processed_lines.get(stream.name))
  print('Streaming log updates...')
  # TODO: use a request session so that only one TCP connection gets opened.
  # Opening and closing oodles of connections is probably slowing things down.
  while True:
    for stream in log_streams:
      last_line = consume_log_output(stream, processed_lines.get(stream.name))
      processed_lines.update_in_memory(stream, last_line)
    processed_lines.save_to_disk()
    time.sleep(10)


if __name__ == '__main__':
  main()

#!/usr/bin/env python3


import datetime
import http.server

import db
from parse_auctions import parser


ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'

PARSER = parser.Parser()


def get_client_time_offset(now, client_time_str):
  """Get the offset between client time and server time.

  We want this because EQ log messages don't have a timezone and are in client
  time.  That means that, in order to get something reasonably consistent
  between different clients, we need to know each client's time skew.  Thus,
  each client sends us their local time, and the server figures out how
  different that is from server time.

  We don't just want to use something like datetime.datetime.now().timestamp()
  because that would normalize everything into UTC timestamps, and we want to
  capture the client timezone too.

  This offset should be ADDED to client times to get server times.
  """
  client_datetime = datetime.datetime.strptime(client_time_str, ISO_FORMAT)
  return now - client_datetime


class RequestHandler(http.server.BaseHTTPRequestHandler):

  def do_POST(self):
    self.log_message('New request')
    if self.path != '/upload_log':
      self.send_error(404)
    content_length = int(self.headers.get('content-length', 0))
    body = self.rfile.read(content_length).decode('utf-8').strip()
    client_time_str, sep, log_message = body.partition(' ')
    now = datetime.datetime.now()
    if not sep or not log_message:
      self.send_error(400, 'Need a timestamp followed by an EQ log message')
      return
    log_timestamp, character, auction = parser.split_line(log_message)
    if not log_timestamp or not character or not auction:
      self.send_error(400, 'Need a valid auction message')
      return
    client_time_offset = get_client_time_offset(now, client_time_str)
    normalized_time = parser.parse_timestamp_normalized(
        log_timestamp, client_time_offset)
    character_id = db.get_or_create_character(character)
    items = PARSER.parse_auction(auction)
    # TODO: check for duplicate items before inserting it into the db
    raw_id = db.add_raw_auction(normalized_time, character_id, auction)
    for item in items:
      db.add_clean_auction(
          raw_id, character_id, item.item_id, normalized_time,
          item.is_selling, item.price)
    self.send_response(200)
    self.end_headers()


def main():
  print('Serving /upload_log on port 8000')
  server_address = ('', 8000)
  httpd = http.server.HTTPServer(server_address, RequestHandler)
  httpd.serve_forever()


if __name__ == '__main__':
  main()

#!/usr/bin/env python3

import os

import psycopg2


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
PASSWORD_FILE_PATH = os.path.join(ROOT_PATH, 'database-password')
DB_NAME = 'p99tunnel'
DB_USER = 'p99tunnel'

CACHED_CONNECTION = None


def get_db_password():
  with open(PASSWORD_FILE_PATH, 'r') as password_file:
    return password_file.read().strip()


def connect():
  password = get_db_password()
  return psycopg2.connect(
      dbname=DB_NAME, user=DB_USER, password=password,
      host='localhost')


def get_or_create_connection():
  global CACHED_CONNECTION
  if CACHED_CONNECTION is None:
    CACHED_CONNECTION = connect()
  return CACHED_CONNECTION


def get_or_create_character(name):
  """Returns the ID associated with name, creating a row if necessary."""
  with get_or_create_connection() as conn:
    with conn.cursor() as cur:
      cur.execute('SELECT id FROM characters WHERE name = %s', (name,))
      result = cur.fetchone()
      if result:
        return result[0]
      cur.execute(
          'INSERT INTO characters (name) VALUES (%s) RETURNING id', (name,))
      result = cur.fetchone()
      return result[0]

def add_raw_auction(timestamp, character_id, message):
  """Adds a raw auction to the db and returns its ID."""
  with get_or_create_connection() as conn:
    with conn.cursor() as cur:
      cur.execute(
          'INSERT INTO raw_auctions (timestamp, character_id, message) '
          'VALUES (%s, %s, %s) RETURNING id',
          (timestamp, character_id, message))
      result = cur.fetchone()
      return result[0]


def add_clean_auction(
    raw_auction_id, character_id, item_id, timestamp, is_selling, price):
  with get_or_create_connection() as conn:
    with conn.cursor() as cur:
      cur.execute(
          'INSERT INTO clean_auctions ( '
          '  raw_auction_id, character_id, item_id, timestamp, is_selling, '
          '  price) '
          'VALUES (%s, %s, %s, %s, %s, %s)',
          (raw_auction_id, character_id, item_id, timestamp, is_selling, price))

def get_all_items():
  with get_or_create_connection() as conn:
    with conn.cursor() as cur:
      cur.execute('SELECT id, canonical_name FROM items')
      return cur.fetchall()

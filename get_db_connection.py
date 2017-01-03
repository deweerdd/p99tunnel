#!/usr/bin/env python3

import os

import psycopg2


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
PASSWORD_FILE_PATH = os.path.join(ROOT_PATH, 'database-password')
DB_NAME = 'p99tunnel'
DB_USER = 'p99tunnel'


def get_db_password():
  with open(PASSWORD_FILE_PATH, 'r') as password_file:
    return password_file.read().strip()

def connect():
  password = get_db_password()
  return psycopg2.connect(
      dbname=DB_NAME, user=DB_USER, password=password,
      host='localhost')

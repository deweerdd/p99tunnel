#!/usr/bin/env python3

import csv

import get_db_connection


def main():
  with open('items.csv', 'r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    with get_db_connection.connect() as conn:
      with conn.cursor() as cur:
        for row in csv_reader:
          cur.execute(
              'INSERT INTO items (wiki_link, canonical_name) VALUES (%s, %s)',
              (row['wiki_link'], row['name']))


if __name__ == '__main__':
  main()

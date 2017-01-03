#!/usr/bin/env python3


import get_db_connection


# The limits on character fields were determined by looking at a sample of logs
# and figuring out how big things could be.
CREATE_TABLE_STATEMENTS = [
  """CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    name varchar(16)
  );""",
  """CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    wiki_link varchar(128),
    canonical_name varchar(128)
  );""",
  """CREATE TABLE item_names (
    id SERIAL PRIMARY KEY,
    item_id integer REFERENCES items(id),
    name varchar(128)
  );""",
  """CREATE TABLE raw_auctions (
    id SERIAL PRIMARY KEY,
    timestamp timestamp,
    character_id integer REFERENCES characters(id),
    message varchar(1024)
  );""",
  """CREATE TABLE clean_auctions (
    id SERIAL PRIMARY KEY,
    raw_auctions_id integer REFERENCES raw_auctions(id),
    character_id integer REFERENCES characters(id),
    item_id integer REFERENCES items(id),
    timestamp timestamp,
    is_selling bool,
    price integer
  );""",
]


def main():
  with get_db_connection.connect() as conn:
    with conn.cursor() as cur:
      for statement in CREATE_TABLE_STATEMENTS:
        cur.execute(statement)


if __name__ == '__main__':
  main()

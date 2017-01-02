#!/usr/bin/env python3

import bs4
import urllib.request

BASE_WIKI_URL = 'http://wiki.project1999.com'
# For some reason, if we don't use pageuntil=A to get the first page, we miss
# out on some stuff like '2nd Piece of Staff'
WIKI_ITEMS_URL = BASE_WIKI_URL + '/index.php?title=Category:Items&pageuntil=A'


class Item(object):
  """An item with a name and a wiki link."""

  def __init__(self, name, wiki_path):
    assert wiki_path.startswith('/')
    self.name = name
    self.wiki_link = BASE_WIKI_URL + wiki_path

  def __repr__(self):
    return self.name


def parse_one_page(url_to_scrape):
  print('Parsing Page: {}'.format(url_to_scrape))
  page = urllib.request.urlopen(url_to_scrape)
  scraper = bs4.BeautifulSoup(page)
  links = scraper.find(id='mw-pages')
  items = []
  next_url = None
  for link in links.find_all('a'):
    href = link.get('href')
    if 'index.php?' not in href:
      items.append(Item(link.get('title'), href))
    if 'next 200' == link.string:
      next_url = BASE_WIKI_URL + href
  return items, next_url


def main():
  next_url = WIKI_ITEMS_URL
  items = []
  while next_url is not None:
    new_items, next_url = parse_one_page(next_url)
    items += new_items
  print(len(items))


if __name__ == '__main__':
  main()

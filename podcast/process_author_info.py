#!/usr/bin/env python3
import sys
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = sys.argv[1]
html = sys.stdin.read()
soup = BeautifulSoup(html, 'html.parser')

author_url = None

# Try toplink third link
toplink = soup.find('p', class_='toplink')
if toplink:
    links = toplink.find_all('a')
    if len(links) >= 2:
        author_url = links[2].get('href', '')

# Fallback to nav third link
if not author_url:
    nav = soup.find('nav')
    if nav:
        links = nav.find_all('a')
        if len(links) >= 3:
            author_url = links[2].get('href', '')

if not author_url:
    sys.exit(0)

author_url = urljoin(base_url, author_url)

# Fetch author page
with urllib.request.urlopen(author_url) as response:
    author_html = response.read().decode('utf-8')

author_soup = BeautifulSoup(author_html, 'html.parser')

# Clean author page
for nav in author_soup.find_all('nav'):
    nav.decompose()

h1 = author_soup.find('h1')
div_data = author_soup.find('div', class_='data')
p_texto = author_soup.find_all('p', class_='texto-sem-espaco')

new_body = author_soup.new_tag('body')
if h1:
    new_body.append(h1.extract())
if div_data:
    new_body.append(div_data.extract())
for p in p_texto:
    new_body.append(p.extract())
    new_body.append(author_soup.new_tag('br'))

author_soup.body.replace_with(new_body)
print(author_soup)


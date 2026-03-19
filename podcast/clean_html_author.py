#!/usr/bin/env python3
import sys
from bs4 import BeautifulSoup

html = sys.stdin.read()
soup = BeautifulSoup(html, 'html.parser')

for nav in soup.find_all('nav'):
    nav.decompose()

# Extract elements
h1 = soup.find('h1')
div_data = soup.find('div', class_='data')
p_texto = soup.find_all('p', class_='texto-sem-espaco')

# Create new body
new_body = soup.new_tag('body')
if h1:
    new_body.append(h1.extract())
if div_data:
    new_body.append(div_data.extract())
for p in p_texto:
    new_body.append(p.extract())
    new_body.append(soup.new_tag('br'))

soup.body.replace_with(new_body)

print(soup)

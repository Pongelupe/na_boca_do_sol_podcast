#!/usr/bin/env python3
import sys
import re
from bs4 import BeautifulSoup

html = sys.stdin.read()
soup = BeautifulSoup(html, 'html.parser')

hrs = soup.find_all('hr')
if len(hrs) >= 2:
    current = hrs[0].next_sibling
    while current and current != hrs[1]:
        next_sibling = current.next_sibling
        if hasattr(current, 'decompose'):
            current.decompose()
        current = next_sibling

for tag in soup.find_all(['nav', 'footer', 'img', 'hr', 'table']):
    tag.decompose()
for p in soup.find_all('p', class_=['toplink', 'link', 'note']):
    p.decompose()
for p in soup.find_all('div', class_=['datas']):
    p.decompose()

# Clean text for better TTS rhythm
text = str(soup)
text = re.sub(r'\^?\(\d+\)', '', text)  # Remove footnote markers
text = re.sub(r'[★]+', '', text)  # Remove star separators

print(text)

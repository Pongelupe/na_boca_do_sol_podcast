#!/usr/bin/env python3
import sys
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

for tag in soup.find_all(['nav', 'footer', 'img', 'hr']):
    tag.decompose()
for toplink in soup.find_all('p', class_='toplink'):
    toplink.decompose()

print(soup)

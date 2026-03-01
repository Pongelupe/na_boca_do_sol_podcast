#!/usr/bin/env python3
import sys
import re
from bs4 import BeautifulSoup

html = sys.stdin.read()
soup = BeautifulSoup(html, 'html.parser')

# Remove navigation between first HR and first substantial content (h4 or p)
hrs = soup.find_all('hr')
if len(hrs) >= 1:
    current = hrs[0].next_sibling
    while current:
        next_sibling = current.next_sibling
        # Stop if we hit substantial content (headings or paragraphs with text)
        if hasattr(current, 'name'):
            if current.name in ['h4', 'h3', 'h2', 'h1']:
                break
            if current.name == 'p' and current.get_text(strip=True) and len(current.get_text(strip=True)) > 50:
                break
        # Remove only navigation links and empty elements
        if hasattr(current, 'name') and current.name == 'p':
            if current.get('class') and 'toplink' in current.get('class'):
                current.decompose()
        current = next_sibling

for tag in soup.find_all(['nav', 'footer', 'img', 'hr', 'table']):
    tag.decompose()
for tag in soup.find_all('sup'):  # Remove superscript footnote references
    tag.decompose()
for p in soup.find_all('p', class_=['toplink', 'link', 'note']):
    p.decompose()
for p in soup.find_all('div', class_=['datas']):
    p.decompose()

# Clean text for better TTS rhythm
text = str(soup)
text = re.sub(r'\^?\(\d+\*?\)', '', text)  # Remove footnote markers like (9) and (1*)
text = re.sub(r'\s*\^\s*', ' ', text)  # Remove standalone ^ characters
text = re.sub(r'[★]+', '', text)  # Remove star separators

print(text)

#!/usr/bin/env python3
import sys
import re
from bs4 import BeautifulSoup

def extract_metadata(html_file):
    with open(html_file) as f:
        soup = BeautifulSoup(f, 'html.parser')

    h1 = soup.find('h1')
    h2 = soup.find('h2')
    h3 = soup.find('h3')
    h4 = soup.find('h4')

    return {
        'title': h1.get_text(strip=True) if h1 else 'Título desconhecido',
        'author': h2.get_text(strip=True) if h2 else 'Autor desconhecido',
        'year': h3.get_text(strip=True) if h3 else None,
        'chapter': h4.get_text(strip=True) if h4 else None
    }

def process_template(template_file, biografy_file, content_file, html_file):
    with open(template_file) as f:
        template = f.read()

    with open(biografy_file) as f:
        biografy = f.read()

    with open(content_file) as f:
        content = f.read()
        line_count = len(content.splitlines())

    metadata = extract_metadata(html_file)

    result = template.replace('{{BIOGRAFY}}', biografy)
    result = result.replace('{{CONTENT}}', content)
    result = result.replace('{{LINE_COUNT}}', str(line_count))
    result = result.replace('{{TITLE}}', metadata['title'])
    result = result.replace('{{TEXT_INFO}}',
                            f"Escrito por {metadata['author']} em {metadata['year']}" if metadata['year'] else f"Capítulo {metadata['chapter']}")

    print(result)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Uso: process_template.py <template> <biografy> <content> <html>")
        sys.exit(1)

    process_template(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

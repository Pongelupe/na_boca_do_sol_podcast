FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    lynx \
    espeak-ng \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY podcast.sh .
COPY script.txt .
COPY *.py ./
#COPY clean_html_article.py .
#COPY clean_html_author.py .

RUN chmod +x podcast.sh

ENTRYPOINT ["./podcast.sh"]

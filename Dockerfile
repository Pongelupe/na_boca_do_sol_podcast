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

COPY podcast.sh kokoro_tts.py clean_html_*.py process_author_info.py process_template.py script.txt ./
COPY sounds/ ./sounds/
RUN chmod +x podcast.sh

ENTRYPOINT ["./podcast.sh"]

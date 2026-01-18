FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    lynx \
    espeak-ng \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

COPY podcast.sh kokoro_tts.py clean_html_*.py process_author_info.py process_template.py script.txt ./
COPY sounds/ ./
RUN chmod +x podcast.sh

ENTRYPOINT ["./podcast.sh"]

#!/usr/bin/env python3
import sys
import soundfile as sf
import os
from kokoro import KPipeline

os.environ['LD_LIBRARY_PATH'] = '/usr/lib'

if len(sys.argv) < 3:
    print("Usage: kokoro_tts.py <input_file> <output_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as f:
    text = f.read()

pipeline = KPipeline(lang_code='p')  # Brazilian Portuguese
audio_chunks = []

for _, _, audio in pipeline(text, voice='pm_alex'):
    audio_chunks.append(audio)

import numpy as np
full_audio = np.concatenate(audio_chunks)
sf.write(output_file, full_audio, 24000)
print(f"✅ Audio saved: {output_file}")

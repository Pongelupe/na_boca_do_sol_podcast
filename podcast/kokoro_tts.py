#!/usr/bin/env python3
import sys
import warnings
warnings.filterwarnings('ignore')
import soundfile as sf
import numpy as np
from kokoro import KPipeline
import os
import json

if len(sys.argv) < 3:
    print("Usage: kokoro_tts.py <input_file> <output_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as f:
    text = f.read()

pipeline = KPipeline(lang_code='p', repo_id='hexgrad/Kokoro-82M')
audio_chunks = []
timestamps = []
offset = 0.0

# Split by pause/sound markers
parts = text.replace('\n\n', '|PAUSE:0.5|').split('|')

for part in parts:
    if part.startswith('PAUSE:'):
        duration = float(part.split(':')[1])
        pause = np.zeros(int(24000 * duration))
        audio_chunks.append(pause)
        offset += len(pause) / 24000
    elif part.startswith('SOUND:'):
        sound_file = part.split(':')[1]
        sound_path = f"sounds/{sound_file}"
        if os.path.exists(sound_path):
            try:
                sound_data, sound_rate = sf.read(sound_path)
                if len(sound_data.shape) > 1:
                    sound_data = np.mean(sound_data, axis=1)
                if sound_rate != 24000:
                    ratio = 24000 / sound_rate
                    new_length = int(len(sound_data) * ratio)
                    sound_data = np.interp(np.linspace(0, len(sound_data), new_length), 
                                         np.arange(len(sound_data)), sound_data)
                audio_chunks.append(sound_data.astype(np.float32))
                offset += len(sound_data) / 24000
                print(f"Added sound: {sound_file}")
            except Exception as e:
                print(f"Error loading {sound_file}: {e}")
    elif part.strip():
        seg_start = offset
        for _, _, audio in pipeline(part.strip(), voice='pm_alex'):
            audio_chunks.append(audio)
            offset += len(audio) / 24000
        timestamps.append({
            "start": round(seg_start, 3),
            "end": round(offset, 3),
            "text": part.strip()
        })

full_audio = np.concatenate(audio_chunks)
sf.write(output_file, full_audio, 24000, format='WAV')
print(f"✅ Audio saved: {output_file}")

ts_file = output_file.rsplit('.', 1)[0] + '_timestamps.json'
with open(ts_file, 'w', encoding='utf-8') as f:
    json.dump({"segments": timestamps}, f, ensure_ascii=False, indent=2)
print(f"✅ Timestamps saved: {ts_file}")

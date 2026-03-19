#!/usr/bin/env python3
import sys
import warnings
warnings.filterwarnings('ignore')
import soundfile as sf
import numpy as np
from kokoro import KPipeline
import os

if len(sys.argv) < 3:
    print("Usage: kokoro_tts.py <input_file> <output_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as f:
    text = f.read()

pipeline = KPipeline(lang_code='p', repo_id='hexgrad/Kokoro-82M')
audio_chunks = []

# Split by pause/sound markers
parts = text.replace('\n\n', '|PAUSE:0.5|').split('|')

for part in parts:
    if part.startswith('PAUSE:'):
        duration = float(part.split(':')[1])
        pause = np.zeros(int(24000 * duration))
        audio_chunks.append(pause)
    elif part.startswith('SOUND:'):
        sound_file = part.split(':')[1]
        sound_path = f"sounds/{sound_file}"
        if os.path.exists(sound_path):
            try:
                sound_data, sound_rate = sf.read(sound_path)
                # Convert to mono if stereo
                if len(sound_data.shape) > 1:
                    sound_data = np.mean(sound_data, axis=1)
                # Simple resampling if needed
                if sound_rate != 24000:
                    ratio = 24000 / sound_rate
                    new_length = int(len(sound_data) * ratio)
                    sound_data = np.interp(np.linspace(0, len(sound_data), new_length), 
                                         np.arange(len(sound_data)), sound_data)
                audio_chunks.append(sound_data.astype(np.float32))
                print(f"Added sound: {sound_file}")
            except Exception as e:
                print(f"Error loading {sound_file}: {e}")
    elif part.strip():
        for _, _, audio in pipeline(part.strip(), voice='pm_alex'):
            audio_chunks.append(audio)

full_audio = np.concatenate(audio_chunks)
sf.write(output_file, full_audio, 24000, format='WAV')
print(f"✅ Audio saved: {output_file}")

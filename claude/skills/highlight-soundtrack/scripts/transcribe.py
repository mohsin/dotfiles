# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["faster-whisper", "librosa"]
# ///
"""Word-timed lyrics from a recording (live/phone audio where LRCLIB timings don't apply).

  uv run transcribe.py <audio_or_video> [--start S --end E] [--model small]

Prints each segment with per-word start times. Feeds faster-whisper a 16 kHz numpy array
(some PyAV versions break its own file decoding). Stadium audio garbles words; anchor on
the distinctive ones (the chorus hook) and confirm with splice.py align.
"""
import argparse

import librosa
from faster_whisper import WhisperModel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio'); ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--end', type=float); ap.add_argument('--model', default='small')
    a = ap.parse_args()
    dur = None if a.end is None else a.end - a.start
    y, _ = librosa.load(a.audio, sr=16000, mono=True, offset=a.start, duration=dur)
    m = WhisperModel(a.model, device='cpu', compute_type='int8')
    segs, _ = m.transcribe(y, language='en', word_timestamps=True, condition_on_previous_text=False)
    for s in segs:
        words = ' '.join(f'{w.word.strip()}@{w.start + a.start:.2f}' for w in (s.words or []))
        print(f'{s.start + a.start:7.2f}-{s.end + a.start:7.2f}  {words or s.text.strip()}')


if __name__ == '__main__':
    main()

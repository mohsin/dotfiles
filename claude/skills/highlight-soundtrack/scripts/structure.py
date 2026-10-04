# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["librosa", "numpy"]
# ///
"""Map a song: beats, loudness, sections, synced lyrics.

  uv run structure.py <audio> [--artist "The Weeknd" --track "Blinding Lights"]

Converts to <audio>.wav if needed, then writes next to it:
  <stem>.beats.npy        beat times in seconds (tracked beats, normalised to 100-180 bpm by
                          adding off-beats when the tracker locks on half-time, and extended at
                          the tempo through drumless intros/outros so cuts there land on the beat)
  <stem>.structure.json   tempo, period, per-second RMS, novelty section boundaries, the
                          point the song really ends (RMS falls to silence), and LRCLIB
                          synced lyrics when artist/track are given
"""
import argparse, json, re, subprocess, urllib.parse, urllib.request
from pathlib import Path

import librosa
import numpy as np


def to_wav(p):
    p = Path(p)
    if p.suffix.lower() == '.wav':
        return p
    w = p.with_suffix('.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(p), '-vn', '-ac', '2', '-ar', '44100', str(w)], check=True)
    return w


def lyrics(artist, track, dur):
    q = urllib.parse.urlencode({'artist_name': artist, 'track_name': track, 'duration': round(dur)})
    try:
        with urllib.request.urlopen(f'https://lrclib.net/api/get?{q}', timeout=20) as r:
            d = json.load(r)
    except Exception as e:  # noqa: BLE001
        return {'error': str(e)}
    lines = []
    for ln in (d.get('syncedLyrics') or '').splitlines():
        m = re.match(r'\[(\d+):(\d+\.\d+)\]\s*(.*)', ln)
        if m:
            lines.append([round(int(m[1]) * 60 + float(m[2]), 2), m[3]])
    return {'duration': d.get('duration'), 'lines': lines}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio'); ap.add_argument('--artist'); ap.add_argument('--track')
    ap.add_argument('--bpm', type=float, help='hint for the beat tracker')
    a = ap.parse_args()
    wav = to_wav(a.audio)
    y, sr = librosa.load(wav, sr=22050)
    dur = len(y) / sr
    kw = {'start_bpm': a.bpm} if a.bpm else {}
    tempo, fr = librosa.beat.beat_track(y=y, sr=sr, **kw)
    bt = librosa.frames_to_time(fr, sr=sr)
    tracked = bt.copy()
    period = float(np.median(np.diff(bt)))
    while period > 0.6:  # half-time detection (< 100 bpm): add the off-beats so pacing in beats stays comparable
        bt = np.sort(np.concatenate([bt, (bt[:-1] + bt[1:]) / 2]))
        period /= 2
    grid = np.concatenate([np.arange(bt[0], -0.01, -period)[::-1][:-1], bt, np.arange(bt[-1] + period, dur, period)])
    np.save(wav.with_suffix('.beats.npy'), grid)
    rms = librosa.feature.rms(y=y, frame_length=sr, hop_length=sr)[0]
    db = (20 * np.log10(rms + 1e-9)).round(0).astype(int).tolist()
    loud = [i for i, v in enumerate(db) if v > max(db) - 30]
    C = librosa.util.sync(librosa.feature.chroma_cqt(y=y, sr=sr), fr, aggregate=np.median)
    bounds = librosa.segment.agglomerative(C, 12)
    out = {'audio': str(wav), 'duration': round(dur, 2), 'tempo': round(60 / period, 1), 'period': round(period, 4),
           'first_beat': round(float(bt[0]), 2), 'last_tracked_beat': round(float(bt[-1]), 2),
           'music_ends_about': loud[-1] + 1 if loud else round(dur),
           'sections': [round(float(tracked[min(b, len(tracked) - 1)]), 1) for b in bounds],
           'rms_db_per_second': db}
    if a.artist and a.track:
        out['lyrics'] = lyrics(a.artist, a.track, dur)
    path = wav.with_suffix('.structure.json')
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != 'rms_db_per_second'}, indent=1)[:4000])
    print('wrote', path, 'and', wav.with_suffix('.beats.npy'))


if __name__ == '__main__':
    main()

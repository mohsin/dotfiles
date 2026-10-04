# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["librosa", "numpy"]
# ///
"""Find splice points that sound seamless.

  uv run splice.py pairs <audio> --from A0 A1 --to B0 B1 [--audio2 other.wav] [--win 8]
      ranks beat pairs (j in [A0,A1], k in [B0,B1]) by how alike the music is after each
      (60% beat-synced chroma, 40% MFCC timbre). Jump at j, continue from k. > 0.9 is
      seamless; < 0.6 means the arrangements differ (fine only at a matching lyric onset).
      With --audio2 the target range is in a second recording of the same performance.

  uv run splice.py align <audio> --at T [--audio2 other.wav] --search S0 S1 [--len 4]
      cross-correlates harmonic chroma (hop 256) of [T, T+len] against the search range:
      use it to land a cut on the exact same lyric onset ("I said, ooh") in both places.
"""
import argparse

import librosa
import numpy as np

SR = 22050


def load(p):
    y, _ = librosa.load(p, sr=SR)
    return y


def beat_feats(y):
    _, fr = librosa.beat.beat_track(y=y, sr=SR)
    bt = librosa.frames_to_time(fr, sr=SR)
    C = librosa.util.sync(librosa.feature.chroma_cqt(y=y, sr=SR), fr, aggregate=np.median)
    M = librosa.util.sync(librosa.feature.mfcc(y=y, sr=SR, n_mfcc=13), fr)
    M = (M - M.mean(1, keepdims=True)) / (M.std(1, keepdims=True) + 1e-9)
    n = min(C.shape[1], M.shape[1], len(bt))
    C, M = C[:, :n], M[:, :n]
    C /= np.linalg.norm(C, axis=0, keepdims=True) + 1e-9
    M /= np.linalg.norm(M, axis=0, keepdims=True) + 1e-9
    return bt[:n], C, M


def pairs(a):
    A = beat_feats(load(a.audio))
    B = beat_feats(load(a.audio2)) if a.audio2 else A
    (ba, Ca, Ma), (bb, Cb, Mb) = A, B
    L = a.win
    res = []
    for j in range(np.searchsorted(ba, a.from_[0]), min(np.searchsorted(ba, a.from_[1]), Ca.shape[1] - L)):
        for k in range(np.searchsorted(bb, a.to[0]), min(np.searchsorted(bb, a.to[1]), Cb.shape[1] - L)):
            s = 0.6 * (Ca[:, j:j + L] * Cb[:, k:k + L]).sum() / L + 0.4 * (Ma[:, j:j + L] * Mb[:, k:k + L]).sum() / L
            res.append((round(float(s), 3), round(float(ba[j]), 2), round(float(bb[k]), 2)))
    for r in sorted(res, reverse=True)[:12]:
        print(f'score {r[0]}  cut {r[1]} -> {r[2]}')


def align(a):
    ya = load(a.audio)
    yb = load(a.audio2) if a.audio2 else ya
    hop = 256
    fr = lambda t: int(round(t * SR / hop))  # noqa: E731
    Ca = librosa.feature.chroma_cqt(y=librosa.effects.harmonic(ya[int(a.at * SR):int((a.at + a.len) * SR)]), sr=SR, hop_length=hop)
    s0, s1 = a.search
    seg = yb[int(s0 * SR):int((s1 + a.len) * SR)]
    Cb = librosa.feature.chroma_cqt(y=librosa.effects.harmonic(seg), sr=SR, hop_length=hop)
    L = Ca.shape[1]
    sc = []
    for s in range(0, Cb.shape[1] - L):
        B = Cb[:, s:s + L]
        sc.append((float((Ca * B).sum() / (np.linalg.norm(Ca) * np.linalg.norm(B) + 1e-9)), s0 + s * hop / SR))
    for v, t in sorted(sc, reverse=True)[:5]:
        print(f'score {v:.3f}  {a.at} aligns to {t:.2f}  (offset {t - a.at:+.2f}s)')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('pairs'); p.add_argument('audio'); p.add_argument('--audio2')
    p.add_argument('--from', dest='from_', nargs=2, type=float, required=True)
    p.add_argument('--to', nargs=2, type=float, required=True); p.add_argument('--win', type=int, default=8)
    p = sub.add_parser('align'); p.add_argument('audio'); p.add_argument('--audio2')
    p.add_argument('--at', type=float, required=True); p.add_argument('--search', nargs=2, type=float, required=True)
    p.add_argument('--len', type=float, default=4.0)
    a = ap.parse_args()
    pairs(a) if a.cmd == 'pairs' else align(a)


if __name__ == '__main__':
    main()

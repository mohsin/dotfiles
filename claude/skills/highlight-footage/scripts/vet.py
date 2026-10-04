# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy"]
# ///
"""Vet a candidate shot before it goes in the edit.

  uv run vet.py <file> <in_seconds> <duration>        one shot
  uv run vet.py --scan <file> <from> <to>             list every cut and still stretch in a range

Reports, for the exact range the shot will use:
  cuts     scene changes inside the range (a stray frame of another scene will flash)
  motion   mean frame difference; < 1.5 reads as a still photo or a locked-off timelapse
  border   bright/black rows or columns at the edges (photos framed inside a video)
  hdr      HLG/PQ transfer (iPhone footage: convert with avconvert, see SKILL.md)
and a one-line verdict.
"""
import argparse, json, re, subprocess

import numpy as np


def cuts(f, a, d, thr=0.3):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-ss', str(a), '-t', str(d), '-i', f,
                        '-vf', f"select='gt(scene,{thr})',showinfo", '-an', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    return [round(float(x) + a, 2) for x in re.findall(r'pts_time:([0-9.]+)', r)]


def frames(f, a, d, fps=5, w=96, h=54):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(d), '-i', f, '-vf',
                          f'fps={fps},scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    return np.frombuffer(out, np.uint8).reshape(-1, h, w).astype(float)


def motion(x):
    return np.abs(np.diff(x, axis=0)).mean(axis=(1, 2)) if len(x) > 1 else np.zeros(1)


def border(f, t):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', f, '-frames:v', '1', '-vf',
                          'scale=480:-2,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                                '-show_entries', 'stream=width,height', '-of', 'json', f]))['streams'][0]
    h = round(480 * probe['height'] / probe['width'] / 2) * 2
    g = np.frombuffer(out, np.uint8).reshape(h, 480).astype(float)
    rows = g[:, 120:360].mean(1)
    flags = []
    for name, idx in (('top', range(0, h // 10)), ('bottom', range(h - 1, h - h // 10, -1))):
        hits = [i for i in idx if rows[i] > 235 or rows[i] < 4]
        if len(hits) >= 2:
            flags.append(f'{name} ~{len(hits) / h:.0%}')
    return flags


def hdr(f):
    s = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                            'stream=color_transfer', '-of', 'json', f]))['streams'][0]
    return s.get('color_transfer') in ('arib-std-b67', 'smpte2084')


def vet(f, a, d):
    c = cuts(f, a, d)
    m = motion(frames(f, a, d))
    b = border(f, a + d / 2)
    mm = float(np.median(m))
    issues = []
    if c:
        issues.append(f'cut at {c} (move in-point past it or shorten)')
    if mm < 1.5:
        issues.append(f'barely moves (motion {mm:.1f}); likely a still photo')
    if b:
        issues.append(f'border {b}: crop with vcrop/box')
    res = {'file': f, 'in': a, 'dur': d, 'cuts': c, 'motion_median': round(mm, 2), 'border': b,
           'hdr': hdr(f), 'verdict': 'OK' if not issues else '; '.join(issues)}
    print(json.dumps(res, indent=1))


def scan(f, a, b):
    c = cuts(f, a, b - a)
    m = motion(frames(f, a, b - a, fps=4))
    still = [round(a + (i + 1) / 4, 2) for i, v in enumerate(m) if v < 1.0]
    print(json.dumps({'cuts': c, 'still_seconds': still[:: 4]}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scan', action='store_true')
    ap.add_argument('file'); ap.add_argument('a', type=float); ap.add_argument('b', type=float)
    x = ap.parse_args()
    scan(x.file, x.a, x.b) if x.scan else vet(x.file, x.a, x.b)


if __name__ == '__main__':
    main()

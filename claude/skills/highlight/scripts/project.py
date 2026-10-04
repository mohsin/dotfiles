# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a highlight working folder with a starter reel.json.

  uv run project.py init "<City>" [--dir ~/Movies/Highlights] [--clips /path/to/own/clips]
  uv run project.py check [reel.json]     validate paths and fields before rendering

Layout:
  <dir>/<city>/
    reel.json            shared state, filled in by the highlight-* skills
    intake.json          questionnaire answers (trip timing, clips, itinerary, event, song)
    clips -> own clips   symlink, when given
    stock/ yt/ audio/ fonts/ covers/ build/ refs/
"""
import argparse, json, os, sys
from pathlib import Path

TEMPLATE = {
    'city': '',
    'fps': 30,
    'output': '',
    'grade': 'eq=contrast=1.04:saturation=1.12',
    'end_fade': 3.5,
    'audio': {'segments': [], 'xfade': 0.03, 'fade_in': 0.5, 'tail_fade': 0, 'loudnorm': -14},
    'title': {'text': '', 'font': '', 'width': 720, 'condense': 0.8, 'bulge': 0.35, 'cy': 1180,
              'shadow': 170, 'until': 3.3, 'fade': 0.8},
    'captions': [],
    'shots': [],
}


def init(city, base, clips):
    d = Path(base).expanduser() / city.lower().replace(' ', '-')
    for sub in ('stock', 'yt', 'audio', 'fonts', 'covers', 'build', 'refs'):
        (d / sub).mkdir(parents=True, exist_ok=True)
    if clips:
        link = d / 'clips'
        if not link.exists():
            link.symlink_to(Path(clips).expanduser().resolve())
    reel = d / 'reel.json'
    if not reel.exists():
        cfg = dict(TEMPLATE, city=city, output=f"{city.lower().replace(' ', '-')}.mp4")
        cfg['title'] = dict(TEMPLATE['title'], text=city)
        reel.write_text(json.dumps(cfg, indent=1, ensure_ascii=False))
    print(d)


def check(path):
    p = Path(path).resolve()
    cfg = json.loads(p.read_text())
    root = p.parent
    problems = []
    for s in cfg['audio']['segments']:
        for k in ('file', 'beats'):
            if not (root / s[k]).exists():
                problems.append(f'audio segment {k} missing: {s[k]}')
        if s['end'] <= s['start']:
            problems.append(f"audio segment ends before it starts: {s}")
    if not cfg['audio']['segments']:
        problems.append('no audio segments (run highlight-soundtrack)')
    if not cfg['shots']:
        problems.append('no shots (run highlight-footage)')
    for i, s in enumerate(cfg['shots']):
        if not (root / s['src']).exists():
            problems.append(f"shot {i} source missing: {s['src']}")
        if s.get('part', 0) >= max(1, len(cfg['audio']['segments'])):
            problems.append(f"shot {i} part {s.get('part')} has no audio segment")
    t = cfg.get('title') or {}
    if t.get('text') and not (root / t.get('font', '')).is_file():
        problems.append(f"title font missing: {t.get('font')} (run highlight-cover)")
    for c in cfg.get('captions', []):
        for ln in c['lines']:
            if not (root / ln['font']).is_file():
                problems.append(f"caption font missing: {ln['font']}")
        if not any(s.get('tag') == c['tag'] for s in cfg['shots']):
            problems.append(f"caption '{c['tag']}' has no tagged shots")
    print('\n'.join(problems) if problems else 'reel.json OK')
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init'); p.add_argument('city')
    p.add_argument('--dir', default=os.environ.get('HIGHLIGHTS_DIR', '~/Movies/Highlights'))
    p.add_argument('--clips')
    p = sub.add_parser('check'); p.add_argument('reel', nargs='?', default='reel.json')
    a = ap.parse_args()
    if a.cmd == 'init':
        init(a.city, a.dir, a.clips)
    else:
        sys.exit(check(a.reel))


if __name__ == '__main__':
    main()

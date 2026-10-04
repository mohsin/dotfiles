# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools"]
# ///
"""Fetch and inspect fonts for a highlight.

  uv run fonts.py fetch <url> [--dir fonts]   download a TTF/OTF (e.g. one a foundry's type
                                              tester serves; grep the page for .ttf/.woff)
  uv run fonts.py defaults [--dir fonts]      Open Sans Bold + SemiBold for captions
  uv run fonts.py info <file> [--text ...]    names, designer, licence fields, glyph coverage
"""
import argparse, json, os, sys, urllib.request
from pathlib import Path

GOOGLE = 'https://github.com/googlefonts/opensans/raw/main/fonts/ttf/OpenSans-{w}.ttf'


def fetch(url, d):
    os.makedirs(d, exist_ok=True)
    dst = Path(d) / Path(url.split('?')[0]).name
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r, open(dst, 'wb') as f:
        f.write(r.read())
    print(dst)
    return dst


def info(path, text):
    from fontTools.ttLib import TTFont
    f = TTFont(path)
    names = {r.nameID: r.toUnicode() for r in f['name'].names if r.platformID == 3}
    cmap = f.getBestCmap()
    missing = sorted({c for c in text if ord(c) not in cmap and not c.isspace()})
    print(json.dumps({'family': names.get(1), 'full': names.get(4), 'designer': names.get(9),
                      'copyright': names.get(0), 'licence': names.get(13), 'licence_url': names.get(14),
                      'missing_glyphs': missing}, indent=1, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('fetch'); p.add_argument('url'); p.add_argument('--dir', default='fonts')
    p = sub.add_parser('defaults'); p.add_argument('--dir', default='fonts')
    p = sub.add_parser('info'); p.add_argument('file')
    p.add_argument('--text', default='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789·')
    a = ap.parse_args()
    if a.cmd == 'fetch':
        fetch(a.url, a.dir)
    elif a.cmd == 'defaults':
        for w in ('Bold', 'SemiBold'):
            fetch(GOOGLE.format(w=w), a.dir)
    else:
        info(a.file, a.text)


if __name__ == '__main__':
    sys.exit(main())

# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Render highlight-cover variants of a title over a frame, plus a comparison sheet.

  uv run cover.py --text Singapore --font fonts/Title.ttf --bg frame.png --out covers/
  uv run cover.py ... --bg clip.mp4 --t 0.5          # grab the frame from a video
  uv run cover.py ... --only lowered,subtle_low       # a subset of presets
  uv run cover.py ... --variant '{"name":"mine","width":760,"bulge":0.3,"cy":1150}'

  uv run cover.py ... --row profile.png --slot 240,1190,151
      also mocks each variant into a screenshot of the user's profile, in the highlight
      slot centred at (x, y) with diameter d (measure it from the screenshot)

Presets: bulge_smile (default), smile, caps_smile, bulge_arch, caps_arched, subtle_low.
Writes <out>/<name>.png (1080x1920), <out>/<name>_inrow.png with --row, and
<out>/compare.jpg (cover + in-row mock, or cover + circles) so the user can choose before
anything goes into the reel.
"""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from textfx import W, H, circle, compose, sky_mask, text_layer, text_mask  # noqa: E402

PRESETS = {
    # approved Singapore cover (Oct 2026): big, middle letters swell, word sags into a smile
    # under the landmark. Text spans ~80% of the circle so it holds up next to the series.
    'bulge_smile': dict(width=880, condense=0.72, bulge=0.6, arch=-0.25, cy=1170, shadow=200),
    'smile': dict(width=860, condense=0.78, bulge=0.3, arch=-0.4, cy=1180, shadow=200),
    'caps_smile': dict(width=870, condense=0.62, bulge=0.2, arch=-0.35, cy=1180, shadow=200, caps=True),
    'bulge_arch': dict(width=880, condense=0.72, bulge=0.6, arch=0.25, cy=1150, shadow=200),
    'caps_arched': dict(width=870, condense=0.62, bulge=0.2, arch=0.35, cy=1160, shadow=200, caps=True),
    'subtle_low': dict(width=720, bulge=0.35, cy=1180, shadow=170),  # too small in the row; kept for contrast
}


def load_bg(path, t):
    p = Path(path)
    if p.suffix.lower() in {'.mp4', '.mov', '.m4v', '.mkv', '.webm'}:
        tmp = Path(tempfile.mkdtemp()) / 'frame.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', str(p), '-frames:v', '1',
                        '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}', str(tmp)],
                       check=True)
        p = tmp
    return Image.open(p).convert('RGB').resize((W, H))


def render(bg, text, font, v):
    frame = bg
    if v.get('zoom', 1.0) != 1.0:  # push in, bottom-aligned, so the landmark rises in the frame
        z = v['zoom']
        big = bg.resize((int(W * z), int(H * z)), Image.LANCZOS)
        ox = (big.width - W) // 2
        frame = big.crop((ox, big.height - H, ox + W, big.height))
    word = text.upper() if v.get('caps') else text
    mask = text_mask(word, font, v.get('width', 880), v.get('condense', 0.72), v.get('bulge', 0.6), v.get('arch', 0.0))
    occ = sky_mask(frame, v.get('threshold', 100)) if v.get('behind') else None
    return compose(frame, text_layer(mask, v.get('cy', 1180), v.get('shadow', 150), occ))


def in_row(img, row, slot):
    """Paste the cover's circle into a profile screenshot (anti-aliased), crop the row."""
    x, y, d = slot
    big = circle(img, d * 4).resize((d, d), Image.LANCZOS)
    m = Image.new('L', (d * 4, d * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    out = row.copy()
    out.paste(big, (int(x - d / 2), int(y - d / 2)), m.resize((d, d), Image.LANCZOS))
    top = max(0, int(y - d * 1.0))
    return out.crop((0, top, out.width, min(out.height, int(y + d * 1.0))))


def sheet_rows(images, mocks, path):
    rows = []
    for name, im in images.items():
        r = mocks[name]
        k = 1100 / r.width
        r = r.resize((1100, int(r.height * k)))
        cell = Image.new('RGB', (1420, max(500, r.height + 40)), (255, 255, 255))
        ImageDraw.Draw(cell).text((10, 8), name, fill='black')
        cell.paste(im.resize((270, 480)), (10, 20))
        cell.paste(r, (300, (cell.height - r.height) // 2))
        rows.append(cell)
    s = Image.new('RGB', (1420, sum(c.height for c in rows)), (255, 255, 255))
    y = 0
    for c in rows:
        s.paste(c, (0, y))
        y += c.height
    s.save(path, quality=90)


def sheet(images, path):
    n = len(images)
    s = Image.new('RGB', (n * 300, 740), (255, 255, 255))
    d = ImageDraw.Draw(s)
    for i, (name, im) in enumerate(images.items()):
        d.text((i * 300 + 15, 8), name, fill='black')
        s.paste(im.resize((270, 480)), (i * 300 + 15, 30))
        s.paste(circle(im, 170), (i * 300 + 15, 530))
        s.paste(circle(im, 80), (i * 300 + 200, 575))
    s.save(path, quality=90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text', required=True)
    ap.add_argument('--font', required=True)
    ap.add_argument('--bg', required=True, help='image, or video with --t')
    ap.add_argument('--t', type=float, default=0.5)
    ap.add_argument('--out', default='covers')
    ap.add_argument('--only', help='comma-separated preset names')
    ap.add_argument('--variant', action='append', default=[], help='JSON variant, may repeat')
    ap.add_argument('--row', help="screenshot of the user's profile with the highlights row")
    ap.add_argument('--slot', help='x,y,d of the highlight circle to replace in --row')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bg = load_bg(a.bg, a.t)
    variants = {k: v for k, v in PRESETS.items() if not a.only or k in a.only.split(',')}
    for js in a.variant:
        v = json.loads(js)
        variants[v.pop('name', f'custom{len(variants)}')] = v
    out = {}
    for name, v in variants.items():
        out[name] = render(bg, a.text, a.font, v)
        out[name].save(f'{a.out}/{name}.png')
    if a.row and a.slot:
        row = Image.open(a.row).convert('RGB')
        slot = [int(float(v)) for v in a.slot.split(',')]
        mocks = {k: in_row(v, row, slot) for k, v in out.items()}
        for k, v in mocks.items():
            v.save(f'{a.out}/{k}_inrow.png')
        sheet_rows(out, mocks, f'{a.out}/compare.jpg')
    else:
        sheet(out, f'{a.out}/compare.jpg')
    print(json.dumps({'compare': f'{a.out}/compare.jpg', 'variants': {k: PRESETS.get(k, {}) for k in out}},
                     default=str, indent=1))


if __name__ == '__main__':
    main()

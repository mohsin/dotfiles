# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Render highlight-cover variants of a title over a frame, plus a comparison sheet.

  uv run cover.py --text Singapore --font fonts/Title.ttf --bg frame.png --out covers/
  uv run cover.py ... --bg clip.mp4 --t 0.5          # grab the frame from a video
  uv run cover.py ... --only lowered,subtle_low       # a subset of presets
  uv run cover.py ... --variant '{"name":"mine","width":760,"bulge":0.3,"cy":1150}'

Presets mirror the decisions in SKILL.md: centred, lowered, subtle_low, zoomed_in, behind.
Writes <out>/<name>.png (1080x1920) and <out>/compare.jpg (full frame + circles at
profile sizes) so the user can choose before anything goes into the reel.
"""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from textfx import W, H, circle, compose, sky_mask, text_layer, text_mask  # noqa: E402

PRESETS = {
    'centred': dict(width=880, bulge=0.6, cy=H / 2),
    'lowered': dict(width=860, bulge=0.6, cy=1240),
    'subtle_low': dict(width=720, bulge=0.35, cy=1180, shadow=170),
    'zoomed_in': dict(width=880, bulge=0.6, cy=1210, zoom=1.2),
    'behind': dict(width=840, bulge=0.5, cy=790, behind=True),
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
    mask = text_mask(text, font, v.get('width', 760), v.get('condense', 0.8), v.get('bulge', 0.35))
    occ = sky_mask(frame, v.get('threshold', 100)) if v.get('behind') else None
    return compose(frame, text_layer(mask, v.get('cy', 1180), v.get('shadow', 150), occ))


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
    sheet(out, f'{a.out}/compare.jpg')
    print(json.dumps({'compare': f'{a.out}/compare.jpg', 'variants': {k: PRESETS.get(k, {}) for k in out}},
                     default=str, indent=1))


if __name__ == '__main__':
    main()

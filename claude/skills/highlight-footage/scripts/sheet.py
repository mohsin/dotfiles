# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Look at footage without transcoding it (fast seeks only).

  uv run sheet.py contact <out.jpg> <file>... [--n 6 | --step 5] [--w 120]
      one row per file: n evenly spaced frames, or one every `step` seconds
  uv run sheet.py crops <out.jpg> <spec>... [--cols 8] [--w 170]
      spec = file@seconds[@x], previews the 9:16 window a landscape source will become
      (x = 0..1 horizontal crop position, default 0.5)
"""
import argparse, io, json, subprocess
from pathlib import Path

from PIL import Image, ImageDraw


def probe(f):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                   'stream=width,height:stream_side_data=rotation:format=duration',
                                   '-of', 'json', f])
    d = json.loads(out)
    s = d['streams'][0]
    w, h = s['width'], s['height']
    if any(abs(x.get('rotation', 0)) == 90 for x in s.get('side_data_list', [])):
        w, h = h, w
    return w, h, float(d['format']['duration'])


def grab(f, t, vf):
    for back in range(4):  # seeking right at the end can return nothing
        out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{max(0, t - back):.2f}', '-i', f,
                              '-frames:v', '1', '-vf', vf, '-f', 'image2pipe', '-vcodec', 'png', '-'],
                             capture_output=True).stdout
        if out:
            return Image.open(io.BytesIO(out)).convert('RGB')
    return None


def label(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width, 14], fill='black')
    d.text((2, 1), text, fill='yellow')
    return im


def contact(out, files, n, step, w):
    rows = []
    for f in files:
        _, _, dur = probe(f)
        ts = [x * step for x in range(int(dur / step) + 1)] if step else [dur * (i + .5) / n for i in range(n)]
        ims = [label(grab(f, t, f'scale={w}:-2') or Image.new('RGB', (w, w * 16 // 9)), f'{t:.0f}s') for t in ts]
        cols = min(len(ims), 12)
        h = ims[0].height
        r = Image.new('RGB', (cols * w, ((len(ims) + cols - 1) // cols) * h))
        for i, im in enumerate(ims):
            r.paste(im, ((i % cols) * w, (i // cols) * h))
        ImageDraw.Draw(r).text((3, h - 14), Path(f).name, fill='white', stroke_width=2, stroke_fill='black')
        rows.append(r)
    sheet = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows)))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(out, quality=82)


def crops(out, specs, cols, w):
    ims = []
    for spec in specs:
        f, t, *x = spec.split('@')
        x = float(x[0]) if x else 0.5
        sw, sh, _ = probe(f)
        if sw > sh:
            cw = int(sh * 9 / 16) // 2 * 2
            vf = f'crop={cw}:{sh}:{int((sw - cw) * x)}:0,scale={w}:-2'
        else:
            vf = f'scale={w}:-2'
        im = grab(f, float(t), vf) or Image.new('RGB', (w, w * 16 // 9))
        ims.append(label(im, f'{Path(f).stem[:14]} {t}' + (f' x{x}' if x != 0.5 else '')))
    h = max(i.height for i in ims)
    g = Image.new('RGB', (cols * w, ((len(ims) + cols - 1) // cols) * h))
    for i, im in enumerate(ims):
        g.paste(im, ((i % cols) * w, (i // cols) * h))
    g.save(out, quality=85)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('contact'); p.add_argument('out'); p.add_argument('files', nargs='+')
    p.add_argument('--n', type=int, default=6); p.add_argument('--step', type=float); p.add_argument('--w', type=int, default=120)
    p = sub.add_parser('crops'); p.add_argument('out'); p.add_argument('specs', nargs='+')
    p.add_argument('--cols', type=int, default=8); p.add_argument('--w', type=int, default=170)
    a = ap.parse_args()
    if a.cmd == 'contact':
        contact(a.out, a.files, a.n, a.step, a.w)
    else:
        crops(a.out, a.specs, a.cols, a.w)
    print(a.out)


if __name__ == '__main__':
    main()

# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Render a highlight reel from reel.json (see ../references/reel-json.md).

  uv run render.py [reel.json] --plan     print the beat-aligned timeline, render nothing
  uv run render.py [reel.json]            render shots (cached), audio, overlays, final MP4
  uv run render.py [reel.json] --cover    also export the first frame as <city>_cover.png

Every cut lands on the audio's beat grid. Shots are cached in build/shots/ by a hash of
everything that affects them, so editing one shot re-renders only that shot.
"""
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / 'highlight-cover' / 'scripts'))
from textfx import text_layer, text_mask  # noqa: E402

W, H = 1080, 1920


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def probe(path):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                   'stream=width,height,color_transfer:stream_side_data=rotation', '-of', 'json', str(path)])
    s = json.loads(out)['streams'][0]
    w, h = s['width'], s['height']
    if any(abs(d.get('rotation', 0)) == 90 for d in s.get('side_data_list', [])):
        w, h = h, w
    return w, h, s.get('color_transfer') in ('arib-std-b67', 'smpte2084')


class Reel:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.root = self.path.parent
        self.cfg = json.loads(self.path.read_text())
        self.fps = self.cfg.get('fps', 30)
        a = self.cfg['audio']
        self.segments = a['segments']
        self.xf = a.get('xfade', 0.03)
        tl, off = [], 0.0
        self.seg_starts = []
        for i, s in enumerate(self.segments):
            self.seg_starts.append(off - self.xf * i)
            grid = np.load(self.p(s['beats']))
            shift = off - s['start'] - self.xf * i
            tl += [t + shift for t in grid if s['start'] <= t < s['end']]
            off += s['end'] - s['start']
        self.total = off - self.xf * (len(self.segments) - 1)
        self.beats = np.array(sorted(tl))

    def p(self, rel):
        return (self.root / rel).resolve()

    def plan(self):
        timed, cur = [], 0.0
        shots = self.cfg['shots']
        for i, s in enumerate(shots):
            part = s.get('part', 0)
            part_end = self.seg_starts[part + 1] if part + 1 < len(self.seg_starts) else self.total
            if s.get('beats') is None or i == len(shots) - 1:
                end = part_end if s.get('beats') is None else self.total
            else:
                k = int(np.searchsorted(self.beats, cur - 0.05))
                end = min(float(self.beats[min(k + s['beats'], len(self.beats) - 1)]), part_end)
            tin = s['in']
            if tin == 'sync':  # play the clip under its own audio
                seg = self.segments[part]
                tin = seg['start'] + (cur - self.seg_starts[part])
            timed.append({**s, 'idx': i, 'in': tin, 'start': cur, 'end': end})
            cur = end
        return timed

    def shot(self, s):
        nframes = round(s['end'] * self.fps) - round(s['start'] * self.fps)
        dur = nframes / self.fps
        src = self.p(s['src'])
        key = json.dumps([str(src), src.stat().st_mtime, s['in'], nframes, {k: v for k, v in s.items()
                          if k not in ('idx', 'start', 'end', 'part', 'beats', 'tag')}, self.cfg.get('grade'), self.fps], default=str)
        out = self.root / 'build' / 'shots' / f"{hashlib.sha1(key.encode()).hexdigest()[:16]}.mp4"
        if out.exists():
            return out
        out.parent.mkdir(parents=True, exist_ok=True)
        w, h, is_hdr = probe(src)
        tin = s['in']
        if s.get('hdr', is_hdr):  # iPhone HLG: macOS tone-maps to SDR and applies rotation
            sdr = out.with_suffix('.sdr.mov')
            run(['avconvert', '-s', str(src), '-p', 'Preset1920x1080', '-o', str(sdr), '--start', str(tin),
                 '--duration', str(dur / s.get('speed', 1) + 1.0), '--replace'], capture_output=True)
            src, tin = sdr, 0.0
            w, h, _ = probe(src)
        chain = [f"setpts=PTS/{s['speed']}"] if s.get('speed') else []
        if w > h:
            top, frac = s.get('vcrop') or (0.0, 0.9 if s.get('wm') else 1.0)
            ch = int(h * frac) // 2 * 2
            cw = int(ch * 9 / 16) // 2 * 2
            chain.append(f"crop={cw}:{ch}:{int((w - cw) * s.get('x', 0.5))}:{int(h * top)}")
        elif s.get('box'):
            bx, by, bw = s['box']
            chain.append(f'crop=iw*{bw}:ih*{bw}:iw*{bx}:ih*{by}')
        elif s.get('wm'):
            chain.append('crop=iw:ih*0.9:0:0')
        z0, z1 = s.get('zoom') or (1.0, 1.0)
        if z0 != z1:  # supersampled push keeps the zoom smooth
            chain += [f"scale=w='2*{W}*({z0}+({z1}-{z0})*t/{dur:.3f})':h=-2:eval=frame:flags=lanczos",
                      f'crop={2 * W}:{2 * H}', f'scale={W}:{H}:flags=lanczos']
        else:
            chain.append(f'scale={W}:{H}:flags=lanczos')
        chain += [f'fps={self.fps}', self.cfg.get('grade', 'eq=contrast=1.04:saturation=1.12'), 'format=yuv420p', 'setsar=1']
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{tin:.3f}', '-i', str(src), '-an', '-vf', ','.join(chain),
             '-frames:v', str(nframes), '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-r', str(self.fps), str(out)])
        return out

    def audio(self):
        a = self.cfg['audio']
        out = self.root / 'build' / 'audio.wav'
        files = sorted({str(self.p(s['file'])) for s in self.segments})
        ins = sum([['-i', f] for f in files], [])
        fc = ''.join(f"[{files.index(str(self.p(s['file'])))}]atrim={s['start']}:{s['end']},asetpts=PTS-STARTPTS[s{i}];"
                     for i, s in enumerate(self.segments))
        last = 's0'
        for i in range(1, len(self.segments)):
            fc += f'[{last}][s{i}]acrossfade=d={self.xf}:c1=tri:c2=tri[x{i}];'
            last = f'x{i}'
        post = [f"afade=t=in:d={a.get('fade_in', 0.3)}"]
        if a.get('tail_fade'):  # only for a crowd/room tail after the music has ended
            post.append(f"afade=t=out:st={self.total - a['tail_fade']:.3f}:d={a['tail_fade']}")
        if a.get('loudnorm'):
            post += ['highpass=f=30', f"loudnorm=I={a['loudnorm']}:TP=-1.5:LRA=11"]
        fc += f"[{last}]{','.join(post)}[out]"
        run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[out]', '-ar', '48000', str(out)])
        return out

    def overlays(self, timed):
        res = []
        t = self.cfg.get('title')
        if t:
            m = text_mask(t['text'], str(self.p(t['font'])), t.get('width', 720), t.get('condense', 0.8), t.get('bulge', 0.35))
            png = self.root / 'build' / 'title.png'
            text_layer(m, t.get('cy', 1180), t.get('shadow', 170)).save(png)
            res.append((png, 0.0, t.get('until', 3.3), 0.0, t.get('fade', 0.8)))
        for c in self.cfg.get('captions', []):
            tagged = [s for s in timed if s.get('tag') == c['tag']]
            if not tagged:
                continue
            png = self.root / 'build' / f"caption_{c['tag']}.png"
            caption_png(png, [(ln['text'], str(self.p(ln['font'])), ln['size'], ln.get('dy', 0)) for ln in c['lines']],
                        c.get('cy', H * 0.66))
            res.append((png, tagged[0]['start'], tagged[-1]['end'], 0.25, 0.25))
        return res

    def render(self, cover=False):
        timed = self.plan()
        files = [self.shot(s) for s in timed]
        lst = self.root / 'build' / 'list.txt'
        lst.write_text(''.join(f"file '{f}'\n" for f in files))
        audio = self.audio()
        inputs = ['-f', 'concat', '-safe', '0', '-i', str(lst), '-i', str(audio)]
        fc, last = [], '0:v'
        for i, (png, a, b, fi, fo) in enumerate(self.overlays(timed)):
            inputs += ['-loop', '1', '-t', f'{b:.3f}', '-i', str(png)]
            fades = ([f'fade=t=in:st={a:.3f}:d={fi}:alpha=1'] if fi else []) + [f'fade=t=out:st={b - fo:.3f}:d={fo}:alpha=1']
            fc += [f"[{i + 2}:v]format=rgba,{','.join(fades)}[t{i}]",
                   f"[{last}][t{i}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{i}]"]
            last = f'v{i}'
        ef = self.cfg.get('end_fade', 3.0)
        fc.append(f'[{last}]fade=t=out:st={self.total - ef:.3f}:d={ef},format=yuv420p[vout]')
        out = self.root / self.cfg.get('output', f"{self.cfg.get('city', 'reel').lower()}.mp4")
        run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '1:a',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-r', str(self.fps), '-c:a', 'aac', '-b:a', '256k',
             '-movflags', '+faststart', '-shortest', str(out)])
        print('wrote', out)
        if cover:
            cv = out.with_name(out.stem + '_cover.png')
            run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.5', '-i', str(out), '-frames:v', '1', str(cv)])
            print('wrote', cv)


def caption_png(path, lines, cy):
    """Event caption: bold white lines with a soft shadow, centred at cy."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for text, font, size, dy in lines:
        f = ImageFont.truetype(font, size)
        x0, y0, x1, y1 = f.getbbox(text)
        x, y = (W - (x1 - x0)) / 2 - x0, cy + dy - (y1 - y0) / 2 - y0
        ImageDraw.Draw(shadow).text((x, y + 4), text, font=f, fill=(0, 0, 0, 120))
        ImageDraw.Draw(img).text((x, y), text, font=f, fill=(255, 255, 255, 240))
    Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)), img).save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('reel', nargs='?', default='reel.json')
    ap.add_argument('--plan', action='store_true')
    ap.add_argument('--cover', action='store_true')
    a = ap.parse_args()
    r = Reel(a.reel)
    for s in r.plan():
        print(f"{s['idx']:02d} {s['start']:6.2f}-{s['end']:6.2f} ({s['end'] - s['start']:.2f}s) "
              f"{s['src']} @{s['in'] if isinstance(s['in'], str) else round(s['in'], 2)}{' [' + s['tag'] + ']' if s.get('tag') else ''}")
    print(f'TOTAL {r.total:.2f}s')
    if not a.plan:
        r.render(a.cover)


if __name__ == '__main__':
    main()

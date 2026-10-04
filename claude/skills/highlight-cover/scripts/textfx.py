"""Title text effects shared by highlight-cover (cover.py) and highlight (render.py).

Renders white display text as an alpha mask (condensed, optionally bulged so the middle
letters stand taller), composites it with a soft drop shadow, optionally behind a bright
sky so a landmark occludes it, and previews a 9:16 frame as Instagram's highlight circle.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920


def text_mask(text, font, width, condense=0.8, bulge=0.35, arch=0.0):
    """Alpha mask of `text` scaled to `width` px. bulge=0 is flat; 0.3-0.6 swells the middle.
    arch > 0 bends the word into an arch with upright letters (fraction of its height the
    middle rises; 0.3-0.6 reads like a hand-lettered sign), < 0 sags it into a smile."""
    f = ImageFont.truetype(font, 400)
    x0, y0, x1, y1 = f.getbbox(text)
    pad = 40
    m = Image.new('L', (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), 0)
    ImageDraw.Draw(m).text((pad - x0, pad - y0), text, font=f, fill=255)
    a = np.asarray(m).astype(np.float32)
    if bulge:
        h, w = a.shape
        out = np.zeros((int(h * (1 + bulge)), w), np.float32)
        h2 = out.shape[0]
        for x in range(w):
            sc = 1 + bulge * np.cos(np.pi * (x / w - 0.5)) ** 1.5
            ys = (np.arange(h2) - h2 / 2) / sc + h / 2
            ok = (ys >= 0) & (ys < h - 1)
            yi = ys[ok].astype(int)
            fr = ys[ok] - yi
            out[ok, x] = a[yi, x] * (1 - fr) + a[yi + 1, x] * fr
        a = out
    if arch:
        h, w = a.shape
        lift = int(abs(arch) * h)
        out = np.zeros((h + lift, w), np.float32)
        for x in range(w):
            u = (x - w / 2) / (w / 2)
            dy = int(round(lift * (1 - u * u)))
            if arch > 0:
                out[lift - dy:lift - dy + h, x] = a[:, x]
            else:
                out[dy:dy + h, x] = a[:, x]
        a = out
    m = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    m = m.crop(m.getbbox())
    m = m.resize((max(1, int(m.width * condense)), m.height), Image.LANCZOS)
    k = width / m.width
    return m.resize((int(m.width * k), int(m.height * k)), Image.LANCZOS)


def curved_mask(text, font, size, radius, centre, side='top', tracking=0.04, size_wh=(W, H)):
    """Full-frame mask with letters set along a circle (radius px, centre (x, y)).

    side='top' runs the word over the top of the circle (a rainbow over the landmark),
    side='bottom' along the bottom (a smile under it). Letters stay tangent to the curve.
    """
    import math
    f = ImageFont.truetype(font, size)
    adv = [f.getlength(c) + size * tracking for c in text]
    span = sum(adv) / radius
    out = Image.new('L', size_wh, 0)
    theta = -span / 2
    for c, a in zip(text, adv):
        mid = theta + a / 2 / radius
        g = Image.new('L', (size * 2, size * 2), 0)
        ImageDraw.Draw(g).text((size, size), c, font=f, fill=255, anchor='ms')
        if side == 'top':
            x = centre[0] + radius * math.sin(mid)
            y = centre[1] - radius * math.cos(mid)
            g = g.rotate(-math.degrees(mid), resample=Image.BICUBIC)
        else:
            x = centre[0] + radius * math.sin(mid)
            y = centre[1] + radius * math.cos(mid)
            g = g.rotate(math.degrees(mid), resample=Image.BICUBIC)
        box = (int(x - size), int(y - size))
        out.paste(Image.fromarray(np.maximum(np.asarray(out.crop((*box, box[0] + 2 * size, box[1] + 2 * size))),
                                            np.asarray(g))), box)
        theta += a / radius
    return out


def text_layer(mask, cy, shadow=170, occluder=None, size=(W, H)):
    """Transparent RGBA layer: white text centred at height cy with a soft shadow.

    occluder: optional L-mode image, 255 where the text may show (e.g. bright sky), so a
    dark landmark in front hides the letters ("text behind the towers").
    """
    w, h = size
    if mask.size == size:  # already a full-frame mask (curved_mask)
        alpha = mask.copy()
    else:
        alpha = Image.new('L', size, 0)
        alpha.paste(mask, ((w - mask.width) // 2, int(cy - mask.height / 2)))
    if occluder is not None:
        alpha = Image.fromarray((np.asarray(alpha).astype(np.float32)
                                 * np.asarray(occluder).astype(np.float32) / 255).astype(np.uint8))
    sh = Image.new('L', size, 0)
    sh.paste(alpha.filter(ImageFilter.GaussianBlur(9)).point(lambda v: v * shadow // 255), (0, 6))
    layer = Image.merge('RGBA', [Image.new('L', size, 0)] * 3 + [sh])
    white = Image.merge('RGBA', [Image.new('L', size, 255)] * 3 + [alpha])
    return Image.alpha_composite(layer, white)


def sky_mask(frame, threshold=100):
    """255 where the frame is bright (sky), for text-behind-landmark covers."""
    g = np.asarray(frame.convert('L')).astype(np.float32)
    m = Image.fromarray(((g > threshold) * 255).astype(np.uint8))
    return m.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.2))


def compose(frame, layer):
    return Image.alpha_composite(frame.convert('RGBA').resize(layer.size), layer).convert('RGB')


def circle(frame, d=170):
    """How a 9:16 frame looks as a highlight cover: centre square, circular crop."""
    w, h = frame.size
    sq = frame.crop((0, (h - w) // 2, w, (h - w) // 2 + w)).resize((d, d), Image.LANCZOS)
    m = Image.new('L', (d, d), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    out = Image.new('RGB', (d, d), (255, 255, 255))
    out.paste(sq, (0, 0), m)
    return out

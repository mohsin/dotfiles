---
name: highlight-cover
description: Design the title screen of a travel highlight so it doubles as the Instagram highlight cover: research a typeface that captures the place (local foundry, open licence), render several cover variants over the opening frame (lowered, subtle, zoomed, text-behind-landmark), preview them as profile-size circles, and let the user pick. Use inside /highlight or alone ("make a highlight cover for Tokyo", "redo the cover").
argument-hint: "<place> [background image or video]"
---

# Highlight cover

The reel's first frame is uploaded as the highlight cover, which Instagram shows as a small
circle cropped from the centre of the 9:16 frame. Design for that circle first.

```
C=~/.claude/skills/highlight-cover/scripts
uv run $C/fonts.py fetch <ttf-url> --dir fonts      # the chosen typeface
uv run $C/fonts.py info fonts/<file>.ttf --text "Tokyo"
uv run $C/cover.py --text Tokyo --font fonts/<file>.ttf --bg build/first.png --out covers
open covers/compare.jpg
```

## 1. Learn the user's series (once per session)

If the user has existing highlight covers, look at them (their Instagram profile in Chrome:
zoom on the highlight row; open one to see a full frame). Note: name placement, weight,
fill of the circle, text effects (e.g. a bulge warp), shadow. Match the series. Known
series so far: city name in heavy white with a soft shadow over the landmark; one cover
uses a bulge warp; the approved Singapore cover is "subtle low" (see house-style.md).

## 2. Choose a typeface that captures the place

- Research what locals and local designers point to (Reddit, local design press, type
  foundries, Luc Devroye's per-country type pages). Prefer a face **from a local foundry
  under an open licence** (Singapore: DT Getai Grotesk by Death of Typography, drawn from
  getai stage lettering, OFL).
- Avoid proprietary signage fonts (e.g. a transit authority's) and unlicensed
  reconstructions; mention them as context only.
- Foundry pages often serve the TTF to their type tester: download the page and grep for
  `.ttf`/`.woff` rather than going through a store checkout (never enter the user's details).
- `fonts.py info`: confirm family, designer and that every glyph of the title exists.
- Cite sources in the report.

## 3. Render variants and let the user choose

1. Get the opening frame without a title: the first shot from `build/shots/` or
   `--bg <video> --t 0.5`.
2. `cover.py` renders the presets: `centred`, `lowered`, `subtle_low`, `zoomed_in`, `behind`
   (text behind the landmark, using a bright-sky mask), plus any `--variant` JSON. Mixed case
   usually shows a display face's character; try caps when the face is built for them.
3. Read `covers/compare.jpg` yourself first. Discard variants where the landmark or sun is
   hidden, the word touches the circle's edge, or the word is unreadable at 80 px (the
   text-behind variant often fails here). Fix and re-render rather than presenting a broken
   one.
4. Open `covers/compare.jpg` for the user, describe each in one line with a recommendation,
   and wait for their pick. Never apply a cover they have not seen.

## 4. Apply

Copy the chosen variant's parameters into `reel.json`:

```json
"title": {"text": "Singapore", "font": "fonts/DTGetaiGroteskDisplay-Black.ttf", "width": 720,
          "condense": 0.8, "bulge": 0.35, "cy": 1180, "shadow": 170, "until": 3.3, "fade": 0.8}
```

Also set the hero-block caption (`captions`, Open Sans from `fonts.py defaults`, since display
faces often lack `·`). After rendering with `--cover`, compare the exported `<city>_cover.png`
as a circle against the chosen variant: they must match.

Tell the user how to apply it: Edit Highlight, Edit Cover, upload `<city>_cover.png` (or pick
the reel's first frame).

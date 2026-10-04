---
name: highlight-cover
description: Design the title screen of a travel highlight so it doubles as the Instagram highlight cover: research a typeface that captures the place (local foundry, open licence), render big curved cover variants over the opening frame (bulge-smile, arched, caps), mock each into a screenshot of the user's highlights row, and let the user pick. Use inside /highlight or alone ("make a highlight cover for Tokyo", "redo the cover").
argument-hint: "<place> [background image or video]"
---

# Highlight cover

The reel's first frame is uploaded as the highlight cover, which Instagram shows as a small
circle cropped from the centre of the 9:16 frame. Design for that circle first.

```
C=~/.claude/skills/highlight-cover/scripts
uv run $C/fonts.py fetch <ttf-url> --dir fonts      # the chosen typeface
uv run $C/fonts.py info fonts/<file>.ttf --text "Tokyo"
uv run $C/cover.py --text Tokyo --font fonts/<file>.ttf --bg build/first.png --out covers \
    --row profile.png --slot 240,1190,151      # mock each variant into the user's profile
open covers/compare.jpg
```

## 1. Learn the user's series (once per session)

If the user has existing highlight covers, look at them (their Instagram profile in Chrome:
zoom on the highlight row; open one to see a full frame). Note: name placement, weight,
fill of the circle, text effects (e.g. a bulge warp), shadow. Match the series. Known
series so far: city name in heavy white with a soft shadow over the landmark, spanning
most of the circle; Amsterdam arches up; the approved Singapore cover is `bulge_smile`
(middle letters swell, word sags into a smile under the landmark).

**Ask for a screenshot of their profile** (the highlights row) and measure the circle the
new cover will occupy: centre x, y and diameter in screenshot pixels (scan a row and a
column through the circle for non-ring pixels). Every variant gets mocked into it.

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
2. `cover.py` renders the presets: `bulge_smile` (default), `smile`, `caps_smile`,
   `bulge_arch`, `caps_arched`, `subtle_low` (shown for contrast), plus any `--variant` JSON
   (`arch` > 0 bends up, < 0 sags into a smile; `bulge` swells the middle; `behind` hides
   letters behind a dark landmark). Mixed case usually shows a display face's character.
   **Size rule:** the word should span about 80% of the circle and stand at least 20% of
   its height; anything smaller vanishes next to the rest of the series. Text set on a
   circle (`textfx.curved_mask`) needs a large radius or it curls into an unreadable U.
3. Read `covers/compare.jpg` yourself first, judging the **in-row mock**, not the full frame:
   discard variants where the landmark or sun is hidden, the word touches the ring, or the
   word looks smaller than its neighbours in the row. Fix and re-render rather than
   presenting a broken one.
4. Open `covers/compare.jpg` for the user, describe each in one line with a recommendation,
   and wait for their pick. Never apply a cover they have not seen.

## 4. Apply

Copy the chosen variant's parameters into `reel.json`:

```json
"title": {"text": "Singapore", "font": "fonts/DTGetaiGroteskDisplay-Black.ttf", "width": 880,
          "condense": 0.72, "bulge": 0.6, "arch": -0.25, "cy": 1170, "shadow": 200, "until": 3.3, "fade": 0.8}
```

Also set the hero-block caption (`captions`, Open Sans from `fonts.py defaults`, since display
faces often lack `·`). After rendering with `--cover`, compare the exported `<city>_cover.png`
as a circle against the chosen variant: they must match.

Tell the user how to apply it: Edit Highlight, Edit Cover, upload `<city>_cover.png` (or pick
the reel's first frame).

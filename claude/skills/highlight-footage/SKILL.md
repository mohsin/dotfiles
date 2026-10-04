---
name: highlight-footage
description: Source, vet and choose vertical footage for a travel highlight: the user's own clips (iPhone HDR included), royalty-free Pexels stock via the browser, and YouTube drone/travel clips via yt-dlp. Builds a landmark-first shot list, catches still photos, hidden cuts, watermarks, borders and strangers, and writes the shots into reel.json. Use inside /highlight or alone ("find Singapore footage", "vet these clips").
argument-hint: "[city] [clips folder]"
---

# Highlight footage

Works in a highlight folder (`reel.json`, `clips/`, `stock/`, `yt/`). The footage mix comes
from the intake (see `../highlight/references/house-style.md`). Scripts:

```
F=~/.claude/skills/highlight-footage/scripts
uv run $F/sheet.py contact out.jpg clips/*.MOV --step 5      # what's in a clip
uv run $F/sheet.py crops out.jpg yt/a.mp4@236 yt/b.mp4@40@0.15 # the 9:16 window it becomes
uv run $F/vet.py yt/a.mp4 236 5.0                              # cuts, motion, borders, HDR
uv run $F/vet.py --scan yt/a.mp4 200 260                       # every cut/still in a range
```

Never full-transcode 4K clips just to look at them: `sheet.py` seeks.

## 1. Own clips (when the intake says there are any)

- Contact sheet every clip (`--step 5`, `--step 8` for long ones). Note per clip: what it
  shows, usable seconds, whether people the user knows are in frame.
- Map clips to itinerary items and the headline event. Event footage is the hero block.
- **Do not use shots of the user's friends or companions** without asking. If a great clip
  has them in part of it, use the other part.
- iPhone footage is HLG HDR; `render.py` auto-converts with `avconvert` (macOS). Nothing to do
  here except not judging colour from raw ffmpeg previews (they look flat).
- Phone audio of a performance can be the soundtrack: tell highlight-soundtrack which clips
  hold the headline song.

## 2. Stock: Pexels (free licence, no attribution required)

The API may refuse new keys, and pexels.com returns 403 to curl. Use the user's Chrome
(claude-in-chrome): open `https://www.pexels.com/search/videos/<query>/?orientation=portrait`,
then run in the page:

```js
const out = {};
for (const q of QUERIES) for (const p of [1, 2]) {
  const html = await fetch(`/search/videos/${encodeURIComponent(q)}/?orientation=portrait&page=${p}`).then(r => r.text());
  const m = html.match(/<script id="__NEXT_DATA__"[^>]*>(.*?)<\/script>/s); if (!m) continue;
  for (const it of JSON.parse(m[1]).props.pageProps.initialData?.data || []) {
    const a = it.attributes, f = (a.video?.video_files || []).filter(f => f.width >= 1080 && f.width <= 1440 && f.height > f.width)
      .sort((x, y) => x.width - y.width)[0];
    if (f) out[a.id] = { q, desc: (a.description || '').slice(0, 70), dur: a.video?.duration, url: f.link };
  }
}
window.__px = out; Object.keys(out).length;
```

Queries: the city, each landmark, "<city> night", "<city> drone". Page the results out in
chunks of about 12 (tool output truncates). Filter descriptions by landmark names, then
download with `curl -L -o stock/px_<id>.mp4 <url>` (the CDN is not blocked). Decline cookie
banners; never log in for this. Close the tab afterwards.

## 3. YouTube (third-party: say so in the report)

```
yt-dlp --flat-playlist --print "%(id)s | %(duration)s | %(title)s | %(channel)s" "ytsearch12:<city> 4K drone sunset night"
yt-dlp -f "bv*[height<=1440][ext=mp4]/bv*[height<=1440]" -o "yt/yt_%(id)s.%(ext)s" -- <id>
```

Best for golden hour, blue hour and night aerials that stock lacks. Expect: channel
watermarks (often bottom: crop with `wm`), titles in the first seconds, end credits, vlog
faces, still photos with borders, and hidden cuts.

## 4. Choose and vet shots

For every candidate:
1. `sheet.py crops` at 2 or 3 times across the planned range and two `x` positions: the
   landmark must stay in the 9:16 window for the whole shot.
2. `vet.py <file> <in> <dur>`: verdict must be OK. Fix rather than ignore: move the in-point
   past a cut, pick another shot when motion < 1.5, crop borders (`vcrop`), crop watermarks
   (`wm`), crop crowds (`box`), or stretch a clean take that is a little short (`speed` 0.9).
3. Reject: strangers as the subject, generic streets, the user's companions, anything static.

## 5. Write shots into reel.json

Lay shots over the audio parts from highlight-soundtrack (house-style pacing, in seconds;
convert with the song's `period`, figures here assume ~172 bpm): opening
8 to 14 beats with a cut on the drum entry, build 6 beats, hero 4 beats tagged (`"tag"`) for
the caption, final shot `"beats": null` so it runs to the end. The last shot of each part is
`null` too. Use `"in": "sync"` for a clip whose own audio is the soundtrack at that point.

Then `uv run ~/.claude/skills/highlight/scripts/render.py --plan`, and re-vet any shot whose
duration changed (a longer shot can run into a cut).

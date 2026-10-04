# reel.json

Shared state for one highlight. `project.py init` creates it; each sub-skill fills its part;
`render.py` reads all of it. Paths are relative to the folder holding reel.json.

```json
{
 "city": "Singapore",
 "fps": 30,
 "output": "singapore.mp4",
 "grade": "eq=contrast=1.04:saturation=1.12",
 "end_fade": 3.5,
 "audio": {
  "segments": [
   {"file": "audio/live_0500.wav", "start": 64.93, "end": 92.58, "beats": "audio/live_0500.beats.npy"},
   {"file": "audio/live_0500.wav", "start": 115.03, "end": 128.03, "beats": "audio/live_0500.beats.npy"},
   {"file": "audio/live_0501.wav", "start": 33.61, "end": 53.62, "beats": "audio/live_0501.beats.npy"}
  ],
  "xfade": 0.03, "fade_in": 0.5, "tail_fade": 1.2, "loudnorm": -14
 },
 "title": {"text": "Singapore", "font": "fonts/DTGetaiGroteskDisplay-Black.ttf", "width": 720,
           "condense": 0.8, "bulge": 0.35, "cy": 1180, "shadow": 170, "until": 3.3, "fade": 0.8},
 "captions": [
  {"tag": "concert", "lines": [
   {"text": "The Weeknd", "font": "fonts/OpenSans-Bold.ttf", "size": 104, "dy": 0},
   {"text": "After Hours Til Dawn · National Stadium", "font": "fonts/OpenSans-SemiBold.ttf", "size": 40, "dy": 92}]}
 ],
 "shots": [
  {"part": 0, "beats": 14, "src": "yt/yt_8YCLcmDzN2w.mp4", "in": 236.0, "zoom": [1.0, 1.07]},
  {"part": 0, "beats": 10, "src": "clips/landing.MOV", "in": 103.0},
  {"part": 0, "beats": 8, "src": "stock/px_3502581.mp4", "in": 20.0, "box": [0.22, 0.12, 0.62]},
  {"part": 0, "beats": null, "src": "yt/yt_nSs1WQdBYeI.mp4", "in": 34.85, "x": 0.12},
  {"part": 2, "beats": 8, "src": "clips/IMG_0501.MOV", "in": "sync", "tag": "concert"},
  {"part": 2, "beats": null, "src": "yt/yt_NNsOihnkVAs.mp4", "in": 366.8, "wm": true, "zoom": [1.08, 1.0]}
 ]
}
```

## Audio

- `segments`: played in order, joined with `xfade` crossfades. `beats` is the beat-time
  array for that file (`structure.py` writes `<stem>.beats.npy`).
- `fade_in`: seconds at the very start. `tail_fade`: only for a crowd tail after the music
  ends (0 for studio tracks that decay naturally). `loudnorm`: target LUFS, or omit.

## Shots

| Field | Meaning |
|---|---|
| `part` | Which audio segment the shot sits in; shots never straddle a splice |
| `beats` | Length in beats; `null` fills to the end of its part (the last shot of a part) |
| `src`, `in` | Source file and in-point (s). `"sync"` plays a clip under its own audio |
| `x` | Horizontal 9:16 crop position for landscape sources (0 left, 0.5 centre, 1 right) |
| `wm` | Crop the bottom 10% (channel watermark) |
| `vcrop` | `[top, height]` fractions, for photos with borders |
| `box` | `[x, y, w]` fractional window for a portrait source (crop above a crowd) |
| `zoom` | `[start, end]` scale for a slow push-in or pull-out |
| `speed` | Playback rate (0.9 stretches a clean take that is slightly short) |
| `hdr` | Force HDR conversion (auto-detected from the file otherwise) |
| `tag` | Groups shots for a caption |

## Title

Rendered by `highlight-cover/scripts/textfx.py`; the same parameters as the chosen
cover variant, so the reel's first frame is the cover.

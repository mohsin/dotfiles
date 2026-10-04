---
name: highlight-soundtrack
description: Pick and cut the song for a travel highlight so it starts on the song's own intro and ends where the music ends by itself, about 60 s, with every splice on a matching beat. Handles studio tracks (synced lyrics from LRCLIB) and live phone recordings of a concert (whisper word timings). Writes audio segments and beat grids into reel.json. Use inside /highlight or alone ("cut this song to 60 s", "use my concert recording").
argument-hint: "[song or recording] [target seconds]"
---

# Highlight soundtrack

```
S=~/.claude/skills/highlight-soundtrack/scripts
uv run $S/structure.py audio/song.m4a --artist "<artist>" --track "<title>"
uv run $S/splice.py pairs audio/song.wav --from 17 28 --to 44 51
uv run $S/splice.py align audio/a.wav --audio2 audio/b.wav --at 129.0 --search 30.5 36
uv run $S/transcribe.py clips/IMG_0501.MOV --start 20 --end 53
```

## 1. Choose the song (ask)

Offer, with a recommendation first:
- The city's signature song (the nostalgic classic locals know; for Singapore, Kit Chan's
  "Home"). This is the series default.
- The headline artist's song when the trip centres on a concert.
- The user's own live recording of that song (their footage, their night), when they have it.
- "Add in Instagram": render with the planned song for timing, then the user swaps in the
  licensed in-app track (needs one continuous excerpt, see step 5).

Download studio audio with `yt-dlp -x --audio-format m4a -o "audio/<name>.%(ext)s" <url>`
(prefer the artist's official upload).

## 2. Map the structure

- Studio track: `structure.py` with artist and track. It writes `<stem>.beats.npy`,
  `<stem>.structure.json`: tempo, sections, where the music really ends, and LRCLIB synced
  lyrics. **Use the lyrics for structure** (intro, verse, pre-chorus, chorus, bridge, final
  line); chroma alone will happily pick musically seamless but useless jumps.
- Live recording: extract audio (`ffmpeg -i clip.MOV -vn -ac 2 -ar 44100 audio/x.wav`), run
  `structure.py` (beats), then `transcribe.py` for word timings. If the user points at a
  timestamp ("from 1:05"), honour it. Render a spectrogram
  (`showspectrumpic=s=1600x400:scale=log:fscale=log:stop=8000`) to see where the band drops
  out and where the crowd takes over: that is the natural ending.
- Recordings from the same night may be separate files with a gap between them
  (check `creation_time`); treat them as one performance at different points.

## 3. Design the cut (~60 s, three parts)

Default shape: **intro** (0:00 to just before the first verse; title and slow shots) then
**build** (the pre-chorus) then **the last chorus line through the natural ending**.

- Start at 0:00 (studio) or the first musical onset at the user's chosen time (live), with a
  0.3 to 0.5 s fade-in. Never mid-verse.
- End where the music decays to silence. Never fade the music early. A crowd tail after the
  music may take a 1.2 s fade (`tail_fade`).
- Splices: within one take, keep both cut points a multiple of 16 beats apart
  (`splice.py pairs`, score > 0.9). Across arrangements, cut at the same lyric onset in both
  places and align it with `splice.py align` (the offsets from `pairs` and `align` should
  agree).
- Too long? Shorten the intro or the build, never the ending.

## 4. Write reel.json

```json
"audio": {"segments": [{"file": "audio/song.wav", "start": 0.0, "end": 26.26, "beats": "audio/song.beats.npy"}, ...],
          "xfade": 0.03, "fade_in": 0.5, "tail_fade": 0, "loudnorm": -14}
```

Tell highlight-footage the timeline landmarks: drum entry, part boundaries, the chorus hook
(the hero block goes there).

## 5. Copyright (be straight with the user)

- Instagram may mute or block a copyrighted song, including a live recording (the
  composition is matched, not just the master).
- Never add noise, pitch-shift, speed-change or otherwise disguise audio to evade detection.
  Refuse plainly and offer: the in-app music library (re-cut the video to one continuous
  excerpt and give the exact start time to pick), or the user's own recording.

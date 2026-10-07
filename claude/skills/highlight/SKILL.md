---
name: highlight
description: Make an Instagram travel highlight for a city or trip: a ~60 s vertical reel cut on the beat to the place's signature song, with a cover-ready title screen. Runs an intake questionnaire (before or after the trip, own clips, itinerary, headline event), then the highlight-footage, highlight-soundtrack and highlight-cover sub-skills, then renders. Use for "make a reel/highlight for <city>", "edit my <trip> clips", or a new entry in a travel highlight series. Reference videos are optional.
argument-hint: "<city or trip> [clips folder] [itinerary file]"
---

# Highlight

Produce `<city>.mp4` (1080x1920, ~60 s) and `<city>_cover.png` in a working folder, driven
by `reel.json`. Scripts run with `uv run` (dependencies install themselves on first use).

```
HL=~/.claude/skills            # skills come from ~/Projects/dotfiles/claude/skills (copied)
```

Read `references/house-style.md` before planning anything: it is the format to follow when
no references are given. `references/lessons.md` lists mistakes that must not repeat.
`references/reel-json.md` documents the state file.

## Step 1: Intake (always ask; never assume)

Ask with AskUserQuestion, in one round where possible. Skip only what the user already
answered in their request.

1. **Timing:** "Before the trip (no clips yet)", "During or after the trip (I have clips)".
2. **Own clips:** if they have any, the folder (Other lets them paste a path). Ask whether
   another person's phone (a travel companion's) holds the event footage too.
3. **Itinerary:** "Yes, here's the file" (path via Other) or "No itinerary".
4. **Headline moment:** a concert, festival, match or event the trip centres on, or none.

Optional follow-ups only when they change the result: reference reels to match (default:
house style), people who must not appear, target length if not ~60 s.

Save answers to `intake.json` in the working folder.

## Step 2: Decide the plan from the answers

- **Footage mix:** use the table in house-style.md. Before the trip means stock and YouTube
  only. With clips, own footage covers personal moments and the headline event; stock covers
  landmarks. With an itinerary, map clips to itinerary items and list the landmarks still
  needing stock.
- **Shot list:** 10 to 14 iconic landmarks plus the itinerary's places (read the itinerary;
  pick visual places, skip hotels and transit). Order: golden hour, blue hour, night.
- **Hero block:** the headline moment, if any; otherwise the most spectacular night landmark.
- Tell the user the plan in a few lines (mix, hero, song direction) before sourcing.

## Step 3: Set up

```
uv run $HL/highlight/scripts/project.py init "<City>" [--clips <folder>]
cd ~/Movies/Highlights/<city>
uv run $HL/highlight-cover/scripts/fonts.py defaults     # caption fonts
```

If reference reels were given, copy them into `refs/` and study them first (scene-cut pacing,
title style, ending): `sheet.py contact` plus `ffmpeg -vf "select='gt(scene,0.25)',showinfo"`.
Their choices override house-style.md.

## Step 4: Run the sub-skills (in this order; each writes its part of reel.json)

1. **highlight-soundtrack:** pick the song (ask), map its structure, choose segments that
   start on the intro and end naturally, write `audio.segments`. The music sets the timeline,
   so this comes before shot timing.
2. **highlight-footage:** source, vet and choose shots; write `shots` with beat lengths that
   follow house-style pacing and the segment boundaries.
3. **highlight-cover:** typeface, title variants, user picks; write `title` (and the
   caption for the hero block).

Invoke each with the Skill tool and follow it fully; they are also usable on their own.

## Step 5: Render and verify

```
uv run $HL/highlight/scripts/project.py check
uv run $HL/highlight/scripts/render.py --plan     # timeline sanity: ~60 s, cuts on beats
uv run $HL/highlight/scripts/render.py --cover
```

Verify before reporting (the user cannot see your checks; do them all):
- Contact sheet of the output at 2 fps: no flashes from cuts, no borders, no watermarks, no
  strangers or companions, every shot moving, day-to-night order.
- Title frame and caption frames at full size; the cover as a circle (highlight-cover's
  `cover.py` or `textfx.circle`).
- Audio: RMS of the first second rises from silence; the last 8 s decays to silence; splices
  hold level (`astats` per 0.5 s); loudness about -14 LUFS (`ebur128`).
- Then report: what is where (timestamps), sources and licences (own, Pexels, YouTube
  creators), the song's copyright status, and that you have not watched it in real time.

## Step 6: Iterate

Feedback usually lands on single shots, the cover or the song. Edit `reel.json` and re-render:
the shot cache re-renders only what changed. When the user corrects something that would
recur, add it to `references/lessons.md` and, if it is a rule, `house-style.md`.

## Rules

- Never publish or post anything; output files only.
- Never alter audio to slip past copyright detection; offer the in-app music library or the
  user's own recording.
- Downloads come from sources the user approved in this session (their clips, Pexels,
  YouTube via yt-dlp).

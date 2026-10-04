# Lessons

Things that went wrong once and must not again. Each is backed by a check in the skills.

## Feedback from the user

- **The ending cut before the music came down** (the Paris reference). The edit must end where
  the recording ends. Check: RMS of the last 8 s decays to silence before the file ends.
- **The song started abruptly** (began mid-verse at 1:00). Start on the real intro.
- **Random people on screen** (riders in front of shophouses). Landmarks only.
- **A friend's face** in a selfie shot. Ask before using anyone the user knows.
- **A shot that did not move** (a vlogger's still photo inside a YouTube video). Vet motion.
- **The title fought the landmark** on the cover. Render variants, keep the landmark visible.
- **The cover is a circle.** Design and preview the title at profile size, not full frame.
- **Too long.** About 60 s; cut stock before the user's own moments.

## Technical traps

- Pexels API key issuance can be paused, and stock sites return 403 to curl. Open the search
  page in the user's Chrome and read `__NEXT_DATA__` (see highlight-footage); the
  `videos.pexels.com` CDN downloads fine.
- iPhone clips are HEVC 10-bit HLG. ffmpeg without zscale cannot tone-map; `avconvert` can.
- Homebrew ffmpeg may lack `drawtext` (no freetype): all text is drawn with PIL and overlaid.
- YouTube compilations hide cuts, titles, credits, still photos and photo borders inside
  ranges that look fine on a contact sheet. `vet.py` every range.
- Beat trackers return nothing through drumless intros and outros: extend the grid at the
  measured period (structure.py does).
- Chroma similarity alone picks musically seamless but useless splices (intro riff straight
  into the identical outro riff). Use synced lyrics for structure.
- Chroma matching cannot identify songs in stadium audio; transcribe instead.
- faster-whisper's own file decoding breaks on some PyAV versions; pass a numpy array.
- The shot cache must be keyed by content, not position, or removing a shot shifts every
  later cached file onto the wrong slot.

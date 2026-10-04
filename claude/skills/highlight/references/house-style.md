# House style

The default format for a city highlight when the user gives no reference videos. It is
distilled from the edits the user rated best (Paris, then the Singapore reel built with
these skills). Reference videos, when given, override any line here.

## Shape

- **Length:** about 60 s. Never past 75 s without asking.
- **Aspect:** 1080x1920, 30 fps, H.264 + AAC 256k, `-movflags +faststart`.
- **Pacing is in seconds; convert to beats for the song** (`beats = seconds / period`, period
  from structure.json; the grid is normalised to 100-180 bpm). Beat counts below assume
  ~172 bpm (period 0.35 s).
- **Three movements, all cut on the beat:**
  1. **Opening (0 to ~27 s):** the song's own intro. Title over a golden-hour or blue-hour
     aerial of the city's signature landmark. Slow shots of 8 to 14 beats (3 to 5 s), with
     one cut landing exactly where the drums enter.
  2. **Build (~27 to ~40 s):** the city at night, 6-beat shots (about 2 s).
  3. **Peak and ending (~40 to 60 s):** the hero moment (an event, a concert, a festival)
     in 4-beat shots (about 1.4 s) with its own caption, then one long final shot (6 to 9 s)
     that fades to black while the music finishes on its own.

## Footage mix (decided from the intake answers)

| Situation | Mix |
|---|---|
| Before the trip, no clips | 100% stock and YouTube: landmarks, golden hour, night aerials |
| Clips, no itinerary | Own clips for personal moments and any event; stock for landmarks |
| Clips and itinerary | Own clips mapped to itinerary items first; stock only for landmarks not filmed |
| Clips of a headline event | That event is the peak block, own footage only, with a caption |

Own clips win whenever they are usable (sharp, steady enough, not just people's faces).
Stock carries the "proper city" look: landmarks, skyline, aerials. Never fill with generic
street scenes.

## Footage rules

- **Landmarks, not strangers.** Drop shots where passers-by, riders or tourists are the
  subject. Crop above the crowd when the landmark is worth keeping.
- **No friends or the user's companions on screen** without asking first, even from the
  user's own clips. The event itself, yes; selfies, no.
- **Everything must move.** Vet every shot: a "video" segment can be a still photo.
- **One continuous take per shot.** No scene cut inside a shot's range.
- **No watermarks, logos, in-video titles, end credits or photo borders.**
- **Order tells the day:** sunset and golden hour before blue hour, before night.

## Title and cover

- The first frame is the Instagram highlight cover, so the title is designed as a cover
  (see highlight-cover).
- **Typeface:** one that captures the place, preferably from a local foundry under an open
  licence (Singapore: DT Getai Grotesk by Death of Typography). Not a generic sans.
- **Approved default (`bulge_smile`):** mixed case, width 880 of 1080, condense 0.72, bulge
  0.6, arch -0.25 (sags into a smile), centred at y 1170, shadow 200. Big enough to match the
  rest of the highlights row; the landmark and sunset sit above the curve.
- **Timing:** fully visible to 2.5 s, fades out by 3.3 s.
- **Always render variants, mock them into a screenshot of the user's highlights row, and
  let the user choose** before it goes into the reel.

## Captions

- One caption, on the hero block only: event name large (Open Sans Bold 104), a detail line
  below (Open Sans SemiBold 40), e.g. "After Hours Til Dawn · National Stadium".
- Fades 0.25 s in and out, at 66% height.

## Sound

- **Start on the song's real intro** (0:00, or the first onset of a live recording), with
  a 0.3 to 0.5 s fade-in. Never start mid-verse.
- **End where the music ends by itself.** Never fade or cut the music early. A crowd or room
  tail after the music may get a short fade.
- Loudness about -14 LUFS, true peak -1.5 dB.
- **Song choice:** the city's signature song by default; the headline artist's song when
  the trip centres on a concert (offer both, user picks).
- **Never alter audio to evade copyright detection.** Offer the in-app music library or the
  user's own recording instead.

## Grade

`eq=contrast=1.04:saturation=1.12` on everything; iPhone HDR tone-mapped to SDR first.

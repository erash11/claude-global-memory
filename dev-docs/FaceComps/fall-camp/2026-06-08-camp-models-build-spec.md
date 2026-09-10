# 2026 Fall Camp — Candidate Models, Build Spec (post-grill)

**Date:** 2026-06-08  **For:** Dave Aranda + defensive staff
**Supersedes the framing of:** `docs/fall-camp/2026-06-05-candidate-camp-models.md`
**Design spec:** `docs/superpowers/specs/2026-06-04-fall-camp-2026-load-model-design.md`

This is the locked build contract from the 2026-06-08 grill. It records every decision so a
context loss can't erase the reasoning. The 6 models get rebuilt to this spec; the relabel
propagates to the docs/decks/script listed at the bottom.

## What changed in this grill (and why)

1. **The "game day / game week" labels were wrong.** The 92-min and 370-min anchors were never
   measured from a game. They come from the in-season **prep-practice** data
   (`docs/fall-camp/inseason_duration_2025.csv`): 370 active min across the four Mon-Thu prep
   practices = an in-season **week**; ÷ 4 = ~92 min = an in-season **day**. Same active-minute
   method (work ÷ intensity) as everything else — the 3-hour broadcast clock was never used.
   → **Relabel** to "in-season day / in-season week." The inoculation pitch gets stronger and more
   honest: *camp builds them up to and past the season's daily demand, so September is nothing new.*
2. **Coach wants a 3-4-5 day-count ramp** (consecutive practice days grow toward a 5-in-a-row
   finish), not the 3/3/4/4 the current models are built on. Block length is Coach's own
   periodization dial (accumulation); intensity is ours (stimulus). They now ramp the same
   direction → one clean Block-4 peak. We present **both** the 14-day and 15-day finishes so Coach
   picks the structure.

## Locked decisions (the build contract)

1. **Relabel.** "in-season day" (92 min) / "in-season week" (370 min). Drop all "game day/week."
   **Lead the room with the block-vs-in-season-**week** comparison**; per-day % stays as cell detail.
2. **Six builds, two-decision navigation.**
   - **Decision 1 (Coach):** structure / how camp finishes — **14-day (3/3/4/4)** vs
     **15-day (3/3/4/5)**.
   - **Decision 2 (Eric):** intensity flavor — **Conservative / Moderate / Aggressive**.
   - Coach navigates **2 then 3, never 6 at once.**
3. **Fixed back end (constant across all 6).** taper → **Mock game week** (in-season 5-practice
   cadence) → real game week → **Auburn, Sep 5**. Shown once at the bottom as the constant bridge;
   the mock week rehearses Week 1.
4. **Hard rule — no two RED days back to back.** Applies to consecutive **practice** days only.
   An **off/film day between two reds counts as recovery** (red → off → red is legal). Current
   Moderate (Aug 20→21) and Aggressive (Aug 20→21, Aug 15→16) **break this and get re-sequenced**;
   Conservative already complies.
5. **Hard rule — the longest block carries the most embedded recovery.** The 5-day peak block
   (15-day structure) is never five straight hard days; it alternates reds with real recovery
   (e.g. R-G-Y-G-R / Y-R-G-Y-R). The peak block being longest is *why* it needs the most recovery,
   not the least — that's the line between a peak and a death march.
6. **Scrimmages ride the intensity axis.** Conservative **2** / Moderate **2** / Aggressive **3**.
   A 3rd scrimmage does not add load — it **re-characterizes** an existing RED from full-pads/thud
   (drill-based) to full-live/situational/officiated. Same active minutes, **higher collision/contact
   exposure** — that's the real cost of "Aggressive." Keeps red *count* driven by flavor, and keeps
   scrimmage count inside Decision 2 (no new axis for Coach).
7. **Taper held constant.** Identical recovery runway into the mock week and Auburn for every model.
   The 15-day's extra install day comes out of the **install middle or an earlier off day — never
   the taper.** Freshness into Game 1 is identical across all 6. Vary the middle, protect the arrival.
8. **Day-type targets (GPS-realized, unchanged).** GREEN 85 min / 9 per · YELLOW 112 / 12 ·
   RED 132 / 13-14, against the ~92-min in-season day. Reps track the day-type; reps gate the
   green/yellow seam (2026-06-03 secondary-modifier test).

## The spine (how Eric walks the room)

- **Recommendation = Moderate intensity.** Textbook polarized build, recovery between every hard
  day, complies with no-back-to-back-reds. Conservative = recovery-safety option; Aggressive =
  max-stress / max-contact contrast.
- **Structure is presented neutral.** 14-day and 15-day get **equal depth and equal framing** in
  the deck. **No "recommended" tag on the 15-day** — the 3-4-5 stays Coach's discovery. The only
  recommendation voiced anywhere is the intensity.

## The seven-word rule Coach can hold

> *"We never stack two max days."* — every hard day earns a recovery before the next.
> The whole polarization thesis in a sentence Coach can repeat and enforce himself.

## Build to-do (after this spec is confirmed)

- **Rebuild all 6 models** to the rules above (re-sequence Moderate & Aggressive for
  no-back-to-back-reds; build the 15-day 3/3/4/5 with embedded recovery in the 5-day block;
  hold taper constant). Calendar is fluid — place days at discretion, flag which off day the
  15-day spends.
- **Propagate the relabel** ("in-season day/week", drop "game") to:
  - `docs/fall-camp/2026-06-05-candidate-camp-models.md`
  - `scripts/render_camp_models.py` (regenerates `2026-fall-camp-models.html`,
    `2026-fall-camp-models-internal.html`, and the `-internal.pdf`)
  - `docs/superpowers/specs/2026-06-04-fall-camp-2026-load-model-design.md`
- **Deck reframe:** lead with block-vs-in-season-week; per-day % as cell detail; both structures
  equal weight; intensity is the only voiced recommendation.

## BUILD COMPLETE — 2026-06-08 (new files, originals untouched)

All six models rebuilt and machine-validated (zero back-to-back reds, every model ramps to a
Block-4 peak, scrimmages 2/2/3, red ladder Cons 3 / Mod 5 / Agg 6 at 14d and 3 / 6 / 7 at 15d).

- `docs/fall-camp/2026-06-08-candidate-camp-models-v2.md` — the six models (source of truth)
- `scripts/render_camp_models_v2.py` — encodes + validates + renders
- `docs/fall-camp/2026-fall-camp-models-v2.html` — coach-facing deck (color toggle)
- `docs/fall-camp/2026-fall-camp-models-internal-v2.html` — internal color-on variant
- `docs/fall-camp/2026-fall-camp-models-internal-v2.pdf` — print-ready landscape
- `docs/superpowers/specs/2026-06-08-load-model-relabel-addendum.md` — relabel note for the spec

**One design finding locked during build:** under no-back-to-back, a 7th red cannot fit the 14-day
(3/3/4/4) without spiking an early block hotter than the finish, so 14-day Aggressive carries 6 reds
(peaks as a B3≈B4 plateau). The 15-day's five-day block absorbs the 7th red into a clean single
peak — a structural argument for 15 days when the staff wants maximum stress.

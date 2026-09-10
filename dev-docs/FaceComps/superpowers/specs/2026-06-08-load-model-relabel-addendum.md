# Relabel Addendum — "in-season day/week" (2026-06-08)

**Applies to:** `docs/superpowers/specs/2026-06-04-fall-camp-2026-load-model-design.md`
**Reason:** the 92-min and 370-min anchors were mislabeled. They are **not** game measurements.

## The correction

The reference anchors come from the in-season **prep-practice** data
(`docs/fall-camp/inseason_duration_2025.csv`), computed with the same active-minute method
(work ÷ intensity) as every other number in the model — never the broadcast clock, never a game.

| Old label (do not use) | Correct label | What it actually is |
|---|---|---|
| "game week" (370 min) | **in-season week** | a normal in-season prep week, 4 Mon-Thu practices |
| "game day" (92 min) | **in-season day** | that week ÷ 4 — a normal in-season practice day |

## Why it matters

- The "3-hour GPS duration" objection never applied: that raw broadcast figure was never used.
- The "a game is only 60 minutes" objection dissolves: the anchor isn't a game, it's a practice day.
- The inoculation pitch gets stronger and more honest: *camp builds them up to and past what the
  season demands every single day, so September is nothing they haven't already done.*
- **Presentation:** lead with the block-vs-**in-season-week** comparison (coaches think in weeks);
  the per-day % stays as cell-level detail.

The design spec's math is unchanged — only the labels move. All downstream artifacts (the v2
candidate-models doc and the v2 HTML/PDF decks) already use the corrected labels.

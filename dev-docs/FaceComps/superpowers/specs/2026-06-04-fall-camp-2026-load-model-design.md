# Fall Camp 2026 Load Model and Macro Calendar — Design Spec

**Date:** 2026-06-04
**Owner:** Eric Rash (Baylor Football, Applied Performance)
**Audience:** Dave Aranda + defensive staff (coach-facing view); Applied Performance (internal view)
**Status:** Design approved; building multiple candidate models for staff selection

> **Update 2026-06-04 (evening):** Two refinements locked after review. (1) The macro unit is
> **work-blocks** (consecutive practice days between off/film days), not calendar weeks — that is
> how fatigue actually accumulates. (2) The deliverable is **multiple candidate camp models** for
> Aranda to react to and pick, not a single prescription. Dress/scrimmage sequencing is flexible.
> See "Macro layer" and "Build sequence" below.

## Purpose

Turn Baylor's own GPS history into a prescriptive plan for the 2026 fall camp: a
day-type model (green / yellow / red) across three calibrated dimensions, ramped across
camp on a deliberate build, and rendered on a days-of-the-week calendar like the staff's
existing camp sheets. Color stays internal (Aranda's call); the coach-facing version shows
duration, periods, and structure without the traffic-light coding.

The deliverable answers one question for every camp day: **how long should we be out
there, how many periods should we run, and how hard should the day be relative to a game
day.**

## Two problems this fixes (both confirmed in Baylor's data)

1. **Front-loaded camps.** 2024/2025 came out hot and stayed hot: Weeks 2 and 3 ran ~180%
   of a game week cumulatively and ~147% per day, with no real ramp-in. The result was
   accumulated fatigue heading into Game 1. Fix: a textbook progressive ramp (lower, later
   peak, taper into the opener).

2. **Training monotony — colors that weren't actually different.** Historical day-types sat
   almost on top of each other: GREEN median 105 min, YELLOW 115, RED 133. Green-to-yellow
   was a 10-minute gap with fully overlapping ranges. A "green" day and a "yellow" day were
   the same day. Day-to-day variation was unstructured noise (~20 min), flatter than an
   in-season game week, which swings 36 min top to bottom with a clear light-Monday /
   peak-Tuesday rhythm. Flat + heavy = high weekly strain. Fix: **polarize** the day-types
   so green is genuine recovery and red is isolated overload.

These two levers reinforce each other, and together they also dissolve the green/yellow
classification fuzziness from the earlier calibration work: when an 85-minute green sits
well below a 112-minute yellow, no secondary rep-gate is needed to tell them apart. Better
programming makes the model cleaner for free.

## Data foundation (all Baylor, all GPS-realized; established 2026-06-04)

| Source | Role | Method / notes |
|---|---|---|
| Baylor 2024/2025 fall camps (35 days) | **Day-type calibration** | Active minutes = `average_player_load / player_load_per_minute` summed over periods after the first stretch (BREAK rows excluded). Joined to realized PL/player zone and FC25 Ones reps. Files: `docs/fall-camp/fall_camp_duration_thresholds.csv`, `fall_camp_daily_thresholds.csv`, `fc25_rep_calibration_QA.xlsx`. |
| Baylor 2025 in-season (11 game weeks) | **Game-week reference (the ramp anchor)** | Same active-minute method. Pulled via `simulator/scripts/build-inseason-duration.ts` → `docs/fall-camp/inseason_duration_2025.csv`. |
| Kansas State 24/25 camp models + Baylor 2026 projected calendar | **Structural template** | `SourceFaces/Camp_Models.pdf` (3 pages). Structure only, no GPS. Provides camp cadence, dress progression, and the 2026 skeleton. |

**Game-week reference (100%):** ~370 active minutes Mon–Thu, i.e. a **game day ≈ 92 min**.
Stable daily microcycle: Mon ~69 (helmets), Tue ~105 (peak, full pads), Wed ~88 (shells),
Thu ~98 (helmets/spiders). In-season weeks decay across the season (early 387–404, late
336–342); the early-season weeks are the closest analog to camp.

## The model

### Micro layer — the day-type spine (three dimensions)

Primary dimension is **active duration**; **period count** tracks with it cleanly; **Ones
reps** are the third dial (paused on the in-season side, kept in the camp model). Anchored
to a 92-min game day. Targets are the **prescribed, polarized 2026 bands**, not the
overlapping historical medians:

| Day | Active min (target / range) | % of game day | Periods | Ones reps | Character |
|---|---|---|---|---|---|
| **GREEN** | **85** (70–95) | 92% | 9–10 | ≤ 20 | True recovery. Helmets/shells, tag. Pulled **down** from the historical 105. |
| **YELLOW** | **112** (105–120) | 122% | ~12 | 24–30 | Bread-and-butter install day. |
| **RED** | **132** (128–145) | 143% | 13–14 | not the lever | Isolated overload. Color comes from **pads and live**, not rep volume. Held, not pushed higher. |

Separation: green→red now differ by ~47 min with no band overlap (was 28 min, overlapping).
Reps cleanly floor green (≤20) but cannot separate yellow from red — red is intensity-driven
(a full-pads live day is red on 16 Ones reps). Dress/tempo, not reps, carry the yellow→red
distinction.

### Macro layer — the ramp

Textbook build, a deliberate change from Baylor's front-loaded history. **Anchored per day**
(keeps any single day from running away), expressed in **both** units. The macro unit is the
**work-block** (consecutive practice days between off/film days), the real fatigue microcycle.

Block structure of the 2026 install camp (per the page-1 calendar, off/film days Aug 8/12/17/22):

| Block | Dates | Days | Ramp | Character |
|---|---|---|---|---|
| **Block 1** | Aug 5–7 | 3 | 70% | ease in, helmets, no red |
| **Block 2** | Aug 9–11 | 3 | ~90% | build, shells, first full pads |
| **Block 3** | Aug 13–16 | 4 | ~105% | longer block; scrimmage 1 |
| **Block 4** | Aug 18–21 | 4 | 120% (peak) | full pads / live; scrimmage 2 |
| **Mock week** | Aug 23–28 | — | run as an in-season game week; controlled-contact Mock (Aug 29) |
| **Game week** | Aug 31–Sep 4 | — | the ~370-min game-week template into Auburn (Sep 5) |

- Block length does part of the ramping: the 3-day blocks carry less than the 4-day blocks
  simply by being shorter, and Block 4 (longest + hardest dress) is the overload.
- The ramp sets each block's **average day**; the block is a *sequence* of green/yellow/red
  day-types, polarized **within** the block (real recovery days between hard days) so strain
  does not compound.
- **Per-day cell** shows intensity as % of a game day. **Per-block banner** shows the ramp
  label plus cumulative active minutes and % of a game week.
- The 120% peak is pinned to a game **day**, so the peak block's hardest day lands near
  ~132 min (143% of a game day) rather than the historical 147%+. Peaks lighter on purpose.
- Color follows dress/tempo (helmets/tag → green floor; shells/thud → yellow; full pads or
  live → red); duration is then polarized to the day-type targets. To make Block 4 the
  unambiguous peak, dress and scrimmage placement may need re-sequencing (it is flexible).

## The artifact

A days-of-the-week calendar (Sun–Sat monthly grid) modeled on the staff's existing Kansas
State and Baylor 2026 sheets, built on the **Baylor 2026 projected structure**
(`Camp_Models.pdf` page 1) as the skeleton.

- **Day cell:** practice number, dress/tempo, situational theme (from the projected
  structure), plus the prescribed duration target, period count, and per-day % of a game
  day. (Ones-rep target added when the in-season rep work is done.)
- **Week banner:** ramp label (70/100/120/taper), cumulative active minutes, % of a game
  week.
- **Two views:** coach-facing (no traffic-light color, per Aranda) and internal (color
  shown). Same grid, color layer toggled.

Output medium (printable HTML vs Excel vs Word) is deferred to the build, decided once the
structure is final.

## Build sequence (what's still needed)

1. **DONE** — 2026 structure reconciled: page-1 calendar (placement, off/film days, Mock,
   Auburn Sep 5) + `fall_camp_faces.json` (P1–P18 dress/tempo/emphasis/minutes content).
   Block structure confirmed by Eric (3/3/4/4 + taper + game week).
2. **Build 2–3 candidate camp models** for Aranda to choose from, e.g.:
   - *Conservative* — lowest open, latest/lowest peak, most green recovery.
   - *Moderate* — the polarized textbook ramp (the working draft).
   - *Aggressive* — closer to Baylor's historical loads, for contrast.
   Each model: per-day green/yellow/red with duration + periods, polarized within each block,
   peak in Block 4, plus block and game-week cumulative.
3. Each model needs dress/scrimmage sequencing resolved so Block 4 is the clean peak
   (sequencing is flexible per Eric).
4. Choose the output medium and render the candidate models as the two-view calendar(s) for
   the coaching review.

## Open / deferred

- **Output medium** — HTML / Excel / Word, decided at build time.
- **In-season Ones reps** — paused (manual counting); revisit to make the game-week anchor
  three-dimensional and firm up the rep targets.
- **FC24 dress/tempo modifier test** — would finish the historical composite toward ~91%,
  but lower priority now that polarization removes the green/yellow boundary fuzziness.
- **Planned-vs-realized color validation** — if Baylor's 24/25 faces hold an intended color
  or dress plan, overlay it against realized zones as proof-of-value.
- **Simulator integration** — eventually attach the model to the `'2026 Fall Camp'` season
  in the deployed app (new macro-planner view).

## Method / provenance notes (for reproducibility)

- All durations are GPS-realized active minutes via `avg_pl / pl_per_min` after the first
  stretch, identical across camp and in-season pulls (Catapult `total_duration` is
  athlete-seconds, not wall-clock — do not use it).
- Pulls use the `catapult-openfield-connect-pp-cli` pipeline / the simulator `CatapultClient`
  with `CATAPULT_TOKEN` from `simulator/.env.local`. In-season activities are named
  `{OPPONENT} - P{N} - MM.DD.YY`; games are `{OPPONENT} - G{N} - ...`.
- Day-color zones use the FC24/FC25 PL/player thresholds (GREEN ≤405, YELLOW 406–459,
  RED >459); duration bands are GREEN ≤102 / YELLOW 102–117 / RED >117 active min for
  *classification* of historical days. The **prescribed** 2026 targets above intentionally
  separate further than those historical bands.

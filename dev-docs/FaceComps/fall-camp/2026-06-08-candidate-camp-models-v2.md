# 2026 Fall Camp — Candidate Macro Models (v2)

**Date:** 2026-06-08  **For:** Dave Aranda + defensive staff
**Build spec:** `docs/fall-camp/2026-06-08-camp-models-build-spec.md`
**Supersedes (does not overwrite):** `docs/fall-camp/2026-06-05-candidate-camp-models.md`

Six calibrated builds of the install camp, presented as **two decisions, not one menu**. Every day
is anchored to GPS-realized in-season practice load. All sequences are machine-checked against the
hard rules below (no two red days back to back; ramp to a single Block-4 peak; scrimmage counts by
flavor).

## What changed from v1

1. **Relabel — the anchor was never a game.** The 92-min and 370-min reference points come from the
   in-season **prep-practice** data (`inseason_duration_2025.csv`), not from a game: 370 active min
   across the four Mon-Thu prep practices = an **in-season week**; ÷ 4 = ~92 min = an **in-season
   day**. Same active-minute method (work ÷ intensity) as everything else. So the deck now reads
   "% of an in-season day / week," and the pitch is cleaner: *camp builds them up to and past what
   the season demands every single day, so September is nothing they haven't already done.*
   **Lead the room with the block-vs-in-season-week comparison.**
2. **Two structures, Coach's 3-4-5.** Coach wants the consecutive-day count itself to ramp toward a
   five-in-a-row finish. So we present both a **14-day (3/3/4/4)** and a **15-day (3/3/4/5)** install
   camp. Block length is Coach's accumulation dial; intensity is ours. They ramp the same direction.

## The two-decision frame

- **Decision 1 (Coach's call) — how does camp finish?** 14-day (3/3/4/4) or 15-day (3/3/4/5). The
  two structures are presented at **equal weight**; there is no recommended structure. The only
  difference at the finish: the 15-day's fifth peak-block day spends the **Aug 22 film day** — the
  taper (Aug 23-28 → Mock Aug 29) is **identical** either way, so freshness into Auburn is the same.
- **Decision 2 (your recommendation) — how hard is the ramp?** Conservative / Moderate / Aggressive.
  **Moderate is the recommendation.** Coach navigates 2 then 3, never 6 at once.

## The problem being fixed

The as-drafted page-1 plan was 4G/4Y/6R but **front-loaded** — Block 2 already ran two reds, so the
back of camp was no harder than the middle. That repeats Baylor's 2024/25 accumulated-fatigue
pattern. Every model below instead ramps **block average-day intensity** up to a single clean
Block-4 peak, then hands off to the taper.

## The rule Coach can hold in seven words

> **"We never stack two max days."** Every hard day earns a recovery before the next one.

An off/film day between two reds counts as that recovery (red → off → red is legal); only two
**practice** days both red is the violation. This rule is a hard filter on all six models.

## The NCAA acclimatization period — the front of camp is fixed by rule, not by us

Aug 5 is **practice day 1** (Baylor runs no pre-camp acclimatization), so the mandatory five-day
acclimatization period governs Days 1–5 of every model:

- **Days 1–2 (Aug 5–6):** helmets & spider pads only → can only be **GREEN**.
- **Days 3–5 (Aug 7, 9, 10):** shoulder pads ("shells") permitted, **no full pads** → never **RED**.
- **One required day off** inside the seven-day window (the Aug 8 film day, ≤2 hrs film/meetings).
- **Full pads and live contact only from Day 6 (Aug 11 / P6).** No more than two consecutive days
  of full contact thereafter (already covered by the no-stacked-red rule).

This is not a design lever — it is the law. **No model can be red before Aug 11**, so the easy-in
start and back-loaded peak are partly *mandated*, which is the strongest possible version of the
anti-front-loading argument. All six sequences are machine-checked against this gate by
`scripts/render_camp_models_v2.py` (`check_acclimatization`).

---

# Decision 1 — 14-day install (3/3/4/4)

### 14-day · Conservative  (5 green / 6 yellow / 3 red · 2 scrimmages)

| P | Date | Day | Color | Dress / Tempo | Active min | Per | % in-season day | Situational |
|---|------|-----|-------|---------------|-----------|-----|-----------------|-------------|
| **B1** | | | | **70% — ease in** | | | **102% avg-day / 76% in-season-wk** | |
| 1 | Aug 5 | Wed | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 2 | Aug 6 | Thu | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 3 | Aug 7 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Call It |
| **B2** | | | | **90% — build** | | | **112% avg-day / 84% in-season-wk** | |
| 4 | Aug 9 | Sun | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 3rd Down |
| 5 | Aug 10 | Mon | GREEN | HELMETS / TAG | 85 | 9 | 92% | 3rd Down |
| 6 | Aug 11 | Tue | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 4-Min / Call It |
| **B3** | | | | **105% — extend** | | | **120% avg-day / 119% in-season-wk** | |
| 7 | Aug 13 | Thu | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Red Zone / Low Red |
| 8 | Aug 14 | Fri | GREEN | HELMETS / TAG | 85 | 9 | 92% | Short Yardage / RZ Lockout |
| 9 | Aug 15 | Sat | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 2-Minute / Call It |
| 10 | Aug 16 | Sun | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #1 |
| **B4** | | | | **120% — PEAK** | | | **125% avg-day / 125% in-season-wk** | |
| 11 | Aug 18 | Tue | RED | FULL PADS / THUD | 132 | 13 | 143% | 4-Min / Call It |
| 12 | Aug 19 | Wed | GREEN | HELMETS / TAG | 85 | 9 | 92% | Goal Line |
| 13 | Aug 20 | Thu | YELLOW | SHELLS / THUD | 112 | 12 | 122% | RZ / 2-Min / Last 2 |
| 14 | Aug 21 | Fri | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #2 |

**Day sequence:** G G Y Y G Y Y G Y R R G Y R

### 14-day · Moderate  (4 green / 5 yellow / 5 red · 2 scrimmages) — RECOMMENDED FLAVOR

| P | Date | Day | Color | Dress / Tempo | Active min | Per | % in-season day | Situational |
|---|------|-----|-------|---------------|-----------|-----|-----------------|-------------|
| **B1** | | | | **70% — ease in** | | | **102% avg-day / 76% in-season-wk** | |
| 1 | Aug 5 | Wed | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 2 | Aug 6 | Thu | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 3 | Aug 7 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Call It |
| **B2** | | | | **90% — build** | | | **119% avg-day / 89% in-season-wk** | |
| 4 | Aug 9 | Sun | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 3rd Down |
| 5 | Aug 10 | Mon | GREEN | HELMETS / TAG | 85 | 9 | 92% | 3rd Down |
| 6 | Aug 11 | Tue | RED | FULL PADS / THUD | 132 | 13 | 143% | 4-Min / Call It |
| **B3** | | | | **105% — extend** | | | **125% avg-day / 125% in-season-wk** | |
| 7 | Aug 13 | Thu | RED | FULL PADS / THUD | 132 | 13 | 143% | Red Zone / Low Red |
| 8 | Aug 14 | Fri | GREEN | HELMETS / TAG | 85 | 9 | 92% | Short Yardage / RZ Lockout |
| 9 | Aug 15 | Sat | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 2-Minute / Call It |
| 10 | Aug 16 | Sun | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #1 |
| **B4** | | | | **120% — PEAK** | | | **133% avg-day / 132% in-season-wk** | |
| 11 | Aug 18 | Tue | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 4-Min / Call It |
| 12 | Aug 19 | Wed | RED | FULL PADS / THUD | 132 | 13 | 143% | Goal Line |
| 13 | Aug 20 | Thu | YELLOW | SHELLS / THUD | 112 | 12 | 122% | RZ / 2-Min / Last 2 |
| 14 | Aug 21 | Fri | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #2 |

**Day sequence:** G G Y Y G R R G Y R Y R Y R  ·  _first full pads Day 6 (Aug 11), NCAA-legal_

### 14-day · Aggressive  (2 green / 7 yellow / 5 red · 3 scrimmages)

| P | Date | Day | Color | Dress / Tempo | Active min | Per | % in-season day | Situational |
|---|------|-----|-------|---------------|-----------|-----|-----------------|-------------|
| **B1** | | | | **70% — ease in (NCAA acclimatization)** | | | **102% avg-day / 76% in-season-wk** | |
| 1 | Aug 5 | Wed | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 2 | Aug 6 | Thu | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 3 | Aug 7 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Call It |
| **B2** | | | | **90% — build** | | | **129% avg-day / 96% in-season-wk** | |
| 4 | Aug 9 | Sun | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 3rd Down |
| 5 | Aug 10 | Mon | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 3rd Down |
| 6 | Aug 11 | Tue | RED | FULL PADS / THUD | 132 | 13 | 143% | 4-Min / Call It |
| **B3** | | | | **105% — extend** | | | **133% avg-day / 132% in-season-wk** | |
| 7 | Aug 13 | Thu | RED | FULL PADS / LIVE | 132 | 14 | 143% | Red Zone / Low Red · MOCK SCRIMMAGE |
| 8 | Aug 14 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Short Yardage / RZ Lockout |
| 9 | Aug 15 | Sat | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 2-Minute / Call It |
| 10 | Aug 16 | Sun | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #1 |
| **B4** | | | | **120% — PEAK** | | | **133% avg-day / 132% in-season-wk** | |
| 11 | Aug 18 | Tue | RED | FULL PADS / THUD | 132 | 13 | 143% | 4-Min / Call It |
| 12 | Aug 19 | Wed | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Goal Line |
| 13 | Aug 20 | Thu | YELLOW | SHELLS / THUD | 112 | 12 | 122% | RZ / 2-Min / Last 2 |
| 14 | Aug 21 | Fri | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #2 |

**Day sequence:** G G Y Y Y R R Y Y R R Y Y R  ·  _full pads start Day 6 (Aug 11); 3 live days all ≥ Day 6_

> **Why 14-day Aggressive now opens 2G/7Y and peaks as a plateau:** the NCAA acclimatization window
> forbids any red before Aug 11, so its old early reds (Aug 7 full pads, Aug 10 live mock) were
> *illegal*, not just hot — the front is now a mandated easy-in (B1 = 102%). It still runs the
> hottest legal floor and a 3rd scrimmage, peaking as a high **plateau** (B2→B4 = 129→133→133%),
> not a single point. The 15-day's longer peak block lets it ramp cleanly to a true back-loaded peak.

---

# Decision 1 — 15-day install (3/3/4/5)

The fifth peak-block day (Aug 22) spends the trailing film day; **the taper is unchanged.** The
five-in-a-row finish carries embedded recovery inside it — never five straight hard days.

### 15-day · Conservative  (5 green / 7 yellow / 3 red · 2 scrimmages)

| P | Date | Day | Color | Dress / Tempo | Active min | Per | % in-season day | Situational |
|---|------|-----|-------|---------------|-----------|-----|-----------------|-------------|
| **B1** | | | | **70% — ease in** | | | **102% avg-day / 76% in-season-wk** | |
| 1 | Aug 5 | Wed | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 2 | Aug 6 | Thu | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 3 | Aug 7 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Call It |
| **B2** | | | | **90% — build** | | | **112% avg-day / 84% in-season-wk** | |
| 4 | Aug 9 | Sun | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 3rd Down |
| 5 | Aug 10 | Mon | GREEN | HELMETS / TAG | 85 | 9 | 92% | 3rd Down |
| 6 | Aug 11 | Tue | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 4-Min / Call It |
| **B3** | | | | **105% — extend** | | | **120% avg-day / 119% in-season-wk** | |
| 7 | Aug 13 | Thu | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Red Zone / Low Red |
| 8 | Aug 14 | Fri | GREEN | HELMETS / TAG | 85 | 9 | 92% | Short Yardage / RZ Lockout |
| 9 | Aug 15 | Sat | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 2-Minute / Call It |
| 10 | Aug 16 | Sun | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #1 |
| **B4** | | | | **120% — PEAK** | | | **125% avg-day / 155% in-season-wk** | |
| 11 | Aug 18 | Tue | RED | FULL PADS / THUD | 132 | 13 | 143% | 4-Min / Call It |
| 12 | Aug 19 | Wed | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Goal Line |
| 13 | Aug 20 | Thu | GREEN | HELMETS / TAG | 85 | 9 | 92% | RZ / 2-Min / Last 2 |
| 14 | Aug 21 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Situational / Last 2 |
| 15 | Aug 22 | Sat | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #2 |

**Day sequence:** G G Y Y G Y Y G Y R R Y G Y R

### 15-day · Moderate  (4 green / 5 yellow / 6 red · 2 scrimmages) — RECOMMENDED FLAVOR

| P | Date | Day | Color | Dress / Tempo | Active min | Per | % in-season day | Situational |
|---|------|-----|-------|---------------|-----------|-----|-----------------|-------------|
| **B1** | | | | **70% — ease in** | | | **102% avg-day / 76% in-season-wk** | |
| 1 | Aug 5 | Wed | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 2 | Aug 6 | Thu | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 3 | Aug 7 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Call It |
| **B2** | | | | **90% — build** | | | **119% avg-day / 89% in-season-wk** | |
| 4 | Aug 9 | Sun | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 3rd Down |
| 5 | Aug 10 | Mon | GREEN | HELMETS / TAG | 85 | 9 | 92% | 3rd Down |
| 6 | Aug 11 | Tue | RED | FULL PADS / THUD | 132 | 13 | 143% | 4-Min / Call It |
| **B3** | | | | **105% — extend** | | | **125% avg-day / 125% in-season-wk** | |
| 7 | Aug 13 | Thu | RED | FULL PADS / THUD | 132 | 13 | 143% | Red Zone / Low Red |
| 8 | Aug 14 | Fri | GREEN | HELMETS / TAG | 85 | 9 | 92% | Short Yardage / RZ Lockout |
| 9 | Aug 15 | Sat | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 2-Minute / Call It |
| 10 | Aug 16 | Sun | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #1 |
| **B4** | | | | **120% — PEAK** | | | **135% avg-day / 168% in-season-wk** | |
| 11 | Aug 18 | Tue | RED | FULL PADS / THUD | 132 | 13 | 143% | 4-Min / Call It |
| 12 | Aug 19 | Wed | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Goal Line |
| 13 | Aug 20 | Thu | RED | FULL PADS / THUD | 132 | 13 | 143% | RZ / 2-Min / Last 2 |
| 14 | Aug 21 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Situational / Last 2 |
| 15 | Aug 22 | Sat | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #2 |

**Day sequence:** G G Y Y G R R G Y R R Y R Y R  ·  _first full pads Day 6 (Aug 11), NCAA-legal_

### 15-day · Aggressive  (2 green / 7 yellow / 6 red · 3 scrimmages)

| P | Date | Day | Color | Dress / Tempo | Active min | Per | % in-season day | Situational |
|---|------|-----|-------|---------------|-----------|-----|-----------------|-------------|
| **B1** | | | | **70% — ease in (NCAA acclimatization)** | | | **102% avg-day / 76% in-season-wk** | |
| 1 | Aug 5 | Wed | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 2 | Aug 6 | Thu | GREEN | HELMETS / TAG | 85 | 9 | 92% | Mixed Downs |
| 3 | Aug 7 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Call It |
| **B2** | | | | **90% — build** | | | **129% avg-day / 96% in-season-wk** | |
| 4 | Aug 9 | Sun | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 3rd Down |
| 5 | Aug 10 | Mon | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 3rd Down |
| 6 | Aug 11 | Tue | RED | FULL PADS / THUD | 132 | 13 | 143% | 4-Min / Call It |
| **B3** | | | | **105% — extend** | | | **133% avg-day / 132% in-season-wk** | |
| 7 | Aug 13 | Thu | RED | FULL PADS / LIVE | 132 | 14 | 143% | Red Zone / Low Red · MOCK SCRIMMAGE |
| 8 | Aug 14 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Short Yardage / RZ Lockout |
| 9 | Aug 15 | Sat | YELLOW | SHELLS / THUD | 112 | 12 | 122% | 2-Minute / Call It |
| 10 | Aug 16 | Sun | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #1 |
| **B4** | | | | **120% — PEAK** | | | **135% avg-day / 168% in-season-wk** | |
| 11 | Aug 18 | Tue | RED | FULL PADS / THUD | 132 | 13 | 143% | 4-Min / Call It |
| 12 | Aug 19 | Wed | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Goal Line |
| 13 | Aug 20 | Thu | RED | FULL PADS / THUD | 132 | 13 | 143% | RZ / 2-Min / Last 2 |
| 14 | Aug 21 | Fri | YELLOW | SHELLS / THUD | 112 | 12 | 122% | Situational / Last 2 |
| 15 | Aug 22 | Sat | RED | FULL PADS / LIVE | 132 | 14 | 143% | SCRIMMAGE #2 |

**Day sequence:** G G Y Y Y R R Y Y R R Y R Y R  ·  _full pads start Day 6 (Aug 11); 3 live days all ≥ Day 6_

> **The 15-day earns Aggressive a clean back-loaded peak:** with the front rule-locked to an easy-in
> (B1 = 102%), the five-day final block absorbs the extra red into the finish (B4 = 135%, the single
> highest block), so even the hottest *legal* model still ramps to the back instead of spiking early.
> That is the structural argument for 15 days when the staff wants maximum stress.

---

## Side-by-side

| Structure | Model | G/Y/R | Scrim | Block avg-day ramp (% in-season day) | Character |
|---|---|---|---|---|---|
| 14-day | Conservative | 5/6/3 | 2 | 102 → 112 → 120 → **125** | Most recovery, a green after every red. Safest into Auburn. |
| 14-day | **Moderate** | 4/5/5 | 2 | 102 → 119 → 125 → **133** | Textbook polarized build. **The recommendation.** |
| 14-day | Aggressive | 2/7/5 | 3 | 102 → 129 → 133 → **133** | Hottest legal floor; front rule-locked to easy-in, peaks as a plateau (rule caps the 4-day peak). |
| 15-day | Conservative | 5/7/3 | 2 | 102 → 112 → 120 → **125** | Same recovery character, longer five-in-a-row finish via accumulation. |
| 15-day | **Moderate** | 4/5/6 | 2 | 102 → 119 → 125 → **135** | Polarized build with the highest clean single peak. |
| 15-day | Aggressive | 2/7/6 | 3 | 102 → 129 → 133 → **135** | Hottest legal build; front rule-locked to easy-in, long peak block ramps cleanly to the back. |

## After the install camp — identical for every model

**Mock week (Aug 23-28), run as an in-season game week** → **Mock Game Aug 29** (controlled contact,
not live) → game week (Aug 31-Sep 4) → **Game 1 vs Auburn, Sep 5**. Shown once because it does not
change: the install camp varies, the runway into Auburn does not. The mock week is drawn day-by-day
on the deck: Sun/Mon green → Tue red grind → Wed yellow → Thu walk-through → Fri fast Friday → Sat
mock; Tue-Sat mirrors Auburn week. It rehearses Week 1.

> **Mock-week refinement (2026-06-16, AJ):** the physical and volume stimuli split across the two
> work days. **Tue (red) = full pads, red zone / short yardage** on a condensed field (collision
> work, like the regular season); **Wed (yellow) = 3rd down** with tempo and vertical plays downfield
> for the volume stimulus (red zone there would cap reps). **Coming out** installs early (Mon).
> Counting back from the Sat mock (MD-0), the **Thu walk-through is MD-2** (Fri = MD-1).

> **Selected build (2026-06-15):** 14-day (3/3/4/4) · Moderate is the plan of record. The
> coach-facing artifact is the pruned **v3** deck (`2026-fall-camp-models-v3`); this v2 set is the
> decision record.

---

_Method: active minutes = avg_pl / pl_per_min after stretch (Catapult, GPS-realized). Day-type
targets GREEN 85 min/9 per · YELLOW 112/12 · RED 132/13-14, vs the ~92-min in-season day / 370-min
in-season week. Color is the internal layer; the coach-facing render drops the traffic-light coding.
All six sequences validated against the NCAA five-day acclimatization gate (helmets D1-2, no full
pads before D6/Aug 11), the no-back-to-back-red rule, and the single-Block-4-peak goal by
`scripts/render_camp_models_v2.py`._

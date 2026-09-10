# Metric Definitions — Retrospective Stress Accounting

Locked 2026-06-11 with Eric. This is the operational catalog behind the two-tier stress
model in `CONTEXT.md` and the SPC frame in `docs/adr/0001`. Every metric here carries a
plain-language justification (the explainability requirement): no black-box composites,
each is defensible to sports med and S&C.

Anchoring: all retrospective series are aligned on BOTH days-to-camp (camp P1) and
days-to-injury (2024-07-10 foot fracture, 2025-07-10 hip strain).

## Surfaces and units
- Weight room: `data/tezino_perch_sets.csv` (Perch set-level). `weight_lbs` is pounds
  (the `weight_unit` "KG" label is wrong, see DATA-INVENTORY section 5). One row per set.
- Field: `data/tezino_gps_sessions.csv` (Catapult, per session).
- Neuromuscular response: force plate CMJ + IMTP. Body weight: `data/tezino_bodyweight.csv`.
- Training day = distinct calendar `date` with >=1 set (Perch `session_id` is a
  per-exercise block, not a workout day, so never count session_id as "sessions").

## Tier 1 — Systemic load (soft eyes): "how much total work"
Computed over ALL loaded resistance sets (any set with `weight_lbs > 0`); Olympic lifts and
accessories included, jumps excluded (no external load).

- **Weekly tonnage (lb)** = sum(`weight_lbs` * `num_reps`) per ISO week (Mon-Sun).
  Justification: total mechanical work moved; the headline volume number coaches expect.
- **Weekly total reps** = sum(`num_reps`) over loaded sets per week.
  Justification: volume independent of load, catches high-rep accumulation.
- **Weekly reps >=80% 1RM** = sum(`num_reps`) over intensity-eligible sets with
  intensity >= 0.80 (see "Intensity" below). Justification: high-intensity neural/joint
  exposure; the part of volume that is heavy, not just long.
- **Training days / week** = distinct dates with a Perch session.
- Catapult tier-1 (field systemic): weekly total player load, total distance, session
  count (already in the GPS extract).

## Tier 2 — Foot-specific mechanical (hard eyes): "what loads the 5th metatarsal"
Principle: barbell movements that load the lower body compressively through a grounded
foot. All squat variants + all deadlift variants + loaded step-ups / split-squats.
Excludes the Olympic-lift family (clean/snatch/jerk/pull/push-press) and presses, which
are ballistic or upper-body, and unloaded jumps.

**Included (present in his data):** Back Squat, Front Squat, Hatfield Squat,
Hatfield Split Squat, Split Squat, Barbell Step Up, Trap Bar Deadlift, Sumo Deadlift.
**Included if they appear (catalog variants, future-proofed in code):** Box Squat,
Safety Bar Squat / Split Squat / Lunge Squat, Anderson / ISO / RLE / Lateral / Overhead /
Dynamic Squat, Deadlift, Snatch-Grip Deadlift, Romanian Deadlift, DB RDL, DB Step Up,
Reverse Lunge Squat.
**Considered and excluded (flip if sports med wants the catch counted):** Power Clean,
Hang Clean, Clean, Clean Pull, Hang Snatch, Split Jerk, Push Press (Olympic / ballistic,
counted in tier-1 only). Box Jump is tracked separately as a small plyometric/impact
signal (n=4, unloaded), not in tier-2 tonnage.

- **Weekly axial tonnage (lb)** = tonnage restricted to the included lifts.
  Justification: the heavy weight-bearing volume the foot absorbs in the weight room.
- **Weekly axial reps >=80% 1RM** = heavy axial exposure (intensity >= 0.80 within the set).
  Justification: the high-load compressive exposures, watched with hard eyes.
- Catapult tier-2 (field mechanical): acceleration count/density, high-speed-running
  distance, change-of-direction and impact counts. THRESHOLDS PENDING (accel band and HSR
  cut for a ~290 lb DL; squad defaults may be wrong). Not locked here.

## Intensity and the rolling 1RM (the >=80% definition)
The raw Perch `pct_1rm` field is sparse on the specialty squats (e.g. Sumo Deadlift 7/47
sets, Hatfield 11/47), so it cannot carry the >=80% metric on its own. Instead intensity is
computed against a rolling estimate of current 1RM:

- **Estimated set 1RM (e1RM)** = `weight_lbs` * (1 + `num_reps` / 30) (Epley), computed only
  for intensity-eligible strength lifts (squat family, deadlift family, bench/incline/
  close-grip/military press) at 1-10 reps where rep-max estimation is valid. Olympic lifts
  and jumps are not intensity-eligible (their "%1RM" is not meaningful from reps).
- **Rolling current 1RM** per lift, per date = the maximum e1RM over a trailing 84-day
  (12-week) window, carried forward from the last estimate when the window is empty. A
  rolling best, not a mean: it tracks his real current capacity and steps up as he gets
  stronger. Justification: 80% should mean 80% of what he can do *now*, not of a stale or
  averaged-down number.
- **Set intensity** = `weight_lbs` / rolling-current-1RM(lift, date).
- A genuine top single re-bases the rolling 1RM immediately (it enters the window as the
  new max).

## Ramp rates (SPC exposure variables, per ADR-0001)
Exposure metrics (tier-1 and tier-2 loads) are non-stationary by design across a summer
ramp, so they are charted as RATES, not raw values, in the SPC layer:
- week-over-week change, and
- current load vs the rolling 28-day average.
Raw weekly values are still shown in the retrospective panels for readability; the control
charts use the rates so the planned progression itself does not trip every limit.

## Response metrics (charted directly, drift is meaningful)
A stable process is expected, so these are plotted as raw values, not rates: CMJ mRSI, CMJ
asymmetry %, IMTP Peak Vertical Force / BM, body weight. Tier coloring (gold/purple/white)
retained on the CMJ panel.

## Pending (not blocking the retrospective build)
- Catapult tier-2 thresholds (accel band, HSR cut) for a ~290 lb DL.
- SPC baseline window choice (post-surgical spring vs first two weeks of June 2026).
- Surgery date + current clearance status (sports med).

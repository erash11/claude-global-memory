# Practice load and readiness response: design and feasibility

**Status:** design complete, simulation complete, **primary analysis blocked on data collection**
**Date:** 2026-07-21

## The question

Does the practice load applied between Monday and Thursday change an athlete's
neuromuscular readiness — and do athletes differ from each other in how they
respond?

The second half is the primary question. The pooled dose-response slope in the
current data is essentially zero (within-athlete r = -0.03), and that is
consistent with two opposite worlds: practice load moves nobody, or it moves
people in opposite directions and the average cancels. Those have very
different operational meanings.

## Why this design and not the obvious one

The original question was whether practice *composition* predicts Saturday
performance. Five findings in the data killed that framing, in order:

1. **The in-season week does not vary.** Position-group weekly player load has
   CV 0.06–0.10. Player load is the heaviest on P1 in 54 of 57 weeks; contacts
   peak on P2 in 50 of 57. Days from last practice to game is 2 in all 58
   weeks. There is no composition contrast to exploit in-season.
2. **Volume and contact are the same variable.** r(week total player load, week
   total contacts) = 0.948. They cannot both enter a model.
3. **The bye week is not rest.** A 14-day gap contains 7–8 practices against a
   normal week's 4. Extra recovery and extra volume move in opposite
   directions, so a null there is uninterpretable. The naive within-athlete
   bye effect on game max velocity was +0.015 m/s (0.013 SD) — nothing.
4. **Game max velocity is a poor readiness measure.** Within-athlete SD is
   15% of the mean, most of it opportunity rather than physiology. GPS game
   `total_duration_s` is session length (median 180 min), not snaps, so the
   GPS data contains no playing-time measure at all.
5. **A normal practice week produces no measurable fatigue.** Mean Monday →
   Thursday change is within ±1.7% on every CMJ metric, with 44–57% of athletes
   declining — a coin flip.

Finding 5 is what moved heterogeneity from a secondary question to the primary
one. A null mean with a non-trivial spread is the signature of a design that
should be asking about variance, not location.

## Design

| Element | Choice |
|---|---|
| Unit | Athlete-week, in-season (Aug–Dec) |
| Exposure | P1–P3 total player load, between the Monday and Thursday tests |
| Exposure scaling | Within-athlete centred, in within-athlete SD units |
| Exposure decomposition | Position-group-week leave-one-out mean (exogenous) + individual deviation (absorbs selection) |
| Outcome | % change in Peak Power / BM, Monday → Thursday |
| Population | Football athletes name-matched between VALD and Catapult (153 of 179 GPS athletes match, 85%) |
| Window | 2023–2025 |
| Primary estimand | tau, the SD of true dose-response slopes across athletes |
| Inference | Parametric bootstrap null (see below) |

### Why Peak Power / BM

Chosen on measured responsiveness, not convention. Monday → Thursday change
across 687 paired athlete-weeks:

| Metric | Mean % change | SD of change |
|---|---|---|
| P2 Concentric Impulse | +1.67 | 8.96 |
| **Peak Power / BM** | **+0.90** | **5.28** |
| Jump Height (Imp-Mom) | +0.52 | 7.56 |
| RSI-modified | +0.51 | 12.18 |
| Concentric Impulse | +0.06 | 3.82 |

**RSI-modified is the field's default readiness metric and is the second
noisiest thing available here.** Peak Power / BM has near-best responsiveness
and second-lowest noise.

## The simulation result

Run `python -m src.research.simulate_power --sensitivity`.

### The analytic test is invalid at this sample size

Cochran's Q referenced against chi-square rejects **90.7%** of the time when
there is no heterogeneity at all. Per-athlete slope standard errors are
estimated from as few as 1 residual degree of freedom, which breaks the
chi-square approximation. The null Q 95th percentile is **1052** by simulation
against **82.6** by chi-square — a factor of 12.7.

On the real data the chi-square test reports p = 0.047, I² = 24%. **That is a
false positive.** The bootstrap-calibrated p-value is **0.936**.

This is the single most important reason to simulate before analysing. The
invalid version of this test would have produced a publishable-looking result
that was pure artefact.

### The design is underpowered as it stands

With the bootstrap-calibrated test (false-positive rate 0.048, correct):

| True tau (% per SD of load) | Power |
|---|---|
| 0.00 | 0.048 |
| 1.00 | 0.048 |
| 2.00 | 0.071 |
| 3.00 | 0.114 |

Power never exceeds 11% at any plausible effect size. Observed slope SD is
3.22 against a mean slope SE of 2.73 — nearly all apparent between-athlete
spread is estimation noise.

### What would fix it

| Weeks/athlete | Residual SD | Power at tau = 1.5 |
|---|---|---|
| **8.1 (current)** | 4.67 | **0.042** |
| 8.1 | 2.33 | 0.204 |
| **16.2** | 4.67 | **0.978** |
| 24.2 | 4.67 | 1.000 |

Halving outcome noise is not enough. Doubling paired weeks per athlete is
decisive.

## The blocker, and it is cheap to remove

Pairing completeness, not roster size or seasons:

| | Athlete-weeks |
|---|---|
| Thursday only | 2,375 |
| Monday only | 314 |
| **Paired** | **687 (20.3%)** |

Athletes appear in a median of 14 distinct in-season weeks, but only 8 paired
ones. **If every Thursday test had a Monday partner, the mean would be 19.0
paired weeks per athlete** — comfortably past the 16 the simulation says is
sufficient.

### Recommendation

Add a Monday CMJ to the existing Thursday routine for the in-season window.
No new athletes, seasons, or equipment. That single operational change takes
this analysis from power 0.04 to roughly 0.98, and it is the only thing
standing between the current data and a well-powered answer.

Until then the primary analysis should not be run — it cannot distinguish
signal from noise, and the invalid analytic test will manufacture a result if
anyone tries.

## Known data constraints

- `total_distance_m` is corrupt: r(player load, distance) = 0.27 overall and
  0.16 within-athlete, where clean football GPS runs 0.8–0.9. Use player load;
  do not use distance or any ratio built on it.
- `impacts_high` is identically zero for 2020–2023; it exists only from 2024.
- `total_high_ima` and `explosive_efforts` are duplicates — never model both.
- Contact counts drift by season (21.3 / 21.3 / 25.7 / 17.2 / 15.4 for
  2021–25). Season fixed effects are mandatory; raw cross-season comparison is
  unsafe.
- 2020 is unusable for contact: 76–81% of values are exact zeros.
- `raw_tests.athlete_name` is blank on 65% of rows; the joinable universe is
  the 236 named athletes in `classified_athletes`.
- Practice scripts are digitized for only 4 in-season weeks (2025 Auburn,
  Arizona State, Oklahoma State, Cincinnati) plus Fall Camp 2025 and spring.

## Where the remaining upside is

Fall camp is the only part of the calendar with large exposure variation —
15–18 practices per block and genuine week-to-week differences, against the
in-season CV of 0.06–0.10. If the goal is to find whether training dose moves
readiness at all, camp is where the contrast lives. That is the natural next
design and it does not depend on the Monday-testing fix.

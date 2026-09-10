# Time-to-unavailability analysis: feasibility scoping

**Status:** feasible — this is the recommended next research question
**Date:** 2026-07-21
**Origin:** Cam Josse's Sport Science Symposium talk (2026-05-30), player-availability
survival curves; scoped after six practice-load designs failed on absent exposure variation.

## Why this question and not the practice-load one

A parallel effort tried six ways to detect a practice-load effect on readiness
and failed every time, for one reason: **Baylor's practice operation has
engineered out the variation that observational research requires.** In-season
position-group weekly load has CV 0.06–0.10; camp is now equally standardized
(2025 CV 0.10); volume and contact are collinear at r = 0.948.

This question survives that problem because its exposure contrast is
**between-athlete cumulative** rather than week-to-week, and between-athlete
variance is where the load variation actually lives (67% of total load
variance, vs 33% within-athlete).

It is also the question Josse posed and answered descriptively — comparing
availability curves for athletes who stayed within load thresholds against
those who spiked. That comparison is between "bodies that tolerated hard
training" and "bodies that didn't," which is selection, not effect. The
version below is the identified form of the same question.

## Data verification

All figures verified directly against the files, 2026-07-21.

### Events

The three injury exports in `data/raw/` are **non-overlapping sequential
windows, not duplicates** — pairwise key overlap is exactly 0:

| Export | Window | Rows |
|---|---|---|
| `e433b3` | 2022-09-01 → 2022-12-22 | 112 |
| `306ff9` | 2023-01-01 → 2023-11-30 | 199 |
| `3ad17d` | 2024-01-01 → 2026-04-23 | 327 |
| **Combined** | **2022-09 → 2026-04** | **638** |

- **272 events** with `Caused Unavailability` = True, across **209 athletes**
- Per Aug-start season, remarkably stable: 63 / 73 / 65 / 71
- Recurrent flag is nearly unused (7 of 638)

### Censoring

Well behaved and does not force any exotic treatment.

- 583 of 638 resolved (**91.4%**); 55 right-censored
- Among unavailability events: 237 resolved, **35 censored (12.9%)**
- Duration median 23 days (IQR 12–53, max 784); among unavailability events
  median 28 (IQR 14–81). Heavy right skew.
- `Duration` is exactly `Issue Resolved Date − Issue Date` — a derived
  calendar field, not an independent clinical measure. Do not treat it as one.

### Athlete linkage — the strongest result

**100% match, 638 of 638 rows.** The injury `Athlete` field is "First Last"
with no commas; normalized against `athletes.csv` it resolves completely. One
name collides with a duplicate athlete ID and must be resolved manually — DOB
is present in both files, so it is resolvable.

This is unusual and worth appreciating: identity resolution is where these
projects normally die.

### Risk set

Constructible. Football is squad 94; filtering gives **170,006 participation
rows** across 2,997 sessions.

Critically, **non-participation is affirmatively recorded rather than being an
absence**: `ParticipationLevel` = Full 159,558 / **No Participation 8,167** /
Modified 2,264 / Partial-DNF-Injury 17. That distinction is what makes a
proper risk set possible at all.

## The three real problems

**1. Concussion is a different data-generating process and will dominate.**
Head is **84 of 272** unavailability events — 31% — and 84 of 95 head issues
cause unavailability, a near-100% time-loss rate driven by protocol rather
than tissue. Knee, by contrast, is 44 of 106.

Pooling protocol-mandated absence with soft-tissue injury in one hazard model
answers neither question. **Stratify or exclude.** Event counts by scope:

| Scope | Events |
|---|---|
| All unavailability | 272 |
| Excluding head | 188 |
| **Lower-limb only** (knee, ankle, thigh, foot, lower leg, groin/hip) | **120** |

**2. The athlete-week grid is ~58% dense.** For 2024, 4,866 of 8,313 possible
athlete-weeks are present. Athletes vanish from the file for stretches, and
the data does not tell you whether a missing week means "off roster" (not at
risk, left-truncated) or "at risk but unlogged." **That assumption is yours to
make and must be stated explicitly**, with a sensitivity analysis under both
readings.

**3. Non-participation has no reason and no key back to the injury record.**
`ParticipationLevelReason` is 100% null across all 170,006 football rows, and
`RelatedExternalIssueId` / `RelatedExternalIssueType` are entirely empty.
Attribution of a non-participation row to a specific injury has to be done by
athlete + date proximity, which is a heuristic, not a join.

Game participations are better — `No Participation - Medical` (511) is
distinguished from `No Participation - Other` (1,551) — but that split exists
only on the game side.

## Covariate budget

At 10 events per variable:

| Window | Events | Max covariates |
|---|---|---|
| All four seasons | 272 | 27 |
| Excluding head | 188 | 18 |
| **Lower-limb only** | **120** | **12** |
| Single season | ~65 | 6 |

**Realistically 12–18.** Enough for a genuine multivariable model; not enough
for a wide feature set. `Pathology` (222 distinct) and `ICD` (118) must be
collapsed to coarse groups or dropped.

## Proposed design

**Discrete-time hazard model on athlete-weeks**, not a Cox model.

Rationale: the exposure is naturally weekly, the risk-set grid is irregular
and incomplete, and time-varying load enters a discrete-time logistic model
without the machinery Cox requires for it. It is also far easier to explain to
a coaching staff, which matters more here than it usually does.

| Element | Choice |
|---|---|
| Unit | Athlete-week at risk |
| Outcome | First lower-limb unavailability event in that week (120 events) |
| Primary exposure | Rolling cumulative training load, between-athlete contrast |
| Covariates | Position group, prior-injury indicator, cumulative weeks exposed, game minutes, season |
| Time | Weeks since season start (captures the seasonal hazard shape Josse showed) |
| Censoring | Right-censor at season end or last logged week |
| Sensitivity | Both readings of missing athlete-weeks; head-included vs excluded |

## What must not be claimed

Load is not randomly assigned. An athlete who accumulates more training load
is an athlete who was healthy enough to accumulate it — the same selection
that undercuts the descriptive version of this analysis. A well-specified
model with prior-injury history and cumulative exposure narrows that gap; it
does not close it.

The honest framing is **"which athletes are at elevated hazard, and when"** —
a stratification and timing question — rather than "how much load causes
injury." The first is useful and defensible. The second is not available from
these data.

## Dead ends, stated plainly so nobody re-checks them

- **`Weather Condition`: 8 of 638 rows (1.3%).** Effectively does not exist.
- **`Surface Quality`: 2 rows.** Does not exist.
- `Surface Type`: 33% filled — back-fillable from `training_sessions.csv` /
  `games.csv` via the session join, but not usable as-is.
- `Games Played` / `Game Minutes Played` are 100% populated but are
  **season-cumulative athlete attributes, not per-event values**. They are an
  exposure covariate, not an outcome.

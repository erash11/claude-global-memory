# Phase 2 design — EPA for the Baylor play-call study

**Date:** 2026-09-09
**Branch:** `phase2-epa`
**Depends on:** Phase 1 (`outputs/joined_plays_enriched.parquet`, 1,935 chart plays)
**Status:** approved in chat, not yet implemented

---

## 1. Purpose

Phase 1 measured play-call outcomes with **success rate**, a binary yardstick.
It found Baylor's early-down running success fell from 61.7% (2024) to 42.7%
(2025). Success rate cannot say how *much* value each call created, only
whether it cleared a bar.

Phase 2 adds **EPA** — expected points added — as a second, continuous
outcome. The study then has two independent lenses on the same plays. The
report's central Phase 2 question is:

> Does EPA agree that 2025 early-down running collapsed, or does it disagree?

Agreement strengthens the Phase 1 finding. Disagreement is itself the finding,
and the report must say so rather than pick the flattering lens.

---

## 2. Where EPA comes from, and why

### 2.1 PFF does not have EPA

Every one of PFF's seven premium play feeds was inspected on 2026-09-09:
`team_play`, `quarterback_charting`, `rushing`, `passing`, `pressure`,
`pass_rush`, `pass_protection`. **None carries EPA, expected points, PPA, WPA,
or any win-probability field.** PFF's play-level value columns are *grades*
(`off_grade`, `run_grade`, `passer_grade`, `coverage_grade`), which are a
different construct: a 0–100 charting judgement of execution, not a change in
scoring expectation.

This is a settled fact, recorded here so nobody re-derives it. If a future PFF
premium category adds EPA, it would be ingested by `PFF_Data_Project`, not
here — see §6.

### 2.2 CFBD PPA is EPA, and it is already on disk

Source: `~/DEV/CFB_Analytics_Lab/data/raw/plays/season=YYYY/*.parquet`,
column `ppa`. Seasons 2019–2025 are present. No API call is required for
Phase 2.

**PPA is CFBD's name for EPA.** This was challenged during design and verified
two independent ways rather than taken on trust.

**Documentary evidence.** CFBD's own glossary defines PPA as its EPA measure.
The underlying model is a multinomial next-score model — the same family as
nflfastR's EPA and Bill Connelly's college work. It predicts which team scores
next in the current half and by what means (seven classes), signs each outcome
from the offence's point of view, and takes expected points as the
probability-weighted sum. EPA is the change in that quantity across a play.

- https://collegefootballdata.com/Glossary
- https://cfbfastr.sportsdataverse.org/articles/college-football-expected-points-model-fundamentals-part-i.html

**Empirical evidence.** Measured over 208,393 FBS scrimmage plays, 2024:

| Check | Result | Consistent with EPA? |
|---|---|---|
| Range | −11.93 to +7.37 | yes |
| Mean | +0.16 | yes |
| Passing TD | +3.26 | yes |
| Rushing TD | +2.54 | yes |
| Rush | +0.04 | yes |
| Sack | −1.26 | yes |
| Interception | −2.09 | yes |
| Fumble lost | −2.24 | yes |

**The decisive test — drive reconciliation.** If PPA is a genuine change in
expected points, then summing it across a drive must approximate
*points scored minus expected points at the drive's start*. For 2024 drives
starting between the offence's own 15 and 40:

| Drive outcome | Observed sum of PPA | EPA theory predicts | n |
|---|---|---|---|
| Touchdown | +5.09 | ≈ +5.5 | 6,545 |
| Field goal | +2.00 | ≈ +1.6 to +2.0 | 2,007 |
| Punt | −0.80 | ≈ −1.4 | 10,273 |

It reconciles. The residual gaps are explained by penalty and special-teams
plays, which carry a null `ppa` and therefore contribute no value to the sum
while still moving the ball. A yards-based proxy or an arbitrary index would
not reconcile to points at all.

**Conclusion:** CFBD `ppa` is a legitimate expected-points-added model. Using
it does not violate the Phase 1 prohibition on shipping a yards-based proxy
labelled EPA. That prohibition stands and its test is *strengthened*, not
removed — see §7.3.

### 2.3 Naming rule

The metric is written **"EPA (CFBD PPA)"** on first use in any report,
artifact or table caption, and **`epa`** in code and column names.

Never write bare "EPA" in prose without the source qualifier. CFBD's model is
calibrated differently from ESPN's, PFF's, or SumerSports'. The same play will
carry different EPA in each. A reader comparing this report against a public
EPA leaderboard must know why the numbers differ.

---

## 3. Repository boundary

Phase 1 established that `PFF_Data_Project` owns all PFF ingest and this repo
opens `pff.db` read-only. Phase 2 adds a second boundary of exactly the same
shape.

**`CFB_Analytics_Lab` owns all CFBD ingest.** This repo:

- reads `~/DEV/CFB_Analytics_Lab/data/raw/plays/**.parquet` **read-only**;
- **never** calls the CFBD API;
- **never** reads, prints, copies or commits `CFB_Analytics_Lab/.env`;
- holds no CFBD credential of any kind.

If a season or week is missing, it is pulled **in `CFB_Analytics_Lab`** using
that repo's `pull.py`, which enforces the free-tier budget guard (1,000 calls
per month, hard reset on the 1st) and writes the durable call ledger. Budget
at design time: 932 calls remaining, resets 2026-10-01.

A loader in this repo that finds a required parquet file absent must **raise
with the exact `CFB_Analytics_Lab` command to run**, never attempt a fetch.

---

## 4. The join

### 4.1 What is being joined

| Side | Grain | Rows |
|---|---|---|
| Left | Phase 1 joined chart+PFF play | 1,935 (948 in 2024, 987 in 2025) |
| Right | CFBD Baylor offensive play | 2,343 (1,828 with non-null `ppa`) |

### 4.2 Game key

Opponent, not week order.

A measured trap: CFBD labels Baylor's 2024 bowl against LSU as
`seasonType='postseason', week=1`. Sorting CFBD games by `week` alone places
LSU **second** in 2024, while the chart's `game_code` order places it
**thirteenth and last**. A positional map would silently misjoin the entire
2024 season. Ordering is not a safe key.

The map is therefore an **explicit lookup** from the chart/PFF four-character
opponent code to the CFBD team name, held in `src/playcalls/cfbd.py` as
`OPPONENT_TO_CFBD`:

```
2024: TXTA→Tarleton State, UTUN→Utah, COAF→Air Force, COUN→Colorado,
      UTBY→BYU, IAST→Iowa State, TXTC→Texas Tech, OKST→Oklahoma State,
      TXCU→TCU, WVUN→West Virginia, TXHO→Houston, KSUN→Kansas, LAST→LSU
2025: ALAU→Auburn, TXMU→SMU, ALSM→Samford, AZST→Arizona State,
      OKST→Oklahoma State, KSST→Kansas State, TXCU→TCU, OHCI→Cincinnati,
      FLCE→UCF, UTUN→Utah, AZUN→Arizona, TXHO→Houston
```

Measured properties that make this safe, both asserted by tests:

- Every chart opponent code maps. No unmapped codes exist in either season.
- No opponent appears twice within a season, so `(season, opponent)` resolves
  to exactly one CFBD `gameId`. A future rematch (conference championship
  against a division opponent) would break this; the test must fail loudly
  rather than pick the first, and the resolver then needs a week tiebreak.

`map_cfbd_games(season)` returns `{game_code: gameId}` and **raises** if any
chart game resolves to zero or more than one CFBD game.

### 4.3 Season filter is mandatory

Trap #5 from Phase 1 applies unchanged. Baylor plays Auburn in both 2025 and
2026. Every CFBD read is filtered on `season` **before** any opponent match.
Never glob across season directories.

### 4.4 Play key — sequence alignment, not independent lookup

The naive approach — match each chart play independently on
`(quarter, down, distance, yards_to_goal)`, break ties by nearest clock — was
measured on all 1,935 rows:

| Outcome | Rows | Share |
|---|---|---|
| Exactly one CFBD candidate | 1,644 | 85.0% |
| More than one candidate | 220 | 11.4% |
| No candidate | 71 | 3.7% |
| **Matched after nearest-clock tiebreak** | 1,864 | **96.3%** |
| **Matched with a non-null `ppa`** | 1,767 | **91.3%** |

Clock gap on matched rows: median 6s, p95 58s, **max 900s**. A 900-second gap
is a full quarter — that is a wrong match that the naive method accepted. The
clock disagrees between sources by design: PFF charts the snap, ESPN's
play-by-play stamps the play differently. Clock is a **tiebreaker within
tolerance, never a key**.

91.3% is below the gate in §5. The response is a better matcher, **not a
looser gate**.

**The matcher.** Within one game, both sources list the same plays in the same
order. That ordering is information the naive method throws away. Phase 2
matches by **monotone sequence alignment**:

1. Restrict both sides to one `gameId` at a time.
2. Order the chart side by `play_no`, the CFBD side by
   `(driveNumber, playNumber)`.
3. Score each candidate pair on agreement across
   `(quarter, down, distance, yards_to_goal)`, plus `gain` vs `yardsGained`
   as a corroborating signal, plus a clock-proximity term.
4. Choose the alignment that maximises total score **subject to monotonicity**:
   if chart play *i* matches CFBD play *p*, then chart play *i+1* may only
   match a CFBD play after *p*. Plays cannot cross.
5. Reject any pair whose clock gap exceeds **120 seconds**, whatever its score.
   This kills the 900-second class of error. **The tolerance does not apply in
   overtime.** College overtime has no game clock, so CFBD stamps `0:00` while
   the chart records a running value; applying the tolerance there rejected all
   15 charted overtime rows.

> **Implementation note.** This was first built as a greedy forward cursor,
> reusing the idiom `join.py` already used against PFF, on the reasoning that a
> cursor that never goes back gives monotonicity for free. It does — but greedy
> also starves later rows to perfect earlier ones. With charted gains of 4 and 4
> against CFBD gains of 3 and 4 the first row takes the perfect match and the
> second finds nothing, yielding one pair where two exist; the same flaw let a
> charted penalty skip CFBD's `Penalty` row for the replay behind it. The
> shipped `epa.align_game` is the dynamic program this section actually
> specifies: it maximises the number of pairs first and only then prefers better
> gain and clock agreement. Replacing greedy with it lifted attached plays from
> 1,722 to 1,736 and 2024's join quality from 94.9% to 95.4%.

Unmatched plays on both sides are kept and written out, never dropped
silently.

### 4.5 Chart clock parsing

28 of 1,935 chart rows have a `game_clock` that does not parse as `MM:SS`.
The parser returns null for these rather than guessing, and a null clock means
the clock term contributes nothing to the alignment score — those rows are
matched on state and sequence alone. Tests cover `'15:00'`, `'0:04'`, an
empty string and a malformed value.

### 4.6 Field position

`join.yards_to_goal` already exists from Phase 1 and is reused unchanged. It
must keep handling all three cases and its existing tests stay: team code
equals the offence (`'TXBA 37'` → 63), team code is the opponent
(`'ALAU 37'` → 37), and a bare midfield `'50'` with no code → 50.

### 4.7 Rows excluded before joining

- PFF rows where `offense != 'TXBA'` (Phase 1 trap #2).
- PFF rows flagged `no_play`.
- Special-teams plays, via the existing `join.is_special_teams`.

---

## 5. Gate 3

Phase 1 refuses to build tables on unvalidated data. Phase 2 adds a third gate
of the same shape, evaluated in `run.py` and recorded in `GATES_PASSED.json`.

**Gate 3 — EPA join quality.** At least **95%** of the charting plays CFBD
*can* score must be attached to one, computed **per season and overall**. All
three must clear the bar.

> **Amended after implementation.** This gate originally read "95% of joined
> chart scrimmage plays must be aligned to a CFBD play carrying a non-null
> `ppa`" — that is, absolute coverage. Building it showed the threshold was
> unreachable, and not because of the join: only **1,796 of the 1,935** charting
> rows have any same-state CFBD play carrying a PPA. The other 139 are plays a
> penalty wiped, which CFBD records with no PPA, plus games where its
> play-by-play is incomplete — against SMU the chart holds 30 fourth-quarter and
> overtime plays and CFBD holds 11 in any form. Absolute coverage is therefore
> capped at **92.8%** however good the matcher is.
>
> Gating the absolute figure would bake the source's data shape into our
> constant, and a season with more penalties would pass a gate it should fail.
> The user was given the choice and chose to gate the join. So the denominator
> became `epa.reachable_count` — a pure existence check on (down, distance,
> yards-to-goal) against rows carrying a PPA, which ignores order, clock and
> period and so owes nothing to `align_game`'s own logic. It is a loose upper
> bound, since a same-state row elsewhere in the game counts, which makes the
> resulting figure a floor rather than a best case.
>
> **Measured:** 1,736 attached of 1,796 reachable — 95.4% (2024), 97.9% (2025),
> **96.7% overall**. Absolute coverage is 89.7% and is reported beside it, never
> in place of it.
>
> Two things the first version got wrong and this one asserts. Only the total
> was checked, which hid a failing 2024 at 94.9% inside a passing 95.9%. And a
> NaN passed, because `nan < gate` is False — a season with nothing reachable
> read as success.
>
> **Invariant.** `attached <= reachable` must hold. The two are computed
> differently on purpose — `align_game` tolerates a null state field while
> `reachable_count` uses a strict tuple a null can never match — so a charting
> row with a null down could be attached without being reachable and the ratio
> would overstate the join. Measured on this data there are no null downs and
> the invariant holds exactly, but it holds by luck of the input, so `run.py`
> raises rather than assuming it.

- Naive-method baseline, measured 2026-09-09: **91.3%** absolute.
- Sequence alignment is expected to close the gap. If it does not, the
  correct response is to **investigate the shortfall and report the true
  figure**, not to lower the threshold. Lowering a gate to make it pass is
  the failure mode this project exists to avoid.
- On failure `run.py` exits 1, `build_tables.py` refuses to run, and no
  report is produced.

**Diagnostics written on every run, pass or fail:**

| File | Contents |
|---|---|
| `outputs/epa_unmatched.csv` | Chart plays with no CFBD match, with the reason |
| `outputs/epa_match_quality.csv` | Per-game match count, coverage, clock-gap median and max |

The 2025 side of the naive probe was six times worse than 2024 (61 unmatched
vs 10). That asymmetry must be explained, not averaged away, because 2025 is
the season carrying the finding.

---

## 6. Score state — a Phase 1 "impossible" item now possible

Phase 1 recorded that neither source carries a running in-game score, so
leading/trailing/garbage-time splits did not exist and quarter was used as a
weak proxy.

CFBD carries `offenseScore` and `defenseScore` on every play. Phase 2 attaches
both, plus a derived `score_margin = offenseScore - defenseScore` from
Baylor's perspective, and a `score_state` bucket:

| Bucket | Rule |
|---|---|
| `trailing_big` | margin ≤ −17 |
| `trailing` | −16 to −9 |
| `one_score` | −8 to +8 |
| `leading` | +9 to +16 |
| `leading_big` | margin ≥ +17 |

**Garbage-time rule.** Decided, not asked, per the conventional line:

- 2nd half, `abs(margin) > 28` → garbage time
- 4th quarter, `abs(margin) > 24` → garbage time

Garbage-time plays are **flagged, not deleted**. Every EPA table is produced
both with and without them, and the report states which it is quoting. A
finding that only survives one treatment is not a finding.

---

## 7. Outputs

### 7.1 Modules

New files only. Phase 1's modules are not restructured.

| File | Responsibility |
|---|---|
| `src/playcalls/cfbd.py` | Read the CFBD parquet read-only; `OPPONENT_TO_CFBD`; `map_cfbd_games`; raise-with-instructions on a missing file |
| `src/playcalls/epa.py` | Sequence alignment, clock parsing/tolerance, score-state derivation, coverage statistics for Gate 3 |

`analysis.py` gains EPA aggregation helpers alongside the existing rate
helpers. `build_tables.py`, `report.py` and `run.py` gain Phase 2 sections.
Nothing existing is rewritten.

### 7.2 Tables

Written under `outputs/tables/`, added to the existing 45:

1. EPA per play by season
2. EPA per play by season × run/pass
3. EPA per play by down
4. EPA per play by down–distance bucket
5. **Early-down run EPA by season** — the direct Phase 1 comparison
6. EPA per play by field zone
7. EPA per play by score state
8. EPA per play by score state, garbage time excluded
9. EPA per play by pressure (dropbacks only — Phase 1 trap #3)
10. EPA per play by personnel grouping
11. EPA per play by run concept
12. **Success rate vs EPA agreement** — for every cut in the Phase 1 report,
    the success-rate delta beside the EPA delta, with the sign of each
13. EPA distribution summary: mean, median, stdev, p10, p90, share of plays
    with EPA > 0

Every table reports **n** alongside every rate. A cut whose 2025 cell has
fewer than 30 plays is marked low-n in the report.

### 7.3 The prohibition test, flipped

Phase 1 shipped a test asserting the report contains no EPA, because no EPA
existed and a yards-based proxy must never be labelled EPA.

That test is **replaced, not deleted**, by a stricter pair:

- `test_epa_is_present_and_sourced` — the report contains EPA, and every
  first mention is qualified "EPA (CFBD PPA)".
- `test_no_yards_proxy_labelled_epa` — the `epa` column is sourced only from
  CFBD `ppa`. It asserts the loader reads `ppa` and that no code path
  computes an `epa` value from `yards`, `gain`, or `yardsGained`.

The original intent — never dress a yards proxy as EPA — is preserved and
made harder to violate.

### 7.4 Report

`outputs/REPORT.md` and `outputs/report.html` gain a Phase 2 section. It must
answer, explicitly:

1. Does EPA agree with the success-rate finding on early-down running?
2. Where do the two lenses disagree, and what does that mean?
3. What does score state show that quarter could not?
4. What is the EPA coverage, and which plays are missing?

The Phase 1 conclusion — that the cause of the decline is not decidable from
this data — is re-examined against EPA and score state, and restated or
revised on the evidence.

**Every headline figure is computed from a table.** No number is typed into
prose. The three Phase 1 regression tests that enforce this are extended to
cover the Phase 2 figures.

---

## 8. Testing

Mirrors the Phase 1 structure: `tests/test_cfbd.py`, `tests/test_epa.py`,
plus additions to `test_analysis.py` and `test_report.py`.

Behaviour that must be covered:

- Opponent map: every chart code resolves; an unknown code raises; a season
  with a repeated opponent raises rather than silently picking one.
- Season isolation: a 2026 Auburn play can never join a 2025 chart row.
- Clock parsing: `'15:00'`, `'0:04'`, `''`, `'abc'`.
- Clock tolerance: a candidate 900s away is rejected even when it is the only
  candidate and its state matches perfectly.
- Monotonicity: an alignment that crosses two plays is rejected.
- `yards_to_goal`: own-half, opponent-half, bare `'50'`.
- Score state: each of the five buckets at its boundary values.
- Garbage time: at, just inside and just outside each threshold.
- Gate 3: passes above 95%, exits 1 below, and writes its diagnostics either
  way.
- The two prohibition tests in §7.3.

---

## 9. Explicitly out of scope

Carried forward from Phase 1 and still not done after Phase 2:

- **Opponent adjustment.** No strength-of-schedule correction. Baylor's 2024
  and 2025 schedules are not equivalent, and EPA is not opponent-adjusted.
  The report must say this plainly, because it is the strongest alternative
  explanation for the decline that this study cannot rule out.
- **Baylor player attribution.** The chart carries no Baylor player ids beyond
  a QB jersey number.
- **A bespoke expected-points model.** CFBD's is used as published. Fitting
  our own on the 2019–2025 corpus is possible but adds a large modelling
  surface for no gain over an already-validated model.
- **Alignment analysis.** That is Phase 4, running in a parallel worktree
  against success rate, and it will pick up EPA once this branch merges.
- **2026 weekly ingest.** That is Phase 3, held at the user's direction
  pending a 2026 play-call chart export.

---

## 10. Risks

| Risk | Handling |
|---|---|
| Gate 3 misses 95% even with alignment | Investigate and report the true figure. Never lower the gate. The unmatched file exists for exactly this. |
| 2025 matches worse than 2024 | Already observed in the probe. Must be explained per game before the finding is trusted, since 2025 carries the result. |
| Alignment accepts a plausible wrong match | Clock tolerance, monotonicity, and `gain` vs `yardsGained` corroboration. Match quality written per game for inspection. |
| CFBD parquet is stale or a week is missing | Loader raises with the exact `CFB_Analytics_Lab` pull command. Never fetches. |
| EPA and success rate disagree | That is a result, not a problem. The report presents both and does not choose the flattering one. |
| A future rematch breaks the opponent map | Test asserts one game per `(season, opponent)` and fails loudly. |

---

## 11. Decisions recorded

1. EPA comes from CFBD `ppa`. Verified as a real expected-points model by
   documentation and by drive reconciliation. No bespoke model is fitted.
2. The metric is always written "EPA (CFBD PPA)" on first use.
3. `CFB_Analytics_Lab` owns CFBD ingest. This repo reads parquet read-only and
   never calls the API.
4. Games are mapped by an explicit opponent lookup, never by week ordering.
5. Plays are matched by monotone sequence alignment within a game, with a
   120-second clock tolerance. Clock is a tiebreaker, never a key.
6. Gate 3 is 95% EPA coverage. A miss triggers investigation, not a lower bar.
7. Garbage time is flagged, not deleted. Every EPA table is produced both ways.
8. Phase 1's no-EPA test is replaced by a stricter pair, not removed.

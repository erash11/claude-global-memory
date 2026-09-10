# Phase 5 design — opponent adjustment

**Written:** 2026-09-10
**Status:** design, approved by default under a stated assumption (see §0)
**Branch:** `worktree-phase5-opponent-adjustment`

---

## 0. Why this phase, and under what assumption

Phase 3 (weekly 2026 ingest) is the sequenced next phase, and it is blocked on
three pieces of data that do not exist yet and that this repo cannot create —
verified on 2026-09-10, not taken from the handoff:

| Blocker | Verified state | Owner |
|---|---|---|
| `2026_All_Games.csv` | absent; repo root holds 2021–2025 | the user's PFF export |
| 2026 CFBD parquet | absent; `CFB_Analytics_Lab` holds `season=2019`…`season=2025` | `CFB_Analytics_Lab` |
| 2026 in `pff.db` | absent; DuckDB `games` table holds seasons 2023, 2024, 2025 only | `PFF_Data_Project` |

The `week1_auburn/` directory exists at
`~/DEV/Football/PFF_Data_Project/data/week1_auburn/` as loose JSON and scratch
scripts. It was never ingested. (Note: `PHASE3-READINESS.md` writes this path as
`PFF_Data_Project/...`; the repo actually lives under `~/DEV/Football/`. The code
in `src/playcalls/pff.py` has the correct absolute path.)

So Phase 3 cannot start. This phase instead closes the largest open analytical
hole in the project, which the Phase 2/4 handoff names explicitly:

> Cause is still not decidable from this data. **Opponent adjustment is absent
> and remains the strongest alternative explanation.**

**Stated assumption.** The user said "proceed with the next phase" while away.
Phase 3 being blocked, this phase was selected without an explicit approval of
*this* topic. If the intent was to wait for the 2026 export, this branch is
discardable and nothing on `main` changes.

---

## 1. The question

Baylor's offence declined from 2024 to 2025 on every cut, and Phase 4 showed the
decline is not explained by *alignment* — Baylor lined up the same, defences
lined up the same, the same concepts produced less.

The remaining structural explanation is **schedule**: 2025 defences may simply
have been better. This phase answers two questions in order.

1. **Descriptive (can refute the explanation in one row).** Were Baylor's 2025
   opponents better defensively than its 2024 opponents? Measured as what each
   opponent's defence allowed to *everyone else*.
2. **Adjusted.** With each opponent's defensive quality subtracted, does the
   2024 → 2025 decline survive, and by how much?

Question 1 comes first and is reported first. If 2025 defences were not
materially stingier, opponent adjustment is refuted as the explanation and the
adjusted numbers are confirmation, not discovery.

---

## 2. Method

### 2.1 The adjustment

A **game-level opponent-adjusted differential**, play-weighted to the season.

For each Baylor game `g` in season `S` against opponent `O`:

```
baylor_g   = Baylor's value per play in game g
baseline_g = what O's defence allowed per play, in O's OTHER games that season
adj_g      = baylor_g - baseline_g
```

Season adjusted value = the play-weighted mean of `adj_g` over Baylor's games.

Equivalently and more simply, computed as pooled sums rather than a mean of
means, so a 90-play game is not weighted equal to a 60-play game:

```
adjusted = (Σ_g baylor_epa_total_g / Σ_g baylor_epa_plays_g)
         - (Σ_g baseline_epa_per_play_g × baylor_epa_plays_g / Σ_g baylor_epa_plays_g)
```

The second term is the **schedule strength** figure that answers question 1 on
its own: the mean EPA (CFBD PPA) that Baylor's schedule allowed to other teams,
weighted by how many plays Baylor ran against each.

**Rejected alternative: ridge / SRS-style iterative adjustment.** It is more
correct in principle — it adjusts each opponent's baseline for *its* schedule,
recursively — but it is opaque, it cannot be checked by hand, and it would put a
regression between the data and a coaching-staff conclusion. The differential is
the standard transparent form and every input is inspectable. If the differential
and the descriptive row disagree, that disagreement is itself reportable.

### 2.2 The baseline excludes Baylor

`baseline_g` is computed over `defense == O AND offense != 'Baylor'`.

Without this the adjustment is circular: Baylor's own bad day against an opponent
makes that opponent look better, which then partly excuses Baylor's bad day. The
exclusion is by offense name, not by game, so a hypothetical second Baylor-vs-O
meeting in the same season is also excluded.

### 2.3 FCS opponents are flagged and excluded from the headline

Baylor played exactly one FCS opponent in each season:

| Season | Opponent | Conference | Non-Baylor plays available |
|---|---|---|---|
| 2024 | Tarleton State (`TXTA`) | UAC | 1,110 (882 with PPA) |
| 2025 | Samford (`ALSM`) | Southern | 936 (704 with PPA) |

Their baselines exist and are large, but they are measured **against FCS
offences**. Subtracting "what Samford allowed to Southern Conference offences"
from what Baylor did to Samford credits Baylor for a level-of-competition gap,
not for execution.

**Decision:** the headline adjusted number excludes FCS opponents. The FCS game
is reported separately with its raw numbers and an explicit note. Because it is
one game per season, the exclusion is symmetric and costs little. Every table
carries an `fcs_excluded` flag in provenance and prints the game count both ways.

### 2.3b Baselines are restricted to FBS offences

An earlier assumption — that the parquet holds only FBS games, so an FBS
opponent's baseline is automatically FBS-on-FBS — is **wrong**. The 2025 season
file carries 311 distinct defences across 40 conferences, including Big Sky,
SWAC, MVFC, Southern, and several Division II leagues. Tarleton State's baseline
draws on 13 distinct offences, all FCS.

So every FBS opponent's baseline currently includes its own body-bag game against
an FCS opponent, which flatters the baseline and therefore *understates* Baylor's
adjusted value. The effect is small — roughly one game in twelve — but it is
systematic and it is free to remove.

**Decision:** baselines filter `offenseConference` to FBS. One module-level
constant does two jobs: it filters baseline offences, and it decides `is_fcs`
for §2.3.

```python
FBS_CONFERENCES = frozenset({
    "ACC", "American Athletic", "Big 12", "Big Ten", "Conference USA",
    "FBS Independents", "Mid-American", "Mountain West", "Pac-12",
    "SEC", "Sun Belt",
})
```

The strings were read from the data, not assumed — CFBD writes
`"American Athletic"`, not `"AAC"`, and `"Mid-American"`, not `"MAC"`. A test
asserts that every Baylor opponent's conference in every run season resolves to a
known value, so a conference realignment or a CFBD rename **raises by name**
rather than silently reclassifying a team as FCS and dropping its game.

### 2.4 Garbage time and non-plays

Applied identically on both sides of the subtraction, reusing existing code:

- `epa.is_non_play` filters Timeout, Kickoff, End Period and the rest. A
  `Timeout` row carries the state of the play behind it and `yardsGained=0`;
  leaving it in inflates any denominator it touches.
- `Penalty` rows stay in the pool, matching this repo's existing rule. CFBD
  assigns PPA to almost none of them (51 of 15,079 in 2025), so they land in
  `plays` and not in `epa_plays`, which is exactly what those two columns exist
  to show.
- `cfbd._attach_pre_snap_score` gives every opponent row its pre-snap score, and
  `epa.is_garbage_time` flags it. **Flagged, not deleted** — every table is also
  written as `*_clean.csv` with garbage-time plays excluded, matching the Phase 2
  convention.

The pre-snap-score derivation is the same function Phase 2 uses, so the
post-play-score trap and the clamped-ordering fix both carry over — but **only
after the function is fixed**, which is the next section.

### 2.4b `_attach_pre_snap_score` must group by (game, offence), not by game

**This is a real defect in existing code, exposed by this phase rather than
introduced by it.** `cfbd._attach_pre_snap_score` does:

```python
grouped = ordered.groupby("gameId", sort=False)
shifted = grouped[column].shift(1).fillna(0)
```

That is correct **only** because `load_baylor_plays` filters `offense = 'Baylor'`
in SQL before calling it. Within any one game, every surviving row shares one
offence, so "the previous row's `offenseScore`" is genuinely Baylor's own
previous score.

`load_season_plays` does not filter to one offence. In an all-teams frame the
offence alternates within a game, so the previous row's `offenseScore` belongs to
**the other team**, and the `clip(upper=...)` clamp is then applied across two
different perspectives. Every garbage-time flag computed that way would be wrong,
and nothing would raise.

**Fix:** group by `["gameId", "offense"]`. For a Baylor-only frame this produces
**identical groups** to `groupby("gameId")`, because `offense` is constant within
each game — so the Phase 2 outputs are unchanged by construction, and a test
asserts that byte-for-byte rather than assuming it. For an all-teams frame it is
the correct grouping.

Two tests: one on a hand-built two-possession fixture where the answer is known
by hand, and one asserting Baylor's 2024 and 2025 pre-snap columns are unchanged
from the values on `main`.

**Belt and braces:** `defence_baseline` filters to `defense == O` before any
score work, so within a game there is one offence regardless. The grouping fix is
still made, because relying on every future caller to filter first is the same
class of silent trap this repo keeps finding.

#### Amendment, 2026-09-10 — the grouping fix above is wrong; here is what shipped

**`groupby(["gameId", "offense"])` does not work, and the failing test written
for it proved so on the first run.** It gives each team its own series inside a
game, so every team's first possession starts at 0-0. A team taking over after
the opponent has already scored then reads its opponent at zero. The two-
possession fixture expects Beta's first snap to read `pre_defense_score` 7,
and the regroup returns 0.

**What was built instead: the score is carried per TEAM through the possession
change.** Each row's two scores are re-expressed against a fixed pair of slots
ordered by team name — stable within a game, because every row of a game names
the same two teams — then shifted within the game, then mapped back to the
row's own perspective. The clamp to the post-play score is unchanged.

For a single-offence frame the slot assignment is constant within each game, so
this reduces exactly to the previous shift. Verified rather than assumed:
Baylor's 2024 and 2025 pre-snap columns hash identically before and after
(`e16145b9…` and `6f765606…`).

**A second correction, from the adversarial review.** CFBD reuses
`driveNumber` and `playNumber` in overtime — 54 duplicate
`(gameId, driveNumber, playNumber)` keys in 2025, and game `401761632`
interleaves period 3 with period 5. Sorting on the bare key lands an overtime
row in front of a third-quarter one, which then inherits a 0-0 pre-play score.
`period` is now part of the sort key, ahead of drive and play number.

### 2.5 Run and pass are classified from CFBD on BOTH sides

This is the subtlest decision in the phase.

Baylor's `run_pass` comes from the chart (`aapff_RUNPASS`), which records the
**play call**. CFBD's `playType` records the **result**. They disagree on real
plays:

| Chart | CFBD | n (EPA-bearing) | What it is |
|---|---|---|---|
| `P` | `Rush` | 46 | scrambles — called pass, ran |
| `R` | `Pass Reception` | 3 | run-pass options that threw |
| `P` | `Sack` | 36 | called pass, sacked (agrees in spirit) |
| `X` | `Rush` | 5 | kneels |

There is no chart for the opponent's other games. Their run/pass can only come
from CFBD. So a Baylor "pass" rate built from the chart would include 46
scrambles that the opponent baseline's "pass" rate structurally excludes, and the
subtraction would silently compare two different things.

**Decision:** for every opponent-adjusted run/pass cut, **both sides are
classified from CFBD `playType`**. The chart-based rate is printed beside it so
the shift is visible, and the disagreement count is reported. The unadjusted
chart-based tables in `REPORT.md` are unchanged; this rule is scoped to Phase 5's
tables.

The mapping is an explicit dictionary, `CFBD_PLAY_TYPE_TO_RUN_PASS`:

- **run** — `Rush`, `Rushing Touchdown`
- **pass** — `Pass Reception`, `Pass Incompletion`, `Sack`, `Passing Touchdown`,
  `Pass Completion`, `Pass Interception Return`, `Interception`,
  `Interception Return Touchdown`
- **unknown** — everything else, including `Fumble Recovery (Own)`,
  `Fumble Recovery (Opponent)`, `Fumble`, `Safety` and `Penalty`. The underlying
  play may have been either and CFBD does not say.

Unknown rows are excluded from run/pass cuts on both sides and **the excluded
share is printed**. A test asserts the mapping covers at least 98% of EPA-bearing
plays, and a second asserts an unmapped play type resolves to `unknown` rather
than defaulting to run or pass.

### 2.6 Success rate is re-derived on both sides

CFBD has no `Efficiency` column, and no other team is hand-charted. An adjusted
success rate therefore cannot use Baylor's charted flag on one side and a derived
flag on the other.

**Decision:** for Phase 5's success-rate tables, success is derived from
`down`, `distance` and gain on both sides, by the standard convention:

| Down | Success |
|---|---|
| 1st | gain ≥ 50% of distance |
| 2nd | gain ≥ 70% of distance |
| 3rd, 4th | gain ≥ 100% of distance |

`CLAUDE.md` already requires that if success is re-derived, it is reconciled
against `Efficiency` and the disagreement rate reported. Phase 5 does exactly
that: one reconciliation table over Baylor's 2024–2025 charted plays, giving the
agreement rate and a breakdown of where the two disagree. That table is a
deliverable in its own right — it tells the staff how much its hand-charted
efficiency flag differs from the industry convention.

**Which fields, on Baylor's side.** The joined table carries two gains: the
chart's `gain` (from `pff_GAINLOSS`) and CFBD's `cfbd_yards_gained`. Choosing
silently would repeat the scramble trap in a new place.

- **Adjusted tables** use CFBD's `down`, `distance` and `cfbd_yards_gained` on
  both sides. That is the only way the subtraction compares like with like, and
  it follows the same rule as §2.5.
- **The reconciliation table** uses the chart's `down`, `distance` and `gain`
  against the chart's `Efficiency`, because its whole purpose is to ask whether
  Baylor's hand-charted flag agrees with the convention **on Baylor's own
  charted fields**. Mixing CFBD gains into that comparison would blend two
  questions and answer neither.

Both choices are asserted by tests, and the gain-source disagreement (chart gain
vs CFBD gain on matched plays) is published as its own provenance figure.

**The denominator.** §2.4 keeps `Penalty` rows in the play pool, and a CFBD
penalty row carries a down, a distance and a `yardsGained` — so a naive derived
flag would score every penalty as a *failure* and quietly depress both sides.

**Decision:** derived success is defined over **run/pass-classified plays only**,
on both sides. `Penalty` already maps to `unknown` in §2.5, so it falls out
without a second rule. On Baylor's side the chart's `run_pass` values `X` and
`PEN` are dropped for the same reason. "Overall" for a success-rate table
therefore means run plus pass, and that is stated in the table itself rather than
left for a reader to assume.

**The weighting.** §2.1's formula weights by `epa_plays`, which is right for EPA
and wrong for success. The success analogue weights by **graded plays** — the
count that survives the exclusions above — because a play with no EPA can still
be graded and a play with EPA can still be ungraded. Every success table prints
`plays`, `graded` and `epa_plays` as three separate columns so the two
denominators are never confused for each other.

Down 5 rows (11 in 2025, 2 in 2024) and rows with a null down are excluded from
derived success on both sides and counted in provenance.

### 2.7 Cuts

Four, matching the four headline rows of the existing report, each with a
like-for-like baseline computed over the same cut of the opponent's other games:

1. **Overall** — every scrimmage play.
2. **Run** — CFBD-classified run.
3. **Pass** — CFBD-classified pass.
4. **Early-down run** — CFBD-classified run on down 1 or 2. This is where Phase 4
   found the −18.0 efficacy gap, so it is the cut that matters most.

`MIN_SAMPLE = 15` applies to `epa_plays`, per the existing rule. Every opponent
baseline sits between 600 and 931 EPA-bearing plays overall, so no opponent is
suppressed at the overall cut; thinner cuts are checked per group and suppressed
rather than printed.

### 2.8 Every table shows the three steps, never just the last one

Excluding the FCS game (§2.3) changes Baylor's **raw** number too. So Phase 5's
raw figure will not equal `REPORT.md`'s headline 57.4% / +0.230, and a reader
setting the two documents side by side would reasonably conclude one of them is
wrong.

**Decision:** every adjusted table prints three columns in this order.

| Column | Meaning |
|---|---|
| `raw_all_games` | Baylor's value over every game — matches `REPORT.md` |
| `raw_fbs_only` | Baylor's value with the FCS game removed |
| `adjusted` | `raw_fbs_only` minus the schedule baseline |

The step from column 1 to column 2 is the schedule-composition effect; the step
from 2 to 3 is the opponent-quality effect. Printing only the last one hides
which of the two moved the number. A test asserts all three columns are present
and that `raw_all_games` for the overall cut reconciles to the value in
`REPORT.md` within rounding.

---

## 3. Module and interfaces

One new module, `src/playcalls/opponent.py`, plus one new builder. Nothing
existing changes behaviour.

```
load_season_plays(season, root=CFBD_PLAYS_ROOT) -> DataFrame
    Every play in one CFBD season, all teams. Same column set and same
    _attach_pre_snap_score treatment as cfbd.load_baylor_plays, but not
    filtered to one offence. ~277k rows (2024), ~293k (2025).
    Raises the same "pull it in CFB_Analytics_Lab" error when a season is absent.

classify_run_pass(play_type) -> "run" | "pass" | "unknown"
    The explicit mapping of §2.5.

derive_success(down, distance, gain) -> bool | None
    The 50/70/100 convention of §2.6. None when down is null or not in 1-4.

is_fbs(conference) -> bool
    Membership in FBS_CONFERENCES (§2.3b). Raises on a conference string that
    is neither a known FBS nor a known FCS/lower value, so a CFBD rename or a
    realignment fails by name instead of silently demoting a team.

defence_baseline(season_plays, opponent_cfbd_name, cut) -> dict
    What one opponent's defence allowed to non-Baylor FBS offences, on one cut.
    Filters defense == O first, so the frame has one offence per game before
    any score work (§2.4b). Returns plays, graded, epa_plays, epa_per_play,
    derived_success_rate, and the garbage-time-excluded versions of each.

schedule_strength(joined, season_plays, season) -> DataFrame
    One row per Baylor game: opponent, is_fcs, Baylor's plays, and the
    opponent's baseline on every cut. This is the descriptive answer to
    question 1 and the input to the adjustment.

adjusted_table(joined, season_plays_by_season, cut) -> DataFrame
    One row per season: raw value, schedule baseline, adjusted value, plays,
    epa_plays, games, games_excluded_fcs.

reconcile_success(joined) -> DataFrame
    Charted Efficiency vs derived success on Baylor's plays. Agreement rate
    and the disagreement breakdown of §2.6.
```

A new root script `build_opponent_tables.py` writes the CSVs, and
`build_opponent_report.py` writes `outputs/OPPONENT.md`. Both follow the shape of
the existing `build_alignment_tables.py` / `build_alignment_report.py` pair and
read the season list from `seasons.resolve_seasons`, never a hardcoded tuple.

### Outputs

```
outputs/tables/opponent_schedule_strength_{season}.csv
outputs/tables/opponent_baseline_by_cut.csv
outputs/tables/opponent_adjusted_{cut}.csv          (+ _clean.csv)
outputs/tables/opponent_success_reconciliation.csv
outputs/tables/opponent_runpass_classification_audit.csv
outputs/OPPONENT.md
outputs/opponent_provenance.json
```

---

## 4. What could make this wrong, and the guard for each

| Risk | Guard |
|---|---|
| Baylor left in its own opponent's baseline (circular) | Filter is `offense != 'Baylor'`; a test asserts zero Baylor rows in every baseline |
| FCS baseline treated as FBS-comparable | `is_fcs` flag from `defenseConference`; headline excludes; test asserts one FCS game per season is excluded |
| Chart-vs-CFBD run/pass mismatch | Both sides from CFBD; test asserts the mapping is total and that `unknown` is the default |
| A new CFBD play type silently counted as a run | `classify_run_pass` returns `unknown` for anything unmapped; test asserts it |
| Post-play score used for garbage time | Reuse `cfbd._attach_pre_snap_score`; test asserts pre-snap columns present before flagging |
| Opponent mapped by week order (bowl trap) | Map by `cfbd.OPPONENT_TO_CFBD`, which raises by name on an unmapped code |
| Thin cut printed as a finding | `MIN_SAMPLE` on `epa_plays`; every table prints `plays` and `epa_plays` separately |
| "EPA" written bare in `OPPONENT.md` | The existing test does **not** cover it — `test_report.py:138` calls `render_report()` directly, so it guards `REPORT.md`'s renderer only. Phase 5 adds the equivalent test against `render_opponent_report()` |
| Pre-snap score wrong on an all-teams frame | §2.4b: group by `(gameId, offense)`; test asserts Baylor's existing output is unchanged |
| FCS body-bag games flattering every FBS baseline | §2.3b: baselines filter `offenseConference` to `FBS_CONFERENCES`; unknown conference raises by name |
| Penalty rows scored as derived failures | §2.6: derived success is defined over run/pass-classified plays only, both sides |
| Chart gain vs CFBD gain chosen silently | §2.6: adjusted tables use CFBD fields, reconciliation uses chart fields; both asserted |
| Phase 5's raw number read as contradicting `REPORT.md` | §2.8: three columns — `raw_all_games`, `raw_fbs_only`, `adjusted` |
| Derived success quietly replacing charted success | Scoped to Phase 5 tables only; reconciliation table published with the disagreement rate |

**All 13 opponent codes in 2024 and all 12 in 2025 are already present in
`OPPONENT_TO_CFBD`** — verified against `outputs/joined_plays_enriched.parquet`.
No map change is needed for this phase.

---

## 5. Testing

Test-driven, in `tests/test_opponent.py`:

- `classify_run_pass` — every known type, an unmapped type, `None`, coverage ≥98%
- `derive_success` — the three thresholds at their boundaries, down 5, null down
- `reconcile_success` — agreement rate is computed over graded plays only,
  `X` and blank `Efficiency` excluded from the denominator; uses chart fields
- `defence_baseline` — excludes Baylor; excludes FCS offences; excludes
  non-plays; keeps penalties out of derived success; `epa_plays` ≤ `plays`
- `is_fbs` — every Baylor opponent's conference resolves; an unknown string
  raises by name
- FCS handling — the headline excludes exactly one game per season
- Adjustment arithmetic — on a hand-built fixture where the answer is known,
  including that EPA weights by `epa_plays` and success weights by `graded`
- `_attach_pre_snap_score` — a two-possession all-teams fixture computed by
  hand, plus Baylor's 2024/2025 pre-snap columns unchanged from `main`
- `render_opponent_report` — "EPA (CFBD PPA)" appears before any bare "EPA",
  the gap `test_report.py` leaves open
- Three-column presentation — `raw_all_games`, `raw_fbs_only`, `adjusted` all
  present; `raw_all_games` reconciles to `REPORT.md` within rounding
- Integration — the four cuts run on real data and produce finite numbers with
  `epa_plays` above `MIN_SAMPLE`

---

## 6. Also delivered: the Phase 3 design question

`PHASE3-READINESS.md` leaves one question deliberately open: does a mid-season
2026 belong in the same tables as two complete seasons?

**Decided here rather than left open:** yes, same pipeline and same tables, with
two requirements.

1. Every cross-season row gains a `games` column, so a six-game rate is never
   printed beside a thirteen-game rate without the reader seeing why.
2. An in-progress season is labelled by its extent everywhere it appears —
   "2026 (through week N)", never a bare "2026".

A full rebuild, not an append. The whole pipeline runs in under a minute, so
there is no performance argument for the more fragile option. This is recorded in
`PHASE3-READINESS.md` as decided.

---

## 7. Out of scope

- Ingesting 2026 into `pff.db`, or pulling 2026 CFBD plays. Different repos,
  different owners, and an API budget that lives elsewhere.
- Fixing `project-triage`'s full render. Different repo, offered and not accepted.
- Opponent adjustment for the alignment tables. The mix/efficacy decomposition
  would need a per-opponent baseline for every alignment group, and most groups
  would fall under `MIN_SAMPLE`. If the four cuts here show something, that is the
  time to argue for it.
- Any adjustment for 2021–2023. Those exports carry no outcome columns at all.

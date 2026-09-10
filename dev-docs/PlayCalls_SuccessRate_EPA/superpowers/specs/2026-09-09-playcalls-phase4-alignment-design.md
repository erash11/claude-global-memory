# Phase 4 — Alignment and Formation vs Play-Call Outcome — Design

**Date:** 2026-09-09
**Branch:** `phase4-alignment`
**Status:** design approved by decision-record (no human gate available; see §0)
**Builds on:** `2026-09-09-playcalls-success-rate-epa-design.md` (Phase 1) and
`outputs/REPORT.md`.

---

## 0. On approval gates

The brainstorming skill requires a human to approve the design before
implementation. No human is available in this session. Every point where approval
would have been sought is instead written here as a **Decision** with its evidence
and its reasoning, and implementation continues. Decisions are numbered `D1`…`D14`
so a reviewer can accept or reject them individually. Assumptions that are *not*
backed by evidence in this repository are marked **ASSUMPTION** in bold.

---

## 1. The question

Phase 1 established, for Baylor offence 2024 → 2025 (same coordinator, same starting
quarterback):

| Cut | 2024 | 2025 |
|---|---|---|
| All plays, success rate | 57.4% | 49.5% |
| Explosive rate | 14.8% | 7.4% |
| Early-down run success | 61.7% | 42.7% |
| Unpressured dropback success | 59.9% | 53.8% |

Phase 1 stopped there and said the cause was not decidable from its data.

Phase 4 asks one question with two competing answers:

- **Mix shift** — Baylor lined up in worse-performing looks more often in 2025, or
  defences lined up against them differently, and the aggregate fell because the
  *weights* changed.
- **Efficacy drop** — the same look running the same concept simply produced less,
  and the aggregate fell because the *rates* changed.

These are separable arithmetically. §6 does it.

**Phase 4 is not asked to explain *why* efficacy fell.** If the answer is "the mix
barely moved and the same looks got worse", that is the finding, and it is reported
as such rather than dressed up.

---

## 2. Scope

**In scope.** Pre-snap alignment and formation, offence and defence, 2024 and 2025
only, success rate as the outcome, explosive rate as a secondary outcome.

**Out of scope.** 2021–2023 (no outcome columns at all — CLAUDE.md, and Phase 1 §2).
EPA (Phase 2 owns it; §7 explains how it drops in). Player-level attribution.
Opponent-strength adjustment. Anything requiring film.

---

## 3. Open data question resolved: what `offense_package` means

The task required this be resolved empirically and not guessed.

### 3.1 The documentation does not answer it

`PFF_Data_Project/docs/swagger/premium-feeds.yaml` declares `offense_package` and
`defense_package` as bare `type: string` with no description
(lines 1942 and 1946). `PFF_API_Reference_2026-09-06.md` and `pff_api_notes.md`
mention `off_package` / `def_package` only in a field list. **No data dictionary for
this field exists in that repository.** It had to be derived.

### 3.2 Evidence

Across all 4,517 `team_play` rows in `pff.db` (every team, not just Baylor), parsing
`offense_package` as four hyphen-separated integers:

| Slot | Range observed | Rows non-zero (of 3,755 parseable) |
|---|---|---|
| 1 | 0–5 | 3,735 |
| 2 | 0–1 | 60 |
| 3 | 0–2 | 3,703 |
| 4 | 0–4 | 3,461 |

The four numbers sum to **5** on 3,628 of 3,755 rows.

On the 1,907 Baylor plays that join to the Phase 1 table, `offense_players` contains
exactly **11 jersey numbers on every single row**, and the slot sum is 5 on 1,906 of
them. Eleven players minus five offensive linemen minus one quarterback leaves five
skill players. The vector counts those five.

Cross-tabulating against the chart's `Personnel` column (standard RB-TE notation)
gives an unambiguous mapping:

| `offense_package` | Dominant chart `Personnel` | n | Reading |
|---|---|---|---|
| `3-0-1-1` | `11` | 1,743 / 1,749 | 3 WR, 1 RB, 1 TE |
| `2-0-1-2` | `12` family | 106 / 110 | 2 WR, 1 RB, 2 TE |
| `4-0-1-0` | `10` | 30 / 30 | 4 WR, 1 RB, 0 TE |
| `1-0-1-3` | `13` | 7 / 7 | 1 WR, 1 RB, 3 TE |

**Decision D1 — the slot order is `WR - FB - RB - TE`, counting the five non-OL,
non-QB players on the field.**

Slots 1, 3 and 4 are proven: `13` personnel puts its 3 in slot 4, which rules out
slot 2 being the tight-end slot; `10` personnel puts 4 in slot 1 and 0 in slot 4,
fixing WR and TE; the remaining 1 is the back, in slot 3.

Slot 2 is **inferred**, not proven. It never exceeds 1 and is non-zero on 60 of
3,755 league-wide rows, which is the signature of a fullback / H-back. **ASSUMPTION:
slot 2 = FB.** It is immaterial to this analysis: it is non-zero on **1 of 2,311**
Baylor snaps.

### 3.3 The suffixes

Values carry trailing annotations. Every `(*)`-suffixed value sums to **less than 5**,
and the deficit equals the number of asterisks:

| Value | Slot sum | Suffix | Sum + implied |
|---|---|---|---|
| `2-1-1-0 (*)` | 4 | one `*` | 5 |
| `1-1-1-0 (**)` | 3 | two `*` | 5 |
| `2-0-1-1 (+Q)` | 4 | `+Q` | 5 |
| `X-X-X-X` | — | — | unidentified play |

**Decision D2 — `(*)` means that many players PFF could not assign a position;
`(+Q)` means a second quarterback occupied one of the five skill slots; `X-X-X-X`
means the personnel was not identified.** These are stripped before parsing and the
row is recorded as `personnel_pff = "OTHER"` rather than being silently coerced.

### 3.4 Consequence for the analysis

**Decision D3 — the chart's `Personnel` column is the primary personnel field;
`offense_package` is a cross-check, not a grouping dimension.**

Reasoning: chart `Personnel` is **100% filled in both seasons**; `offense_package` is
99.4% / 97.8% and is missing precisely on the plays that failed the join. The chart is
also the source Baylor staff read. The two agree on ~98.7% of joined plays.

The residue is interesting but is **not a finding**: `4-0-0-1` (n=4) and `3-0-0-2`
(n=4) are zero-RB packages that the chart calls `11`. The likely reading is that PFF
counts by *where the player aligned* and the chart counts by *who was on the field* —
a back split wide becomes a receiver to PFF. n < 10; recorded, not claimed.

Evidence is emitted as `outputs/tables/alignment_offense_package_crosswalk.csv` so the
claim above is reproducible rather than asserted.

---

## 4. Second open data question resolved: `mofo_coverage_played_shown`

This field is the only defensive-look field with near-complete fill in **both**
seasons and on **both runs and passes**. That makes it load-bearing, so its two
characters had to be resolved before use.

Values are two characters from `{O, C}` — middle-of-field Open / Closed. Fill is
97.9% (2024) and 96.9% (2025); on runs specifically it is 99.8% / 97.1%, so unlike
PFF `coverage_type` it is **not** dropbacks-only (CLAUDE.md trap 3 does not bite here).

### 4.1 Evidence

Baylor's own 2024 `Cover Family` column is 90.1% filled on all plays. Mapping it to
middle-of-field state by convention (`0`, `1`, `3` → closed; `2`, `4`, `6` → open) and
cross-tabulating each character against it, over the 826 plays where both exist:

| Character | Agreement with charted coverage family |
|---|---|
| First (`c1`) | 554 / 826 = **67.1%** |
| Second (`c2`) | 758 / 826 = **91.8%** |

**ASSUMPTION: Baylor's coaches chart the coverage that was played, not the one
shown.** This is the hinge of the whole reading. If they charted the pre-snap shell
instead, the same 91.8% agreement would mean character 2 is the *shown* look and the
field's own word order was right after all. The assumption is well founded — the
`Cover Family` values `0`/`1`/`2`/`3`/`4`/`6` are post-snap coverage families, which
is what a coach grades a play against — but it is an assumption, not a measurement,
and it is marked as one here and in the report.

Taking it, the second character is the played coverage and the first is the pre-snap
shown look.

A second, independent line of evidence agrees: `OC` (first char open, second closed)
occurs 419 times across both seasons and `CO` only 156. Defences showing two-high and
rotating down to a closed middle is roughly three times as common as the reverse,
which is the well-documented modern pattern. If `c1` were the played coverage the
asymmetry would run the other way.

**Decision D4 — `mofo_coverage_played_shown` reads *shown-then-played*: character 1 is
the pre-snap shown look, character 2 is the post-snap played coverage.**

**This contradicts the word order in the field's own name.** That is recorded here
deliberately. The 91.8% / 67.1% split is not marginal, and the rotation asymmetry
corroborates it, so the evidence is followed rather than the label.

### 4.2 Use

- `mofo_shown` (character 1) is the **alignment** field — it is what the defence lined
  up in, which is what this phase asks about.
- `mofo_played` (character 2) is carried as context.
- `mofo_rotated` = `shown != played`, a derived binary: did the defence move after the
  snap?

Evidence is emitted as `outputs/tables/alignment_mofo_resolution.csv`.

---

## 5. Which alignment columns are usable

Fill rates were measured on the raw season CSVs and on the PFF `team_play` payloads.
The full audit ships as `outputs/tables/alignment_column_audit.csv`. Summary and
verdicts:

**Note on the two sets of numbers.** The tables below are measured on the raw
CSVs. `alignment_column_audit.csv` and the report measure the same columns
*after* `load_season` drops the nine 2024 drill rows, so a few 2024 figures differ
by a tenth of a point (`Cover Family` 90.1% raw vs 90.0% cleaned, `Front Adjust`
32.0% vs 32.2%). The cleaned figures are the ones any analysis actually rests on.
Neither set is typed into prose anywhere: the audit measures on every build, and
`COLUMN_VERDICTS` holds only the verdict text, with no figure in it.

### 5.1 Chart columns — usable

| Column | 2024 fill | 2025 fill | Verdict |
|---|---|---|---|
| `Personnel` | 100.0% | 100.0% | **Use**, after normalisation (§5.4) |
| `Form Fam` | 99.4% | 99.9% | **Use**, after normalisation (§5.4) |
| `Formation` | 99.4% | 99.9% | Use only inside the 2-D early-down table; 128/138 distinct labels fragment badly |
| `Form Adjust` | 24.0% | 20.5% | **Use as a binary** (`form_adjust_used`); the label vocabulary is not stable |
| `Motion` | 31.5% | 31.1% | **Use as a binary** (`motion_used`) |
| `Gen Mo` | 31.5% | 31.2% | **Use**, bucketed; 22 vs 29 labels, top families (SH, ARD, MTR, BNC) are shared |
| `Tempo` | 16.0% | 13.5% | **Use as a binary** (`tempo_used`); label sets overlap but shift |
| `pff_DEFPERSONNEL` | 99.9% | 100.0% | **Use** (already `def_personnel` in the joined table) |
| `pff_BOXPLAYERS` | 99.9% | 100.0% | **Use** (already `box_count`) |

### 5.2 Chart columns — excluded, with the reason

| Column | 2024 fill | 2025 fill | Why excluded |
|---|---|---|---|
| `RB Align` | 89.9% | **0.0%** | Not charted in 2025 at all. No cross-year read is possible. |
| `Front` | 98.3% | **0.0%** | Same. PFF `defense_package` replaces it. |
| `Cover Family` | 90.1% | **0.4%** | Same. `mofo_shown` replaces it — and its 2024 values are what resolved §4. |
| `Coverage` | 1.4% | 0.4% | Never usefully charted in either season. |
| `Front Adjust` | 32.0% | 9.5% | Fill collapsed and the vocabulary changed. |
| `Stunt` | 12.5% | 11.4% | Fill is stable but 2025 collapsed to a bare `Y` on 110 of 113 rows — the label carries no information. |
| `Shifts` | 2.5% | 2.2% | Too rare in the chart. PFF `shift` (99.4% / 97.8% filled, 43 vs 50 positives) is used instead. |
| `Hash_O` | **0.0%** | 0.2% | Empty. **Rescued by PFF `ball_snapped_from`** — see §5.3. |

**Decision D5 — every excluded column is named in the report with its reason.** A
reader who expects a front-vs-outcome table must be told it cannot be built rather
than left to assume it was overlooked.

### 5.3 `pff_TEALIGNMENT` — a judgement call

Fill is 54.3% (2024) and 40.3% (2025). That 14-point drop is either a genuine mix
shift (fewer attached tight ends) or a charting-diligence change, and **this data
cannot tell which**.

**Decision D6 — `pff_TEALIGNMENT` is carried with blank treated as an explicit
category (`UNCHARTED`), and every table using it states that the fill change is
unexplained.** It is excluded from the headline decomposition summary because a
mix-vs-efficacy split on a field whose missingness moved 14 points would put a
charting artefact into the mix term.

### 5.4 PFF fields — the cross-year rescue

Measured on the 1,935 joined plays:

| Field | 2024 fill | 2025 fill | Verdict |
|---|---|---|---|
| `ball_snapped_from` | 99.4% | 97.8% | **Use as `hash`** (L/C/R). This is the headline recovery: the chart's `Hash_O` is empty in both seasons and PFF has it on nearly every play. |
| `defense_package` | 99.4% | 97.8% | **Use.** Agrees with the rushing-feed `def_package` on **819 / 819 = 100%** of overlapping rows, and unlike it covers passes too, so trap 3 is sidestepped rather than violated. |
| `mofo_coverage_played_shown` | 97.9% | 96.9% | **Use** (see §4) |
| `motion` | 33.8% | 30.6% | Cross-check against chart `Motion`. Encoded `1` or null — **never `0`** (see D8). |
| `shift` | 99.4% | 97.8% | **Use as binary** |
| `play_action` | 99.4% | 97.8% | **Use as binary** |
| `run_concept_1` | 47.2% | 37.7% | **Use as the cross-year run-concept vocabulary** (see D7) |
| `poa_actual` | 49.9% | 39.6% | **Use, runs only** — point of attack |
| `pistol` | 99.4% | 97.8% | Record only: 0 positives in 2024, 9 in 2025 |
| `option` | 10.5% | 7.2% | Record only |
| `shotgun` | 99.4% | 97.8% | **Exclude** — 937/942 and 964/965 are shotgun. A constant explains nothing. |
| `no_huddle` | 99.4% | 97.8% | **Exclude** — zero positives in either season. |

**Decision D7 — the 2-D formation × concept table uses PFF `run_concept_1`, not the
chart's `Play Type`.** Phase 1 had to build `playtype_crosswalk.csv` because the chart
relabelled `CTR` → `GAP` and `WIDE ZONE` → `OZ` between seasons. PFF's vocabulary did
not move: `Inside Zone`, `Counter`, `Man`, `Outside Zone` appear with the same spelling
in both years. Using it removes the relabelling confound from the one table where a
mix-vs-efficacy answer is most likely to live.

**Decision D8 — PFF booleans arrive as float `1.0` / `0.0` / null, and `motion` and
`option` use `1.0` / null with no explicit zero.** Every such field is normalised with
an explicit `fillna(0)` *only* where null genuinely means "no", and that judgement is
made per field in code with a comment. Getting this wrong silently halves or doubles a
rate; it is exactly the kind of silent failure this repository has been burned by.

---

## 6. Vocabulary drift and the OTHER bucket

Phase 1 found the play-type vocabulary moved between seasons. Alignment columns moved
too:

- `Form Fam`: 2024 writes `UNBALANCED`, 2025 writes `UNBAL`. 28 vs 30 distinct labels.
- `Personnel`: 2024 has 4 labels (`11`, `12`, `10`, `13`); 2025 has 11, because it
  subdivides twelve personnel into `12S`, `12B`, `12W`, `12M`, `12P`, `12J` and adds
  `DAL` (n=5) and `T` (n=1).

Left alone, these produce a decomposition where a pure relabelling reads as a mix
shift. That is precisely the failure mode this phase exists to avoid.

**Decision D9 — normalisation is mechanical and its output is published as a
crosswalk, not hand-mapped from memory.**

- `personnel_base`: strip trailing letters, keep the leading digits
  (`12S` → `12`). Labels that are not two digits (`DAL`, `T`) → `OTHER`.
- `form_fam_norm`: upper-case, strip whitespace, then apply a small explicit
  synonym table derived from the observed label sets (`UNBALANCED` → `UNBAL`). The
  table lives in code, is short, and is printed into the crosswalk CSV with counts so
  a coach can check it.
- **OTHER rule:** after normalisation, a label is kept as its own group only if it has
  **at least 30 graded plays in both seasons**. Everything else falls into `OTHER`.

The 30-play floor does double duty: it guarantees every named group in a
decomposition clears the low-n bar the task set, and it guarantees every group exists
in both seasons, which the decomposition arithmetic requires. **The share of plays
landing in `OTHER` is reported on every decomposition row.** A dimension where OTHER
swallows most of the data is not a result.

Crosswalks ship as `alignment_form_fam_crosswalk.csv` and
`alignment_personnel_crosswalk.csv`.

---

## 7. The outcome abstraction

`analysis.rate_by` hardcodes `efficiency`. It is reused unchanged for the descriptive
cut tables (D10), but the decomposition needs a per-row numeric outcome so that EPA
can replace success rate without a rewrite.

**Decision D10 — the decomposition takes an *outcome specification*, not a metric
name.**

```python
Outcome = namedtuple("Outcome", "name series")   # series: DataFrame -> pd.Series[float]

OUTCOME_SUCCESS   = Outcome("success_rate",   ...)  # Y -> 1.0, N -> 0.0, X/blank -> NaN
OUTCOME_EXPLOSIVE = Outcome("explosive_rate", ...)  # True -> 1.0, False -> 0.0, all plays
# Phase 2 adds: Outcome("epa", lambda df: df["epa"])
```

A group's rate is the mean over non-null values; its weight is the count of non-null
values. For success rate that is *exactly* `successes / graded`, so the decomposition
and `rate_by` must agree to four decimal places — **and a test asserts they do**,
because a silent divergence between the descriptive tables and the decomposition is
the single most dangerous bug available here.

Every public function in `alignment.py` takes `outcome: Outcome = OUTCOME_SUCCESS`.
Explosive rate is run through the same path in this phase, which proves the parameter
works rather than leaving it untested until Phase 2 merges.

---

## 8. The decomposition

For a grouping `g`, with base year 0 = 2024 and comparison year 1 = 2025, weight
share `p` and group rate `r`:

```
Δ = Σ p₁·r₁ − Σ p₀·r₀
  = Σ (p₁−p₀)·r₀        ← MIX        (weights moved, rates held at 2024)
  + Σ p₀·(r₁−r₀)        ← EFFICACY   (rates moved, weights held at 2024)
  + Σ (p₁−p₀)·(r₁−r₀)   ← INTERACTION
```

**Decision D11 — all three terms are reported, never two.** The two-term Oaxaca forms
bury the interaction inside whichever term is evaluated at year-1 weights, which
flatters whichever story the analyst already believes. The three terms sum to Δ
exactly; **a test asserts the identity to 1e-9 on real data and on synthetic data.**

**Decision D11a — the null-result verdict is guarded on `mix + interaction`, not on
`mix` alone.** The counterfactual the report actually states — hold 2025 usage at its
2024 level and see what happens — is Σp₀·r₁ − Σp₁·r₁ = Σ(p₁−p₀)·r₁, which expands to
*mix plus interaction*. A guard on `|mix|` would let a negligible mix with a large
interaction through as a null result. On this data both are small (the largest
combined weights effect on any dimension is about 1.4 points against an eight-point
efficacy term), so the verdict is unchanged — but the guard now tests the sentence it
is guarding, which matters once Phase 2's EPA replaces success rate.

**Decision D12 — the decomposition is run on four subsets:**

| Subset | Why |
|---|---|
| All plays | The headline 57.4% → 49.5%. |
| Early downs (1st & 2nd), all plays | Phase 1's "the problem is earlier in the series". |
| Early-down runs | Phase 1's sharpest cut, 61.7% → 42.7%. **The primary target.** |
| Runs, all downs | Separates "early down" from "run" as the driver. |

`alignment_decomposition_summary.csv` is one row per (dimension × subset), with
columns: `dimension, subset, outcome, n_2024, n_2025, rate_2024, rate_2025, delta,
mix, efficacy, interaction, other_share, groups`. Per-group detail ships as
`alignment_decomposition_<dimension>_<subset>.csv`.

Dimensions in the summary: `personnel_base`, `form_fam_norm`, `motion_used`,
`gen_mo_family`, `form_adjust_used`, `tempo_used`, `hash`, `shift`, `play_action`,
`def_package_norm`, `box_count_band`, `mofo_shown`, `mofo_rotated`.

---

## 9. Tables to build

All write to `outputs/tables/alignment_*.csv`. Every rate carries its `n`; every table
this phase builds itself carries a `low_n` boolean (`graded < 30`).

**Evidence / provenance**
1. `alignment_column_audit.csv` — every candidate column, fill by season, verdict, reason
2. `alignment_offense_package_crosswalk.csv` — §3 evidence
3. `alignment_mofo_resolution.csv` — §4 evidence
4. `alignment_form_fam_crosswalk.csv`, `alignment_personnel_crosswalk.csv` — §6 evidence
5. `alignment_source_agreement.csv` — chart vs PFF where both carry a field
   (personnel, motion, def package)

**Descriptive cuts** (via `analysis.rate_by`, so `MIN_SAMPLE=15` suppression applies)
6. `alignment_by_<dim>.csv` for each dimension in §8
7. `alignment_mix_<dim>.csv` — usage share by season, no outcome, so nothing is suppressed

**Decomposition**
8. `alignment_decomposition_summary.csv` — **the single most valuable table**
9. `alignment_decomposition_<dim>_<subset>.csv` — per-group detail

**The two-dimensional cut**
10. `alignment_formation_concept_early_run.csv` — `form_fam_norm` × `run_concept_1`,
    early-down runs only, both seasons, with `n` and `low_n` on every cell. This is
    where "same look, same call, less output" would show if it exists.

---

## 10. The report

`build_alignment_report.py` → `outputs/ALIGNMENT.md`.

**Decision D13 — every figure in the prose is read out of a table at render time.
None is typed.** Phase 1 shipped two wrong numbers in a published report with 68
tests passing, because the tests tested what had been thought of. Three regression
tests in `tests/test_report.py` already exist for this; Phase 4 copies the pattern:
render the report twice with different table values and assert the prose changes.

**Decision D14 — the report carries a statistical-honesty section, placed before the
findings, not after them.**

There are roughly 300 early-down runs per season. A formation cell of 40 graded plays
has a 95% interval of roughly ±15 points on its success rate. Consequences the report
must state plainly:

- The decomposition **totals** are stable — they are weighted sums over the whole
  sample, so per-cell noise largely cancels.
- Individual per-cell "efficacy drops" mostly **are not** findings, and cells are
  therefore **not ranked by change**. Ranking noisy cells by their movement is how a
  null result gets dressed up as an insight.
- Any cell with `graded < 30` is marked and no claim is built on it.

**If the mix term is near zero across every dimension, the report says alignment does
not explain the decline — in the first paragraph, in those words.** No flattering
slice is to be hunted for.

---

## 11. Module boundary

Phase 2 is editing `analysis.py`, `build_tables.py`, `report.py` and `run.py` in
parallel. Phase 4 therefore touches none of them.

**New:** `src/playcalls/alignment.py`, `build_alignment_tables.py`,
`build_alignment_report.py`, `tests/test_alignment.py`.

**One edit, strictly additive:** `charting.py`'s `_COLUMNS` gains the alignment
columns. Nothing existing changes. Verified safe: `load_season` is called only for
2024 and 2025 (`run.py:26 SEASONS = (2024, 2025)`, `gamemap.py`, and the tests), and
all added columns exist in both files. It already cannot read 2021–2023, which lack
`pff_DOWN`.

**Re-attaching the widened columns.** `outputs/joined_plays_enriched.parquet` was
written before the widening, so the new chart columns are not in it. They are
re-attached by re-reading the season CSVs through the widened `load_season` and
merging on `(season, game_code, play_no)`.

**Decision — this merge is asserted, not trusted.** The key must be unique on both
sides, the merge must be 1:1, and it must leave **zero** unmatched rows
(1,935 = 948 + 987; the nine 2024 drill rows are already dropped by the `def_team`
regex in `load_season`). A test enforces all three. PFF fields are attached on
`analysis._play_key(play_id)` — never `.astype(str)`, per CLAUDE.md trap 1 — and the
match rate is asserted at ≥ 98%.

---

## 12. Testing strategy

`tests/test_alignment.py`. The existing 76 tests must keep passing.

**Arithmetic identity**
- The three decomposition terms sum to Δ to 1e-9, on synthetic data and on the real
  joined table, for every dimension and subset.
- Group rates from the decomposition equal `analysis.rate_by`'s `success_rate` to 4 dp.

**The outcome parameter actually works**
- Running `OUTCOME_EXPLOSIVE` through the same code path reproduces `rate_by`'s
  `explosive_rate`.
- A synthetic third outcome (a plain numeric column, standing in for Phase 2's `epa`)
  decomposes correctly — this is the test that proves EPA drops in without a rewrite.

**The traps**
- `_play_key` is used: a test that a naive `.astype(str)` join matches zero rows and
  the real one matches ≥ 98%, so the trap cannot silently regress.
- Only 2024 and 2025 rows ever reach an alignment table.
- `defense_package` from `team_play` and `def_package` from `rushing` agree where both
  exist — asserted, so the two are never accidentally pooled.
- PFF `motion` null-handling: a fixture with nulls asserts the motion rate is
  computed against all plays, not against the non-null subset.

**Normalisation**
- `UNBALANCED` and `UNBAL` land in the same group; `12S` and `12` land in `12`;
  `DAL` lands in `OTHER`.
- Every group in a decomposition exists in both seasons (the OTHER rule holds).

**Report**
- Three hardcoded-figure regression tests, in the style of
  `tests/test_report.py::test_perfect_game_count_is_not_hardcoded`: change a table
  value, assert the rendered prose changes.
- Low-n cells are marked in the rendered report.
- If the mix term is negligible, the report contains the plain-language null
  statement.

---

## 13. What this phase will not be able to answer

Stated here so the report can state it too:

- **Why efficacy fell**, if that is the answer. Blocking, receiver separation and
  defensive quality are unmeasured here.
- **Front and coverage-family effects**, because Baylor stopped charting them in 2025
  (§5.2). PFF's `mofo_shown` is a coarser substitute, not an equivalent.
- **Running-back alignment**, for the same reason.
- **Whether the `pff_TEALIGNMENT` fill drop is real or a charting change** (§5.3).
- **Opponent strength.** Unchanged from Phase 1; no adjustment is made.
- **Cause and effect between mix and efficacy.** If Baylor ran less *because* running
  stopped working, the decomposition still splits the arithmetic correctly, but it
  cannot say which came first.

---

## 14. Notes for `CLAUDE.md` and `AGENTS.md`

Phase 4 does not edit those two files (they are kept in sync deliberately and must
never be symlinked). The lines it recommends adding are listed in the final report to
the user, sourced from §3, §4, §5.2, §5.4 and §6 of this spec.

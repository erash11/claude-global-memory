# Play-Call Success Rate & EPA — Design

**Date:** 2026-09-09
**Owner:** Eric Rash, Applied Performance, Baylor Athletics
**Status:** Approved in shape; awaiting spec review

---

## 1. Purpose

Turn five seasons of Baylor offensive play-call charting into an analytical picture
of *what the offense calls, what works, and against what*.

The core questions, in Eric's words:

- What plays are the most successful?
- What play calls are most successful against certain defenses, from certain field
  positions, in certain situations?
- What is the coordinator's profile — what does he like, what does he avoid, how does
  personnel drive his decisions, what does he do in specific game situations?

**Audience:** analysts. Eric, plus a small number of people in the analytics
department. **Not** the coordinator, and **not** position coaches. That matters: the
report may show its work, carry uncertainty, and use analytic vocabulary. It does not
need to survive a position meeting.

**Decision it serves:** identifying where the offense's stated identity and its actual
results diverge. It is a self-scout, not an opponent scout.

---

## 2. Scope

### Phase 1 — this spec

Baylor play-call charting for **2024 and 2025**, joined to PFF play-level data,
producing a written analytical report.

### Deferred, deliberately

| Phase | Contents | Why deferred |
|---|---|---|
| 2 | EPA via an expected-points model, CFBD integration | Needs a model this repo does not contain; see §8 |
| 3 | Weekly 2026 in-season ingest | Build on a proven Phase 1 pipeline, not before |

The repository is named `PlayCalls_SuccessRate_EPA`. Phase 1 delivers **success rate,
not EPA**. This is a known and accepted gap, recorded here so nobody reads the folder
name as a promise.

### Out of scope permanently

2021–2023. Those files carry 8 columns — play call, personnel, formation, motion — and
no outcome fields at all. No down, no distance, no yards gained, no field position.
Success rate is not computable for them from this data. They can support play-call
*frequency* work later, but they are not part of this analysis and must not be silently
pooled into any number.

---

## 3. Data inventory — verified 2026-09-09

### 3.1 Baylor charting CSVs (this repo)

| File | Rows | Games | Outcome columns |
|---|---|---|---|
| `2021_All_Games.csv` | 971 | 14 | none |
| `2022_All_Games.csv` | 967 | 13 | none |
| `2023_All_Games.csv` | 896 | 12 | none |
| `2024_All_Games.csv` | 957 | 13 | 49 columns |
| `2025_All_Games.csv` | 987 | 12 | 49 columns |

Headline number already computed from `Efficiency`:

| Season | Success rate | Graded plays |
|---|---|---|
| 2024 | **57.4%** | 928 |
| 2025 | **49.5%** | 986 |

An eight-point drop. This is the report's opening question: what explains it?

### 3.2 PFF DuckDB (upstream, sister project)

`~/DEV/Football/PFF_Data_Project/data/pff.db` — 518 MB, last written 2026-06-01.

| Table | Rows |
|---|---|
| `pff_stats` | 4,776,445 |
| `pff_premium` | 378,505 |
| `pff_grades` | 175,559 |
| `player_seasons` | 15,974 |
| `players` | 12,258 |
| `games` | 5,042 |
| `teams` | 957 |
| `ingest_log` | 52 |

`pff_premium` is **play-level** — it carries `play_id`, `game_id`, `season`, `week`,
`pff_player_id` and a `raw_json` payload.

**Baylor coverage is complete for the seasons we need:**

| Season | Baylor games | With play-level premium |
|---|---|---|
| 2023 | 12 | 12 |
| 2024 | 13 | 13 |
| 2025 | 12 | 12 |

The 2025 PFF game list aligns 1:1 with the CSV game order — CSV `2501 vs AUB` is PFF
game 28762, Baylor vs Auburn, 2025-08-30, and all twelve follow in sequence.

**Categories present:** `pass_protection`, `pass_rush`, `pressure`, `passing`.
**Categories missing and required:** `team_play`, `rushing`, `quarterback_charting`.

`quarterback_charting` is where per-play `coverage` lives. `team_play` is the master
play list carrying `offense`, `defense`, `down`, `distance`, `field_position`,
`offense_players`, `defense_players`, `shotgun`, `pistol`, `play_action`, `screen`,
`draw`, `no_huddle`, `shift`, `trick`, `redzone`. `rushing` carries the run-side
detail including `def_package`.

### 3.3 Local scratch probe

`~/DEV/Football/PFF_Data_Project/data/week1_auburn/` holds a full 11-category pull for
one game plus ~30 exploratory scripts, dated 2026-09-06/07.

**That game is season 2026, week 1** — Baylor at Auburn, 2026-09-05, final 17–16. It is
*not* the 2025 Auburn game. Do not confuse the two. It is, however, the first game of
the Phase 3 weekly pipeline, already downloaded.

`playdeck.py` in that folder is a working play-level join prototype. It joins
`quarterback_charting` + `premium_passing` + `premium_pressure` + `premium_pass_rush` +
`premium_team_play` on `play_id`. Phase 1 builds on it rather than starting fresh.

Its output (`lagway_plays.json`, 59 Baylor dropbacks) shows the achievable field
richness, with fill rates measured on that game:

| Field | Fill | Example values |
|---|---|---|
| `coverage` | 93% | Single, Hole in Zone, Underneath, Top |
| `def_pkg` | 100% | 4-2-5, 3-3-5 |
| `pressured` | 100% | 0/1 |
| `rushers` | 95% | 3, 4, 5, 6, 7 |
| `target` | 93% | player names |
| `route`, `depth` | 90–93% | route code, yards |

**Correction to the project's own Phase 0 notes:** `docs/pff_api_notes.md` (2026-05-24)
states the premium feeds are "aggregated advanced stats per player/team per game — not
raw play-by-play." The 2026-09-07 probe disproves this. They are play-level, keyed by
`play_id`. That note should be amended when `PFF_Data_Project` is next touched.

---

## 4. Architecture

### 4.1 Repository boundary — decided

```
PFF_Data_Project/          (upstream, owns all PFF ingest)
  data/pff.db              ← extended with team_play, rushing, quarterback_charting
        │
        │ read-only
        ▼
PlayCalls_SuccessRate_EPA/ (this repo, owns the join and the analysis)
  2024_All_Games.csv
  2025_All_Games.csv
```

`PFF_Data_Project/CLAUDE.md` states its contract plainly: the DuckDB *is* the
deliverable, and downstream consumers own visualisation and cross-domain joins. This
project is a downstream consumer.

**Therefore:** the three missing premium categories are added to `PFF_Data_Project`'s
loader, in that repo, as a separate change. This repo opens `pff.db` **read-only** and
never writes to it, never re-fetches from the PFF API, and never holds PFF credentials.

Rejected alternative: pulling PFF directly into this repo. Faster to start, but creates
a second copy of PFF data that will drift, puts credentials in two places, and breaks
the sister project's stated boundary.

### 4.2 Pipeline

```
  Baylor CSV ──► clean ──► normalise ──┐
                                       ├──► joined play table ──► analysis ──► report
  pff.db ──────► extract play-level ───┘
```

Five units, each independently testable:

| Unit | Input | Output | Responsibility |
|---|---|---|---|
| `load_charting` | season CSVs | tidy frame | BOM, quoted commas, apostrophe casting, drop junk rows |
| `crosswalk` | tidy frame | normalised frame | map 2024 and 2025 vocabularies onto one taxonomy |
| `load_pff` | `pff.db` | play-level frame | flatten `raw_json`, one row per `play_id` |
| `join` | both frames | joined table + match report | align charting rows to PFF plays |
| `analyse` | joined table | result tables | success rate cuts, tendency profile |

The report is written from the result tables, not from raw data.

---

## 5. The join — the central risk

### 5.1 The problem

The Baylor CSV has **no `play_id`**, no quarter and no game clock. The only shared keys
are game, down, distance and field position.

Collisions are guaranteed: every drive starting after a touchback is 1st-and-10 from the
25.

### 5.2 The hypothesis

The Baylor columns are named `pff_DOWN`, `pff_DISTANCE`, `pff_FIELDPOSITION`,
`pff_DRIVE`, `pff_GAINLOSS`, and the opponent codes (`ALAU`, `TXCU`, `OKST`) are PFF
codes. The `pff_` prefix suggests the charting tool **imported these fields from PFF**.

If true, the values match exactly rather than approximately, and the `#` column may
preserve PFF play sequence — which would make the join near-trivial.

This is a hypothesis. It has not been tested against a single row.

### 5.3 Join strategy, in order of preference

1. **Sequence alignment.** Order both sides within a game and align. Cheapest if `#`
   tracks PFF order.
2. **Composite key** on (`game_id`, `down`, `distance`, `yards_to_goal`), with
   `gain/loss` as a tie-breaker for collisions.
3. **Drive-scoped alignment.** Use `pff_DRIVE` to partition, then align within drive.

### 5.4 The gate

Step 0 of the build joins **one game** — 2025 game 1, Baylor vs Auburn (PFF 28762) —
and reports the row-level match rate.

**If the match rate is below 95%, the build stops** and the approach is revisited before
any analysis is written. An unproven join silently produces confident, wrong numbers.

---

## 6. Open data questions — resolved before analysis

### 6.0 RESOLVED 2026-09-09 — both gates passed

**The rushing gap did not exist.** It was a comparison error in this spec's own
research, corrected here rather than quietly dropped.

The "20 charted runs vs 43 PFF runs" figure in §6.1 compared Baylor's **2025** charting
file against the PFF pull sitting in `PFF_Data_Project/data/week1_auburn/`. That folder
is the **2026** season opener (Baylor at Auburn, 2026-09-05), not the 2025 one. Two
different games a year apart. Baylor plays Auburn in both seasons, which is what made
the mistake easy to miss.

Measured properly against PFF game 28762 — Baylor vs Auburn, 2025-08-30 — PFF holds
exactly **20** Baylor rushes for that game. The chart and PFF agree.

Across all 25 games:

| Season | Charted runs | PFF runs | Charted passes | PFF passes | Shortfall |
|---|---|---|---|---|---|
| 2024 | 447 | 448 | 486 | 500 | **1.6%** |
| 2025 | 382 | 383 | 598 | 597 | **0.0%** |

**Gate results:**

- **Join match rate: 98.6%** across 1,935 charted plays. **15 of 25** games matched
  100%. Threshold was 95%. The weakest game is 2508 vs Cincinnati at 91.0% (61 of 67).
- **Charting shortfall: 1.6% worst case** (2024 — 14 pass plays and 1 run, 15 in
  total). Threshold was 2%. 2025 is complete.

The 390 unclaimed PFF plays break down as:

| Classification | Count |
|---|---|
| `special_teams` | 368 |
| `unmatched_pass` | 11 |
| `unknown` | 8 |
| `unmatched_run` | 3 |

The 8 `unknown` rows are special teams that PFF left untagged: six are 4th-down punts
or field-goal attempts with a null `st_play_type`, and two are extra-point attempts
(`down = 0` at the opponent 3). They appear in neither the rushing nor the passing
feed, which is why the classifier could not place them from those. None is a scrimmage
down.

Only 3 rushes and 11 passes are unclaimed scrimmage downs, and since the season totals
agree those are join misses rather than charting gaps.

**Consequence:** success rates rest on a complete denominator for 2025 and a
98.4%-complete one for 2024. The 2024 figure carries a small upward bias if the 14
uncharted passes were disproportionately unsuccessful. The report states this.

**The join hypothesis in §5.2 is confirmed.** Opponent codes match across both sources
with zero difference in either season, and 18 of 25 games join perfectly on
down/distance/yard-line. The charting tool imported its `pff_`-prefixed columns from
PFF, so the values agree exactly.

---

### 6.1 The rushing gap — highest priority *(superseded by §6.0)*

2025 game 1:

| Source | Passes | Runs |
|---|---|---|
| Baylor chart | 59 | **20** |
| PFF | 59 | **43** |

Passes match exactly. Runs differ by 23.

Two candidate explanations, with very different consequences:

- **PFF counts more things as runs** — scrambles, kneels, sacks charged as rushes,
  plays negated by penalty. Benign; needs a mapping rule.
- **The Baylor chart is missing ~23 run plays** for that game. If so, *every*
  success-rate number computed from this file is wrong, and the 57.4% → 49.5% drop may
  be partly an artefact of charting coverage.

A 59/20 split is 75% pass. The 2025 season is 61% pass. That gap is itself a reason to
suspect under-charting of runs.

**This is resolved before anything else is built.** It is not assumed away.

**How it gets resolved (decided 2026-09-09).** Eric's answer was "PFF would know", so
PFF is treated as the reference and the question is settled empirically rather than by
opinion:

1. Pull all 43 PFF rush plays for 2025 game 1 (PFF game 28762) with down, distance,
   yard line, ball carrier and gain.
2. Match them against the 20 runs in the Baylor chart.
3. **Classify the 23 unmatched plays individually.** Scrambles, kneels, sacks charged as
   rushes, and penalty-negated plays are benign and become documented mapping rules.
4. Any unmatched play that is a genuine designed run with no charting row is a
   **charting coverage gap**. If those exist in material numbers, the finding is
   escalated to Eric before the analysis proceeds, because it would mean the file's
   success rates are computed on an incomplete denominator.

The classification table is a permanent artefact, not a throwaway check. Whatever the
answer, the 2024-vs-2025 comparison must state the charting coverage for each season.

### 6.2 The vocabulary crosswalk

The play-call vocabulary appears to be the **same system re-punctuated**, not a new
playbook:

| 2024 | 2025 |
|---|---|
| `IRENE/ITALY` | `IRENE.ITALY` |
| `MARK/MOLLY` | `MARK.MOLLY` |
| `RDY/LRY` | `RANDY.LARRY` |
| `GARY/GAIL` | `GARY.GAIL` |

A naive comparison reports ~90% playbook turnover, which would be false.

But normalisation is **not** a simple separator swap:

- `RDY/LRY` → `RANDY.LARRY` is abbreviation expansion, not punctuation.
- 2024 already contains dot-form values (`IRENE.ITALY SPLIT`, `RAZOR.BLADE SPLIT`), so
  the change happened mid-season or varied by charter. Normalise **per row**, never per
  file.
- 2025 is more granular on modifiers: `RAZOR/BLADE` (104, unmodified) in 2024 becomes
  `RAZOR.BLADE SPLIT` (94) + `RAZOR.BLADE SAME SIDE` (19) in 2025. Cross-year comparison
  is safe at **base concept** only; modifier-level 2024-vs-2025 is not supported.
- `Play Type` is a genuine regrouping, not punctuation. 2024 has `CTR`, `PWR`,
  `WIDE ZONE`, `ZONE READ`, `QBM`. 2025 has `GAP`, `OZ`, `MVMT`, `DRAW`, `OPTION`.

Build the cross-year key on `Run`, `Pro Fam` and `Pass Concept` — the named concepts,
which are stable across years after normalisation. Derive `Play Type` groupings from
those; do not use `Play Type` as the join layer.

**How the `Play Type` mapping gets settled (decided 2026-09-09).** Eric was asked
whether `CTR`+`PWR` → `GAP` and `WIDE ZONE` → `OZ`, and answered "not sure". So the
mapping is **derived from the data, not guessed and not asked again**:

1. Normalise the named concepts (`Run`, `Pro Fam`, `Pass Concept`) across both years.
2. For each normalised concept, tabulate which `Play Type` label it carried in 2024 and
   which it carried in 2025.
3. A concept appearing in both years with a stable label on each side *is* the mapping
   evidence. `RAZOR.BLADE` tagged `CTR` in 2024 and `GAP` in 2025 across dozens of reps
   is a real correspondence, not a guess.
4. Emit the derived crosswalk as a table with the supporting rep counts, and flag any
   concept whose mapping is ambiguous or thinly supported.

Eric reviews that derived table as a **sanity check**, not as a memory test. Concepts
that cannot be mapped from evidence are reported as unmapped and excluded from
cross-year `Play Type` comparison rather than force-fitted.

**No cross-year number is produced before the derived crosswalk is reviewed.**

### 6.3 Confounds to carry into the report

- **Quarterback.** 2024 used QB 13 (813 snaps) and QB 7 (136 snaps). 2025 is almost
  entirely QB 13. A 2024-vs-2025 gap partly measures a QB change; splits should show it.
- **Coordinator — confirmed same, 2024 and 2025** (Eric, 2026-09-09). This is load
  bearing. It means the 57.4% → 49.5% drop is *not* a change of play-caller, so the
  2024-vs-2025 comparison is a legitimate read on scheme evolution, personnel and
  execution under one system. The report should say this explicitly, because a reader
  will otherwise assume a staff change explains the gap.
- **Defensive charting collapsed in 2025**, in the Baylor file:

  | Column | 2024 fill | 2025 fill |
  |---|---|---|
  | `Front` | 98.3% | **0.0%** |
  | `Cover Family` | 90.1% | **0.4%** |
  | `Coverage` | 1.4% | 0.4% |
  | `Def Play Call` | 0.0% | 2.5% |

  PFF supplies coverage per play, so this is recoverable — but PFF coverage comes from
  `quarterback_charting`, which covers **dropbacks only**. Run-play defensive context
  comes from `def_package` in the `rushing` feed instead. The two are not the same
  field and must not be pooled.

- **Other year-over-year collapses:** `Gen Play` 47.1% → 0.0%; `RB Align` 89.9% → 0.0%;
  `Group #` 0.0% → 49.2%. None of these support cross-year grouping.

### 6.4 Known cleaning rules

- **UTF-8 BOM** on every header — read with `encoding='utf-8-sig'`.
- **`Name` contains a comma** inside quotes (`"2501 BU OFF vs AUB, Play 001"`). Naive
  `awk -F,` / `cut -d,` shifts every later column by one. Use a real CSV parser.
- **`Name` format differs by season** — `YY.GG` in 2021–2022, `YYGG` in 2023–2025, and
  2021's first game reads `20.01 BU vs TXST OFF` with a different word order.
- **`pff_FIELDPOSITION` is a signed yard line**, not a distance: `'-34` = own 34,
  `'+18` = opponent 18. The apostrophe is Excel's text guard. Prefer
  `pff_YARDSTOGOALLINE`, a clean unsigned integer, verified consistent on all 987 rows
  of 2025 (`100 − |FP|` own side, `FP` opponent side).
- **`pff_GAINLOSS`** carries the apostrophe on negatives only.
- **9 junk rows in 2024** carry drill names in `pff_DEFTEAM` (`HAL SPEED CUT`,
  `THROW BY JC`, `SPLIT RELEASE`, `m`). Drop them. Effect on 2024 success rate:
  57.6% → 57.4%.
- **`Prac Period` is not a practice flag.** Values are `CHECKED` (2024) and alignment
  tags `OPEN` / `TE WEAK` / `TE STRONG` (2025). Do not filter on it.
- **`Efficiency = X`** is 1 row in 2025 and 7 in 2024; all are victory-formation kneels
  or penalties. Exclude `X` and blank from the success-rate denominator.
- **`EXPL`** is `Y` or blank — blank means not explosive, not missing.
- **`pff_DRIVEENDEVENT`** is a drive attribute repeated on every play of the drive.
  `TOUCHDOWN` does not mean *this* play scored.
- **`pff_DOWN` includes `5`** — 11 rows in 2025, 2 in 2024. Inspect before use.

---

## 7. Analysis deliverables

All cuts report **n** alongside every rate, and suppress cells below a minimum sample
(default n < 15) rather than printing noise as insight.

**A. Success-rate profile**
By base concept, formation family, personnel, play type, down-and-distance bucket,
field zone, and quarter. Both seasons, separately and combined.

**B. Situational profile**
Third-and-short vs third-and-long. Red zone. Backed up. Two-minute. Early-down
run/pass balance.

**C. Versus-defense profile**
Success rate by PFF `coverage`, by defensive package, by pressure and by rusher count.
Dropbacks use `quarterback_charting` coverage; runs use `def_package`. 2024 additionally
supports the Baylor-charted `Front` and `Cover Family`.

**D. Coordinator tendency profile**
Call distribution by down, distance, field zone, personnel and quarter. What is
over-used, what is abandoned, what is never called in a given situation. Tendency is
reported as *frequency*, and paired with success rate so predictability and
productivity can be read together.

**Score state is not available and is not promised.** Neither source carries a running
in-game score: the Baylor file has none, and PFF's `team_play` gives `quarter` and
`game_clock` but no score. Score-aware tendency (trailing, leading, garbage time)
requires CFBD play-by-play and belongs to Phase 2. Quarter and game clock are the
closest Phase 1 proxies and will be labelled as proxies, not as game situation.

**E. 2024 vs 2025**
Base-concept comparison only, on the approved crosswalk, with QB and charting-coverage
confounds stated on the page rather than in a footnote.

---

## 8. On EPA

There is **no EPA column** in any file and no expected-points model in this repository.

EPA requires modelling expected points from game state, fitted on a large play-by-play
corpus. Twenty-five games of one team's offense is far too small. The realistic path is
CFBD's public play-by-play, either using its published predicted-points values or
fitting a model against it, then joining back on game, drive, down, distance and yard
line.

That is a self-contained project. It is **Phase 2**. Phase 1 must not present a
yards-based proxy and call it EPA.

---

## 9. Verification

- Cleaning and normalisation functions get unit tests over fixture rows drawn from the
  real files, including every trap in §6.4.
- The join emits a **match report** every run: rows matched, rows unmatched, and the
  reason. This is a permanent artefact, not a one-off check.
- Season success rates recomputed from the joined table must reproduce 57.4% (2024) and
  49.5% (2025) from the charting file alone. A divergence means the join dropped or
  duplicated rows.
- Raw CSVs stay immutable. Derived tables are written to new paths.

---

## 10. Questions answered 2026-09-09

| # | Question | Eric's answer | Consequence |
|---|---|---|---|
| 1 | Same OC in 2024 and 2025? | **Same coordinator** | The 8-point drop is scheme/personnel/execution, not a staff change. §6.3 |
| 2 | Is `CTR`+`PWR` → `GAP`, `WIDE ZONE` → `OZ`? | **Not sure** | Mapping is derived from concept-level evidence, then sanity-checked. §6.2 |
| 3 | Is 20 charted runs plausible? | **"PFF would know"** | PFF is the reference; the 23 unmatched plays get classified individually. §6.1 |
| 4 | Report format? | **"Whatever makes the most sense"** | Decided below. |

### Report format — decided

**Two outputs, one source.**

1. **Markdown in-repo** at `outputs/` — the source of truth. Diffable, reviewable in a
   pull request, and it sits next to the code that produced it. Every number in it is
   regenerable.
2. **An HTML artifact** published at the end — the readable, shareable version for the
   analytics department, so Eric has a private link rather than a file to email around.

Rationale: the audience is analysts, so the substance belongs in version control where
claims can be traced to code. But "a few others in the analytics department" is a real
audience, and a Markdown file in a git repo is not something a colleague reads
comfortably. The artifact is generated from the Markdown, not written separately, so the
two cannot drift.

No PDF unless asked. It adds a third copy and nobody named a print use case.

---

## 11. Remaining open items

None blocking. The two data risks in §6.1 and §5.4 are gates inside the build, not
questions for Eric — they are answered with evidence during step 0 and escalated only if
they fail.

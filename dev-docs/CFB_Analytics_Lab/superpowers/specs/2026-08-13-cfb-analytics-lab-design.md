# CFB Analytics Lab — Design

**Date:** 2026-08-13
**Status:** Approved, pending implementation plan
**Location:** `~/DEV/CFB_Analytics_Lab`

## Purpose

A stateful learning workspace for working through data-science techniques from
*Football Analytics with Python and R* (Eric A. Eager & Richard A. Erickson,
O'Reilly, 2023), applied to **college** football data from the CollegeFootballData
(CFBD) API rather than the book's NFL/`nflfastR` data.

**Success criterion:** Eric can fluently apply regression, "over expected" metrics,
GLMs, clustering/PCA, tree ensembles, and Bayesian hierarchical models to football
data *and explain why each works*. The deliverable is demonstrated fluency, not a
predictive product.

Explicitly **not** goals: beating the betting market, producing a Baylor-facing
coaching deliverable, or improving the existing `CFB_Victory_Model` forecast. Those
are separate projects that may later consume this one's output.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Purpose | Learn the techniques | Chosen over Baylor-facing analysis, extending the Victory Model, or portfolio work |
| Techniques | Over-expected metrics, GLMs (logistic + Poisson), stability analysis, clustering + PCA, tree ensembles, Bayesian hierarchical | User selected all four offered plus ML and Bayesian as additions |
| Toolchain | Python only, with PyMC | Bayesian hierarchical models subsume the multilevel/mixed-effects chapter, removing the only reason to install R |
| Format | Teach-workspace + notebooks with drills | Mirrors `~/DEV/Terminal_Fluency`, built 2026-08-13 via `mattpocock-skills:teach` |
| Data scope | All `/plays` 2019-2025 — stored as returned (FBS **and** FCS), filtered to FBS at analysis time | ~125 API calls; 7 seasons yields 6 year-over-year pairs for stability work |
| Architecture | Layered: raw Parquet -> thin shared module -> notebooks | Chosen over notebook-centric (duplication risk) and package-first (wrong optimization for a learning project) |

**Bayesian methods are not in Eager's book.** The text stops at frequentist GLMs,
mixed-effects models, and tree ensembles. Lesson 0007 is a deliberate extension past
the source material and is the steepest part of the curriculum.

## Verified environment facts

All confirmed by live probe on 2026-08-13. Do not re-derive.

### CFBD API access

- Key lives at `~/DEV/CFB_Victory_Model/.env` as `CFBD_API_KEY`. Registered in
  `~/.claude/CREDENTIALS.md` row 9.
- **All 74 OpenAPI spec paths probed.** 67 return 200; 7 are tier-gated.
- Tier: **Free (`patronLevel: 0`), 1,000 calls/month**, reset `2026-09-01T00:00:00Z`.
  As of the probe: 72 used, 928 remaining. The CFB and CBB budgets are a **shared pool**
  (`sharedPool: true`).
- `GET /info` returns tier, limit, remaining, and reset. `GET /info/usage` returns a
  rolling 7-day per-endpoint breakdown.
- Gated endpoints (HTTP 401): `/live/plays` (Tier 2), `/scoreboard` (Tier 1),
  `/games/weather` (Tier 1), and all four `/wepa/*` opponent-adjusted EPA endpoints.
  Everything historical and play-level is available.
- `api.collegefootballdata.com` and `apinext.collegefootballdata.com` serve a
  **byte-identical spec** (169,696 bytes, same 74 paths) and identical responses on the
  same key. There is no v1/v2 migration decision. Use `api.collegefootballdata.com`.

### Play-by-play specifics

- `/plays` is **not truncated**. Week 5 2025 returned 18,837 rows across 107 gameIds =
  all 53 FBS games + all 54 FCS games, with zero FBS games missing. (Total games that
  week across all divisions: 266 — 85 D-III, 73 D-II, 54 FCS, 53 FBS.)
- **`/plays` includes FCS games.** Classification filtering must be explicit.
- **`/plays` requires an explicit `week` for BOTH `regular` and `postseason`.** Omitting
  it returns 400 Validation Failed — verified for both season types on 2026-08-13. There
  is no whole-season single call; per-week iteration is mandatory and sets the cost floor.
  Postseason must be fetched by iterating weeks from 1 until a response is empty.
- Payload is ~11.7 MB JSON per regular-season week. Seven seasons ~= 1.4 GB raw JSON,
  ~200-300 MB as Parquet.
- Cost: ~17-19 calls per season (~16 regular weeks + 1-3 postseason). **7 seasons ~= 125 calls.**

`/plays` record schema:
`gameId, driveId, id, driveNumber, playNumber, offense, offenseConference,
offenseScore, defense, defenseConference, defenseScore, home, away, period,
clock{minutes,seconds}, offenseTimeouts, defenseTimeouts, yardline, yardsToGoal,
down, distance, yardsGained, scoring, playType, playText, ppa, wallclock`

`ppa` (predicted points added) ships on every play — the college analogue of
nflfastR's `epa`, and unadjusted for opponent. `offenseTimeouts`/`defenseTimeouts`
were `null` in all sampled rows; treat as unavailable.

### Known API traps

- **`/plays/stats` silently truncates at exactly 2000 rows.** An unfiltered week query
  returned 2000 rows spanning only 10 of ~107 games — no error, no cursor. Confirmed a
  response cap, not per-game: game 401752717 returns 218 rows both in bulk and filtered.
  Always narrow by `gameId` or `team`.
- **`/games/media` appears capped at 100 rows.** Returned exactly 100 unfiltered vs. 8
  when filtered to `conference=B12`. Low priority; not used by this project.
- Parameters that reject the obvious guess: `/game/box/advanced` takes `id` not
  `gameId`; `/player/season/overview` requires both `playerId` and `year`;
  `/coaches/profile` takes `coachId`; `/conferences/changes` requires `year`.

### Local machine

- Python 3.14.6 at `/opt/homebrew/bin/python3`, PEP 668-managed — venvs only.
- `uv` 0.11.6 at `~/.local/bin/uv`.
- **No data-science packages installed globally.** pandas, numpy, scipy, statsmodels,
  scikit-learn, matplotlib, seaborn, pyarrow, duckdb are all absent.
- **R is not installed** and is not needed under the Python-only decision.
- **PyMC resolves cleanly on Python 3.14**: verified `pymc==6.3.0`, `pytensor==3.2.4`,
  `numpy==2.4.6`, `pandas==3.0.5`, `scipy==1.18.0`, `xarray==2026.7.0`.
- WARNING: the resolver selects **pandas 3.0.5**. The book targets pandas 1.x/2.x;
  copy-on-write semantics and some removed idioms will require small adaptations to
  book code.

### Existing local data (free to reuse, zero API cost)

`~/DEV/CFB_Victory_Model/data/cfbd/` holds 101 CSVs / 58 MB covering 2019-2026:
`lines` (15), `games` (15), `drives` (14), `advanced_game` (14), `fbs_teams` (8),
`talent` (7), `season_advanced` (7), `returning` (7), `ratings_sp` (7),
`game_team_stats` (7). **No play-by-play** — that is the gap this project fills.

Lesson 0001 runs entirely on this existing data and requires no API calls.

## Architecture

```
CFB_Analytics_Lab/
├── MISSION.md            # what fluency means here; grounding for every lesson
├── NOTES.md              # teaching preferences, verified env, lesson ledger
├── GLOSSARY.md           # terms promoted only after correct use
├── RESOURCES.md          # book + CFBD docs, each fetched and confirmed
├── README.md
├── pyproject.toml        # uv-managed
├── .env                  # CFBD_API_KEY (gitignored)
├── .gitignore
├── src/cfblab/
│   ├── __init__.py
│   ├── pull.py           # budget-guarded CFBD puller
│   ├── io.py             # Parquet / DuckDB loaders
│   └── filters.py        # FBS classification, season flags
├── data/
│   ├── raw/plays/season=YYYY/*.parquet   # gitignored, regenerable
│   └── curated/                          # gitignored
├── lessons/              # NNNN-topic.ipynb
├── learning-records/     # NNNN-drill-result.md
├── docs/superpowers/specs/
└── tests/
```

The four root markdown files mirror `~/DEV/Terminal_Fluency` so the workspace is
self-describing and resumable: `cd` in, read `MISSION.md` then `NOTES.md`, then the
newest `learning-records/` entry. Do not re-interview about the mission.

`src/cfblab/` stays deliberately thin — only what every lesson needs. Analytical
transformation happens **in the notebooks**, because in a learning project the
transformation is the lesson. DuckDB queries the Parquet directly so 1.3M plays never
need to fit in memory.

### Data flow

```
CFBD API --pull.py--> data/raw/plays/season=YYYY/week=NN.parquet  (immutable)
                              |
                         io.py / DuckDB
                              |
                      lessons/*.ipynb --> learning-records/*.md
```

Raw is written once and never mutated. Re-deriving anything means re-running a
notebook, not re-calling the API.

## Pull safety

The expensive failure mode: a botched pull burns the monthly budget and locks the
project out until Sept 1. Five safeguards in `pull.py`:

1. **Pre-flight budget check.** Call `/info`, compute estimated cost, and refuse to
   start if `remainingCalls < cost * 1.2`. No partial pulls that strand the budget.
2. **Append-only call ledger** at `data/call_ledger.csv` — endpoint, timestamp, HTTP
   status, row count, for every request. `/info/usage` only covers a rolling 7 days;
   this is the durable record.
3. **Truncation tripwire.** Assert `len(rows) not in (2000, 100)` on every response,
   and raise loudly on violation. This class of bug is silent by default.
4. **Resumable and idempotent.** Skip any season/week already present on disk. A crash
   costs nothing.
5. **Postseason iteration.** Walk postseason weeks from 1 until a response is empty.

Requests are serial with a 1-second delay, matching the existing `cfbd_pull.py`
convention for a free community API.

### Schema decisions

- **Classification is explicit, never implicit.** Join `/games` to tag each play with
  home/away classification (`fbs`/`fcs`/`ii`/`iii`). `/plays` ships FCS games alongside
  FBS; an FBS-vs-FCS blowout leaking into a completion-percentage-over-expected model
  corrupts it. Filtering must be a visible act in the notebook, never a hidden default.
- **2020 carries a `covid_season` boolean column.** The season is not dropped — it is
  marked. Lesson 0001 uses it to *show* why year-over-year correlations spanning 2020
  misbehave (shortened season, partial Big Ten/Pac-12 schedules, near-absent
  non-conference play) rather than hiding the distortion.
- Writes stream week-by-week to Parquet; raw JSON never accumulates in memory.

## Lesson sequence

Stability comes first because it needs **no API pull** — it runs on the existing
`CFB_Victory_Model` CSVs, so learning starts while the play-by-play pull runs. It also
reframes every later lesson: knowing which metrics are noise changes how every
subsequent model is read.

| # | Lesson | Teaches | Drill |
|---|---|---|---|
| 0001 | Stability / year-over-year | Correlation, regression to the mean, descriptive vs. predictive | Rank 5 team metrics by stability, defend the ordering |
| 0002 | EDA + regression on plays | Distributions, down/distance effects, simple -> multiple OLS | Model yards gained; explain each coefficient |
| 0003 | "Over expected" metrics | Residual-as-metric — CPOE and RYOE for college | Build RYOE; name its top-3 confounders |
| 0004 | GLMs — logistic & Poisson | Link functions, completion probability, 4th-down conversion, count models | Fit a 4th-down model; find where it is badly calibrated |
| 0005 | Clustering + PCA | k-means archetypes, dimension reduction, choosing k | Cluster WRs by usage; argue the k chosen |
| 0006 | Trees & ensembles | Random forest, gradient boosting, feature importance and its traps | Beat the 0004 GLM; explain whether it actually did |
| 0007+ | Bayesian hierarchical | Priors, partial pooling across 136 teams, uncertainty as output | Re-fit an earlier model hierarchically; compare shrinkage |

Lessons 0003-0004 are the book's spine. Lesson 0007 is the extension past the text —
and the place college data is genuinely more interesting than NFL data, because partial
pooling is the correct tool for a 136-team talent spread.

**Per the `teach` protocol: the next lesson is built only after the previous drill is
reported.** No batch-generating notebooks; that produces reading material, not fluency.
Glossary terms are promoted only after Eric uses them correctly, never on introduction.

## Testing

Tests target the **foundation, not the analysis**. Unit-testing a regression is theater;
unit-testing the join that feeds it is not.

- `tests/test_pull.py` — budget guard refuses when short; tripwire fires at 2000 rows;
  resume skips existing files; postseason iteration terminates on empty.
- `tests/test_filters.py` — FBS classification correct on known FBS-vs-FCS games.
- `tests/test_crossvalidation.py` — **the check that matters most.** Aggregate
  play-level data up to a **team-season** and assert it matches CFBD's own
  `/stats/season` (e.g. Baylor 2025 rushing attempts). Silent join bugs are the
  likeliest way this project produces confident nonsense; this catches them.

  *Revised 2026-08-13 during planning.* This originally specified a **player**-season
  check against `/stats/player/season`. That is not achievable from `/plays` alone:
  `/plays` carries no structured player attribution — athlete names appear only inside
  the free-text `playText` field. Structured per-player data lives in `/plays/stats`,
  which silently truncates at 2000 rows and would require ~950 calls per season to pull
  safely, far beyond the monthly budget. Team-season validation exercises the same joins
  and catches the same class of bug at a fraction of the cost.
- Notebooks carry inline assertions on row counts and known values rather than test files.

No TDD on notebooks — exploration is the point there.

## Risks

| Risk | Mitigation |
|---|---|
| Pull burns budget, locks project out until Sept 1 | Pre-flight budget check + ledger + resumability |
| Silent truncation corrupts a dataset | 2000/100-row tripwire asserted on every response |
| FCS contamination skews over-expected models | Explicit classification column; filtering visible in notebooks |
| 2020 distorts stability analysis | `covid_season` flag; lesson uses it as a teaching case |
| pandas 3.0 breaks book code idioms | Flagged upfront; adaptations expected, not surprises |
| Scope (6 technique areas) stalls the project | Lessons built one at a time, gated on drill completion |
| Join bugs produce plausible-but-wrong results | Cross-validation against CFBD's own season endpoints |

## Out of scope

Web scraping (the book's chapter is unnecessary given an API), R and the book's R
column, live/in-game data (tier-gated), opponent-adjusted EPA via `/wepa/*`
(tier-gated — compute it manually if needed), and any modification to
`CFB_Victory_Model`, which has a hard weekly cron dependency.

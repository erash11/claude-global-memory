# Phase 3 readiness — 2026 weekly ingest

**Written:** 2026-09-10
**Status:** groundwork done, blocked on data

Phase 3 runs the pipeline weekly on the live 2026 season. The code is ready for
it. The data is not, and it is blocked on three separate things, not one.

`tests/test_seasons.py::test_2026_is_not_yet_runnable_and_the_reason_is_specific`
checks all three on every test run. **When it fails, Phase 3 can start.** That
is deliberate — a blocker nobody re-checks is a blocker everybody forgets.

---

## What is done

The season list used to be hardcoded as `(2024, 2025)` in three files: `run.py`,
`build_tables.py` and `build_alignment_tables.py`. Adding a season meant editing
all three and hoping none was missed, which produces a report short a season
without raising anything.

It is now derived once, in `src/playcalls/seasons.py`, from the charting files
actually present. A season becomes available by **dropping its CSV in the repo
root** — no code change.

The refactor was verified by hashing all 177 generated files before and after:
**byte-identical output.**

### The rule that keeps it safe

A season is usable only if its export carries the outcome columns:

```
Efficiency, aapff_RUNPASS, pff_DOWN, pff_DISTANCE,
pff_YARDSTOGOALLINE, pff_GAINLOSS
```

The 2021–2023 exports do not have them — eight columns, no down, no distance,
no gain, no field position. Globbing `*_All_Games.csv` and running would not
raise; it would produce three seasons of empty cells beside two real ones. The
header is checked before the file is parsed, and a rejected season is reported
with the columns it is missing rather than dropped silently.

### Running one season

```bash
PLAYCALLS_SEASONS=2025 .venv/bin/python run.py
```

Validated against what is on disk. A typo'd year raises rather than producing a
quietly empty report.

---

## The three blockers

### 1. No 2026 charting export — **yours**

The repo has `2021`–`2025_All_Games.csv`. There is no `2026_All_Games.csv`.

Export it from PFF the same way as 2025, drop it in the repo root, and the
pipeline picks it up with no code change. It must carry the outcome columns
above or it will be refused by name.

### 2. No 2026 CFBD play-by-play — **a pull in `CFB_Analytics_Lab`**

`CFB_Analytics_Lab/data/raw/plays/` holds `season=2019` through `season=2025`.
No 2026.

```bash
cd ~/DEV/CFB_Analytics_Lab
.venv/bin/python -m cfblab.pull plays --season 2026
```

That repo owns CFBD ingest and enforces the free-tier budget guard — 1,000 calls
a month, hard reset on the 1st. **This repo never calls the CFBD API.** As of
2026-09-09 there were 932 calls remaining.

Without this there is no EPA for 2026. Success rate and alignment would still
work; Gate 3 would fail.

### 3. No 2026 data in `pff.db` — **an ingest in `PFF_Data_Project`**

`pff.db` holds 2023, 2024 and 2025. It has no 2026 games at all. Re-verified
2026-09-10 against the DuckDB `games` table.

The 2026 week-1 Auburn pull exists, but as loose JSON in
`~/DEV/Football/PFF_Data_Project/data/week1_auburn/` — it was never ingested
into the database. `PFF_Data_Project` owns all PFF ingest; **this repo opens
`pff.db` read-only and must not ingest anything.**

**Path correction.** Earlier versions of this document wrote the repository as
`PFF_Data_Project/`. It actually lives at `~/DEV/Football/PFF_Data_Project/`.
`src/playcalls/pff.py` has always carried the correct absolute path; only this
document was wrong. `pff.db` is also a **DuckDB** file, not SQLite — opening it
with `sqlite3` gives "file is not a database".

Without this the Phase 1 join has nothing to join against, so nothing downstream
runs.

---

## Trap carried forward

`week1_auburn/` is the **2026** season, not 2025. Baylor plays Auburn in both.
This cost real time in Phase 1 — a phantom 23-play discrepancy — and it will cost
it again if a 2026 pull is compared against the 2025 chart. Every read filters on
season explicitly.

---

## Order of work once unblocked

1. Ingest 2026 into `pff.db` (in `PFF_Data_Project`).
2. Pull 2026 CFBD plays (in `CFB_Analytics_Lab`).
3. Drop `2026_All_Games.csv` in this repo root.
4. Add 2026's opponents to `cfbd.OPPONENT_TO_CFBD` — the map raises by name on
   an unmapped code, so this fails loudly rather than dropping games.
5. Run the pipeline. All three gates apply to 2026 exactly as they do to 2024
   and 2025, per season.

Step 4 is the only code change, and it is a dictionary entry per opponent.

---

## The weekly cadence — decided 2026-09-10

Everything above describes a full rebuild. A weekly run mid-season raised a
question this groundwork did not answer: does week *n* rebuild every season
from scratch, or append? And should a mid-season 2026 sit in the same tables
as two complete seasons, where a six-game sample would be read beside
thirteen-game ones?

**Decided in the Phase 5 spec, §6. Same pipeline, same tables, full rebuild,
with two requirements.**

1. **Every cross-season row carries a `games` column.** A six-game rate is
   never printed beside a thirteen-game rate without the reader seeing why
   they might differ.
2. **An in-progress season is labelled by its extent everywhere it appears** —
   "2026 (through week N)", never a bare "2026". In table headers, in prose,
   and in the provenance file.

A full rebuild rather than an append: the whole pipeline runs in well under a
minute, so there is no performance argument for the more fragile option, and
an append path would need its own correctness tests for a problem that does
not exist.

Phase 5 supplies a third requirement that was not obvious when this was
written. **Print the standard error beside every season mean, clustered by
game.** Between two *complete* seasons, no cut in Phase 5 separated by two
standard errors — not the overall figure, not early-down run. A six-game
season will be noisier still, and a weekly number quoted without its
uncertainty is the single most likely way this project produces a wrong
conclusion.

Clustered, not naive: plays inside one game share an opponent, a game plan
and a quarterback's day, and treating them as independent understates the
error in the direction that flatters a finding. Twelve games is a small
sample of games whatever the play count beside it says — and six is smaller.

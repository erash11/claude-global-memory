# Phase 4 — Alignment and Formation vs Outcome — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether Baylor's 2024→2025 offensive decline is explained by a shift in
alignment *mix* or by a drop in *efficacy* of the same alignments, and report the answer
honestly including a null result.

**Architecture:** One new pure module (`src/playcalls/alignment.py`) that assembles an
alignment-enriched play table from the Phase 1 parquet plus the widened charting CSVs plus
PFF `team_play`, normalises drifting vocabularies, and runs a three-term shift-share
decomposition parameterised by an outcome specification. Two new top-level scripts write
tables and the report. `charting.py` gains columns and nothing else.

**Tech Stack:** Python 3, pandas, duckdb (read-only), pytest. Interpreter is
`.venv/bin/python` in this worktree.

**Spec:** `docs/superpowers/specs/2026-09-09-playcalls-phase4-alignment-design.md`

## Global Constraints

- **Never `cd` to `/Users/kristinarash/DEV/PlayCalls_SuccessRate_EPA`.** Work only in
  `/Users/kristinarash/DEV/PlayCalls_SuccessRate_EPA/.worktrees/phase4-alignment`.
- **Do NOT edit** `analysis.py`, `build_tables.py`, `report.py`, `run.py`, `join.py`,
  `pff.py`, `unmatched.py`, `normalise.py`, `gamemap.py`, `build_report.py`,
  `build_artifact.py`, `CLAUDE.md`, `AGENTS.md`, or any existing test file. Phase 2 is
  editing several of these in parallel.
- **One permitted edit:** `src/playcalls/charting.py`'s `_COLUMNS` dict, additively only.
- **`play_id` is float64.** Always join through `analysis._play_key`. A `.astype(str)`
  gives `"5642403.0"` and matches zero rows.
- **PFF feeds name Baylor inconsistently.** `team_play` uses `offense`; Baylor is `TXBA`.
- **Coverage from `quarterback_charting` is dropbacks only** and must never be pooled with
  run-play `def_package`. Phase 4 avoids this by taking `defense_package` from `team_play`,
  which covers all plays.
- **`week1_auburn/` in PFF_Data_Project is the 2026 season.** Never widen a season filter.
- **2021–2023 have no outcome columns.** Nothing in Phase 4 touches them.
- `MIN_SAMPLE = 15` from `analysis.py` governs suppression in `rate_by` tables.
  Phase 4's own `LOW_N = 30` marks (does not drop) thin cells.
- `pff.db` is opened **read-only**. Never call the PFF API. Never read
  `PFF_Data_Project/.env`.
- Charting data is proprietary. No Artifact, no external service, no public destination.
- Run `.venv/bin/python -m pytest -q` before **every** commit. All 76 pre-existing tests
  must pass.
- Every commit message ends with exactly:

  ```
  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
  ```

---

## File structure

| File | Responsibility |
|---|---|
| `src/playcalls/charting.py` | **Modify.** `_COLUMNS` gains 10 alignment columns. Nothing else changes. |
| `src/playcalls/alignment.py` | **Create.** Everything Phase 4 computes: PFF alignment loading, chart re-attach, normalisers, the `Outcome` abstraction, the decomposition, the audit tables. Pure functions; no file I/O except reading `pff.db` through `pff.load_category`. |
| `build_alignment_tables.py` | **Create.** Top-level script. Assembles the table, writes every `outputs/tables/alignment_*.csv`. |
| `build_alignment_report.py` | **Create.** Top-level script. Reads the tables back off disk and renders `outputs/ALIGNMENT.md`. Rendering lives in `alignment.render_alignment_report(tables, provenance)` so it is testable without file I/O. |
| `tests/test_alignment.py` | **Create.** All Phase 4 tests. |

---

## Task 1: Widen the charting column selection

**Files:**
- Modify: `src/playcalls/charting.py` (the `_COLUMNS` dict only)
- Test: `tests/test_alignment.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `charting.load_season(path)` returns the existing columns plus
  `form_adjust`, `gen_mo`, `shifts`, `tempo`, `rb_align`, `te_alignment`,
  `front_adjust`, `stunt`, `pressure_call`, `hash_o` — all `str`, stripped.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_alignment.py
import pandas as pd
import pytest

from src.playcalls import charting

NEW_CHART_COLUMNS = (
    "form_adjust", "gen_mo", "shifts", "tempo", "rb_align",
    "te_alignment", "front_adjust", "stunt", "pressure_call", "hash_o",
)


@pytest.fixture(scope="module")
def chart_2024():
    return charting.load_season("2024_All_Games.csv")


@pytest.fixture(scope="module")
def chart_2025():
    return charting.load_season("2025_All_Games.csv")


def test_widened_columns_are_present_in_both_seasons(chart_2024, chart_2025):
    for column in NEW_CHART_COLUMNS:
        assert column in chart_2024.columns, column
        assert column in chart_2025.columns, column


def test_widening_did_not_disturb_the_existing_columns(chart_2025):
    """Phase 1's columns and row count must be untouched."""
    for column in ("efficiency", "explosive", "formation", "form_fam", "personnel",
                   "box_count", "season", "game_code", "play_no"):
        assert column in chart_2025.columns
    assert len(chart_2025) == 987


def test_rb_align_is_empty_in_2025_and_full_in_2024(chart_2024, chart_2025):
    """The spec excludes RB Align cross-year. If this ever flips, revisit that."""
    assert (chart_2024["rb_align"] != "").mean() > 0.8
    assert (chart_2025["rb_align"] != "").mean() == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: FAIL — `assert 'form_adjust' in chart_2024.columns`.

- [ ] **Step 3: Write minimal implementation**

In `src/playcalls/charting.py`, inside `_COLUMNS`, after the `"QB#": "qb",` entry, add:

```python
    # Phase 4 (alignment) additions. Additive only: nothing above changes.
    # Fill rates differ sharply by season - see the Phase 4 spec section 5 before
    # using any of these cross-year. RB Align, Front Adjust and Hash_O are carried
    # so the report can state *why* they are unusable, not because they are usable.
    "Form Adjust": "form_adjust",
    "Gen Mo": "gen_mo",
    "Shifts": "shifts",
    "Tempo": "tempo",
    "RB Align": "rb_align",
    "pff_TEALIGNMENT": "te_alignment",
    "Front Adjust": "front_adjust",
    "Stunt": "stunt",
    "Pressure": "pressure_call",
    "Hash_O": "hash_o",
```

- [ ] **Step 4: Run the full suite**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS, 76 pre-existing + 3 new.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/charting.py tests/test_alignment.py
git commit   # message body: what was added, why it is additive-only, and that
             # load_season is only ever called for 2024/2025 (run.py:26)
```

---

## Task 2: Load PFF alignment fields from `team_play`

**Files:**
- Create: `src/playcalls/alignment.py`
- Test: `tests/test_alignment.py`

**Interfaces:**
- Consumes: `pff.load_category(game_id, "team_play")`, `pff.BAYLOR_CODE`,
  `analysis._play_key`.
- Produces:
  - `alignment.PFF_ALIGNMENT_FIELDS: tuple[str, ...]`
  - `alignment.load_pff_alignment(game_ids: Iterable[str], db_path: str = pff.PFF_DB_PATH) -> pd.DataFrame`
    — one row per Baylor play, columns `_pid` plus every field in
    `PFF_ALIGNMENT_FIELDS`.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_alignment.py
from src.playcalls import alignment


@pytest.fixture(scope="module")
def joined():
    return pd.read_parquet("outputs/joined_plays_enriched.parquet")


@pytest.fixture(scope="module")
def pff_alignment(joined):
    return alignment.load_pff_alignment(sorted(joined["pff_game_id"].dropna().unique()))


def test_pff_alignment_carries_the_documented_fields(pff_alignment):
    for field in alignment.PFF_ALIGNMENT_FIELDS:
        assert field in pff_alignment.columns, field
    assert "_pid" in pff_alignment.columns


def test_pff_alignment_is_one_row_per_play(pff_alignment):
    assert pff_alignment["_pid"].is_unique
    assert len(pff_alignment) > 2000


def test_pff_alignment_is_baylor_offence_only(pff_alignment):
    assert (pff_alignment["offense"] == "TXBA").all()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: FAIL — `ModuleNotFoundError` / `AttributeError: load_pff_alignment`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/playcalls/alignment.py
"""Phase 4 - alignment and formation versus play-call outcome.

Everything here is a pure function over frames. The only I/O is reading
PFF_Data_Project's DuckDB through src.playcalls.pff, which is read-only by
contract.

Two PFF fields used here are undocumented upstream and were resolved
empirically; see the Phase 4 design spec, sections 3 and 4:

  offense_package             WR-FB-RB-TE counts of the five non-OL, non-QB players
  mofo_coverage_played_shown  character 1 is SHOWN, character 2 is PLAYED - which
                              is the reverse of the word order in the field name
"""

from __future__ import annotations

from typing import Callable, Iterable, NamedTuple

import pandas as pd

from src.playcalls import pff
from src.playcalls.analysis import _play_key

# Fields pulled out of team_play. Every one is present on Baylor rows in both
# 2024 and 2025; the spec's section 5.4 records each one's fill rate and verdict.
PFF_ALIGNMENT_FIELDS = (
    "offense", "offense_package", "offense_players", "defense_package",
    "ball_snapped_from", "mofo_coverage_played_shown", "motion", "shift",
    "play_action", "pistol", "option", "run_concept_1", "run_concept_2",
    "poa_actual", "shotgun", "no_huddle",
)


def load_pff_alignment(
    game_ids: Iterable[str], db_path: str = pff.PFF_DB_PATH
) -> pd.DataFrame:
    """Baylor-offence alignment fields from team_play, one row per play.

    team_play holds both teams' rows for a game and they collide on play_id, so
    the offense filter is not optional.
    """
    frames = []
    for game_id in game_ids:
        team_play = pff.load_category(str(game_id), "team_play", db_path)
        if team_play.empty:
            continue
        baylor = team_play[team_play["offense"] == pff.BAYLOR_CODE].copy()
        if baylor.empty:
            continue
        for field in PFF_ALIGNMENT_FIELDS:
            if field not in baylor.columns:
                baylor[field] = pd.NA
        keep = baylor[["play_id", *PFF_ALIGNMENT_FIELDS]].copy()
        keep["pff_game_id"] = str(game_id)
        frames.append(keep)

    if not frames:
        return pd.DataFrame(columns=["_pid", "pff_game_id", *PFF_ALIGNMENT_FIELDS])

    result = pd.concat(frames, ignore_index=True)
    # float play_id would stringify as "5642403.0" and match nothing.
    result["_pid"] = _play_key(result["play_id"])
    return result.drop(columns="play_id").drop_duplicates("_pid").reset_index(drop=True)
```

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/alignment.py tests/test_alignment.py
git commit   # body: why the offense filter is load-bearing, why _play_key is used
```

---

## Task 3: Assemble the alignment play table

**Files:**
- Modify: `src/playcalls/alignment.py`
- Test: `tests/test_alignment.py`

**Interfaces:**
- Consumes: `load_pff_alignment`, `charting.load_season`.
- Produces:
  - `alignment.attach_chart_columns(joined: pd.DataFrame, charts: dict[int, pd.DataFrame]) -> pd.DataFrame`
    — merges the widened chart columns onto the joined table on
    `(season, game_code, play_no)`; raises `ValueError` if the key is not unique on
    either side or if any joined row fails to match.
  - `alignment.attach_pff_alignment(df: pd.DataFrame, pff_alignment: pd.DataFrame) -> pd.DataFrame`
    — left-merges on `_play_key(play_id)`; PFF columns are suffixed `_pff` where they
    collide with an existing column.
  - `alignment.build_alignment_table(joined, charts, pff_alignment) -> pd.DataFrame`
    — both of the above plus the derived columns from Task 4.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_alignment.py

@pytest.fixture(scope="module")
def charts(chart_2024, chart_2025):
    return {2024: chart_2024, 2025: chart_2025}


def test_chart_reattach_is_one_to_one_and_complete(joined, charts):
    result = alignment.attach_chart_columns(joined, charts)
    assert len(result) == len(joined) == 1935
    for column in NEW_CHART_COLUMNS:
        assert column in result.columns
    # rb_align is 100% filled in 2024; if the merge silently missed rows it would not be
    assert (result.loc[result.season == 2024, "rb_align"] != "").mean() > 0.8


def test_chart_reattach_rejects_a_duplicated_key(joined, charts):
    broken = {2024: pd.concat([charts[2024], charts[2024].head(1)]), 2025: charts[2025]}
    with pytest.raises(ValueError, match="not unique"):
        alignment.attach_chart_columns(joined, broken)


def test_chart_reattach_rejects_an_unmatched_row(joined, charts):
    broken = {2024: charts[2024].iloc[1:].copy(), 2025: charts[2025]}
    with pytest.raises(ValueError, match="unmatched"):
        alignment.attach_chart_columns(joined, broken)


def test_naive_play_id_string_join_matches_nothing(joined, pff_alignment):
    """CLAUDE.md trap 1, pinned as a test so it cannot silently regress."""
    naive = joined["play_id"].astype(str)
    assert naive.isin(set(pff_alignment["_pid"])).sum() == 0


def test_pff_alignment_attach_matches_at_least_98_percent(joined, pff_alignment):
    result = alignment.attach_pff_alignment(joined, pff_alignment)
    assert result["ball_snapped_from"].notna().mean() >= 0.98
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: FAIL — `AttributeError: attach_chart_columns`.

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/playcalls/alignment.py

CHART_KEY = ("season", "game_code", "play_no")

# Columns the Phase 1 parquet already carries; re-attaching them would create
# duplicate _x/_y pairs, so they are dropped from the chart side before merging.
def _chart_extra_columns(chart: pd.DataFrame, joined: pd.DataFrame) -> list[str]:
    return [c for c in chart.columns if c not in joined.columns or c in CHART_KEY]


def attach_chart_columns(
    joined: pd.DataFrame, charts: dict[int, pd.DataFrame]
) -> pd.DataFrame:
    """Merge the widened charting columns onto the Phase 1 joined table.

    The Phase 1 parquet predates the widening, so the new columns are not in it.
    The merge is asserted rather than trusted: a silent many-to-one here would
    inflate every denominator downstream.
    """
    chart = pd.concat(
        [charts[season] for season in sorted(charts)], ignore_index=True
    )
    extra = _chart_extra_columns(chart, joined)
    chart = chart[extra].copy()

    if chart.duplicated(list(CHART_KEY)).any():
        raise ValueError("charting key (season, game_code, play_no) is not unique")
    if joined.duplicated(list(CHART_KEY)).any():
        raise ValueError("joined key (season, game_code, play_no) is not unique")

    result = joined.merge(chart, on=list(CHART_KEY), how="left", validate="one_to_one")
    if len(result) != len(joined):
        raise ValueError(f"chart merge changed row count: {len(joined)} -> {len(result)}")

    probe = extra[-1]
    unmatched = int(result[probe].isna().sum())
    if unmatched:
        raise ValueError(f"chart merge left {unmatched} unmatched joined rows")
    return result


def attach_pff_alignment(
    df: pd.DataFrame, pff_alignment: pd.DataFrame
) -> pd.DataFrame:
    """Left-merge PFF alignment fields onto the play table on the normalised play id."""
    result = df.copy()
    result["_pid"] = _play_key(result["play_id"])
    right = pff_alignment.drop(columns=[c for c in ("pff_game_id",) if c in pff_alignment])
    overlapping = [c for c in right.columns if c in result.columns and c != "_pid"]
    right = right.rename(columns={c: f"{c}_pff" for c in overlapping})
    return result.merge(right, on="_pid", how="left").drop(columns="_pid")
```

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/alignment.py tests/test_alignment.py
git commit   # body: why the merge is asserted; the naive-astype(str) regression pin
```

---

## Task 4: Normalisers and derived alignment columns

**Files:**
- Modify: `src/playcalls/alignment.py`
- Test: `tests/test_alignment.py`

**Interfaces:**
- Produces:
  - `alignment.FORM_FAM_SYNONYMS: dict[str, str]`
  - `alignment.normalise_personnel(series) -> pd.Series`
  - `alignment.normalise_form_fam(series) -> pd.Series`
  - `alignment.decode_offense_package(series) -> pd.DataFrame` with columns
    `wr, fb, rb, te, personnel_pff, package_note`
  - `alignment.split_mofo(series) -> pd.DataFrame` with columns
    `mofo_shown, mofo_played, mofo_rotated`
  - `alignment.box_band(series) -> pd.Series` — `"<=5"`, `"6"`, `"7"`, `">=8"`
  - `alignment.add_derived(df) -> pd.DataFrame` — adds `personnel_base`,
    `form_fam_norm`, `motion_used`, `gen_mo_family`, `form_adjust_used`,
    `tempo_used`, `hash`, `shift_used`, `play_action_used`, `def_package_norm`,
    `box_count_band`, `mofo_shown`, `mofo_played`, `mofo_rotated`, `te_align_norm`,
    `run_concept`, `poa`
  - `alignment.build_alignment_table(joined, charts, pff_alignment) -> pd.DataFrame`

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_alignment.py

def test_personnel_normalisation_folds_the_2025_subdivisions():
    s = pd.Series(["11", "12", "12S", "12B", "12W", "10", "13", "DAL", "T", ""])
    out = alignment.normalise_personnel(s).tolist()
    assert out == ["11", "12", "12", "12", "12", "10", "13", "OTHER", "OTHER", "OTHER"]


def test_form_fam_normalisation_folds_the_label_change():
    s = pd.Series(["UNBALANCED", "UNBAL", " unbal ", "DUO", ""])
    out = alignment.normalise_form_fam(s).tolist()
    assert out == ["UNBAL", "UNBAL", "UNBAL", "DUO", "OTHER"]


def test_offense_package_decodes_to_wr_fb_rb_te():
    s = pd.Series(["3-0-1-1", "2-0-1-2", "4-0-1-0", "1-0-1-3",
                   "2-1-1-0 (*)", "2-0-1-1 (+Q)", "X-X-X-X", None])
    out = alignment.decode_offense_package(s)
    assert out.loc[0, ["wr", "fb", "rb", "te"]].tolist() == [3, 0, 1, 1]
    assert out.loc[0, "personnel_pff"] == "11"
    assert out.loc[1, "personnel_pff"] == "12"
    assert out.loc[2, "personnel_pff"] == "10"
    assert out.loc[3, "personnel_pff"] == "13"
    # a starred value is short a player; it is not silently coerced
    assert out.loc[4, "package_note"] == "unidentified"
    assert out.loc[4, "personnel_pff"] == "OTHER"
    assert out.loc[5, "package_note"] == "extra_qb"
    assert out.loc[6, "personnel_pff"] == "OTHER"
    assert out.loc[7, "personnel_pff"] == "OTHER"


def test_mofo_splits_shown_from_played():
    """Character 1 is SHOWN, character 2 is PLAYED - resolved in spec section 4."""
    out = alignment.split_mofo(pd.Series(["OO", "CC", "OC", "CO", None]))
    assert out["mofo_shown"].tolist()[:4] == ["O", "C", "O", "C"]
    assert out["mofo_played"].tolist()[:4] == ["O", "C", "C", "O"]
    assert out["mofo_rotated"].tolist()[:4] == [False, False, True, True]
    assert pd.isna(out.loc[4, "mofo_shown"])


def test_pff_motion_null_means_no_motion_not_missing():
    """PFF writes 1.0 or null for motion. Averaging the non-nulls gives 100%."""
    df = pd.DataFrame({"motion_pff": [1.0, None, None, 1.0]})
    assert alignment._binary_from_pff(df["motion_pff"]).tolist() == [True, False, False, True]


def test_box_band_buckets_the_tails():
    s = pd.Series([4, 5, 6, 7, 8, 9])
    assert alignment.box_band(s).tolist() == ["<=5", "<=5", "6", "7", ">=8", ">=8"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: FAIL — `AttributeError: normalise_personnel`.

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/playcalls/alignment.py
import re

OTHER = "OTHER"

# Observed label drift between the two seasons. Derived from the label sets, not
# from memory: 2024 writes UNBALANCED, 2025 writes UNBAL, and they are the same
# family. Every entry is published in alignment_form_fam_crosswalk.csv with counts.
FORM_FAM_SYNONYMS = {
    "UNBALANCED": "UNBAL",
}

_PERSONNEL_BASE = re.compile(r"^(\d{2})")


def normalise_personnel(series: pd.Series) -> pd.Series:
    """Fold 2025's subdivided personnel labels back to the base RB-TE code.

    2024 charts four labels; 2025 charts eleven because it splits twelve
    personnel into 12S/12B/12W/12M/12P/12J. Left alone, a pure relabelling would
    read as a mix shift.
    """
    cleaned = series.fillna("").astype(str).str.strip().str.upper()
    base = cleaned.str.extract(_PERSONNEL_BASE, expand=False)
    return base.fillna(OTHER)


def normalise_form_fam(series: pd.Series) -> pd.Series:
    cleaned = series.fillna("").astype(str).str.strip().str.upper()
    cleaned = cleaned.replace(FORM_FAM_SYNONYMS)
    return cleaned.replace({"": OTHER})


_PACKAGE_CORE = re.compile(r"^(\d+)-(\d+)-(\d+)-(\d+)")


def decode_offense_package(series: pd.Series) -> pd.DataFrame:
    """Decode PFF's undocumented offense_package into WR/FB/RB/TE counts.

    Resolved empirically - see the Phase 4 spec section 3. Slot order is
    WR-FB-RB-TE over the five non-OL, non-QB players. A "(*)" suffix means that
    many players PFF could not place; "(+Q)" means a second quarterback took a
    skill slot; "X-X-X-X" means the personnel was not identified. None of those
    is coerced into a personnel code.
    """
    raw = series.fillna("").astype(str).str.strip()
    note = pd.Series("", index=raw.index, dtype=object)
    note = note.mask(raw.str.contains(r"\(\*+\)", regex=True), "unidentified")
    note = note.mask(raw.str.contains(r"\(\+Q\)", regex=True), "extra_qb")
    note = note.mask(raw.str.upper().str.startswith("X-"), "unidentified_play")
    note = note.mask(raw.eq(""), "missing")

    parts = raw.str.extract(_PACKAGE_CORE)
    parts.columns = ["wr", "fb", "rb", "te"]
    parts = parts.apply(pd.to_numeric, errors="coerce")

    clean = note.eq("") & parts.notna().all(axis=1)
    personnel = pd.Series(OTHER, index=raw.index, dtype=object)
    personnel = personnel.mask(
        clean,
        parts["rb"].fillna(0).astype("Int64").astype(str)
        + parts["te"].fillna(0).astype("Int64").astype(str),
    )

    out = parts.copy()
    out["personnel_pff"] = personnel
    out["package_note"] = note
    return out


def split_mofo(series: pd.Series) -> pd.DataFrame:
    """Split mofo_coverage_played_shown into the shown and played looks.

    Character 1 is what the defence SHOWED before the snap; character 2 is what
    it PLAYED. That is the reverse of the word order in the field name, and it is
    what the evidence says - see the Phase 4 spec section 4.
    """
    raw = series.where(series.notna()).astype("object")
    text = raw.fillna("").astype(str).str.strip().str.upper()
    valid = text.str.fullmatch(r"[OC]{2}").fillna(False)

    shown = text.str[0].where(valid)
    played = text.str[1].where(valid)
    rotated = (shown != played).where(valid)
    return pd.DataFrame(
        {"mofo_shown": shown, "mofo_played": played, "mofo_rotated": rotated}
    )


def _binary_from_pff(series: pd.Series) -> pd.Series:
    """PFF writes 1.0 for yes and either 0.0 or null for no, depending on field.

    Averaging only the non-nulls on a null-for-no field (motion, option) reports
    100%. Null is therefore read as False for every field this module treats as a
    binary; fields where null genuinely means 'not applicable' are not routed
    through here.
    """
    return pd.to_numeric(series, errors="coerce").fillna(0.0).eq(1.0)


def box_band(series: pd.Series) -> pd.Series:
    numbers = pd.to_numeric(series, errors="coerce")
    return pd.Series(
        [
            "<=5" if n <= 5 else "6" if n == 6 else "7" if n == 7 else ">=8"
            if pd.notna(n)
            else OTHER
            for n in numbers
        ],
        index=series.index,
        dtype=object,
    )


def _nonblank(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().ne("")


def add_derived(df: pd.DataFrame) -> pd.DataFrame:
    """Add every alignment dimension the decomposition groups on."""
    out = df.copy()

    out["personnel_base"] = normalise_personnel(out["personnel"])
    out["form_fam_norm"] = normalise_form_fam(out["form_fam"])

    # Chart Motion is 31.5% / 31.1% filled; blank means no motion was charted.
    out["motion_used"] = _nonblank(out["motion"])
    out["gen_mo_family"] = out["gen_mo"].fillna("").astype(str).str.strip().str.upper()
    out["gen_mo_family"] = out["gen_mo_family"].replace({"": "NONE"})
    out["form_adjust_used"] = _nonblank(out["form_adjust"])
    out["tempo_used"] = _nonblank(out["tempo"])
    out["te_align_norm"] = out["te_alignment"].fillna("").astype(str).str.strip()
    out["te_align_norm"] = out["te_align_norm"].replace({"": "UNCHARTED"})

    out["hash"] = out["ball_snapped_from"].fillna(OTHER).astype(str).str.strip()
    out["shift_used"] = _binary_from_pff(out["shift"])
    out["play_action_used"] = _binary_from_pff(
        out["play_action_pff"] if "play_action_pff" in out else out["play_action"]
    )
    out["def_package_norm"] = (
        out["defense_package"].fillna(OTHER).astype(str).str.strip().replace({"": OTHER})
    )
    out["box_count_band"] = box_band(out["box_count"])
    out = pd.concat([out, split_mofo(out["mofo_coverage_played_shown"])], axis=1)
    out = pd.concat([out, decode_offense_package(out["offense_package"])], axis=1)

    out["run_concept"] = (
        out["run_concept_1"].fillna("").astype(str).str.strip().replace({"": "NONE"})
    )
    out["poa"] = out["poa_actual"].fillna("").astype(str).str.strip().replace({"": "NONE"})
    return out


def build_alignment_table(
    joined: pd.DataFrame,
    charts: dict[int, pd.DataFrame],
    pff_alignment: pd.DataFrame,
) -> pd.DataFrame:
    """The Phase 1 joined table, widened with chart and PFF alignment fields."""
    result = attach_chart_columns(joined, charts)
    result = attach_pff_alignment(result, pff_alignment)
    return add_derived(result)
```

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/alignment.py tests/test_alignment.py
git commit   # body: the vocabulary drift each normaliser fixes and why a
             # relabelling would otherwise read as a mix shift
```

---

## Task 5: The outcome abstraction

**Files:**
- Modify: `src/playcalls/alignment.py`
- Test: `tests/test_alignment.py`

**Interfaces:**
- Produces:
  - `alignment.Outcome` — `NamedTuple("Outcome", [("name", str), ("series", Callable[[pd.DataFrame], pd.Series])])`
  - `alignment.OUTCOME_SUCCESS`, `alignment.OUTCOME_EXPLOSIVE`
  - `alignment.group_rates(df, dimension, outcome=OUTCOME_SUCCESS) -> pd.DataFrame`
    with columns `[dimension, n, rate]`, `n` = count of non-null outcome values.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_alignment.py
from src.playcalls import analysis


def test_success_outcome_grades_exactly_like_charting():
    df = pd.DataFrame({"efficiency": ["Y", "N", "X", "", "Y"]})
    values = alignment.OUTCOME_SUCCESS.series(df)
    assert values.tolist()[:2] == [1.0, 0.0]
    assert values.isna().tolist() == [False, False, True, True, False]
    assert values.mean() == pytest.approx(2 / 3)


def test_group_rates_match_rate_by_on_real_data(alignment_table):
    ours = alignment.group_rates(alignment_table, "form_fam_norm")
    theirs = analysis.rate_by(alignment_table, "form_fam_norm", min_sample=1)
    merged = ours.merge(theirs, on="form_fam_norm")
    assert len(merged) == len(theirs)
    pd.testing.assert_series_equal(
        merged["rate"].round(4), merged["success_rate"].round(4),
        check_names=False,
    )
    pd.testing.assert_series_equal(
        merged["n"], merged["graded"], check_names=False, check_dtype=False,
    )


def test_explosive_outcome_runs_through_the_same_path(alignment_table):
    ours = alignment.group_rates(alignment_table, "form_fam_norm",
                                 outcome=alignment.OUTCOME_EXPLOSIVE)
    theirs = analysis.rate_by(alignment_table, "form_fam_norm", min_sample=1)
    merged = ours.merge(theirs, on="form_fam_norm")
    pd.testing.assert_series_equal(
        merged["rate"].round(4), merged["explosive_rate"].round(4), check_names=False,
    )


def test_a_plain_numeric_outcome_works(alignment_table):
    """Phase 2 adds an epa column. It must drop in with no rewrite."""
    df = alignment_table.copy()
    df["fake_epa"] = df["gain"].astype(float)
    outcome = alignment.Outcome("fake_epa", lambda d: d["fake_epa"])
    out = alignment.group_rates(df, "form_fam_norm", outcome=outcome)
    expected = df.groupby("form_fam_norm")["fake_epa"].mean().sort_index()
    got = out.set_index("form_fam_norm")["rate"].sort_index()
    pd.testing.assert_series_equal(got, expected, check_names=False)
```

Add the shared fixture near the top of the test file:

```python
@pytest.fixture(scope="module")
def alignment_table(joined, charts, pff_alignment):
    return alignment.build_alignment_table(joined, charts, pff_alignment)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: FAIL — `AttributeError: OUTCOME_SUCCESS`.

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/playcalls/alignment.py
from src.playcalls.charting import SUCCESS_RATE_EXCLUDED

LOW_N = 30  # cells thinner than this are marked, never used to carry a claim


class Outcome(NamedTuple):
    """A per-row numeric outcome, so the same code serves success rate and EPA.

    series() returns one float per row; NaN means the row is not graded for this
    outcome and is excluded from both numerator and denominator. Group rate is
    the mean of the non-null values; group weight is their count. For success
    rate that is exactly successes/graded, which a test pins against rate_by.
    """

    name: str
    series: Callable[[pd.DataFrame], pd.Series]


def _success_series(df: pd.DataFrame) -> pd.Series:
    efficiency = df["efficiency"].fillna("").astype(str).str.strip()
    graded = ~efficiency.isin(SUCCESS_RATE_EXCLUDED)
    return efficiency.eq("Y").astype(float).where(graded)


def _explosive_series(df: pd.DataFrame) -> pd.Series:
    # EXPL is Y or blank; blank means not explosive, so every play counts.
    return df["explosive"].astype(bool).astype(float)


OUTCOME_SUCCESS = Outcome("success_rate", _success_series)
OUTCOME_EXPLOSIVE = Outcome("explosive_rate", _explosive_series)


def group_rates(
    df: pd.DataFrame, dimension: str, outcome: Outcome = OUTCOME_SUCCESS
) -> pd.DataFrame:
    """Rate and weight for one grouping dimension. No suppression: the
    decomposition needs every group, and thin ones are marked instead."""
    working = df.copy()
    working["_value"] = outcome.series(working)
    grouped = (
        working.groupby(dimension, dropna=False)["_value"]
        .agg(n="count", rate="mean")
        .reset_index()
    )
    grouped["low_n"] = grouped["n"] < LOW_N
    return grouped
```

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/alignment.py tests/test_alignment.py
git commit   # body: why outcome is a parameter, and that the rate_by
             # equivalence test is what catches a silent divergence
```

---

## Task 6: The three-term decomposition

**Files:**
- Modify: `src/playcalls/alignment.py`
- Test: `tests/test_alignment.py`

**Interfaces:**
- Produces:
  - `alignment.apply_other_rule(df, dimension, outcome=OUTCOME_SUCCESS, floor=LOW_N) -> pd.Series`
    — the grouped labels with rare ones folded to `OTHER`; a label survives only
    if it has at least `floor` non-null outcome rows in **both** seasons.
  - `alignment.decompose(df, dimension, outcome=OUTCOME_SUCCESS, base=2024, comparison=2025) -> tuple[pd.DataFrame, dict]`
    — `(per_group_detail, summary_dict)`. Summary keys: `dimension`, `outcome`,
    `n_2024`, `n_2025`, `rate_2024`, `rate_2025`, `delta`, `mix`, `efficacy`,
    `interaction`, `other_share`, `groups`.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_alignment.py
import itertools

SUBSETS = {
    "all_plays": lambda d: d,
    "early_downs": lambda d: d[d.early_down],
    "early_down_runs": lambda d: d[d.early_down & d.run_pass.eq("R")],
    "runs": lambda d: d[d.run_pass.eq("R")],
}

DIMENSIONS = (
    "personnel_base", "form_fam_norm", "motion_used", "gen_mo_family",
    "form_adjust_used", "tempo_used", "hash", "shift_used", "play_action_used",
    "def_package_norm", "box_count_band", "mofo_shown", "mofo_rotated",
)


def test_decomposition_terms_sum_to_delta_on_synthetic_data():
    df = pd.DataFrame({
        "season": [2024] * 6 + [2025] * 6,
        "look": ["A", "A", "A", "B", "B", "B", "A", "A", "B", "B", "B", "B"],
        "efficiency": ["Y", "Y", "N", "Y", "N", "N", "Y", "N", "Y", "N", "N", "N"],
    })
    detail, summary = alignment.decompose(df, "look")
    assert summary["delta"] == pytest.approx(
        summary["mix"] + summary["efficacy"] + summary["interaction"], abs=1e-12
    )


def test_decomposition_terms_sum_to_delta_on_every_real_cut(alignment_table):
    for dimension, (name, subset) in itertools.product(DIMENSIONS, SUBSETS.items()):
        frame = subset(alignment_table)
        detail, summary = alignment.decompose(frame, dimension)
        assert summary["delta"] == pytest.approx(
            summary["mix"] + summary["efficacy"] + summary["interaction"], abs=1e-9
        ), f"{dimension}/{name}"


def test_decomposition_reproduces_the_phase_1_headline(alignment_table):
    """Whatever the split, the total change must be the published 57.4 -> 49.5."""
    _, summary = alignment.decompose(alignment_table, "form_fam_norm")
    assert summary["rate_2024"] == pytest.approx(0.5744, abs=0.0005)
    assert summary["rate_2025"] == pytest.approx(0.4949, abs=0.0005)


def test_every_decomposition_group_exists_in_both_seasons(alignment_table):
    for dimension in DIMENSIONS:
        detail, _ = alignment.decompose(alignment_table, dimension)
        assert (detail["n_2024"] > 0).all(), dimension
        assert (detail["n_2025"] > 0).all(), dimension


def test_other_rule_folds_labels_thin_in_either_season():
    df = pd.DataFrame({
        "season": [2024] * 40 + [2025] * 40,
        "look": ["A"] * 35 + ["B"] * 5 + ["A"] * 35 + ["B"] * 5,
        "efficiency": ["Y"] * 80,
    })
    labels = alignment.apply_other_rule(df, "look", floor=30)
    assert set(labels.unique()) == {"A", "OTHER"}


def test_decomposition_works_with_a_numeric_outcome(alignment_table):
    df = alignment_table.copy()
    df["fake_epa"] = df["gain"].astype(float)
    outcome = alignment.Outcome("fake_epa", lambda d: d["fake_epa"])
    _, summary = alignment.decompose(df, "form_fam_norm", outcome=outcome)
    assert summary["delta"] == pytest.approx(
        summary["mix"] + summary["efficacy"] + summary["interaction"], abs=1e-9
    )
    assert summary["outcome"] == "fake_epa"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: FAIL — `AttributeError: decompose`.

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/playcalls/alignment.py

BASE_SEASON = 2024
COMPARISON_SEASON = 2025


def apply_other_rule(
    df: pd.DataFrame,
    dimension: str,
    outcome: Outcome = OUTCOME_SUCCESS,
    floor: int = LOW_N,
    base: int = BASE_SEASON,
    comparison: int = COMPARISON_SEASON,
) -> pd.Series:
    """Fold labels that are thin in either season into OTHER.

    Two jobs at once. It guarantees every named group clears the low-n bar, and
    it guarantees every group exists in both seasons, which the decomposition
    arithmetic requires - a group present in only one year has no counterpart
    rate to difference against.
    """
    working = df.copy()
    working["_value"] = outcome.series(working)
    counts = (
        working.dropna(subset=["_value"])
        .groupby([dimension, "season"])
        .size()
        .unstack(fill_value=0)
    )
    for season in (base, comparison):
        if season not in counts.columns:
            counts[season] = 0
    keep = set(counts.index[(counts[base] >= floor) & (counts[comparison] >= floor)])
    labels = working[dimension].astype(object)
    return labels.where(labels.isin(keep), OTHER)


def decompose(
    df: pd.DataFrame,
    dimension: str,
    outcome: Outcome = OUTCOME_SUCCESS,
    base: int = BASE_SEASON,
    comparison: int = COMPARISON_SEASON,
    floor: int = LOW_N,
) -> tuple[pd.DataFrame, dict]:
    """Split the base-to-comparison change into mix, efficacy and interaction.

        delta = sum (p1 - p0) * r0        mix        - the weights moved
              + sum p0 * (r1 - r0)        efficacy   - the rates moved
              + sum (p1 - p0) * (r1 - r0) interaction

    All three are reported. The two-term Oaxaca forms fold the interaction into
    whichever term is evaluated at year-1 weights, which flatters whichever story
    the analyst already believes. These three sum to delta exactly, and a test
    asserts it.
    """
    working = df.copy()
    working["_group"] = apply_other_rule(
        working, dimension, outcome=outcome, floor=floor, base=base, comparison=comparison
    )
    working["_value"] = outcome.series(working)
    working = working.dropna(subset=["_value"])

    pivot = (
        working.groupby(["_group", "season"])["_value"]
        .agg(["count", "mean"])
        .unstack("season")
    )
    for season in (base, comparison):
        for stat in ("count", "mean"):
            if (stat, season) not in pivot.columns:
                pivot[(stat, season)] = 0.0 if stat == "count" else float("nan")

    detail = pd.DataFrame({
        "group": pivot.index.astype(str),
        f"n_{base}": pivot[("count", base)].fillna(0).astype(int).to_numpy(),
        f"n_{comparison}": pivot[("count", comparison)].fillna(0).astype(int).to_numpy(),
        f"rate_{base}": pivot[("mean", base)].to_numpy(),
        f"rate_{comparison}": pivot[("mean", comparison)].to_numpy(),
    })

    total_base = detail[f"n_{base}"].sum()
    total_comparison = detail[f"n_{comparison}"].sum()
    detail[f"share_{base}"] = detail[f"n_{base}"] / total_base
    detail[f"share_{comparison}"] = detail[f"n_{comparison}"] / total_comparison

    # A group can be empty in one season only if the OTHER rule was bypassed by a
    # caller-supplied floor; rate then has no counterpart, so treat it as the
    # season's own rate, which contributes zero to the efficacy term.
    r0 = detail[f"rate_{base}"].fillna(detail[f"rate_{comparison}"]).fillna(0.0)
    r1 = detail[f"rate_{comparison}"].fillna(detail[f"rate_{base}"]).fillna(0.0)
    p0 = detail[f"share_{base}"].fillna(0.0)
    p1 = detail[f"share_{comparison}"].fillna(0.0)

    detail["mix"] = (p1 - p0) * r0
    detail["efficacy"] = p0 * (r1 - r0)
    detail["interaction"] = (p1 - p0) * (r1 - r0)
    detail["low_n"] = (detail[f"n_{base}"] < LOW_N) | (detail[f"n_{comparison}"] < LOW_N)

    rate_base = float((p0 * r0).sum())
    rate_comparison = float((p1 * r1).sum())
    other = detail[detail["group"] == OTHER]
    other_share = float(other[f"share_{comparison}"].sum()) if not other.empty else 0.0

    summary = {
        "dimension": dimension,
        "outcome": outcome.name,
        f"n_{base}": int(total_base),
        f"n_{comparison}": int(total_comparison),
        f"rate_{base}": rate_base,
        f"rate_{comparison}": rate_comparison,
        "delta": rate_comparison - rate_base,
        "mix": float(detail["mix"].sum()),
        "efficacy": float(detail["efficacy"].sum()),
        "interaction": float(detail["interaction"].sum()),
        "other_share": other_share,
        "groups": int(len(detail)),
    }
    return detail.reset_index(drop=True), summary
```

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/alignment.py tests/test_alignment.py
git commit   # body: the three-term identity, why all three are reported,
             # and what the OTHER rule buys
```

---

## Task 7: Evidence and audit tables

**Files:**
- Modify: `src/playcalls/alignment.py`
- Test: `tests/test_alignment.py`

**Interfaces:**
- Produces:
  - `alignment.column_audit(charts, aligned) -> pd.DataFrame` — columns
    `source, column, fill_2024, fill_2025, distinct_2024, distinct_2025, verdict, reason`
  - `alignment.offense_package_crosswalk(aligned) -> pd.DataFrame` — columns
    `offense_package, personnel, plays`
  - `alignment.mofo_resolution(aligned) -> pd.DataFrame` — columns
    `character, agrees, compared, agreement_rate`
  - `alignment.form_fam_crosswalk(aligned) -> pd.DataFrame` and
    `alignment.personnel_crosswalk(aligned) -> pd.DataFrame` — columns
    `raw_label, normalised, season, plays`
  - `alignment.source_agreement(aligned) -> pd.DataFrame` — columns
    `comparison, agree, compared, agreement_rate`

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_alignment.py

def test_mofo_resolution_favours_character_two_as_played(alignment_table):
    """The evidence behind spec section 4, pinned so a data refresh cannot
    silently invert the conclusion the report is built on."""
    out = alignment.mofo_resolution(alignment_table).set_index("character")
    assert out.loc["played (char 2)", "agreement_rate"] > 0.85
    assert out.loc["shown (char 1)", "agreement_rate"] < 0.75


def test_offense_package_crosswalk_shows_the_documented_mapping(alignment_table):
    out = alignment.offense_package_crosswalk(alignment_table)
    top = out.sort_values("plays", ascending=False).iloc[0]
    assert top["offense_package"] == "3-0-1-1"
    assert top["personnel"] == "11"


def test_source_agreement_confirms_the_two_def_package_feeds_match(alignment_table):
    out = alignment.source_agreement(alignment_table).set_index("comparison")
    row = out.loc["def_package (rushing) vs defense_package (team_play)"]
    assert row["agreement_rate"] == pytest.approx(1.0)


def test_column_audit_flags_the_dead_2025_columns(alignment_table, charts):
    out = alignment.column_audit(charts, alignment_table).set_index("column")
    for column in ("RB Align", "Front"):
        assert out.loc[column, "fill_2025"] == pytest.approx(0.0)
        assert out.loc[column, "verdict"] == "exclude"
    assert out.loc["Hash_O", "verdict"] == "exclude"
    assert out.loc["ball_snapped_from", "verdict"] == "use"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: FAIL — `AttributeError: mofo_resolution`.

- [ ] **Step 3: Write minimal implementation**

Implement each function as a straightforward aggregation. The audit's verdict/reason
pairs come from the spec's §5 tables and are held in a module-level constant
`COLUMN_VERDICTS: dict[str, tuple[str, str]]` mapping raw column name →
`(verdict, reason)`; `column_audit` measures the fill rates from the data and joins
the verdicts on, so a fill rate is never typed by hand.

`mofo_resolution` compares each character against Baylor's 2024 `Cover Family`
mapped by `{"0","1","3"} -> "C"`, `{"2","4","6"} -> "O"`, restricted to rows where
both exist, and returns one row per character.

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/alignment.py tests/test_alignment.py
git commit   # body: these tables are the evidence for the spec's two resolutions;
             # the mofo test pins the conclusion against a silent data-refresh flip
```

---

## Task 8: `build_alignment_tables.py`

**Files:**
- Create: `build_alignment_tables.py`
- Test: `tests/test_alignment.py`

**Interfaces:**
- Consumes: everything in `alignment.py`.
- Produces: `outputs/tables/alignment_*.csv` and, for the report script,
  `outputs/alignment_provenance.json`.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_alignment.py
import subprocess, sys, json, pathlib


def test_build_alignment_tables_writes_the_expected_set():
    subprocess.run([sys.executable, "build_alignment_tables.py"], check=True)
    tables = pathlib.Path("outputs/tables")
    required = [
        "alignment_column_audit.csv",
        "alignment_offense_package_crosswalk.csv",
        "alignment_mofo_resolution.csv",
        "alignment_form_fam_crosswalk.csv",
        "alignment_personnel_crosswalk.csv",
        "alignment_source_agreement.csv",
        "alignment_decomposition_summary.csv",
        "alignment_formation_concept_early_run.csv",
    ]
    for name in required:
        assert (tables / name).exists(), name
    assert pathlib.Path("outputs/alignment_provenance.json").exists()


def test_summary_covers_every_dimension_and_subset():
    summary = pd.read_csv("outputs/tables/alignment_decomposition_summary.csv")
    assert set(summary["subset"]) == set(SUBSETS)
    assert set(summary["dimension"]) >= set(DIMENSIONS)
    assert (summary["delta"] - (summary["mix"] + summary["efficacy"]
                                + summary["interaction"])).abs().max() < 1e-9


def test_no_table_contains_a_season_outside_2024_2025():
    for path in pathlib.Path("outputs/tables").glob("alignment_*.csv"):
        frame = pd.read_csv(path)
        if "season" in frame.columns:
            assert set(frame["season"].dropna().unique()) <= {2024, 2025}, path
```

Note the interpreter: `sys.executable` under `.venv/bin/python -m pytest` is the venv's
Python, so the subprocess inherits pandas.

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: FAIL — `FileNotFoundError: build_alignment_tables.py`.

- [ ] **Step 3: Write the script**

Structure:

```python
"""Build every Phase 4 alignment table. Writes outputs/tables/alignment_*.csv.

Phase 4 owns only alignment_* files. build_tables.py (Phase 2) owns the rest and
is not touched.
"""
# 1. load joined parquet, both season charts, PFF alignment
# 2. aligned = alignment.build_alignment_table(...)
# 3. evidence tables (Task 7)
# 4. for each dimension: rate_by cut table + usage-share table
# 5. for each (dimension, subset): decompose -> detail csv + summary row
# 6. the 2-D early-down-run table: form_fam_norm x run_concept
# 7. dump provenance json: row counts, match rates, other_share extremes,
#    the mofo agreement rates, the offense_package top mapping
```

Every figure the report will quote must land in one of these files or in the
provenance JSON. Nothing is computed in the report script.

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add build_alignment_tables.py tests/test_alignment.py
git commit
```

---

## Task 9: `build_alignment_report.py` and `outputs/ALIGNMENT.md`

**Files:**
- Modify: `src/playcalls/alignment.py` (add `render_alignment_report`)
- Create: `build_alignment_report.py`
- Test: `tests/test_alignment.py`

**Interfaces:**
- Produces:
  - `alignment.render_alignment_report(tables: dict[str, pd.DataFrame], provenance: dict) -> str`
  - `build_alignment_report.py` writes `outputs/ALIGNMENT.md`.

**Report structure (in this order):**

1. Title and scope.
2. **How much of this you can believe** — before the findings, not after. The
   ~300-early-down-runs point, the ±15-point per-cell interval, the statement that
   totals are stable and cells are not, and that cells are not ranked by change.
3. The verdict paragraph — mix vs efficacy, with the numbers read from
   `alignment_decomposition_summary.csv`.
4. Decomposition summary table.
5. Offence alignment cuts.
6. Defence alignment cuts.
7. The 2-D early-down-run table.
8. What could not be built, and why (the excluded columns).
9. The two resolved data questions, with their evidence tables.
10. What this cannot answer.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_alignment.py

def _fake_tables():
    return {
        "summary": pd.DataFrame([
            {"dimension": "form_fam_norm", "subset": "all_plays",
             "outcome": "success_rate", "n_2024": 928, "n_2025": 986,
             "rate_2024": 0.5744, "rate_2025": 0.4949, "delta": -0.0795,
             "mix": -0.0031, "efficacy": -0.0748, "interaction": -0.0016,
             "other_share": 0.06, "groups": 5},
        ]),
    }


def _fake_provenance():
    return {"rows": 1935, "match_rate": 0.986,
            "mofo_char2_agreement": 0.918, "mofo_char1_agreement": 0.671,
            "early_down_run_n_2024": 347, "early_down_run_n_2025": 295,
            "low_n_threshold": 30}


def test_report_reads_the_decomposition_from_the_table_not_from_prose():
    tables, prov = _fake_tables(), _fake_provenance()
    text = alignment.render_alignment_report(tables, prov)
    assert "-7.5" in text or "7.5" in text          # efficacy, points
    tables["summary"].loc[0, "efficacy"] = -0.0210
    tables["summary"].loc[0, "mix"] = -0.0569
    changed = alignment.render_alignment_report(tables, prov)
    assert changed != text
    assert "5.7" in changed


def test_report_states_a_null_result_plainly_when_mix_is_negligible():
    tables, prov = _fake_tables(), _fake_provenance()
    text = alignment.render_alignment_report(tables, prov)
    assert "does not explain" in text


def test_report_says_so_when_mix_dominates():
    tables, prov = _fake_tables(), _fake_provenance()
    tables["summary"].loc[0, "mix"] = -0.0600
    tables["summary"].loc[0, "efficacy"] = -0.0179
    text = alignment.render_alignment_report(tables, prov)
    assert "does not explain" not in text


def test_report_carries_the_small_denominator_warning():
    text = alignment.render_alignment_report(_fake_tables(), _fake_provenance())
    assert "30" in text
    assert "not ranked" in text or "not rank" in text


def test_report_names_the_columns_it_could_not_use():
    text = alignment.render_alignment_report(_fake_tables(), _fake_provenance())
    for column in ("RB Align", "Front", "Cover Family"):
        assert column in text


def test_report_states_the_two_resolved_pff_fields():
    text = alignment.render_alignment_report(_fake_tables(), _fake_provenance())
    assert "offense_package" in text
    assert "mofo_coverage_played_shown" in text
    assert "91.8%" in text  # rendered from provenance, not typed


def test_report_does_not_hardcode_the_early_down_run_counts():
    prov = _fake_provenance()
    text = alignment.render_alignment_report(_fake_tables(), prov)
    assert "347" in text
    prov["early_down_run_n_2024"] = 999
    assert "999" in alignment.render_alignment_report(_fake_tables(), prov)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_alignment.py -q`
Expected: FAIL — `AttributeError: render_alignment_report`.

- [ ] **Step 3: Implement**

`render_alignment_report` composes markdown from the passed tables and provenance
dict. Every numeral is formatted from a value in those two arguments. The verdict
paragraph branches on `abs(mix) < abs(efficacy) / 3` → "alignment mix does not explain
the decline"; otherwise it states the mix share. `build_alignment_report.py` reads the
CSVs and the provenance JSON off disk and writes `outputs/ALIGNMENT.md`.

- [ ] **Step 4: Run the full suite and build the real report**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python build_alignment_tables.py
.venv/bin/python build_alignment_report.py
```

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/alignment.py build_alignment_report.py tests/test_alignment.py \
        outputs/ALIGNMENT.md outputs/tables/alignment_*.csv outputs/alignment_provenance.json
git commit
```

---

## Task 10: Verification pass

- [ ] **Step 1:** Invoke `superpowers:verification-before-completion`.
- [ ] **Step 2:** `.venv/bin/python -m pytest -q` — all 76 pre-existing plus Phase 4.
- [ ] **Step 3:** `git diff main --stat` — confirm no forbidden file is touched. The
      only non-new file in the diff must be `src/playcalls/charting.py`.
- [ ] **Step 4:** Grep `outputs/ALIGNMENT.md` for every percentage and confirm each one
      traces to a table cell or provenance key.
- [ ] **Step 5:** Confirm no Artifact was created and nothing left the machine.
- [ ] **Step 6:** Final commit if anything moved.

---

## Self-review

**Spec coverage.** §3 → Tasks 4, 7. §4 → Tasks 4, 7. §5 → Tasks 1, 2, 7. §6 → Task 4.
§7 → Task 5. §8 → Task 6. §9 → Tasks 7, 8. §10 → Task 9. §11 → Tasks 1, 3 and the
global constraints. §12 → every task. §13 → Task 9 step 3 (report section 10).

**Placeholders.** Task 7 step 3 and Task 8 step 3 describe structure rather than
quoting full code; both are mechanical aggregation and file-writing over interfaces
fully specified above them, and both have their assertions written out in step 1.
Everything else carries literal code.

**Type consistency.** `Outcome.series` returns `pd.Series[float]` everywhere.
`decompose` returns `(DataFrame, dict)` in Tasks 6, 8 and 9. `group_rates` returns
`[dimension, n, rate, low_n]`. `OTHER` and `LOW_N` are module constants used by
Tasks 4, 5, 6 and 9.

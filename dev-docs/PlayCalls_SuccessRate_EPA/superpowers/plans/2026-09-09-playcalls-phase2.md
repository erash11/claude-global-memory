# Phase 2 — EPA via CFBD PPA — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Status: executed and superseded in part.** This plan is kept as the record
> of what was planned, not as a description of what shipped. Two things changed
> during execution and the design spec, not this file, is the current truth:
>
> - **The aligner is a dynamic program, not the forward cursor sweep described
>   below.** Greedy starved later rows to perfect earlier ones. See spec §4.4.
> - **Gate 3 measures join quality, not absolute EPA coverage**, and is checked
>   per season as well as overall. The 95% absolute threshold this plan sets was
>   unreachable — CFBD caps it at 92.8%. See spec §5.
>
> An adversarial review after execution found nine further defects, all fixed.

**Goal:** Attach EPA (CFBD PPA) and in-game score state to the 1,935 joined Baylor play-call rows, gate the coverage, and answer whether EPA agrees with the Phase 1 success-rate finding.

**Architecture:** Two new modules. `cfbd.py` reads `CFB_Analytics_Lab`'s play parquet read-only and maps chart games to CFBD `gameId` by explicit opponent lookup. `epa.py` aligns chart plays to CFBD plays with the same forward-only cursor sweep `join.py` already uses for PFF, adds a clock tolerance and a gain-corroboration tiebreak, and derives score state. `run.py` gains Gate 3; `build_tables.py`, `report.py` and `build_artifact.py` gain Phase 2 sections. No Phase 1 module is restructured.

**Tech Stack:** Python 3, pandas, duckdb (parquet reads), pytest. `uv` venv at `.venv`. `uv` lives at `/Users/kristinarash/.local/bin/uv` — a standalone install, **not** Homebrew.

**Spec:** `docs/superpowers/specs/2026-09-09-playcalls-phase2-epa-design.md` — read it before Task 1. §2.2 records why PPA is EPA; §4.4 records the measured match rates that justify the aligner design.

**Branch:** `phase2-epa`. Phase 4 runs in parallel in `.worktrees/phase4-alignment`.

---

## Global Constraints

Copied verbatim from the spec. Every task's requirements implicitly include this section.

- **Naming.** The metric is written **"EPA (CFBD PPA)"** on first use in any report, artifact or table caption. In code and column names it is `epa`. Never bare "EPA" in prose without the source qualifier.
- **Read-only boundary.** This repo reads `/Users/kristinarash/DEV/CFB_Analytics_Lab/data/raw/plays/season=YYYY/*.parquet` read-only. It **never** calls the CFBD API, **never** reads/prints/copies/commits `CFB_Analytics_Lab/.env`, and holds no CFBD credential. A missing parquet file raises with the exact `CFB_Analytics_Lab` command to run — it never fetches.
- **Same rule for PFF.** `PFF_Data_Project` owns PFF ingest. `pff.db` is opened read-only. Never call the PFF API, never touch that repo's `.env`.
- **Season isolation.** Every CFBD read filters on `season` **before** any opponent match. Baylor plays Auburn in both 2025 and 2026. Never glob across season directories.
- **Gate 3 is 0.95.** If the implementation cannot reach it, investigate and report the true figure. **Never lower the constant to make it pass.** Naive-method baseline measured 2026-09-09 was 0.913.
- **Clock tolerance is 120 seconds.** Clock is a tiebreaker within tolerance, never a key.
- **Garbage time is flagged, never deleted.** Every EPA table is produced both with and without it.
- **Every headline figure in prose is computed from a table.** No number typed into text. Extend the three existing regression tests in `tests/test_report.py` to cover Phase 2 figures.
- **Report `n` beside every rate.** `analysis.MIN_SAMPLE` is 15 and existing cuts drop groups below it.
- **Do not touch** `.worktrees/`. Phase 4 is live in there.
- **Every commit message ends with exactly:**
  ```
  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
  ```
- **Run `.venv/bin/python -m pytest -q` before every commit.** All 76 Phase 1 tests must still pass.

### The six Phase 1 traps — all fail silently

1. `play_id` is float64 in the joined table. `.astype(str)` gives `"5642403.0"` against PFF's `"5642403"` and every merge matches zero rows. Use `analysis._play_key`.
2. PFF names Baylor inconsistently: `quarterback_charting` uses `team`; `rushing`/`passing`/`team_play` use `offense`. Baylor is `TXBA`.
3. Coverage data is dropbacks only. Run plays take `def_package` from `rushing`. Never pool them.
4. Pressure is not a column. Derived from the `pressure` feed's `defensive_grade_type` ∈ (SK, H, P).
5. `week1_auburn/` in `PFF_Data_Project` is the **2026** season, not 2025.
6. The 2021–2023 CSVs have no outcome columns. Success rate is impossible for them.

### Trap 7 — new in Phase 2

CFBD labels Baylor's 2024 bowl vs LSU as `seasonType='postseason', week=1`. Sorting CFBD games by `week` puts LSU **second** in 2024 while the chart's `game_code` order puts it **thirteenth**. A positional game map silently misjoins the whole 2024 season. Map by opponent, never by order. A test must enforce this.

---

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `src/playcalls/cfbd.py` | create | Read CFBD parquet read-only; `OPPONENT_TO_CFBD`; `map_cfbd_games`; raise-with-instructions on missing file |
| `src/playcalls/epa.py` | create | Clock parsing, forward-cursor alignment with tolerance, score state, garbage time, coverage stats |
| `tests/test_cfbd.py` | create | Loader and game-map behaviour |
| `tests/test_epa.py` | create | Alignment, clock, score state, garbage time, coverage |
| `src/playcalls/analysis.py` | modify (additive) | `epa_by()` alongside the existing `rate_by()` |
| `run.py` | modify | Attach EPA after the Phase 1 join; Gate 3; two diagnostic files |
| `build_tables.py` | modify | 13 new tables |
| `src/playcalls/report.py` | modify | Phase 2 report section |
| `build_artifact.py` | modify | Phase 2 HTML section |
| `tests/test_analysis.py` | modify (additive) | `epa_by` cases |
| `tests/test_report.py` | modify | Flip the prohibition test; extend the three no-hardcode regression tests |
| `CLAUDE.md`, `AGENTS.md` | modify | Document Phase 2. **Kept in sync by hand. NEVER symlink them.** |

---

## Task 1: CFBD loader and game map

**Files:**
- Create: `src/playcalls/cfbd.py`
- Test: `tests/test_cfbd.py`

**Interfaces:**
- Consumes: nothing from other Phase 2 tasks.
- Produces:
  - `CFBD_PLAYS_ROOT: str`
  - `OPPONENT_TO_CFBD: dict[str, str]`
  - `load_baylor_plays(season: int, root: str = CFBD_PLAYS_ROOT) -> pd.DataFrame`
  - `map_cfbd_games(season: int, chart_df: pd.DataFrame, cfbd_df: pd.DataFrame) -> dict[str, int]`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cfbd.py
"""CFBD loader and game map.

The game map is the highest-risk piece in Phase 2. CFBD labels Baylor's 2024
LSU bowl as seasonType=postseason week=1, so ordering games by week puts it
second rather than last. A positional map would misjoin the entire season and
every EPA number after it. These tests exist to make that impossible.
"""

import pandas as pd
import pytest

from src.playcalls import cfbd


def _chart(codes_and_opponents):
    return pd.DataFrame(
        [{"game_code": c, "def_team": o} for c, o in codes_and_opponents]
    )


def _cfbd(rows):
    return pd.DataFrame(
        [{"gameId": g, "defense": d, "week": w, "seasonType": s}
         for g, d, w, s in rows]
    )


def test_every_2024_opponent_code_is_mapped():
    codes = ["TXTA", "UTUN", "COAF", "COUN", "UTBY", "IAST", "TXTC",
             "OKST", "TXCU", "WVUN", "TXHO", "KSUN", "LAST"]
    for code in codes:
        assert code in cfbd.OPPONENT_TO_CFBD


def test_every_2025_opponent_code_is_mapped():
    codes = ["ALAU", "TXMU", "ALSM", "AZST", "OKST", "KSST",
             "TXCU", "OHCI", "FLCE", "UTUN", "AZUN", "TXHO"]
    for code in codes:
        assert code in cfbd.OPPONENT_TO_CFBD


def test_bowl_game_maps_by_opponent_not_by_week_order():
    """Trap 7. LSU is week=1 postseason but the chart's last game.

    A positional map would give 2402 the LSU gameId. This asserts it does not.
    """
    chart = _chart([("2401", "TXTA"), ("2402", "UTUN"), ("2413", "LAST")])
    plays = _cfbd([
        (401636610, "Tarleton State", 1, "regular"),
        (401636618, "Utah", 2, "regular"),
        (401677104, "LSU", 1, "postseason"),
    ])
    mapping = cfbd.map_cfbd_games(2024, chart, plays)
    assert mapping == {"2401": 401636610, "2402": 401636618, "2413": 401677104}


def test_unknown_opponent_code_raises():
    chart = _chart([("2401", "ZZZZ")])
    plays = _cfbd([(1, "Tarleton State", 1, "regular")])
    with pytest.raises(KeyError, match="ZZZZ"):
        cfbd.map_cfbd_games(2024, chart, plays)


def test_opponent_missing_from_cfbd_raises():
    chart = _chart([("2401", "TXTA")])
    plays = _cfbd([(1, "Utah", 1, "regular")])
    with pytest.raises(ValueError, match="Tarleton State"):
        cfbd.map_cfbd_games(2024, chart, plays)


def test_repeated_opponent_in_one_season_raises():
    """A conference-championship rematch must fail loudly, not pick the first."""
    chart = _chart([("2401", "TXCU")])
    plays = _cfbd([
        (11, "TCU", 3, "regular"),
        (22, "TCU", 13, "regular"),
    ])
    with pytest.raises(ValueError, match="more than one"):
        cfbd.map_cfbd_games(2024, chart, plays)


def test_missing_parquet_raises_with_the_pull_command():
    """Never fetch. Tell the user which repo owns the pull."""
    with pytest.raises(FileNotFoundError) as excinfo:
        cfbd.load_baylor_plays(1999, root="/nonexistent/plays")
    message = str(excinfo.value)
    assert "CFB_Analytics_Lab" in message
    assert "1999" in message


def test_loader_returns_only_baylor_offence_for_one_season():
    frame = cfbd.load_baylor_plays(2024)
    assert not frame.empty
    assert set(frame["season"].unique()) == {2024}
    assert set(frame["offense"].unique()) == {"Baylor"}


def test_loader_carries_the_columns_phase_2_needs():
    frame = cfbd.load_baylor_plays(2024)
    for column in ("gameId", "defense", "period", "down", "distance",
                   "yardsToGoal", "yardsGained", "clock_rem", "playType",
                   "ppa", "offenseScore", "defenseScore",
                   "driveNumber", "playNumber", "season"):
        assert column in frame.columns
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_cfbd.py -q`
Expected: FAIL, `ModuleNotFoundError: No module named 'src.playcalls.cfbd'`

- [ ] **Step 3: Write the implementation**

```python
# src/playcalls/cfbd.py
"""Read CFBD play-by-play, read-only.

CFB_Analytics_Lab owns all CFBD ingest. This module opens its parquet output
and nothing else. It never calls the CFBD API, never reads that repo's .env,
and holds no credential. If a season's parquet is absent, it raises with the
command to run over there rather than fetching, because the free tier is 1,000
calls a month and the budget guard and call ledger both live in that repo.

Games are mapped to chart game codes by opponent, never by week order. CFBD
labels Baylor's 2024 LSU bowl seasonType=postseason week=1, so ordering by week
places it second in the season instead of thirteenth. A positional map would
misjoin all of 2024 without erroring.
"""

from __future__ import annotations

import pathlib

import duckdb
import pandas as pd

CFBD_PLAYS_ROOT = "/Users/kristinarash/DEV/CFB_Analytics_Lab/data/raw/plays"

# Chart / PFF four-character opponent code -> CFBD team name.
# Explicit by design. Derivation from the code's letters is not reliable:
# TXTA is Tarleton State, TXTC is Texas Tech, TXCU is TCU, TXMU is SMU.
OPPONENT_TO_CFBD = {
    # 2024
    "TXTA": "Tarleton State",
    "UTUN": "Utah",
    "COAF": "Air Force",
    "COUN": "Colorado",
    "UTBY": "BYU",
    "IAST": "Iowa State",
    "TXTC": "Texas Tech",
    "OKST": "Oklahoma State",
    "TXCU": "TCU",
    "WVUN": "West Virginia",
    "TXHO": "Houston",
    "KSUN": "Kansas",
    "LAST": "LSU",
    # 2025
    "ALAU": "Auburn",
    "TXMU": "SMU",
    "ALSM": "Samford",
    "AZST": "Arizona State",
    "KSST": "Kansas State",
    "OHCI": "Cincinnati",
    "FLCE": "UCF",
    "AZUN": "Arizona",
}

_QUERY = """
select
    season,
    gameId,
    week,
    seasonType,
    offense,
    defense,
    period,
    down,
    distance,
    yardsToGoal,
    yardsGained,
    "clock.minutes" * 60 + "clock.seconds" as clock_rem,
    playType,
    ppa,
    offenseScore,
    defenseScore,
    driveNumber,
    playNumber
from read_parquet(?, union_by_name = true)
where offense = 'Baylor'
"""


def load_baylor_plays(
    season: int, root: str = CFBD_PLAYS_ROOT
) -> pd.DataFrame:
    """Every Baylor offensive play in one season, from CFBD parquet.

    The season is baked into the glob rather than filtered afterwards. Baylor
    plays Auburn in 2025 and again in 2026; a cross-season glob would let a
    2026 play join a 2025 charting row.
    """
    directory = pathlib.Path(root) / f"season={season}"
    if not directory.is_dir() or not list(directory.glob("*.parquet")):
        raise FileNotFoundError(
            f"No CFBD plays for {season} at {directory}.\n"
            "This repo never calls the CFBD API. Pull it in the repo that "
            "owns CFBD ingest, which enforces the free-tier budget guard:\n"
            f"  cd ~/DEV/CFB_Analytics_Lab && "
            f".venv/bin/python -m cfblab.pull plays --season {season}"
        )

    connection = duckdb.connect()
    try:
        frame = connection.execute(
            _QUERY, [str(directory / "*.parquet")]
        ).df()
    finally:
        connection.close()

    frame["season"] = frame["season"].astype(int)
    return frame


def map_cfbd_games(
    season: int, chart_df: pd.DataFrame, cfbd_df: pd.DataFrame
) -> dict[str, int]:
    """Return {chart game_code: CFBD gameId} for one season.

    Raises rather than guessing. An unmapped code, an opponent CFBD does not
    have, or an opponent played twice all stop the run — a wrong game map
    corrupts every EPA number downstream and produces no error of its own.
    """
    games = (
        chart_df[["game_code", "def_team"]]
        .drop_duplicates("game_code")
        .sort_values("game_code")
    )

    by_name: dict[str, list[int]] = {}
    for name, group in cfbd_df.groupby("defense"):
        by_name[name] = sorted(group["gameId"].unique().tolist())

    mapping: dict[str, int] = {}
    for _, row in games.iterrows():
        code = row["def_team"]
        if code not in OPPONENT_TO_CFBD:
            raise KeyError(
                f"{season} game {row['game_code']}: opponent code {code!r} is "
                "not in OPPONENT_TO_CFBD. Add it rather than letting the game "
                "drop out of the EPA join silently."
            )
        name = OPPONENT_TO_CFBD[code]
        candidates = by_name.get(name, [])
        if not candidates:
            raise ValueError(
                f"{season} game {row['game_code']}: CFBD has no plays against "
                f"{name!r}. The season parquet may be short a week."
            )
        if len(candidates) > 1:
            raise ValueError(
                f"{season} game {row['game_code']}: CFBD has more than one "
                f"game against {name!r} ({candidates}). Baylor played this "
                "opponent twice. The map needs a week tiebreak before this "
                "season can be joined."
            )
        mapping[row["game_code"]] = int(candidates[0])

    return mapping
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_cfbd.py -q`
Expected: PASS, 9 tests.

- [ ] **Step 5: Run the full suite**

Run: `.venv/bin/python -m pytest -q`
Expected: 85 passed (76 Phase 1 + 9 new).

- [ ] **Step 6: Commit**

```bash
git add src/playcalls/cfbd.py tests/test_cfbd.py
git commit -F - <<'EOF'
Add the CFBD loader and map games by opponent, not by week

CFB_Analytics_Lab owns CFBD ingest, so this module opens its parquet
read-only and raises with that repo's pull command when a season is absent.
It never calls the API and never reads its .env. The free tier is 1,000 calls
a month and both the budget guard and the call ledger live over there.

Games map through an explicit opponent lookup because ordering is not a safe
key. CFBD labels Baylor's 2024 LSU bowl seasonType=postseason week=1, so
sorting the season by week places LSU second rather than thirteenth, and a
positional map would misjoin all of 2024 while erroring on nothing. A test
pins that specific case.

The map raises on an unmapped code, on an opponent CFBD lacks, and on an
opponent played twice in a season. A rematch has no correct answer without a
week tiebreak, so it stops the run rather than taking the first candidate.

Season is baked into the parquet glob rather than filtered after the read.
Baylor plays Auburn in 2025 and again in 2026, and a cross-season glob would
let a 2026 play join a 2025 charting row.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
EOF
```

---

## Task 2: Clock parsing, score state, garbage time

**Files:**
- Create: `src/playcalls/epa.py`
- Test: `tests/test_epa.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `CLOCK_TOLERANCE_SECONDS: int = 120`
  - `parse_clock(value) -> int | None`
  - `score_state(margin: int) -> str`
  - `is_garbage_time(quarter: int, margin: int) -> bool`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_epa.py
"""EPA attachment: clock, score state, garbage time, alignment, coverage."""

import numpy as np
import pandas as pd
import pytest

from src.playcalls import epa


class TestParseClock:
    def test_normal(self):
        assert epa.parse_clock("15:00") == 900

    def test_single_digit_minute(self):
        assert epa.parse_clock("0:04") == 4

    def test_empty_string_is_none(self):
        assert epa.parse_clock("") is None

    def test_malformed_is_none(self):
        assert epa.parse_clock("abc") is None

    def test_nan_is_none(self):
        assert epa.parse_clock(np.nan) is None

    def test_none_is_none(self):
        assert epa.parse_clock(None) is None


class TestScoreState:
    """Buckets are from Baylor's perspective: margin = offense - defense."""

    def test_boundaries(self):
        assert epa.score_state(-17) == "trailing_big"
        assert epa.score_state(-16) == "trailing"
        assert epa.score_state(-9) == "trailing"
        assert epa.score_state(-8) == "one_score"
        assert epa.score_state(0) == "one_score"
        assert epa.score_state(8) == "one_score"
        assert epa.score_state(9) == "leading"
        assert epa.score_state(16) == "leading"
        assert epa.score_state(17) == "leading_big"


class TestGarbageTime:
    def test_first_half_is_never_garbage_time(self):
        assert epa.is_garbage_time(1, 50) is False
        assert epa.is_garbage_time(2, -50) is False

    def test_second_half_threshold_is_28(self):
        assert epa.is_garbage_time(3, 28) is False
        assert epa.is_garbage_time(3, 29) is True
        assert epa.is_garbage_time(3, -29) is True

    def test_fourth_quarter_threshold_is_24(self):
        assert epa.is_garbage_time(4, 24) is False
        assert epa.is_garbage_time(4, 25) is True
        assert epa.is_garbage_time(4, -25) is True

    def test_overtime_uses_the_fourth_quarter_rule(self):
        assert epa.is_garbage_time(5, 25) is True
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_epa.py -q`
Expected: FAIL, `ModuleNotFoundError: No module named 'src.playcalls.epa'`

- [ ] **Step 3: Write the implementation**

```python
# src/playcalls/epa.py
"""Attach EPA (CFBD PPA) and score state to the joined play table.

Two sources disagree about the clock by design: PFF charts the snap and ESPN's
play-by-play stamps the play differently. The measured median gap is 6 seconds
and the 95th percentile is 58. So the clock is a tiebreaker inside a tolerance,
never a key. Matching independently on state alone accepted a pairing 900
seconds apart -- a full quarter wrong.

Alignment therefore reuses the forward-only cursor sweep join.py already uses
against PFF: both sources list the same plays in the same order, and a cursor
that never goes back makes a late play claiming an early one impossible.
"""

from __future__ import annotations

import math

CLOCK_TOLERANCE_SECONDS = 120

# Score-state bucket edges, from Baylor's perspective.
TRAILING_BIG = -17
TRAILING = -9
LEADING = 9
LEADING_BIG = 17

# Garbage time. Conventional thresholds; recorded in the spec as a decision.
GARBAGE_SECOND_HALF = 28
GARBAGE_FOURTH = 24


def parse_clock(value) -> int | None:
    """Seconds remaining in the quarter, from an "MM:SS" string.

    Returns None rather than guessing. 28 of the 1,935 charting rows carry a
    clock that does not parse, and a null clock simply contributes nothing to
    the alignment score instead of inventing a position for the play.
    """
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        minutes, _, seconds = str(value).partition(":")
        return int(minutes) * 60 + int(seconds)
    except (ValueError, TypeError):
        return None


def score_state(margin: int) -> str:
    """Bucket the score margin. margin = Baylor score - opponent score."""
    margin = int(margin)
    if margin <= TRAILING_BIG:
        return "trailing_big"
    if margin <= TRAILING:
        return "trailing"
    if margin >= LEADING_BIG:
        return "leading_big"
    if margin >= LEADING:
        return "leading"
    return "one_score"


def is_garbage_time(quarter: int, margin: int) -> bool:
    """True when the score has put the play outside normal competitive calling.

    Garbage-time plays are flagged, never deleted. Every EPA table is produced
    with and without them, because a finding that survives only one treatment
    is not a finding.
    """
    quarter, margin = int(quarter), abs(int(margin))
    if quarter >= 4:
        return margin > GARBAGE_FOURTH
    if quarter == 3:
        return margin > GARBAGE_SECOND_HALF
    return False
```

**Boundary note:** `TRAILING` is `-9` and the comparison is `<=`, so `score_state(-9)` returns `"trailing"` and `score_state(-8)` returns `"one_score"`. `LEADING` is `9` with `>=`, so `score_state(9)` returns `"leading"`. The buckets are inclusive at the edge nearest zero on the trailing side and inclusive at the edge nearest zero on the leading side. The tests pin all six boundaries.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_epa.py -q`
Expected: PASS, 15 tests.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/epa.py tests/test_epa.py
git commit -F - <<'EOF'
Add clock parsing, score state and the garbage-time rule

The two sources disagree about the clock by design: PFF charts the snap, ESPN
stamps the play. Measured median gap is 6 seconds, p95 is 58. So the clock
becomes a tiebreaker inside a 120-second tolerance rather than a key. Matching
on state alone accepted a pairing 900 seconds apart, a full quarter wrong.

parse_clock returns None rather than guessing. 28 of the 1,935 charting rows
carry a clock that does not parse as MM:SS, and a null clock should contribute
nothing to an alignment score instead of inventing a position for the play.

Score state is the item Phase 1 recorded as impossible. Neither PFF nor the
chart carries a running score, so leading/trailing splits did not exist and
quarter stood in as a weak proxy. CFBD carries offenseScore and defenseScore on
every play, so the real thing is now available.

Garbage-time plays are flagged, not deleted, at the conventional thresholds --
more than 28 in the second half, more than 24 in the fourth. Every EPA table
will be produced both ways, because a finding that survives only one treatment
is not a finding.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
EOF
```

---

## Task 3: The aligner

**Files:**
- Modify: `src/playcalls/epa.py`
- Test: `tests/test_epa.py`

**Interfaces:**
- Consumes: `parse_clock`, `CLOCK_TOLERANCE_SECONDS` from Task 2.
- Produces:
  - `align_game(chart_df: pd.DataFrame, cfbd_df: pd.DataFrame) -> pd.DataFrame`
    Returns one row per chart row, in `play_no` order, with these columns added:
    `epa` (float, nullable), `cfbd_play_type` (str), `offense_score` (Int64),
    `defense_score` (Int64), `cfbd_yards_gained` (Int64), `clock_gap` (Int64),
    `epa_match` (bool).

The chart side must carry `play_no`, `quarter`, `down`, `distance`,
`yards_to_goal`, `game_clock`, `gain`. The CFBD side must carry the columns
`cfbd.load_baylor_plays` produces.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_epa.py`:

```python
def _chart_rows(rows):
    """rows: (play_no, quarter, down, distance, ytg, clock, gain)"""
    return pd.DataFrame(
        [{"play_no": p, "quarter": q, "down": d, "distance": dist,
          "yards_to_goal": y, "game_clock": c, "gain": g}
         for p, q, d, dist, y, c, g in rows]
    )


def _cfbd_rows(rows):
    """rows: (driveNumber, playNumber, period, down, distance, ytg,
              clock_rem, yardsGained, ppa, playType)"""
    return pd.DataFrame(
        [{"driveNumber": dr, "playNumber": pn, "period": per, "down": d,
          "distance": dist, "yardsToGoal": y, "clock_rem": c,
          "yardsGained": yg, "ppa": ppa, "playType": pt,
          "offenseScore": 0, "defenseScore": 0}
         for dr, pn, per, d, dist, y, c, yg, ppa, pt in rows]
    )


class TestAlignGame:
    def test_exact_match_attaches_epa(self):
        chart = _chart_rows([(1, 1, 1, 10, 75, "14:55", 4)])
        plays = _cfbd_rows([(1, 1, 1, 1, 10, 75, 895, 4, 0.31, "Rush")])
        out = epa.align_game(chart, plays)
        assert len(out) == 1
        assert out.loc[0, "epa"] == pytest.approx(0.31)
        assert bool(out.loc[0, "epa_match"]) is True

    def test_candidate_outside_clock_tolerance_is_rejected(self):
        """The 900-second failure. Perfect state agreement is not enough."""
        chart = _chart_rows([(1, 1, 1, 10, 75, "14:55", 4)])
        plays = _cfbd_rows([(1, 1, 1, 1, 10, 75, 5, 4, 0.31, "Rush")])
        out = epa.align_game(chart, plays)
        assert pd.isna(out.loc[0, "epa"])
        assert bool(out.loc[0, "epa_match"]) is False

    def test_alignment_never_moves_backward(self):
        """Chart play 2 may not claim a CFBD play before play 1's match."""
        chart = _chart_rows([
            (1, 1, 1, 10, 75, "14:00", 3),
            (2, 4, 1, 10, 75, "02:00", 3),
        ])
        plays = _cfbd_rows([
            (1, 1, 1, 1, 10, 75, 840, 3, 0.10, "Rush"),
            (9, 1, 4, 1, 10, 75, 120, 3, 0.90, "Rush"),
        ])
        out = epa.align_game(chart, plays).sort_values("play_no")
        assert out.iloc[0]["epa"] == pytest.approx(0.10)
        assert out.iloc[1]["epa"] == pytest.approx(0.90)

    def test_gain_corroborates_between_two_same_state_candidates(self):
        """Both candidates match state and clock. Gain breaks the tie."""
        chart = _chart_rows([(1, 2, 2, 5, 60, "07:00", 12)])
        plays = _cfbd_rows([
            (3, 1, 2, 2, 5, 60, 425, 1, -0.20, "Rush"),
            (3, 2, 2, 2, 5, 60, 415, 12, 1.05, "Rush"),
        ])
        out = epa.align_game(chart, plays)
        assert out.loc[0, "epa"] == pytest.approx(1.05)

    def test_null_clock_still_matches_on_state_and_order(self):
        chart = _chart_rows([(1, 1, 3, 2, 40, "", 7)])
        plays = _cfbd_rows([(2, 4, 1, 3, 2, 40, 600, 7, 1.4, "Rush")])
        out = epa.align_game(chart, plays)
        assert out.loc[0, "epa"] == pytest.approx(1.4)

    def test_matched_row_with_null_ppa_is_not_an_epa_match(self):
        """A Penalty row matches on state but carries no PPA."""
        chart = _chart_rows([(1, 1, 1, 10, 75, "14:55", 0)])
        plays = _cfbd_rows([
            (1, 1, 1, 1, 10, 75, 895, 0, None, "Penalty")
        ])
        out = epa.align_game(chart, plays)
        assert bool(out.loc[0, "epa_match"]) is False
        assert out.loc[0, "cfbd_play_type"] == "Penalty"

    def test_unmatched_chart_row_is_kept_not_dropped(self):
        chart = _chart_rows([
            (1, 1, 1, 10, 75, "14:55", 4),
            (2, 1, 2, 6, 71, "14:20", 2),
        ])
        plays = _cfbd_rows([(1, 1, 1, 1, 10, 75, 895, 4, 0.31, "Rush")])
        out = epa.align_game(chart, plays)
        assert len(out) == 2
        assert bool(out.loc[1, "epa_match"]) is False

    def test_score_columns_are_attached_on_a_match(self):
        chart = _chart_rows([(1, 3, 1, 10, 75, "10:00", 4)])
        plays = _cfbd_rows([(5, 1, 3, 1, 10, 75, 600, 4, 0.2, "Rush")])
        plays.loc[0, "offenseScore"] = 14
        plays.loc[0, "defenseScore"] = 31
        out = epa.align_game(chart, plays)
        assert int(out.loc[0, "offense_score"]) == 14
        assert int(out.loc[0, "defense_score"]) == 31
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_epa.py -q -k AlignGame`
Expected: FAIL, `AttributeError: module 'src.playcalls.epa' has no attribute 'align_game'`

- [ ] **Step 3: Write the implementation**

Append to `src/playcalls/epa.py`:

```python
import pandas as pd

ATTACHED_COLUMNS = (
    "epa", "cfbd_play_type", "offense_score", "defense_score",
    "cfbd_yards_gained", "clock_gap", "epa_match",
)

_UNMATCHED = {
    "epa": None,
    "cfbd_play_type": None,
    "offense_score": None,
    "defense_score": None,
    "cfbd_yards_gained": None,
    "clock_gap": None,
    "epa_match": False,
}


def _state_matches(chart_row, play) -> bool:
    return (
        int(play["period"]) == int(chart_row["quarter"])
        and play["down"] == chart_row["down"]
        and play["distance"] == chart_row["distance"]
        and play["yardsToGoal"] == chart_row["yards_to_goal"]
    )


def align_game(chart_df: pd.DataFrame, cfbd_df: pd.DataFrame) -> pd.DataFrame:
    """Attach CFBD EPA to one game's charting rows.

    A forward-only cursor sweep, the same idiom join.py uses against PFF. Both
    sources list the same plays in the same order, so a cursor that never goes
    back makes a fourth-quarter row claiming a first-quarter play impossible
    however well the down, distance and yard line agree.

    Within the window ahead of the cursor, the first state match wins unless a
    later candidate at the same state agrees better on yards gained. Candidates
    outside the clock tolerance are rejected outright.
    """
    chart = chart_df.sort_values("play_no").reset_index(drop=True)
    plays = (
        cfbd_df.sort_values(["driveNumber", "playNumber"])
        .reset_index(drop=True)
        .copy()
    )
    plays["_clock"] = pd.to_numeric(plays["clock_rem"], errors="coerce")

    cursor = 0
    rows = []

    for _, chart_row in chart.iterrows():
        record = chart_row.to_dict()
        chart_clock = parse_clock(chart_row.get("game_clock"))

        best_position = None
        best_gain_error = None

        for position in range(cursor, len(plays)):
            play = plays.loc[position]
            if not _state_matches(chart_row, play):
                continue

            gap = None
            if chart_clock is not None and pd.notna(play["_clock"]):
                gap = abs(int(play["_clock"]) - chart_clock)
                if gap > CLOCK_TOLERANCE_SECONDS:
                    continue

            gain_error = abs(
                float(play["yardsGained"]) - float(chart_row["gain"])
            ) if pd.notna(play["yardsGained"]) and pd.notna(chart_row["gain"]) \
                else 99.0

            if best_position is None or gain_error < best_gain_error:
                best_position, best_gain_error = position, gain_error
                if gain_error == 0:
                    break
            # A same-state candidate further ahead only wins on a better gain.
            if best_gain_error == 0:
                break

        if best_position is None:
            record.update(_UNMATCHED)
        else:
            play = plays.loc[best_position]
            cursor = best_position + 1
            gap = None
            if chart_clock is not None and pd.notna(play["_clock"]):
                gap = abs(int(play["_clock"]) - chart_clock)
            record.update({
                "epa": (
                    float(play["ppa"]) if pd.notna(play["ppa"]) else None
                ),
                "cfbd_play_type": play["playType"],
                "offense_score": play["offenseScore"],
                "defense_score": play["defenseScore"],
                "cfbd_yards_gained": play["yardsGained"],
                "clock_gap": gap,
                "epa_match": bool(pd.notna(play["ppa"])),
            })

        rows.append(record)

    return pd.DataFrame(rows)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_epa.py -q`
Expected: PASS, 23 tests.

If `test_gain_corroborates_between_two_same_state_candidates` fails, the search loop is breaking on the first state match before it sees the better-gain candidate. Fix the loop, not the test.

- [ ] **Step 5: Run the full suite**

Run: `.venv/bin/python -m pytest -q`
Expected: 99 passed.

- [ ] **Step 6: Commit**

```bash
git add src/playcalls/epa.py tests/test_epa.py
git commit -F - <<'EOF'
Align charting rows to CFBD plays with a forward-only cursor

Reuses the idiom join.py already proved against PFF rather than inventing a
second matcher. Both sources list the same plays in the same order, so a
cursor that never goes back makes a fourth-quarter row claiming a
first-quarter play impossible however well the down, distance and yard line
agree. That is the exact failure the naive probe hit: it accepted a pairing
900 seconds apart because the field state matched perfectly.

Two guards sit on top of the sweep. Candidates more than 120 seconds from the
charted clock are rejected outright. Among same-state candidates inside the
window, the one that agrees best on yards gained wins, which separates a
penalty replay from the play it replayed.

A row that matches a CFBD play carrying no PPA -- a penalty, a timeout -- is
recorded as matched-but-not-an-EPA-match rather than silently counted. That
distinction is what makes the coverage gate honest, since the naive probe
matched 96.3% of rows but only 91.3% carried an EPA.

Unmatched charting rows are kept with null EPA, never dropped. A denominator
that quietly shrinks is how a coverage problem turns into a wrong rate.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
EOF
```

---

## Task 4: Coverage statistics and Gate 3

**Files:**
- Modify: `src/playcalls/epa.py`, `run.py`
- Test: `tests/test_epa.py`

**Interfaces:**
- Consumes: `align_game` (Task 3), `cfbd.load_baylor_plays`, `cfbd.map_cfbd_games` (Task 1), `score_state`, `is_garbage_time` (Task 2).
- Produces:
  - `attach_score_state(df: pd.DataFrame) -> pd.DataFrame` — adds `score_margin` (Int64), `score_state` (str), `garbage_time` (bool).
  - `coverage_by_game(df: pd.DataFrame) -> pd.DataFrame` — columns `season`, `game_code`, `charted_plays`, `epa_matched`, `epa_coverage`, `clock_gap_median`, `clock_gap_max`.
  - `overall_coverage(df: pd.DataFrame) -> float`
  - In `run.py`: `EPA_COVERAGE_GATE = 0.95`, `build_epa(joined) -> tuple[pd.DataFrame, pd.DataFrame]`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_epa.py`:

```python
class TestAttachScoreState:
    def test_margin_state_and_garbage_flag_are_added(self):
        frame = pd.DataFrame([
            {"quarter": 1, "offense_score": 7, "defense_score": 0},
            {"quarter": 4, "offense_score": 3, "defense_score": 45},
        ])
        out = epa.attach_score_state(frame)
        assert int(out.loc[0, "score_margin"]) == 7
        assert out.loc[0, "score_state"] == "one_score"
        assert bool(out.loc[0, "garbage_time"]) is False
        assert int(out.loc[1, "score_margin"]) == -42
        assert out.loc[1, "score_state"] == "trailing_big"
        assert bool(out.loc[1, "garbage_time"]) is True

    def test_unmatched_rows_get_null_state_not_a_wrong_bucket(self):
        frame = pd.DataFrame([
            {"quarter": 2, "offense_score": None, "defense_score": None},
        ])
        out = epa.attach_score_state(frame)
        assert pd.isna(out.loc[0, "score_margin"])
        assert pd.isna(out.loc[0, "score_state"])
        assert bool(out.loc[0, "garbage_time"]) is False


class TestCoverage:
    def _frame(self):
        return pd.DataFrame([
            {"season": 2024, "game_code": "2401", "epa_match": True,
             "clock_gap": 4},
            {"season": 2024, "game_code": "2401", "epa_match": True,
             "clock_gap": 10},
            {"season": 2024, "game_code": "2401", "epa_match": False,
             "clock_gap": None},
            {"season": 2025, "game_code": "2501", "epa_match": True,
             "clock_gap": 2},
        ])

    def test_per_game_coverage(self):
        out = epa.coverage_by_game(self._frame())
        row = out[out["game_code"] == "2401"].iloc[0]
        assert int(row["charted_plays"]) == 3
        assert int(row["epa_matched"]) == 2
        assert row["epa_coverage"] == pytest.approx(2 / 3)
        assert row["clock_gap_max"] == 10

    def test_overall_coverage(self):
        assert epa.overall_coverage(self._frame()) == pytest.approx(0.75)

    def test_overall_coverage_of_empty_frame_is_nan(self):
        assert math.isnan(epa.overall_coverage(pd.DataFrame()))
```

Add `import math` at the top of `tests/test_epa.py`.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_epa.py -q -k "ScoreState or Coverage"`
Expected: FAIL with `AttributeError`.

- [ ] **Step 3: Write the implementation**

Append to `src/playcalls/epa.py`:

```python
def attach_score_state(df: pd.DataFrame) -> pd.DataFrame:
    """Add score_margin, score_state and garbage_time.

    Rows with no CFBD match get a null margin and a null state rather than
    landing in one_score by default. An unknown score is not a tied score.
    """
    out = df.copy()
    offense = pd.to_numeric(out["offense_score"], errors="coerce")
    defense = pd.to_numeric(out["defense_score"], errors="coerce")
    margin = offense - defense

    out["score_margin"] = margin.astype("Int64")
    out["score_state"] = [
        score_state(value) if pd.notna(value) else None for value in margin
    ]
    out["garbage_time"] = [
        is_garbage_time(quarter, value)
        if pd.notna(value) and pd.notna(quarter) else False
        for quarter, value in zip(out["quarter"], margin)
    ]
    return out


def coverage_by_game(df: pd.DataFrame) -> pd.DataFrame:
    """Per game: how many charted plays carry an EPA, and how far the clocks sat.

    Written on every run, pass or fail. A gate that fails without saying which
    games failed is a gate nobody can act on.
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "season", "game_code", "charted_plays", "epa_matched",
            "epa_coverage", "clock_gap_median", "clock_gap_max",
        ])

    working = df.copy()
    working["clock_gap"] = pd.to_numeric(working["clock_gap"], errors="coerce")

    grouped = (
        working.groupby(["season", "game_code"], dropna=False)
        .agg(
            charted_plays=("epa_match", "size"),
            epa_matched=("epa_match", "sum"),
            clock_gap_median=("clock_gap", "median"),
            clock_gap_max=("clock_gap", "max"),
        )
        .reset_index()
    )
    grouped["epa_coverage"] = (
        grouped["epa_matched"] / grouped["charted_plays"]
    ).round(4)
    return grouped[[
        "season", "game_code", "charted_plays", "epa_matched",
        "epa_coverage", "clock_gap_median", "clock_gap_max",
    ]].sort_values(["season", "game_code"]).reset_index(drop=True)


def overall_coverage(df: pd.DataFrame) -> float:
    """Fraction of charted plays carrying a non-null EPA."""
    if df.empty:
        return float("nan")
    return float(df["epa_match"].sum() / len(df))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_epa.py -q`
Expected: PASS, 28 tests.

- [ ] **Step 5: Wire Gate 3 into `run.py`**

Read `run.py` first. Make these changes and no others:

1. Add to the imports:
   ```python
   from src.playcalls.cfbd import load_baylor_plays, map_cfbd_games
   from src.playcalls.epa import (
       align_game, attach_score_state, coverage_by_game, overall_coverage,
   )
   ```
2. Add the constant beside the other gates:
   ```python
   EPA_COVERAGE_GATE = 0.95
   ```
3. Add `"epa_coverage.csv"` and `"epa_unmatched.csv"` to `PRODUCED`.
4. Add this function:
   ```python
   def build_epa(joined: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
       """Attach EPA (CFBD PPA) and score state to the Phase 1 joined table.

       Returns (joined_with_epa, per_game_coverage).
       """
       frames = []
       for season in SEASONS:
           cfbd_plays = load_baylor_plays(season)
           season_chart = joined[joined["season"] == season]
           mapping = map_cfbd_games(season, season_chart, cfbd_plays)

           for game_code, game_id in sorted(mapping.items()):
               game_chart = season_chart[season_chart["game_code"] == game_code]
               game_plays = cfbd_plays[cfbd_plays["gameId"] == game_id]
               aligned = align_game(game_chart, game_plays)
               aligned["cfbd_game_id"] = game_id
               frames.append(aligned)

       with_epa = attach_score_state(pd.concat(frames, ignore_index=True))
       return with_epa, coverage_by_game(with_epa)
   ```
5. In `main()`, **after** the Phase 1 charting-gap gate passes and **before**
   `_promote()`, insert:
   ```python
       with_epa, epa_coverage = build_epa(joined)
       with_epa.to_parquet(STAGING / "joined_plays.parquet", index=False)
       epa_coverage.to_csv(STAGING / "epa_coverage.csv", index=False)
       with_epa[~with_epa["epa_match"]].to_csv(
           STAGING / "epa_unmatched.csv", index=False
       )

       epa_overall = overall_coverage(with_epa)
       print("\nEPA (CFBD PPA) coverage by game:")
       print(epa_coverage.to_string(index=False))
       print(f"\noverall EPA coverage: {epa_overall:.1%}")

       if epa_overall < EPA_COVERAGE_GATE:
           worst_games = epa_coverage.nsmallest(5, "epa_coverage")
           print(worst_games.to_string(index=False))
           return _abort(
               f"GATE FAILED: EPA coverage {epa_overall:.1%} is below "
               f"{EPA_COVERAGE_GATE:.0%}. See outputs/.staging/epa_unmatched.csv. "
               "Investigate the shortfall. Do not lower the gate."
           )
   ```
   Note it **overwrites** the staged `joined_plays.parquet` with the EPA-bearing
   version, so downstream reads one table, not two.
6. Add to the `PASS_RECORD` JSON:
   ```python
       "epa_coverage": round(float(epa_overall), 4),
       "epa_source": "CFBD PPA",
   ```

- [ ] **Step 6: Run the pipeline and record the real coverage**

Run: `.venv/bin/python run.py`

If coverage clears 95%, note the figure — it goes in the Task 7 report.

**If it does not clear 95%:** stop. Read `outputs/.staging/epa_unmatched.csv`, group the misses by `cfbd_play_type` and by `game_code`, and find out why. The naive baseline was 91.3% and 2025 missed six times more often than 2024, so start there. Fix the aligner or explain the shortfall in the spec. **Do not change `EPA_COVERAGE_GATE`.**

- [ ] **Step 7: Run the full suite**

Run: `.venv/bin/python -m pytest -q`
Expected: 104 passed.

- [ ] **Step 8: Commit**

```bash
git add src/playcalls/epa.py tests/test_epa.py run.py
git commit -F - <<'EOF'
Add Gate 3: refuse to build tables below 95% EPA coverage

Phase 1 established that nothing reaches outputs/ until the data gates pass.
EPA gets the same treatment rather than being trusted because it arrived from
a reputable source.

The gate is 95% of charted plays carrying a non-null EPA, checked overall and
written per game either way. A gate that fails without naming the failing
games is a gate nobody can act on, so epa_coverage.csv and epa_unmatched.csv
are produced on every run, pass or fail.

Score state is attached here too. Rows with no CFBD match get a null margin
and a null state rather than defaulting into one_score, because an unknown
score is not a tied score -- that default would have quietly loaded every
unmatched play into the most common bucket.

The staged joined_plays.parquet is overwritten with the EPA-bearing version so
everything downstream reads one table rather than choosing between two.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
EOF
```

---

## Task 5: EPA aggregation helper

**Files:**
- Modify: `src/playcalls/analysis.py` (additive only)
- Test: `tests/test_analysis.py` (additive only)

**Interfaces:**
- Consumes: nothing new.
- Produces:
  - `epa_by(df, *columns, min_sample=MIN_SAMPLE, exclude_garbage=False) -> pd.DataFrame`
    Columns out: the grouping columns, then `plays`, `epa_plays`, `epa_per_play`, `epa_total`, `success_rate_epa_positive`.

`success_rate_epa_positive` is the share of EPA-bearing plays with `epa > 0`. It is the natural EPA analogue of a success rate and makes the two lenses directly comparable.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_analysis.py`:

```python
class TestEpaBy:
    def _frame(self):
        return pd.DataFrame([
            {"run_pass": "R", "epa": 1.0, "garbage_time": False},
            {"run_pass": "R", "epa": -1.0, "garbage_time": False},
            {"run_pass": "R", "epa": None, "garbage_time": False},
            {"run_pass": "R", "epa": 3.0, "garbage_time": True},
            {"run_pass": "P", "epa": 0.5, "garbage_time": False},
        ])

    def test_epa_per_play_ignores_null_epa_rows(self):
        out = analysis.epa_by(self._frame(), "run_pass", min_sample=1)
        runs = out[out["run_pass"] == "R"].iloc[0]
        assert int(runs["plays"]) == 4
        assert int(runs["epa_plays"]) == 3
        assert runs["epa_per_play"] == pytest.approx(1.0)

    def test_exclude_garbage_drops_those_plays(self):
        out = analysis.epa_by(
            self._frame(), "run_pass", min_sample=1, exclude_garbage=True
        )
        runs = out[out["run_pass"] == "R"].iloc[0]
        assert int(runs["epa_plays"]) == 2
        assert runs["epa_per_play"] == pytest.approx(0.0)

    def test_positive_epa_share(self):
        out = analysis.epa_by(
            self._frame(), "run_pass", min_sample=1, exclude_garbage=True
        )
        runs = out[out["run_pass"] == "R"].iloc[0]
        assert runs["success_rate_epa_positive"] == pytest.approx(0.5)

    def test_min_sample_drops_thin_groups(self):
        out = analysis.epa_by(self._frame(), "run_pass", min_sample=3)
        assert set(out["run_pass"]) == {"R"}

    def test_no_grouping_column_raises(self):
        with pytest.raises(ValueError):
            analysis.epa_by(self._frame())
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_analysis.py -q -k EpaBy`
Expected: FAIL, `AttributeError: module 'src.playcalls.analysis' has no attribute 'epa_by'`

- [ ] **Step 3: Write the implementation**

Append to `src/playcalls/analysis.py`:

```python
def epa_by(
    df: pd.DataFrame,
    *columns: str,
    min_sample: int = MIN_SAMPLE,
    exclude_garbage: bool = False,
) -> pd.DataFrame:
    """EPA (CFBD PPA) per play, grouped by one or more columns.

    `plays` counts every play in the group; `epa_plays` counts only those
    carrying an EPA. They differ, and the difference is the coverage shortfall
    -- printing one and calling it the other is how a coverage problem becomes
    a wrong rate.

    `min_sample` is applied to `epa_plays`, not `plays`, for the same reason.
    """
    if not columns:
        raise ValueError("epa_by needs at least one grouping column")

    working = df.copy()
    if exclude_garbage and "garbage_time" in working.columns:
        working = working[~working["garbage_time"].fillna(False).astype(bool)]

    working["_epa"] = pd.to_numeric(working["epa"], errors="coerce")
    working["_has_epa"] = working["_epa"].notna()
    working["_positive"] = working["_has_epa"] & (working["_epa"] > 0)

    grouped = (
        working.groupby(list(columns), dropna=False)
        .agg(
            plays=("_epa", "size"),
            epa_plays=("_has_epa", "sum"),
            epa_total=("_epa", "sum"),
            positives=("_positive", "sum"),
        )
        .reset_index()
    )

    grouped = grouped[grouped["epa_plays"] >= min_sample].copy()
    if grouped.empty:
        return grouped.drop(columns=["positives"], errors="ignore")

    grouped["epa_per_play"] = (
        grouped["epa_total"] / grouped["epa_plays"]
    ).round(4)
    grouped["success_rate_epa_positive"] = (
        grouped["positives"] / grouped["epa_plays"]
    ).round(4)
    grouped["epa_total"] = grouped["epa_total"].round(2)

    return (
        grouped.drop(columns=["positives"])
        .sort_values("epa_per_play", ascending=False)
        .reset_index(drop=True)
    )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest -q`
Expected: 109 passed.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/analysis.py tests/test_analysis.py
git commit -F - <<'EOF'
Add epa_by alongside rate_by

Additive. rate_by and every Phase 1 cut are untouched, because Phase 4 is
building alignment tables against them in a parallel worktree.

epa_by reports plays and epa_plays as separate columns rather than one count.
They differ by exactly the coverage shortfall, and printing one while calling
it the other is how a coverage problem turns into a wrong rate. min_sample
applies to epa_plays for the same reason -- a group of 40 plays with 12 EPA
values is a thin group, whatever its size column says.

success_rate_epa_positive is the share of EPA-bearing plays above zero. It is
the natural EPA analogue of a binary success rate, which is what lets the
report set the two lenses side by side rather than asserting they agree.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
EOF
```

---

## Task 6: The thirteen EPA tables

**Files:**
- Modify: `build_tables.py`
- Test: `tests/test_analysis.py`

**Interfaces:**
- Consumes: `analysis.epa_by` (Task 5), the EPA-bearing `outputs/joined_plays.parquet` (Task 4).
- Produces: 13 CSVs under `outputs/tables/`, prefixed `epa_`.

- [ ] **Step 1: Read `build_tables.py` and follow its existing pattern**

It refuses to run without `outputs/GATES_PASSED.json`. Keep that. Add the EPA tables to the same staging-and-promote flow the 45 existing tables use. Do not restructure it.

- [ ] **Step 2: Add the tables**

| File under `outputs/tables/` | Call |
|---|---|
| `epa_by_season.csv` | `epa_by(df, "season")` |
| `epa_by_season_runpass.csv` | `epa_by(df, "season", "run_pass")` |
| `epa_by_down.csv` | `epa_by(df, "season", "down")` |
| `epa_by_down_distance.csv` | `epa_by(df, "season", "down_distance")` |
| `epa_early_down_run.csv` | `epa_by(df[df.early_down & (df.run_pass == "R")], "season", min_sample=1)` |
| `epa_by_field_zone.csv` | `epa_by(df, "season", "field_zone")` |
| `epa_by_score_state.csv` | `epa_by(df, "season", "score_state")` |
| `epa_by_score_state_clean.csv` | `epa_by(df, "season", "score_state", exclude_garbage=True)` |
| `epa_by_pressure.csv` | `epa_by(df[df.run_pass == "P"], "season", "pressured")` — dropbacks only, trap 3 |
| `epa_by_personnel.csv` | `epa_by(df, "season", "personnel")` |
| `epa_by_concept.csv` | `epa_by(df, "season", "concept")` |
| `epa_vs_success_agreement.csv` | see Step 3 |
| `epa_distribution.csv` | mean, median, stdev, p10, p90, share above zero, by season |

Every one of these is also written in an `_clean` variant with
`exclude_garbage=True`, **except** `epa_by_score_state_clean.csv` which already
is one. Name them `<stem>_clean.csv`.

- [ ] **Step 3: Build the agreement table**

This is the table the Phase 2 report turns on. For each cut that appears in the
Phase 1 report, put the success-rate delta beside the EPA delta:

```python
def _agreement(df):
    """2024 -> 2025 change, measured both ways, for every headline cut.

    Same cut, same rows, two yardsticks. Where the signs disagree, the report
    must say so rather than quoting whichever lens is kinder.
    """
    cuts = {
        "overall": df,
        "early_down_run": df[df["early_down"] & (df["run_pass"] == "R")],
        "first_and_ten": df[df["down_distance"] == "1st & 10"],
        "run": df[df["run_pass"] == "R"],
        "pass": df[df["run_pass"] == "P"],
        "clean_pocket": df[(df["run_pass"] == "P") & (~df["pressured"])],
    }
    rows = []
    for name, frame in cuts.items():
        rate = analysis.rate_by(frame, "season", min_sample=1)
        value = analysis.epa_by(frame, "season", min_sample=1)
        row = {"cut": name}
        for season in (2024, 2025):
            r = rate[rate["season"] == season]
            v = value[value["season"] == season]
            row[f"success_rate_{season}"] = (
                float(r["success_rate"].iloc[0]) if len(r) else None
            )
            row[f"epa_per_play_{season}"] = (
                float(v["epa_per_play"].iloc[0]) if len(v) else None
            )
            row[f"epa_plays_{season}"] = (
                int(v["epa_plays"].iloc[0]) if len(v) else 0
            )
        row["success_rate_delta"] = (
            row["success_rate_2025"] - row["success_rate_2024"]
            if None not in (row["success_rate_2024"], row["success_rate_2025"])
            else None
        )
        row["epa_delta"] = (
            row["epa_per_play_2025"] - row["epa_per_play_2024"]
            if None not in (row["epa_per_play_2024"], row["epa_per_play_2025"])
            else None
        )
        row["lenses_agree"] = (
            None if None in (row["success_rate_delta"], row["epa_delta"])
            else (row["success_rate_delta"] < 0) == (row["epa_delta"] < 0)
        )
        rows.append(row)
    return pd.DataFrame(rows)
```

- [ ] **Step 4: Add a regression test that the agreement table is honest**

Append to `tests/test_analysis.py`:

```python
def test_agreement_table_flags_disagreement():
    """A cut where success rate rises while EPA falls must be flagged False.

    The whole point of the table is to surface disagreement, so it needs a
    test that proves it can.
    """
    import pandas as pd
    from build_tables import _agreement

    frame = pd.DataFrame(
        [{"season": 2024, "run_pass": "R", "efficiency": "N", "explosive": 0,
          "epa": 2.0, "early_down": True, "down_distance": "1st & 10",
          "pressured": False, "garbage_time": False}] * 20
        + [{"season": 2025, "run_pass": "R", "efficiency": "Y", "explosive": 0,
            "epa": -2.0, "early_down": True, "down_distance": "1st & 10",
            "pressured": False, "garbage_time": False}] * 20
    )
    out = _agreement(frame)
    overall = out[out["cut"] == "overall"].iloc[0]
    assert overall["success_rate_delta"] > 0
    assert overall["epa_delta"] < 0
    assert bool(overall["lenses_agree"]) is False
```

- [ ] **Step 5: Run and verify**

Run:
```bash
.venv/bin/python run.py && .venv/bin/python build_tables.py && .venv/bin/python -m pytest -q
```
Expected: gates pass, tables written, all tests pass.

Then read `outputs/tables/epa_vs_success_agreement.csv` yourself. Note which cuts agree and which do not. Those numbers go into Task 7.

- [ ] **Step 6: Commit**

```bash
git add build_tables.py tests/test_analysis.py
git commit -F - <<'EOF'
Build the thirteen EPA tables, each in a garbage-time-clean variant too

Every table is produced with and without garbage time rather than picking one
treatment. A finding that survives only one of them is not a finding, and the
report has to be able to say which it is quoting.

The pressure cut is restricted to dropbacks. Coverage and pressure data exist
only for dropbacks; pooling run plays into that cut would divide a dropback
numerator by a whole-offence denominator.

epa_vs_success_agreement.csv is the table the Phase 2 report turns on. For
every headline cut in the Phase 1 report it sets the success-rate delta beside
the EPA delta and flags whether the two lenses point the same way. It carries
its own test proving it reports disagreement rather than smoothing it, because
a table whose only job is to surface conflict needs evidence it can.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
EOF
```

---

## Task 7: Report section and the flipped prohibition tests

**Files:**
- Modify: `src/playcalls/report.py`, `build_artifact.py`, `tests/test_report.py`
- Test: `tests/test_report.py`

**Interfaces:**
- Consumes: the tables from Task 6.
- Produces: a Phase 2 section in `outputs/REPORT.md` and `outputs/report.html`.

- [ ] **Step 1: Replace the prohibition test**

Find the Phase 1 test asserting the report contains no EPA. **Replace** it with this pair. Do not delete without replacing — the original intent still stands.

```python
def test_epa_is_present_and_always_source_qualified():
    """EPA now exists. Every first mention must name its source.

    CFBD's model is calibrated differently from ESPN's or PFF's. The same play
    carries a different EPA in each. A reader comparing this against a public
    leaderboard has to know why the numbers differ.
    """
    text = pathlib.Path("outputs/REPORT.md").read_text()
    assert "EPA" in text
    assert "EPA (CFBD PPA)" in text


def test_no_yards_proxy_is_labelled_epa():
    """The Phase 1 prohibition, preserved and made stricter.

    EPA must come from CFBD's ppa column and nowhere else. A yards-derived
    figure dressed as EPA is the specific failure this guards.
    """
    source = pathlib.Path("src/playcalls/cfbd.py").read_text()
    assert "ppa" in source

    for module in ("epa.py", "analysis.py"):
        text = pathlib.Path(f"src/playcalls/{module}").read_text()
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or '"""' in stripped:
                continue
            if "epa" in stripped and "=" in stripped:
                assert "yards" not in stripped.lower(), (
                    f"{module}: EPA assigned from a yards expression: {line!r}"
                )
                assert "gain" not in stripped.lower(), (
                    f"{module}: EPA assigned from a gain expression: {line!r}"
                )
```

- [ ] **Step 2: Extend the three no-hardcode regression tests**

Find the three existing tests in `tests/test_report.py` that stop a hardcoded
figure creeping back into prose. Extend each to cover the Phase 2 figures the
same way: recompute the number from its table and assert the rendered text
contains that computed value, never a literal.

- [ ] **Step 3: Write the report section**

Add to `render_report` in `src/playcalls/report.py`. It must answer four
questions explicitly, and every number in it must come from `_lookup` against a
table — never typed:

1. **Does EPA agree with the success-rate finding on early-down running?**
   Quote both deltas from `epa_vs_success_agreement.csv`.
2. **Where do the lenses disagree, and what does that mean?** Enumerate every
   row where `lenses_agree` is False. If none disagree, say so plainly.
3. **What does score state show that quarter could not?** Compare
   `epa_by_score_state.csv` with its `_clean` variant. State how many plays
   garbage time removed.
4. **What is the EPA coverage and which plays are missing?** From
   `GATES_PASSED.json` and `epa_coverage.csv`. Name the worst game.

Then revisit the Phase 1 conclusion. Phase 1 said the cause of the decline is
not decidable from its data. State whether EPA and score state change that, and
if they do not, say so. **Do not upgrade a hedge into a claim because a second
metric agreed.**

The section must also carry, in prose:
- the naming rule: "EPA (CFBD PPA)" and why the numbers differ from other sources;
- that opponent adjustment is still absent, and that it remains the strongest
  alternative explanation this study cannot rule out.

- [ ] **Step 4: Mirror the section into `build_artifact.py`**

Follow the existing HTML pattern. Before writing any chart, invoke
`Skill("dataviz")`. Do **not** publish the artifact — the report contains
proprietary Baylor play-call terminology.

- [ ] **Step 5: Run the whole pipeline**

```bash
.venv/bin/python run.py \
  && .venv/bin/python build_tables.py \
  && .venv/bin/python build_report.py \
  && .venv/bin/python build_artifact.py \
  && .venv/bin/python -m pytest -q
```

- [ ] **Step 6: Recompute every prose figure by hand**

This is the step Phase 1 skipped, and it shipped two wrong numbers. For each
figure in the new report section, query the table directly and confirm the
rendered text matches. Do not trust the render.

- [ ] **Step 7: Commit**

```bash
git add src/playcalls/report.py build_artifact.py tests/test_report.py
git commit -F - <<'EOF'
Report whether EPA agrees with the success-rate finding

The section answers four questions explicitly rather than presenting tables and
leaving the reader to draw the conclusion: does EPA agree on early-down
running, where do the lenses disagree, what does score state show that quarter
could not, and what is the coverage shortfall.

Phase 1's test asserting no EPA exists is replaced rather than deleted. Two
tests take its place: one requiring every first mention to be source-qualified
as "EPA (CFBD PPA)", because CFBD's calibration differs from ESPN's and PFF's
and a reader comparing against a public leaderboard needs to know why; and one
asserting no EPA value is ever assigned from a yards or gain expression, which
is the original prohibition made harder to violate.

The Phase 1 conclusion -- that the cause of the decline is not decidable from
this data -- is re-examined rather than assumed to survive. A second metric
agreeing is not grounds to upgrade a hedge into a claim, and opponent
adjustment is still absent, which remains the strongest alternative
explanation this study cannot rule out.

Every figure was recomputed from its table by hand before commit. Phase 1
shipped two wrong numbers past 68 green tests by trusting the render.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
EOF
```

---

## Task 8: Documentation and verification

**Files:**
- Modify: `CLAUDE.md`, `AGENTS.md`

- [ ] **Step 1: Document Phase 2 in both agent guides**

Both files. **Kept in sync by hand — NEVER symlink them.** Add:

- the `CFB_Analytics_Lab` read-only boundary and the pull command;
- Gate 3, its threshold, and the rule that a miss is investigated not lowered;
- **trap 7** — the postseason `week=1` game-ordering trap;
- the "EPA (CFBD PPA)" naming rule;
- the updated pipeline commands and test count.

- [ ] **Step 2: Verify**

Invoke `Skill("superpowers:verification-before-completion")`.

Confirm every one of these:
- [ ] `.venv/bin/python -m pytest -q` — all pass, count recorded.
- [ ] Full pipeline runs clean from a wiped `outputs/.staging/`.
- [ ] `GATES_PASSED.json` carries `epa_coverage` and `epa_source`.
- [ ] Deleting `GATES_PASSED.json` makes `build_tables.py` refuse.
- [ ] Forcing `EPA_COVERAGE_GATE = 0.999` makes `run.py` exit 1 and leave `outputs/` unchanged. **Restore 0.95 afterwards.**
- [ ] `grep -rn "0\.913\|91\.3" src/ *.py` returns nothing — no measured figure hardcoded.
- [ ] No file in `src/` or the root reads `CFB_Analytics_Lab/.env` or calls the CFBD API.
- [ ] `git status` is clean; nothing under `.worktrees/` was touched.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md AGENTS.md
git commit -F - <<'EOF'
Document Phase 2 in both agent guides

CLAUDE.md and AGENTS.md carry the same content and are maintained by hand.
They are deliberately not symlinked.

Records the CFB_Analytics_Lab read-only boundary with the pull command to run
when a season is missing, Gate 3 and the rule that a miss is investigated
rather than lowered, and the "EPA (CFBD PPA)" naming rule.

Adds trap 7 to the list of silent failures: CFBD labels a bowl game
seasonType=postseason week=1, so ordering a season by week puts it second
rather than last and a positional game map misjoins everything after it
without raising.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cpiq4uQvzv6fct94zkaVCX
EOF
```

- [ ] **Step 4: Do not merge**

Leave `phase2-epa` for the user. A dcg guard blocks agents from deleting
branches, so branch cleanup is the user's to run.

---

## Self-Review

**Spec coverage.** §2 Tasks 1, 7. §3 Task 1. §4.2 Task 1. §4.3 Tasks 1, 8. §4.4 Task 3. §4.5 Task 2. §4.6 reuses Phase 1 unchanged. §4.7 reuses Phase 1 unchanged. §5 Task 4. §6 Tasks 2, 4. §7.1 Tasks 1–3. §7.2 Task 6. §7.3 Task 7. §7.4 Task 7. §8 spread across all tasks. §9 stated in the Task 7 report text. §10 handled by the gate and diagnostics. §11 recorded throughout.

**One gap, deliberate.** §4.6's `yards_to_goal` needs no task — Phase 1 already implements and tests it, and Phase 2 reuses it unchanged. Noted so a reviewer does not read it as an omission.

**Type consistency.** `epa_match` is `bool` everywhere. `epa` is nullable float. `score_margin` is `Int64`. `map_cfbd_games` returns `dict[str, int]`; `gameId` stays an int across `cfbd.py`, `run.py` and the parquet. `align_game` returns one row per chart row and never fewer.

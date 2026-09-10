# Play-Call Success Rate — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Join Baylor's 2024 and 2025 offensive play-call charting to PFF play-level data, then produce an analytical report on play-call success rate, situational performance, and the coordinator's tendency profile.

**Architecture:** `PFF_Data_Project` owns all PFF ingest and gains three missing premium categories. This repo opens its DuckDB read-only, normalises the Baylor charting CSVs, joins the two on play, and writes derived tables plus a Markdown report. Two hard gates sit before any analysis: a proven row-level join, and a resolved run-count discrepancy.

**Tech Stack:** Python 3.12, `uv` for environment management, pandas, duckdb, pytest. No new services, no cloud, no scheduler.

**Spec:** `docs/superpowers/specs/2026-09-09-playcalls-success-rate-epa-design.md`

## Global Constraints

- **Python environment:** `uv` is a standalone install at `/Users/kristinarash/.local/bin/uv` — **not** Homebrew. System Python is PEP 668-managed; never `pip install` globally.
- **`timeout` is not installed** on this machine (no GNU coreutils). Never use it in scripts.
- **Raw CSVs are immutable.** Never edit `20*_All_Games.csv`. Derived output goes to new paths.
- **`pff.db` is opened read-only from this repo.** `duckdb.connect(path, read_only=True)`. This repo never writes to it, never calls the PFF API, and never holds PFF credentials.
- **Data is proprietary Baylor play-call terminology.** Private repo only. Never paste play-call strings into an external service.
- **Every reported rate carries its `n`.** Cells with `n < 15` are suppressed, not printed.
- **Seasons 2021–2023 are out of scope.** They have no outcome columns. Never pool them into a success-rate number.
- **Phase 1 delivers success rate, not EPA.** No yards-based proxy may be labelled EPA.
- **All CSV reads use `encoding="utf-8-sig"`** (UTF-8 BOM on every header).
- **Paths:**
  - This repo: `/Users/kristinarash/DEV/PlayCalls_SuccessRate_EPA`
  - PFF project: `/Users/kristinarash/DEV/Football/PFF_Data_Project`
  - PFF DuckDB: `/Users/kristinarash/DEV/Football/PFF_Data_Project/data/pff.db`

---

## File Structure

| File | Responsibility |
|---|---|
| `src/playcalls/charting.py` | Load and clean the Baylor season CSVs. Owns every trap in spec §6.4. |
| `src/playcalls/normalise.py` | Separator/abbreviation normalisation of play-call vocabulary; derive the `Play Type` crosswalk from evidence. |
| `src/playcalls/pff.py` | Read `pff.db` read-only; flatten `raw_json` into one row per `play_id`. |
| `src/playcalls/gamemap.py` | Map CSV game codes (`2501`) to PFF `game_id` using team codes and week order. |
| `src/playcalls/join.py` | Align charting rows to PFF plays; emit the match report. |
| `src/playcalls/analysis.py` | Success-rate cuts and tendency tables. Pure functions over the joined frame. |
| `src/playcalls/report.py` | Render result tables to Markdown. |
| `run.py` | CLI entry point wiring the stages together. |
| `tests/` | One test module per source module. |
| `outputs/` | Derived tables, match reports, and the final report. Committed. |

---

## Task 1: Add the three missing premium categories to PFF_Data_Project

This task is in the **sister repo**, not this one. It ends with `pff.db` containing `team_play`, `rushing` and `quarterback_charting` for every Baylor 2024 and 2025 game.

**Files:**
- Modify: `/Users/kristinarash/DEV/Football/PFF_Data_Project/src/ingest/pipeline.py:26`
- Modify: `/Users/kristinarash/DEV/Football/PFF_Data_Project/docs/pff_api_notes.md`
- Modify: `/Users/kristinarash/DEV/Football/PFF_Data_Project/src/db.py:12`
- Test: `/Users/kristinarash/DEV/Football/PFF_Data_Project/tests/test_pipeline.py`

**Interfaces:**
- Consumes: `PFFClient.get_premium_game(game_id, category)` — already exists at `src/ingest/pff_client.py:178`, works for any category string.
- Produces: rows in `pff_premium` with `category` ∈ {`team_play`, `rushing`, `quarterback_charting`} for Baylor games in seasons 2024 and 2025.

- [ ] **Step 1: Write the failing test**

Add to `/Users/kristinarash/DEV/Football/PFF_Data_Project/tests/test_pipeline.py`:

```python
from src.ingest.pipeline import PREMIUM_CATEGORIES


def test_premium_categories_include_play_level_feeds():
    """team_play, rushing and quarterback_charting are play-level feeds keyed by
    play_id. The play-call analysis needs all three: team_play is the master play
    list, rushing carries def_package for run plays, and quarterback_charting is
    the only source of per-play coverage."""
    for category in ("team_play", "rushing", "quarterback_charting"):
        assert category in PREMIUM_CATEGORIES
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/kristinarash/DEV/Football/PFF_Data_Project
/Users/kristinarash/.local/bin/uv run --with pytest --with requests --with PyJWT --with python-dotenv --with duckdb --with pandas --with pyyaml pytest tests/test_pipeline.py::test_premium_categories_include_play_level_feeds -v
```

Expected: FAIL — `AssertionError` on `team_play`.

- [ ] **Step 3: Add the three categories**

`src/ingest/pipeline.py` line 26. Replace:

```python
PREMIUM_CATEGORIES = ["passing", "pass_rush", "pressure", "pass_protection"]
```

with:

```python
# Play-level feeds, all keyed by play_id:
#   team_play             master play list (down, distance, field_position, personnel)
#   rushing               run-side detail incl. def_package
#   quarterback_charting  per-play coverage; dropbacks only
PREMIUM_CATEGORIES = [
    "passing",
    "pass_rush",
    "pressure",
    "pass_protection",
    "team_play",
    "rushing",
    "quarterback_charting",
]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/kristinarash/DEV/Football/PFF_Data_Project
/Users/kristinarash/.local/bin/uv run --with pytest --with requests --with PyJWT --with python-dotenv --with duckdb --with pandas --with pyyaml pytest tests/test_pipeline.py -v
```

Expected: PASS, and no existing test broken.

- [ ] **Step 5: Correct the two stale "no play-by-play" claims**

Both files assert the premium feeds are not play-level. The 2026-09-07 probe in `data/week1_auburn/` disproves this — `premium_team_play.json` carries `play_id`, `down`, `distance`, `field_position` per play.

In `src/db.py`, line 12, replace the phrase:

```
replaced with `pff_premium`, because the PFF API exposes no raw play-by-play — its
```

with:

```
replaced with `pff_premium`. NOTE (2026-09-09): an earlier note here claimed the PFF
API exposes no raw play-by-play. That is wrong. The premium feeds ARE play-level,
keyed by play_id — verified against team_play/rushing/quarterback_charting payloads. Its
```

In `docs/pff_api_notes.md`, find the Premium section note reading "these are *aggregated advanced stats per player/team per game* — **not raw play-by-play**" and replace it with:

```
**Corrected 2026-09-09:** these feeds ARE play-level. Every row carries `play_id`.
`team_play` is the master play list (down, distance, field_position, offense/defense,
offense_players, defense_players, shotgun, play_action, screen, draw, no_huddle).
`quarterback_charting` carries per-play `coverage_type` (93% filled on the game
sampled). `rushing` carries `def_package`. The original claim in this file predates the
2026-09-07 probe in `data/week1_auburn/` and was never true.
```

- [ ] **Step 6: Backfill Baylor 2024 and 2025 for the three new categories**

Run the pipeline's premium refresh for the two seasons. Inspect `run_pipeline.py --help` first to get the exact flag names; do not guess them.

```bash
cd /Users/kristinarash/DEV/Football/PFF_Data_Project
/Users/kristinarash/.local/bin/uv run --with requests --with PyJWT --with python-dotenv --with duckdb --with pandas --with pyyaml python run_pipeline.py --help
```

Then run the premium fetch scoped to seasons 2024 and 2025.

This makes ~150 API calls (25 games × 3 categories × 2 seasons of scope). If the pipeline has no season filter, add one rather than refetching all seasons and all categories.

- [ ] **Step 7: Verify the backfill landed**

```bash
/Users/kristinarash/.local/bin/uv run --with duckdb python3 -c "
import duckdb
c = duckdb.connect('/Users/kristinarash/DEV/Football/PFF_Data_Project/data/pff.db', read_only=True)
q = '''
select p.season, p.category, count(*) rows, count(distinct p.game_id) games
from pff_premium p
join games g on g.game_id = p.game_id
where g.is_baylor_game and p.season in (2024, 2025)
  and p.category in ('team_play','rushing','quarterback_charting')
group by 1,2 order by 1,2
'''
for r in c.execute(q).fetchall():
    print(r)
"
```

Expected: 6 rows. `games` must be **13** for every 2024 category and **12** for every 2025 category. Anything less means games were missed — investigate before continuing.

- [ ] **Step 8: Commit (in the sister repo)**

```bash
cd /Users/kristinarash/DEV/Football/PFF_Data_Project
git add src/ingest/pipeline.py src/db.py docs/pff_api_notes.md tests/test_pipeline.py
git commit -m "Add play-level premium categories and correct the play-by-play claim

team_play, rushing and quarterback_charting are play-level feeds keyed by
play_id. Two places in this repo asserted the premium feeds were per-game
aggregates with no play-by-play; the 2026-09-07 probe in data/week1_auburn
disproves that, so both notes are corrected rather than left to mislead the
next reader.

Backfilled Baylor 2024 (13 games) and 2025 (12 games) for the three new
categories. Consumed by PlayCalls_SuccessRate_EPA, which reads this DB
read-only."
```

---

## Task 2: Scaffold this repo and load the charting CSVs

**Files:**
- Create: `requirements.txt`, `src/playcalls/__init__.py`, `src/playcalls/charting.py`, `tests/__init__.py`, `tests/test_charting.py`, `pytest.ini`
- Modify: `.gitignore`

**Interfaces:**
- Produces:
  - `load_season(path: str) -> pandas.DataFrame` — one row per charted play, cleaned.
  - Columns guaranteed on the returned frame: `season:int`, `game_code:str`, `play_no:int`, `def_team:str`, `down:int`, `distance:int`, `yards_to_goal:int`, `gain:int`, `efficiency:str`, `explosive:bool`, `run_pass:str`, `play_result:str`, `personnel:str`, `full_play_call:str`, `formation:str`, `form_fam:str`, `motion:str`, `run:str`, `pro_fam:str`, `pass_concept:str`, `play_type:str`, `def_personnel:str`, `box_count:int`, `qb:str`, `front:str`, `cover_family:str`.
  - `SUCCESS_RATE_EXCLUDED = ("X", "")` — `Efficiency` values excluded from the denominator.

- [ ] **Step 1: Create the environment and dependency list**

```bash
cd /Users/kristinarash/DEV/PlayCalls_SuccessRate_EPA
cat > requirements.txt <<'EOF'
pandas>=2.2
duckdb>=0.10
pytest>=8.0
EOF
/Users/kristinarash/.local/bin/uv venv
/Users/kristinarash/.local/bin/uv pip install -r requirements.txt
mkdir -p src/playcalls tests outputs
touch src/playcalls/__init__.py tests/__init__.py
cat > pytest.ini <<'EOF'
[pytest]
testpaths = tests
pythonpath = .
EOF
printf '\n.venv/\n' >> .gitignore
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_charting.py`. These assert the real traps from spec §6.4, using the real files as fixtures.

```python
import pandas as pd
import pytest

from src.playcalls.charting import load_season

CSV_2024 = "2024_All_Games.csv"
CSV_2025 = "2025_All_Games.csv"


@pytest.fixture(scope="module")
def df25():
    return load_season(CSV_2025)


@pytest.fixture(scope="module")
def df24():
    return load_season(CSV_2024)


def test_bom_is_stripped_from_first_column(df25):
    """Every header carries a UTF-8 BOM. Without utf-8-sig the first column
    becomes '﻿#' and every lookup on it fails."""
    assert not any(c.startswith("﻿") for c in df25.columns)


def test_name_comma_does_not_shift_columns(df25):
    """Name is quoted and contains a comma ("2501 BU OFF vs AUB, Play 001").
    Naive splitting shifts every later column by one."""
    assert df25["def_team"].str.fullmatch(r"[A-Z]{4}").all()


def test_negative_yardage_apostrophe_is_cast(df25):
    """pff_GAINLOSS is a string with a leading apostrophe on negatives ('-1)."""
    assert df25["gain"].dtype.kind == "i"
    assert (df25["gain"] < 0).sum() > 0


def test_yards_to_goal_is_unsigned_int(df25):
    assert df25["yards_to_goal"].dtype.kind == "i"
    assert df25["yards_to_goal"].between(1, 99).all()


def test_junk_defteam_rows_are_dropped(df24):
    """9 rows in 2024 carry drill names in pff_DEFTEAM (HAL SPEED CUT,
    THROW BY JC, SPLIT RELEASE, 'm'). They are not games."""
    assert len(df24) == 957 - 9
    assert df24["def_team"].str.fullmatch(r"[A-Z]{4}").all()


def test_game_code_parses_for_both_naming_formats(df24, df25):
    """2023-2025 use YYGG. 12 games in 2025, 13 in 2024."""
    assert df25["game_code"].nunique() == 12
    assert df24["game_code"].nunique() == 13


def test_season_is_set(df24, df25):
    assert (df24["season"] == 2024).all()
    assert (df25["season"] == 2025).all()


def test_success_rate_matches_known_values(df24, df25):
    """Regression anchors from the spec. 2024 is post-junk-drop."""
    from src.playcalls.charting import success_rate

    assert round(success_rate(df24) * 100, 1) == 57.4
    assert round(success_rate(df25) * 100, 1) == 49.5


def test_explosive_blank_means_not_explosive(df25):
    """EXPL is Y or blank. Blank is False, not missing."""
    assert df25["explosive"].dtype == bool
    assert df25["explosive"].sum() == 73
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/kristinarash/DEV/PlayCalls_SuccessRate_EPA
.venv/bin/pytest tests/test_charting.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.playcalls.charting'`.

- [ ] **Step 4: Implement the loader**

Create `src/playcalls/charting.py`:

```python
"""Load and clean the Baylor offensive play-call charting CSVs.

Every trap documented in the design spec section 6.4 is handled here so that no
downstream module has to know about them.
"""

from __future__ import annotations

import re

import pandas as pd

# Efficiency values excluded from the success-rate denominator. "X" is a
# victory-formation kneel or a penalty; blank is ungraded.
SUCCESS_RATE_EXCLUDED = ("X", "")

# Charting column -> our name. Only columns we actually use are carried forward.
_COLUMNS = {
    "#": "play_no",
    "Name": "name",
    "pff_DEFTEAM": "def_team",
    "pff_DRIVE": "drive",
    "pff_DRIVEENDEVENT": "drive_end",
    "pff_DOWN": "down",
    "pff_DISTANCE": "distance",
    "pff_FIELDPOSITION": "field_position",
    "pff_YARDSTOGOALLINE": "yards_to_goal",
    "pff_GAINLOSS": "gain",
    "Efficiency": "efficiency",
    "EXPL": "explosive",
    "aapff_RUNPASS": "run_pass",
    "Play Result": "play_result",
    "Personnel": "personnel",
    "Full Play Call": "full_play_call",
    "Formation": "formation",
    "Form Fam": "form_fam",
    "Motion": "motion",
    "Run": "run",
    "Pro Fam": "pro_fam",
    "Pass Concept": "pass_concept",
    "Play Type": "play_type",
    "pff_DEFPERSONNEL": "def_personnel",
    "pff_BOXPLAYERS": "box_players",
    "Front": "front",
    "Cover Family": "cover_family",
    "QB#": "qb",
}

_INT_COLUMNS = ("play_no", "down", "distance", "yards_to_goal", "gain", "drive")


def _to_int(series: pd.Series) -> pd.Series:
    """Cast a charting numeric column to int.

    Negative values arrive as Excel-guarded strings with a leading apostrophe
    ("'-1"). Field position additionally uses "'+18" for opponent territory.
    """
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace("'", "", regex=False)
        .str.replace("+", "", regex=False)
        .replace({"": None, "nan": None})
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0).astype(int)


def _box_count(series: pd.Series) -> pd.Series:
    """pff_BOXPLAYERS is a compound string: a box count, then the defenders.

    "6; ALAU D00 (30); ALAU D15 (29); ..." -> 6
    """
    first = series.astype(str).str.split(";").str[0].str.strip()
    return pd.to_numeric(first, errors="coerce").fillna(0).astype(int)


def _season_from_path(path: str) -> int:
    match = re.search(r"(\d{4})_All_Games\.csv$", path)
    if not match:
        raise ValueError(f"cannot infer season from path: {path}")
    return int(match.group(1))


def load_season(path: str) -> pd.DataFrame:
    """Read one season CSV and return a cleaned frame, one row per charted play."""
    raw = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")

    missing = set(_COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f"{path} is missing expected columns: {sorted(missing)}")

    df = raw[list(_COLUMNS)].rename(columns=_COLUMNS).copy()
    df = df.apply(lambda s: s.str.strip() if s.dtype == object else s)

    # Drop rows whose opponent code is not a real 4-letter PFF team code. In 2024
    # nine rows carry drill names (HAL SPEED CUT, THROW BY JC, SPLIT RELEASE, "m").
    df = df[df["def_team"].str.fullmatch(r"[A-Z]{4}")].copy()

    for column in _INT_COLUMNS:
        df[column] = _to_int(df[column])

    df["box_count"] = _box_count(df["box_players"])
    df = df.drop(columns=["box_players"])

    # EXPL is "Y" or blank. Blank means not explosive, not missing.
    df["explosive"] = df["explosive"].eq("Y")

    df["season"] = _season_from_path(path)
    # "2501 BU OFF vs AUB, Play 001" -> "2501"
    df["game_code"] = df["name"].str.split(",").str[0].str.split().str[0]

    return df.reset_index(drop=True)


def success_rate(df: pd.DataFrame) -> float:
    """Fraction of graded plays marked efficient.

    X and blank are excluded from both numerator and denominator.
    """
    graded = df[~df["efficiency"].isin(SUCCESS_RATE_EXCLUDED)]
    if graded.empty:
        return float("nan")
    return float(graded["efficiency"].eq("Y").mean())
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd /Users/kristinarash/DEV/PlayCalls_SuccessRate_EPA
.venv/bin/pytest tests/test_charting.py -v
```

Expected: all PASS. If `test_success_rate_matches_known_values` fails, the cleaning changed the denominator — do not adjust the expected numbers to match; find out why.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt pytest.ini .gitignore src/ tests/
git commit -m "Load and clean the Baylor charting CSVs

Handles every trap from spec 6.4 in one place: the UTF-8 BOM, the comma inside
the quoted Name field, apostrophe-guarded negative yardage, the compound
pff_BOXPLAYERS string, and the nine 2024 rows carrying drill names in the
opponent column.

Tests anchor on the known season success rates (57.4% and 49.5%) so a future
cleaning change that shifts the denominator fails loudly instead of quietly
moving the headline number."
```

---

## Task 3: Read play-level PFF data out of the DuckDB

**Files:**
- Create: `src/playcalls/pff.py`, `tests/test_pff.py`

**Interfaces:**
- Consumes: `pff.db` (read-only), categories loaded in Task 1.
- Produces:
  - `PFF_DB_PATH: str` — module constant.
  - `load_plays(game_id: str, db_path: str = PFF_DB_PATH) -> pandas.DataFrame` — one row per `play_id` for that game, offense side only, with columns `play_id:int`, `offense:str`, `defense:str`, `down:int`, `distance:int`, `field_position:str`, `quarter:int`, `game_clock:str`, `shotgun:int`, `play_action:int`, `screen:int`, `draw:int`, `no_huddle:int`, `st_play_type:str`.
  - `load_category(game_id: str, category: str, db_path: str = PFF_DB_PATH) -> pandas.DataFrame` — flattened `raw_json` for one category, one row per source row.
  - `baylor_games(season: int, db_path: str = PFF_DB_PATH) -> pandas.DataFrame` — columns `game_id:str`, `week:int`, `game_date`, `opponent_code:str`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_pff.py`:

```python
import pandas as pd
import pytest

from src.playcalls.pff import PFF_DB_PATH, baylor_games, load_category, load_plays

GAME_2025_WK1 = "28762"  # Baylor vs Auburn, 2025-08-30


def test_baylor_2025_has_twelve_games():
    games = baylor_games(2025)
    assert len(games) == 12
    assert games["week"].is_monotonic_increasing


def test_baylor_2024_has_thirteen_games():
    assert len(baylor_games(2024)) == 13


def test_load_plays_returns_one_row_per_play_id():
    plays = load_plays(GAME_2025_WK1)
    assert plays["play_id"].is_unique
    assert len(plays) > 0


def test_load_plays_is_offense_only():
    plays = load_plays(GAME_2025_WK1)
    assert (plays["offense"] == "TXBA").all()


def test_quarterback_charting_has_coverage():
    """Coverage is the field the 2025 Baylor charting lost entirely."""
    qc = load_category(GAME_2025_WK1, "quarterback_charting")
    assert "coverage_type" in qc.columns
    assert qc["coverage_type"].notna().mean() > 0.5


def test_rushing_has_def_package():
    """Run plays get their defensive context from def_package, not coverage."""
    rush = load_category(GAME_2025_WK1, "rushing")
    assert "def_package" in rush.columns
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/test_pff.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.playcalls.pff'`.

- [ ] **Step 3: Implement the reader**

Create `src/playcalls/pff.py`:

```python
"""Read play-level PFF data out of PFF_Data_Project's DuckDB.

This module is read-only by contract. PFF_Data_Project owns ingest; this repo
never writes to pff.db, never calls the PFF API and never holds credentials.
"""

from __future__ import annotations

import json

import duckdb
import pandas as pd

PFF_DB_PATH = "/Users/kristinarash/DEV/Football/PFF_Data_Project/data/pff.db"

BAYLOR_CODE = "TXBA"


def _connect(db_path: str):
    return duckdb.connect(db_path, read_only=True)


def load_category(
    game_id: str, category: str, db_path: str = PFF_DB_PATH
) -> pd.DataFrame:
    """Flatten one premium category's raw_json into a frame, one row per source row."""
    with _connect(db_path) as con:
        rows = con.execute(
            "select raw_json from pff_premium "
            "where game_id = ? and category = ? order by row_seq",
            [str(game_id), category],
        ).fetchall()

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([json.loads(r[0]) for r in rows])


def load_plays(game_id: str, db_path: str = PFF_DB_PATH) -> pd.DataFrame:
    """Baylor-offense plays for one game, from the team_play master list."""
    team_play = load_category(game_id, "team_play", db_path)
    if team_play.empty:
        raise ValueError(
            f"no team_play rows for game {game_id}; run the Task 1 backfill first"
        )

    plays = team_play[team_play["offense"] == BAYLOR_CODE].copy()

    keep = [
        "play_id", "offense", "defense", "down", "distance", "field_position",
        "quarter", "game_clock", "shotgun", "play_action", "screen", "draw",
        "no_huddle", "st_play_type",
    ]
    for column in keep:
        if column not in plays.columns:
            plays[column] = None

    plays = plays[keep].drop_duplicates(subset="play_id")
    return plays.sort_values("play_id").reset_index(drop=True)


def baylor_games(season: int, db_path: str = PFF_DB_PATH) -> pd.DataFrame:
    """Baylor's games for a season, in week order, with the opponent's PFF code.

    The opponent code is read from the premium payload rather than the teams
    table: teams.abbreviation is "AUBURN", but the payloads and the Baylor
    charting file both use the four-character form "ALAU".
    """
    with _connect(db_path) as con:
        games = con.execute(
            "select game_id, week, start_time::date as game_date "
            "from games where is_baylor_game and season = ? order by week",
            [season],
        ).fetchdf()

    opponents = []
    for game_id in games["game_id"]:
        team_play = load_category(str(game_id), "team_play", db_path)
        if team_play.empty:
            opponents.append(None)
            continue
        baylor_rows = team_play[team_play["offense"] == BAYLOR_CODE]
        opponents.append(
            baylor_rows["defense"].mode().iat[0] if not baylor_rows.empty else None
        )

    games["opponent_code"] = opponents
    games["game_id"] = games["game_id"].astype(str)
    return games
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_pff.py -v
```

Expected: all PASS. A failure on `test_load_plays_returns_one_row_per_play_id` means Task 1's backfill did not land — go back and check step 7 of Task 1.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/pff.py tests/test_pff.py
git commit -m "Read play-level PFF data from the sister project's DuckDB

Read-only by contract. Opponent codes come from the premium payloads rather
than the teams table, because teams.abbreviation is AUBURN while both the
payloads and Baylor's charting file use the four-character ALAU form. That
shared code is what makes the game mapping in the next task possible."
```

---

## Task 4: Map CSV games to PFF games, then join and report the match rate

**This task is a gate.** It ends with a number. If that number is below 95%, stop and report rather than continuing.

**Files:**
- Create: `src/playcalls/gamemap.py`, `src/playcalls/join.py`, `tests/test_gamemap.py`, `tests/test_join.py`
- Output: `outputs/match_report.csv`

**Interfaces:**
- Consumes: `load_season` (Task 2), `load_plays`/`baylor_games` (Task 3).
- Produces:
  - `map_games(season: int) -> dict[str, str]` — CSV `game_code` (`"2501"`) to PFF `game_id` (`"28762"`).
  - `join_game(chart_df, plays_df) -> tuple[pandas.DataFrame, pandas.DataFrame]` — `(joined, unmatched)`. `joined` carries every charting column plus `play_id` and the PFF play columns.
  - `match_rate(joined, chart_df) -> float`.

- [ ] **Step 1: Write the failing test for the game map**

Create `tests/test_gamemap.py`:

```python
from src.playcalls.gamemap import map_games


def test_2025_maps_all_twelve_games():
    mapping = map_games(2025)
    assert len(mapping) == 12


def test_2025_week1_maps_to_auburn():
    """CSV 2501 vs AUB is PFF game 28762, Baylor vs Auburn, 2025-08-30."""
    assert map_games(2025)["2501"] == "28762"


def test_2024_maps_all_thirteen_games():
    assert len(map_games(2024)) == 13


def test_mapping_is_injective():
    """Two CSV games must never point at the same PFF game."""
    mapping = map_games(2025)
    assert len(set(mapping.values())) == len(mapping)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_gamemap.py -v
```

Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Implement the game map**

Create `src/playcalls/gamemap.py`:

```python
"""Map Baylor charting game codes to PFF game ids.

The charting file's pff_DEFTEAM column and PFF's premium payloads use the same
four-character opponent code (ALAU, TXCU, OKST), which makes the mapping a
lookup rather than a guess. Week order is used as a cross-check.
"""

from __future__ import annotations

import pandas as pd

from src.playcalls.charting import load_season
from src.playcalls.pff import baylor_games


def map_games(season: int) -> dict[str, str]:
    """Return {csv_game_code: pff_game_id} for one season.

    Raises if the two sources disagree, rather than silently mapping a
    charting game onto the wrong PFF game.
    """
    chart = load_season(f"{season}_All_Games.csv")
    pff = baylor_games(season)

    # CSV games in code order; the code's trailing digits are the game number.
    chart_games = (
        chart[["game_code", "def_team"]]
        .drop_duplicates("game_code")
        .sort_values("game_code")
        .reset_index(drop=True)
    )

    by_opponent: dict[str, list[str]] = {}
    for _, row in pff.iterrows():
        by_opponent.setdefault(row["opponent_code"], []).append(row["game_id"])

    mapping: dict[str, str] = {}
    for _, row in chart_games.iterrows():
        candidates = by_opponent.get(row["def_team"], [])
        if len(candidates) != 1:
            raise ValueError(
                f"{season} game {row['game_code']} vs {row['def_team']}: "
                f"expected exactly one PFF game, found {len(candidates)}"
            )
        mapping[row["game_code"]] = candidates[0]

    if len(set(mapping.values())) != len(mapping):
        raise ValueError(f"{season}: two charting games mapped to one PFF game")

    return mapping
```

- [ ] **Step 4: Run test to verify it passes**

```bash
.venv/bin/pytest tests/test_gamemap.py -v
```

Expected: PASS. If a season raises "expected exactly one PFF game", Baylor played that opponent twice (a rematch) — extend the function to disambiguate on week order before continuing.

- [ ] **Step 5: Write the failing test for the join**

Create `tests/test_join.py`:

```python
import pandas as pd

from src.playcalls.charting import load_season
from src.playcalls.gamemap import map_games
from src.playcalls.join import join_game, match_rate
from src.playcalls.pff import load_plays


def test_join_one_game_matches_at_least_95_percent():
    """The gate. Below 95% the approach is wrong and analysis must not proceed."""
    chart = load_season("2025_All_Games.csv")
    game = chart[chart["game_code"] == "2501"]
    plays = load_plays(map_games(2025)["2501"])

    joined, _ = join_game(game, plays)
    assert match_rate(joined, game) >= 0.95


def test_join_never_duplicates_a_charting_row():
    chart = load_season("2025_All_Games.csv")
    game = chart[chart["game_code"] == "2501"]
    plays = load_plays(map_games(2025)["2501"])

    joined, _ = join_game(game, plays)
    assert len(joined) <= len(game)
    assert joined["play_no"].is_unique


def test_join_never_reuses_a_pff_play():
    chart = load_season("2025_All_Games.csv")
    game = chart[chart["game_code"] == "2501"]
    plays = load_plays(map_games(2025)["2501"])

    joined, _ = join_game(game, plays)
    matched = joined[joined["play_id"].notna()]
    assert matched["play_id"].is_unique
```

- [ ] **Step 6: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_join.py -v
```

Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 7: Implement the join**

Create `src/playcalls/join.py`:

```python
"""Align Baylor charting rows to PFF plays.

The charting file has no play_id. The only shared keys are down, distance and
field position, and those collide on every drive that starts first-and-ten from
the 25. So the join is greedy and ordered: both sides are sorted into play
order, and each charting row takes the earliest still-unclaimed PFF play that
agrees on down, distance and yards-to-goal.

Ordering is what breaks the ties. A repeated 1st-and-10-from-the-25 in the
fourth quarter cannot claim a first-quarter play, because the first-quarter
play was consumed earlier in the sweep.
"""

from __future__ import annotations

import pandas as pd

BAYLOR_CODE = "TXBA"


def _yards_to_goal(field_position: str) -> int | None:
    """PFF field_position is "TXBA 22" (own 22) or "ALAU 49" (opponent 49)."""
    if not isinstance(field_position, str) or " " not in field_position:
        return None
    team, _, yard = field_position.partition(" ")
    try:
        yard_line = int(yard)
    except ValueError:
        return None
    return 100 - yard_line if team == BAYLOR_CODE else yard_line


def join_game(
    chart_df: pd.DataFrame, plays_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (joined, unmatched_pff_plays) for a single game."""
    chart = chart_df.sort_values("play_no").reset_index(drop=True)

    plays = plays_df.copy()
    plays["yards_to_goal"] = plays["field_position"].map(_yards_to_goal)
    plays = plays.sort_values("play_id").reset_index(drop=True)
    plays["_claimed"] = False

    pff_columns = [
        "play_id", "defense", "quarter", "game_clock", "shotgun",
        "play_action", "screen", "draw", "no_huddle", "st_play_type",
    ]

    matched_rows = []
    for _, row in chart.iterrows():
        candidates = plays[
            (~plays["_claimed"])
            & (plays["down"] == row["down"])
            & (plays["distance"] == row["distance"])
            & (plays["yards_to_goal"] == row["yards_to_goal"])
        ]
        record = row.to_dict()
        if candidates.empty:
            record.update({column: None for column in pff_columns})
        else:
            index = candidates.index[0]
            plays.loc[index, "_claimed"] = True
            for column in pff_columns:
                record[column] = plays.loc[index, column]
        matched_rows.append(record)

    joined = pd.DataFrame(matched_rows)
    unmatched = plays[~plays["_claimed"]].drop(columns="_claimed")
    return joined, unmatched.reset_index(drop=True)


def match_rate(joined: pd.DataFrame, chart_df: pd.DataFrame) -> float:
    """Fraction of charting rows that found a PFF play."""
    if len(chart_df) == 0:
        return float("nan")
    return float(joined["play_id"].notna().sum() / len(chart_df))
```

- [ ] **Step 8: Run test — this is the gate**

```bash
.venv/bin/pytest tests/test_join.py -v
```

Expected: PASS.

**If `test_join_one_game_matches_at_least_95_percent` fails, STOP.** Do not lower the threshold, do not proceed to Task 5. Print the actual rate and a sample of unmatched rows, then report to Eric with the number and what the misses look like. The spec's fallback strategies (drive-scoped alignment, sequence alignment on the `#` column) are the next thing to try, and that is a decision to surface, not to make silently.

- [ ] **Step 9: Write the full match report across all 25 games**

Create `run.py` at the repo root:

```python
"""Phase 1 entry point."""

from __future__ import annotations

import sys

import pandas as pd

from src.playcalls.charting import load_season
from src.playcalls.gamemap import map_games
from src.playcalls.join import join_game, match_rate
from src.playcalls.pff import load_plays

SEASONS = (2024, 2025)


def build_joined() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Join every game in both seasons. Returns (joined, match_report)."""
    joined_frames, report_rows = [], []

    for season in SEASONS:
        chart = load_season(f"{season}_All_Games.csv")
        mapping = map_games(season)

        for game_code, game_id in sorted(mapping.items()):
            game_chart = chart[chart["game_code"] == game_code]
            plays = load_plays(game_id)
            joined, unmatched = join_game(game_chart, plays)

            joined_frames.append(joined)
            report_rows.append({
                "season": season,
                "game_code": game_code,
                "pff_game_id": game_id,
                "charted_plays": len(game_chart),
                "matched": int(joined["play_id"].notna().sum()),
                "match_rate": round(match_rate(joined, game_chart), 4),
                "pff_plays_unclaimed": len(unmatched),
            })

    return pd.concat(joined_frames, ignore_index=True), pd.DataFrame(report_rows)


def main() -> int:
    joined, report = build_joined()
    joined.to_parquet("outputs/joined_plays.parquet", index=False)
    report.to_csv("outputs/match_report.csv", index=False)

    overall = report["matched"].sum() / report["charted_plays"].sum()
    print(report.to_string(index=False))
    print(f"\noverall match rate: {overall:.1%}")

    if overall < 0.95:
        print("\nGATE FAILED: overall match rate below 95%. Stop and report.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 10: Run it across all 25 games**

```bash
cd /Users/kristinarash/DEV/PlayCalls_SuccessRate_EPA
.venv/bin/python run.py
```

Expected: exit 0, a per-game table, and an overall rate at or above 95%. A single game far below the others is more informative than the average — inspect it before moving on.

- [ ] **Step 11: Commit**

```bash
git add src/playcalls/gamemap.py src/playcalls/join.py tests/test_gamemap.py tests/test_join.py run.py outputs/match_report.csv
git commit -m "Join charting rows to PFF plays and report the match rate

The charting file has no play_id, and down/distance/yardline collide on every
post-touchback drive, so the join is a greedy ordered sweep: each charting row
claims the earliest unclaimed PFF play that agrees on all three. Ordering is
what breaks the ties.

The 95% match rate is enforced as a test and as a non-zero exit from run.py,
because an unproven join produces confident wrong numbers rather than errors."
```

---

## Task 5: Classify the unmatched plays and resolve the run-count gap

**This task is a gate.** Baylor charted 20 runs in 2025 game 1 where PFF has 43. Either PFF counts more things as runs, or the charting file is missing plays and every success rate is computed on an incomplete denominator.

**Files:**
- Create: `src/playcalls/unmatched.py`, `tests/test_unmatched.py`
- Output: `outputs/unmatched_classification.csv`

**Interfaces:**
- Consumes: `join_game` (Task 4), `load_category` (Task 3).
- Produces:
  - `classify_unmatched(unmatched_plays, rushing_df, passing_df) -> pandas.DataFrame` — adds a `classification` column with one of `kneel`, `scramble`, `sack`, `penalty_negated`, `special_teams`, `designed_run_missing`, `unknown`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_unmatched.py`:

```python
import pandas as pd

from src.playcalls.unmatched import CLASSIFICATIONS, classify_unmatched


def test_every_row_gets_a_classification():
    unmatched = pd.DataFrame([
        {"play_id": 1, "st_play_type": "kickoff_tb", "down": 0, "distance": 0},
        {"play_id": 2, "st_play_type": None, "down": 1, "distance": 10},
    ])
    result = classify_unmatched(unmatched, pd.DataFrame(), pd.DataFrame())
    assert result["classification"].isin(CLASSIFICATIONS).all()


def test_special_teams_plays_are_labelled():
    unmatched = pd.DataFrame([
        {"play_id": 1, "st_play_type": "kickoff_tb", "down": 0, "distance": 0},
    ])
    result = classify_unmatched(unmatched, pd.DataFrame(), pd.DataFrame())
    assert result.loc[0, "classification"] == "special_teams"


def test_designed_run_with_no_charting_row_is_flagged():
    """The dangerous case: a real run play PFF saw and the chart did not."""
    unmatched = pd.DataFrame([
        {"play_id": 99, "st_play_type": None, "down": 2, "distance": 7},
    ])
    rushing = pd.DataFrame([
        {"play_id": 99, "scramble": 0, "kneel": 0, "no_play": 0, "player": "RB"},
    ])
    result = classify_unmatched(unmatched, rushing, pd.DataFrame())
    assert result.loc[0, "classification"] == "designed_run_missing"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_unmatched.py -v
```

Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Inspect the real rushing columns before implementing**

The classifier keys off fields whose exact names must be confirmed, not assumed:

```bash
.venv/bin/python -c "
from src.playcalls.pff import load_category
rush = load_category('28762', 'rushing')
print(sorted(rush.columns))
print(rush[['play_id','down','distance']].head())
"
```

Note which of `scramble`, `kneel`, `no_play`, `qb_kneel`, `designed_run` actually exist. Use the real names in step 4; if a field this task assumes is absent, adapt the predicate rather than inventing the column.

- [ ] **Step 4: Implement the classifier**

Create `src/playcalls/unmatched.py`:

```python
"""Classify PFF plays that no charting row claimed.

The point is to separate benign accounting differences (PFF counts a kneel or a
scramble as a rush; the chart does not) from the dangerous case: a designed run
PFF recorded and the charting file simply does not contain.
"""

from __future__ import annotations

import pandas as pd

CLASSIFICATIONS = (
    "special_teams",
    "kneel",
    "scramble",
    "sack",
    "penalty_negated",
    "designed_run_missing",
    "designed_pass_missing",
    "unknown",
)


def _flag(frame: pd.DataFrame, play_id, column: str) -> bool:
    if frame.empty or column not in frame.columns:
        return False
    rows = frame[frame["play_id"] == play_id]
    return bool(not rows.empty and rows.iloc[0][column] in (1, True))


def classify_unmatched(
    unmatched: pd.DataFrame, rushing: pd.DataFrame, passing: pd.DataFrame
) -> pd.DataFrame:
    """Label each unclaimed PFF play. Order matters: most specific first."""
    result = unmatched.copy()
    labels = []

    for _, row in result.iterrows():
        play_id = row["play_id"]
        st_type = row.get("st_play_type")

        if isinstance(st_type, str) and st_type.strip():
            labels.append("special_teams")
        elif _flag(rushing, play_id, "kneel") or _flag(rushing, play_id, "qb_kneel"):
            labels.append("kneel")
        elif _flag(rushing, play_id, "scramble"):
            labels.append("scramble")
        elif _flag(passing, play_id, "sack"):
            labels.append("sack")
        elif _flag(rushing, play_id, "no_play") or _flag(passing, play_id, "no_play"):
            labels.append("penalty_negated")
        elif not rushing.empty and (rushing["play_id"] == play_id).any():
            labels.append("designed_run_missing")
        elif not passing.empty and (passing["play_id"] == play_id).any():
            labels.append("designed_pass_missing")
        else:
            labels.append("unknown")

    result["classification"] = labels
    return result
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_unmatched.py -v
```

Expected: all PASS.

- [ ] **Step 6: Run the classifier across all 25 games and read the answer**

Add to `run.py`, called from `main()` after the joined frame is built:

```python
def classify_all(mapping_by_season: dict[int, dict[str, str]]) -> pd.DataFrame:
    """Classify every unclaimed PFF play across both seasons."""
    from src.playcalls.pff import load_category
    from src.playcalls.unmatched import classify_unmatched

    frames = []
    for season, mapping in mapping_by_season.items():
        chart = load_season(f"{season}_All_Games.csv")
        for game_code, game_id in sorted(mapping.items()):
            game_chart = chart[chart["game_code"] == game_code]
            _, unmatched = join_game(game_chart, load_plays(game_id))
            if unmatched.empty:
                continue
            labelled = classify_unmatched(
                unmatched,
                load_category(game_id, "rushing"),
                load_category(game_id, "passing"),
            )
            labelled["season"] = season
            labelled["game_code"] = game_code
            frames.append(labelled)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
```

Run it and write `outputs/unmatched_classification.csv`, then print the summary:

```bash
.venv/bin/python -c "
import pandas as pd
df = pd.read_csv('outputs/unmatched_classification.csv')
print(df.groupby(['season','classification']).size().unstack(fill_value=0))
"
```

- [ ] **Step 7: Act on what the classification says**

**This is the gate.** Read the `designed_run_missing` count.

- **Near zero** — the gap is accounting. Record the mapping rules in the spec and continue.
- **Material** (say, more than 2% of charted plays in a season) — **stop.** The charting file is incomplete, and every success rate in this repo is computed on a partial denominator. Report to Eric with the count per season and per game before any analysis is written. Do not proceed to Task 6 on the assumption it will wash out.

Either way, record the finding in the spec's §6.1 so the answer is not rediscovered.

- [ ] **Step 8: Commit**

```bash
git add src/playcalls/unmatched.py tests/test_unmatched.py run.py outputs/unmatched_classification.csv docs/superpowers/specs/2026-09-09-playcalls-success-rate-epa-design.md
git commit -m "Classify unmatched PFF plays and settle the run-count gap

Baylor charted 20 runs in 2025 game 1 where PFF has 43. This separates the
benign explanations - kneels, scrambles, sacks charged as rushes, penalty
negated plays, special teams - from the one that matters: a designed run PFF
recorded and the charting file does not contain.

The finding is recorded in the spec rather than left in a commit message,
because it decides whether every success rate in this repo rests on a complete
denominator."
```

---

## Task 6: Normalise the play-call vocabulary and derive the Play Type crosswalk

**Files:**
- Create: `src/playcalls/normalise.py`, `tests/test_normalise.py`
- Output: `outputs/playtype_crosswalk.csv`, `outputs/concept_crosswalk.csv`

**Interfaces:**
- Consumes: `load_season` (Task 2).
- Produces:
  - `normalise_concept(value: str) -> str` — one concept string to canonical form.
  - `ABBREVIATIONS: dict[str, str]` — expansions like `{"RDY": "RANDY", "LRY": "LARRY"}`.
  - `derive_playtype_crosswalk(df_2024, df_2025) -> pandas.DataFrame` — columns `concept`, `play_type_2024`, `play_type_2025`, `reps_2024`, `reps_2025`, `confidence`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_normalise.py`:

```python
import pandas as pd

from src.playcalls.normalise import derive_playtype_crosswalk, normalise_concept


def test_separator_is_normalised():
    """2024 wrote IRENE/ITALY; 2025 writes IRENE.ITALY. Same play."""
    assert normalise_concept("IRENE/ITALY") == normalise_concept("IRENE.ITALY")


def test_abbreviations_are_expanded():
    """RDY/LRY in 2024 is RANDY.LARRY in 2025. Not a punctuation change."""
    assert normalise_concept("RDY/LRY") == normalise_concept("RANDY.LARRY")


def test_modifiers_are_stripped_to_base_concept():
    """2025 charts modifiers 2024 did not. Cross-year comparison is base only."""
    assert normalise_concept("RAZOR.BLADE SPLIT") == normalise_concept("RAZOR/BLADE")
    assert normalise_concept("RAZOR.BLADE SAME SIDE") == normalise_concept("RAZOR/BLADE")


def test_case_and_whitespace_are_normalised():
    assert normalise_concept("  gary.gail  ") == normalise_concept("GARY/GAIL")


def test_blank_stays_blank():
    assert normalise_concept("") == ""


def test_crosswalk_reports_reps_and_confidence():
    df24 = pd.DataFrame({"run": ["RAZOR/BLADE"] * 30, "play_type": ["CTR"] * 30})
    df25 = pd.DataFrame({"run": ["RAZOR.BLADE SPLIT"] * 25, "play_type": ["GAP"] * 25})

    crosswalk = derive_playtype_crosswalk(df24, df25)
    row = crosswalk[crosswalk["concept"] == "RAZOR BLADE"].iloc[0]

    assert row["play_type_2024"] == "CTR"
    assert row["play_type_2025"] == "GAP"
    assert row["reps_2024"] == 30
    assert row["reps_2025"] == 25
    assert row["confidence"] == "high"


def test_thin_evidence_is_marked_low_confidence():
    df24 = pd.DataFrame({"run": ["PLUNGE"], "play_type": ["PWR"]})
    df25 = pd.DataFrame({"run": ["PLUNGE"], "play_type": ["GAP"]})

    crosswalk = derive_playtype_crosswalk(df24, df25)
    assert crosswalk[crosswalk["concept"] == "PLUNGE"].iloc[0]["confidence"] == "low"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/test_normalise.py -v
```

Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Implement normalisation and crosswalk derivation**

Create `src/playcalls/normalise.py`:

```python
"""Normalise play-call vocabulary across 2024 and 2025, and derive the Play Type
crosswalk from evidence.

Eric was asked whether CTR+PWR maps to GAP and answered "not sure", so the
mapping is derived rather than guessed: a concept tagged CTR in 2024 and GAP in
2025 across many reps is the correspondence.
"""

from __future__ import annotations

import re

import pandas as pd

# 2024 shorthand -> the expanded form 2025 uses.
ABBREVIATIONS = {
    "RDY": "RANDY",
    "LRY": "LARRY",
}

# Modifiers 2025 charts that 2024 largely did not. Stripped for base-concept
# comparison; the unstripped value stays available for within-year work.
_MODIFIERS = ("SPLIT", "SAME SIDE", "SAME", "SLOW", "FAST")

_CONFIDENCE_THRESHOLD = 10


def normalise_concept(value: str) -> str:
    """Reduce a play-call concept to its canonical, cross-year comparable form."""
    if not isinstance(value, str):
        return ""

    text = value.strip().upper()
    if not text:
        return ""

    # Separators: 2024 used "/", 2025 uses ".". Both become a space.
    text = re.sub(r"[/.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = [ABBREVIATIONS.get(word, word) for word in text.split(" ")]
    text = " ".join(words)

    # Strip trailing modifiers, longest first so "SAME SIDE" beats "SAME".
    for modifier in sorted(_MODIFIERS, key=len, reverse=True):
        if text.endswith(" " + modifier):
            text = text[: -(len(modifier) + 1)].strip()

    return text


def _dominant(series: pd.Series) -> tuple[str, int]:
    """Most common non-blank value and its count."""
    values = series[series.astype(str).str.strip() != ""]
    if values.empty:
        return "", 0
    counts = values.value_counts()
    return str(counts.index[0]), int(counts.iloc[0])


def derive_playtype_crosswalk(
    df_2024: pd.DataFrame, df_2025: pd.DataFrame, concept_column: str = "run"
) -> pd.DataFrame:
    """Derive the 2024 -> 2025 Play Type mapping from shared concepts.

    Confidence is "high" when both years carry at least ten reps of the concept,
    otherwise "low". Concepts present in only one year are reported with a blank
    on the missing side rather than dropped.
    """
    frames = {}
    for year, df in ((2024, df_2024), (2025, df_2025)):
        working = df.copy()
        working["concept"] = working[concept_column].map(normalise_concept)
        frames[year] = working[working["concept"] != ""]

    concepts = sorted(set(frames[2024]["concept"]) | set(frames[2025]["concept"]))

    rows = []
    for concept in concepts:
        type_24, reps_24 = _dominant(
            frames[2024].loc[frames[2024]["concept"] == concept, "play_type"]
        )
        type_25, reps_25 = _dominant(
            frames[2025].loc[frames[2025]["concept"] == concept, "play_type"]
        )
        both_years = reps_24 > 0 and reps_25 > 0
        strong = reps_24 >= _CONFIDENCE_THRESHOLD and reps_25 >= _CONFIDENCE_THRESHOLD
        rows.append({
            "concept": concept,
            "play_type_2024": type_24,
            "play_type_2025": type_25,
            "reps_2024": reps_24,
            "reps_2025": reps_25,
            "confidence": "high" if (both_years and strong) else "low",
        })

    return pd.DataFrame(rows).sort_values(
        ["confidence", "reps_2025"], ascending=[True, False]
    ).reset_index(drop=True)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_normalise.py -v
```

Expected: all PASS.

- [ ] **Step 5: Produce the real crosswalk for Eric to sanity-check**

```bash
.venv/bin/python -c "
from src.playcalls.charting import load_season
from src.playcalls.normalise import derive_playtype_crosswalk

df24 = load_season('2024_All_Games.csv')
df25 = load_season('2025_All_Games.csv')

runs = derive_playtype_crosswalk(df24, df25, 'run')
runs.to_csv('outputs/playtype_crosswalk.csv', index=False)

high = runs[runs['confidence'] == 'high']
print(high.to_string(index=False))
print()
print('high-confidence concepts:', len(high), 'of', len(runs))
"
```

Read the high-confidence rows. If `RAZOR BLADE` shows `CTR` → `GAP` and `IRENE ITALY` shows `ZONE` → `ZONE`, the mapping hypothesis from the spec is confirmed by evidence rather than by guess.

- [ ] **Step 6: Surface the crosswalk to Eric before any cross-year number**

Present the high-confidence table. Ask only for a sanity check — is there a row where the derived mapping is football-wrong? Low-confidence and one-year-only concepts are reported as unmapped and excluded from cross-year `Play Type` comparison, not force-fitted.

- [ ] **Step 7: Commit**

```bash
git add src/playcalls/normalise.py tests/test_normalise.py outputs/playtype_crosswalk.csv
git commit -m "Derive the play-call crosswalk from evidence instead of guessing

Separator normalisation alone is not enough: RDY/LRY became RANDY.LARRY, which
is abbreviation expansion, and 2025 charts modifiers 2024 did not, so cross-year
comparison happens at base concept only.

The Play Type mapping is derived rather than asked for. A concept tagged CTR in
2024 and GAP in 2025 across thirty reps is the correspondence. Concepts with
thin evidence are marked low confidence and excluded from cross-year comparison
rather than force-fitted into a mapping nobody verified."
```

---

## Task 7: Success-rate and situational analysis

**Files:**
- Create: `src/playcalls/analysis.py`, `tests/test_analysis.py`
- Output: `outputs/tables/*.csv`

**Interfaces:**
- Consumes: `outputs/joined_plays.parquet` (Task 4), `normalise_concept` (Task 6).
- Produces:
  - `MIN_SAMPLE = 15`
  - `rate_by(df, *columns, min_sample=MIN_SAMPLE) -> pandas.DataFrame` — columns `<group columns>`, `plays:int`, `graded:int`, `success_rate:float`, `explosive_rate:float`. Groups below `min_sample` are dropped.
  - `situational_buckets(df) -> pandas.DataFrame` — adds `down_distance:str`, `field_zone:str`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_analysis.py`:

```python
import pandas as pd

from src.playcalls.analysis import MIN_SAMPLE, rate_by, situational_buckets


def _frame(n_success: int, n_fail: int, label: str = "ZONE") -> pd.DataFrame:
    rows = [{"play_type": label, "efficiency": "Y", "explosive": False}] * n_success
    rows += [{"play_type": label, "efficiency": "N", "explosive": False}] * n_fail
    return pd.DataFrame(rows)


def test_rate_by_computes_success_rate():
    result = rate_by(_frame(15, 5), "play_type")
    assert result.iloc[0]["success_rate"] == 0.75
    assert result.iloc[0]["graded"] == 20


def test_small_groups_are_suppressed():
    """Below MIN_SAMPLE a rate is noise. It is dropped, not printed."""
    result = rate_by(_frame(3, 2), "play_type")
    assert result.empty


def test_x_and_blank_are_excluded_from_the_denominator():
    df = pd.DataFrame(
        [{"play_type": "ZONE", "efficiency": "Y", "explosive": False}] * 10
        + [{"play_type": "ZONE", "efficiency": "N", "explosive": False}] * 10
        + [{"play_type": "ZONE", "efficiency": "X", "explosive": False}] * 5
        + [{"play_type": "ZONE", "efficiency": "", "explosive": False}] * 5
    )
    result = rate_by(df, "play_type")
    assert result.iloc[0]["graded"] == 20
    assert result.iloc[0]["plays"] == 30
    assert result.iloc[0]["success_rate"] == 0.5


def test_down_distance_buckets():
    df = pd.DataFrame([
        {"down": 1, "distance": 10, "yards_to_goal": 75},
        {"down": 3, "distance": 2, "yards_to_goal": 40},
        {"down": 3, "distance": 9, "yards_to_goal": 15},
    ])
    result = situational_buckets(df)
    assert result.loc[0, "down_distance"] == "1st & 10"
    assert result.loc[1, "down_distance"] == "3rd & short"
    assert result.loc[2, "down_distance"] == "3rd & long"
    assert result.loc[2, "field_zone"] == "red zone"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/test_analysis.py -v
```

Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Implement the analysis functions**

Create `src/playcalls/analysis.py`:

```python
"""Success-rate and situational cuts over the joined play table.

Pure functions. Every returned table carries its n, and groups thinner than
MIN_SAMPLE are dropped rather than printed as though they meant something.
"""

from __future__ import annotations

import pandas as pd

from src.playcalls.charting import SUCCESS_RATE_EXCLUDED

MIN_SAMPLE = 15


def rate_by(
    df: pd.DataFrame, *columns: str, min_sample: int = MIN_SAMPLE
) -> pd.DataFrame:
    """Success and explosive rate grouped by one or more columns."""
    if not columns:
        raise ValueError("rate_by needs at least one grouping column")

    working = df.copy()
    working["_graded"] = ~working["efficiency"].isin(SUCCESS_RATE_EXCLUDED)
    working["_success"] = working["_graded"] & working["efficiency"].eq("Y")

    grouped = working.groupby(list(columns), dropna=False).agg(
        plays=("efficiency", "size"),
        graded=("_graded", "sum"),
        successes=("_success", "sum"),
        explosives=("explosive", "sum"),
    ).reset_index()

    grouped = grouped[grouped["graded"] >= min_sample].copy()
    if grouped.empty:
        return grouped.drop(columns=["successes", "explosives"], errors="ignore")

    grouped["success_rate"] = grouped["successes"] / grouped["graded"]
    grouped["explosive_rate"] = grouped["explosives"] / grouped["plays"]

    return (
        grouped.drop(columns=["successes", "explosives"])
        .sort_values("success_rate", ascending=False)
        .reset_index(drop=True)
    )


def _down_distance(down: int, distance: int) -> str:
    names = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
    name = names.get(int(down), f"{int(down)}th")
    if int(down) == 1 and int(distance) == 10:
        return "1st & 10"
    if distance <= 3:
        return f"{name} & short"
    if distance <= 7:
        return f"{name} & medium"
    return f"{name} & long"


def _field_zone(yards_to_goal: int) -> str:
    if yards_to_goal <= 20:
        return "red zone"
    if yards_to_goal <= 40:
        return "fringe"
    if yards_to_goal >= 80:
        return "backed up"
    return "open field"


def situational_buckets(df: pd.DataFrame) -> pd.DataFrame:
    """Add down_distance and field_zone labels."""
    result = df.copy()
    result["down_distance"] = [
        _down_distance(d, dist)
        for d, dist in zip(result["down"], result["distance"])
    ]
    result["field_zone"] = result["yards_to_goal"].map(_field_zone)
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_analysis.py -v
```

Expected: all PASS.

- [ ] **Step 5: Generate the real tables**

```bash
mkdir -p outputs/tables
.venv/bin/python -c "
import pandas as pd
from src.playcalls.analysis import rate_by, situational_buckets
from src.playcalls.normalise import normalise_concept

df = pd.read_parquet('outputs/joined_plays.parquet')
df = situational_buckets(df)
df['concept'] = df['run'].map(normalise_concept)

cuts = {
    'by_season':        ('season',),
    'by_play_type':     ('season', 'play_type'),
    'by_concept':       ('season', 'concept'),
    'by_formation':     ('season', 'form_fam'),
    'by_personnel':     ('season', 'personnel'),
    'by_down_distance': ('season', 'down_distance'),
    'by_field_zone':    ('season', 'field_zone'),
    'by_run_pass':      ('season', 'run_pass'),
    'by_qb':            ('season', 'qb'),
    'by_box_count':     ('season', 'box_count'),
    'by_def_personnel': ('season', 'def_personnel'),
}
for name, columns in cuts.items():
    table = rate_by(df, *columns)
    table.to_csv(f'outputs/tables/{name}.csv', index=False)
    print(f'{name:20s} {len(table):3d} rows')
"
```

- [ ] **Step 6: Commit**

```bash
git add src/playcalls/analysis.py tests/test_analysis.py outputs/tables/
git commit -m "Add success-rate and situational cuts

Every table carries its n, and groups below fifteen graded plays are dropped
rather than printed. A 100% success rate on three reps is not a finding, and
publishing it as one is how a coach loses trust in the whole report.

Efficiency values X and blank are excluded from the denominator but still
counted in plays, so the gap between the two columns stays visible."
```

---

## Task 8: Versus-defence and coordinator tendency profile

**Files:**
- Modify: `src/playcalls/analysis.py`
- Modify: `tests/test_analysis.py`
- Output: `outputs/tables/vs_defense_*.csv`, `outputs/tables/tendency_*.csv`

**Interfaces:**
- Consumes: `rate_by`, `situational_buckets` (Task 7), `load_category` (Task 3).
- Produces:
  - `attach_coverage(joined_df) -> pandas.DataFrame` — adds `coverage:str` from `quarterback_charting` (dropbacks only) and `def_package:str` from `rushing`.
  - `tendency_by(df, situation_column, call_column, min_sample=MIN_SAMPLE) -> pandas.DataFrame` — columns `<situation>`, `<call>`, `plays`, `call_share:float`, `success_rate:float`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_analysis.py`:

```python
def test_tendency_shares_sum_to_one_within_a_situation():
    df = pd.DataFrame(
        [{"down_distance": "3rd & long", "run_pass": "P", "efficiency": "Y",
          "explosive": False}] * 30
        + [{"down_distance": "3rd & long", "run_pass": "R", "efficiency": "N",
            "explosive": False}] * 20
    )
    from src.playcalls.analysis import tendency_by

    result = tendency_by(df, "down_distance", "run_pass", min_sample=10)
    assert round(result["call_share"].sum(), 6) == 1.0
    assert result.set_index("run_pass").loc["P", "call_share"] == 0.6


def test_coverage_is_only_attached_to_dropbacks():
    """quarterback_charting covers dropbacks. Runs must not get a coverage label."""
    from src.playcalls.analysis import attach_coverage

    joined = pd.DataFrame([
        {"play_id": 1, "run_pass": "P"},
        {"play_id": 2, "run_pass": "R"},
    ])
    qc = pd.DataFrame([{"play_id": 1, "coverage_type": "Single"}])
    rushing = pd.DataFrame([{"play_id": 2, "def_package": "4-2-5"}])

    result = attach_coverage(joined, qc, rushing)
    assert result.set_index("play_id").loc[1, "coverage"] == "Single"
    assert pd.isna(result.set_index("play_id").loc[2, "coverage"])
    assert result.set_index("play_id").loc[2, "def_package"] == "4-2-5"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/test_analysis.py -v
```

Expected: FAIL — `ImportError: cannot import name 'tendency_by'`.

- [ ] **Step 3: Implement both functions**

Append to `src/playcalls/analysis.py`:

```python
def attach_coverage(
    joined: pd.DataFrame,
    quarterback_charting: pd.DataFrame,
    rushing: pd.DataFrame,
) -> pd.DataFrame:
    """Attach per-play defensive context from PFF.

    Coverage comes from quarterback_charting, which charts dropbacks only, so
    run plays get no coverage label. Run-side defensive context comes from
    def_package in the rushing feed instead. The two are different fields and
    must never be pooled into one column.
    """
    result = joined.copy()

    if not quarterback_charting.empty and "coverage_type" in quarterback_charting:
        coverage = quarterback_charting[["play_id", "coverage_type"]].rename(
            columns={"coverage_type": "coverage"}
        )
        result = result.merge(coverage, on="play_id", how="left")
    else:
        result["coverage"] = pd.NA

    if not rushing.empty and "def_package" in rushing:
        package = rushing[["play_id", "def_package"]].drop_duplicates("play_id")
        result = result.merge(package, on="play_id", how="left")
    else:
        result["def_package"] = pd.NA

    return result


def tendency_by(
    df: pd.DataFrame,
    situation_column: str,
    call_column: str,
    min_sample: int = MIN_SAMPLE,
) -> pd.DataFrame:
    """How often each call is used within a situation, and how well it works.

    Frequency and success are reported together so predictability and
    productivity can be read on one line.
    """
    working = df.copy()
    working["_graded"] = ~working["efficiency"].isin(SUCCESS_RATE_EXCLUDED)
    working["_success"] = working["_graded"] & working["efficiency"].eq("Y")

    grouped = working.groupby(
        [situation_column, call_column], dropna=False
    ).agg(
        plays=("efficiency", "size"),
        graded=("_graded", "sum"),
        successes=("_success", "sum"),
    ).reset_index()

    situation_totals = grouped.groupby(situation_column)["plays"].transform("sum")
    grouped["call_share"] = grouped["plays"] / situation_totals
    grouped["success_rate"] = (
        grouped["successes"] / grouped["graded"].replace(0, pd.NA)
    )

    grouped = grouped[grouped["plays"] >= min_sample]

    return (
        grouped.drop(columns=["successes"])
        .sort_values([situation_column, "call_share"], ascending=[True, False])
        .reset_index(drop=True)
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_analysis.py -v
```

Expected: all PASS.

- [ ] **Step 5: Generate the versus-defence and tendency tables**

```bash
.venv/bin/python -c "
import pandas as pd
from src.playcalls.analysis import attach_coverage, rate_by, situational_buckets, tendency_by
from src.playcalls.gamemap import map_games
from src.playcalls.pff import load_category

df = pd.read_parquet('outputs/joined_plays.parquet')

qc, rush = [], []
for season in (2024, 2025):
    for game_id in map_games(season).values():
        qc.append(load_category(game_id, 'quarterback_charting'))
        rush.append(load_category(game_id, 'rushing'))
qc = pd.concat([f for f in qc if not f.empty], ignore_index=True)
rush = pd.concat([f for f in rush if not f.empty], ignore_index=True)

df = attach_coverage(situational_buckets(df), qc, rush)
df.to_parquet('outputs/joined_plays_enriched.parquet', index=False)

rate_by(df[df.run_pass=='P'], 'season', 'coverage').to_csv('outputs/tables/vs_defense_coverage.csv', index=False)
rate_by(df[df.run_pass=='R'], 'season', 'def_package').to_csv('outputs/tables/vs_defense_package.csv', index=False)
rate_by(df, 'season', 'box_count').to_csv('outputs/tables/vs_defense_box.csv', index=False)

for situation in ('down_distance', 'field_zone', 'quarter'):
    for call in ('run_pass', 'play_type', 'personnel'):
        t = tendency_by(df, situation, call)
        t.to_csv(f'outputs/tables/tendency_{situation}_{call}.csv', index=False)
        print(f'tendency_{situation}_{call}: {len(t)} rows')
"
```

- [ ] **Step 6: Commit**

```bash
git add src/playcalls/analysis.py tests/test_analysis.py outputs/tables/ outputs/joined_plays_enriched.parquet
git commit -m "Add versus-defence and coordinator tendency tables

Coverage comes from quarterback_charting, which charts dropbacks only, so runs
carry def_package from the rushing feed instead. The two are separate columns
and a test enforces that a run play never gets a coverage label - pooling them
would invent a coverage read on plays PFF never charted for coverage.

Tendency reports call frequency and success rate on the same line, so a call
that is both predictable and unproductive is visible in one glance."
```

---

## Task 9: Write the report

**Files:**
- Create: `src/playcalls/report.py`, `tests/test_report.py`
- Output: `outputs/REPORT.md`

**Interfaces:**
- Consumes: every table in `outputs/tables/`, `outputs/match_report.csv`, `outputs/unmatched_classification.csv`.
- Produces: `render_report(tables: dict[str, pandas.DataFrame], provenance: dict) -> str` — the complete Markdown document.

- [ ] **Step 1: Write the failing test**

Create `tests/test_report.py`:

```python
import pandas as pd

from src.playcalls.report import render_report


def _tables():
    return {
        "by_season": pd.DataFrame([
            {"season": 2024, "plays": 948, "graded": 928, "success_rate": 0.574,
             "explosive_rate": 0.15},
            {"season": 2025, "plays": 987, "graded": 986, "success_rate": 0.495,
             "explosive_rate": 0.074},
        ]),
    }


def _provenance():
    return {
        "match_rate": 0.97,
        "designed_run_missing": 4,
        "same_coordinator": True,
        "seasons": "2024-2025",
    }


def test_report_states_the_headline_drop():
    text = render_report(_tables(), _provenance())
    assert "57.4" in text and "49.5" in text


def test_report_states_the_scope_limit():
    """2021-2023 have no outcome columns. The report must say so."""
    text = render_report(_tables(), _provenance())
    assert "2021" in text and "2024" in text


def test_report_never_claims_epa():
    """Phase 1 delivers success rate. Calling anything here EPA is a lie."""
    text = render_report(_tables(), _provenance())
    assert "EPA is not" in text or "not EPA" in text


def test_report_discloses_the_join_match_rate():
    text = render_report(_tables(), _provenance())
    assert "97" in text


def test_report_states_the_coordinator_was_unchanged():
    text = render_report(_tables(), _provenance())
    assert "coordinator" in text.lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_report.py -v
```

Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Implement the renderer**

Create `src/playcalls/report.py`:

```python
"""Render the analysis tables into the Phase 1 Markdown report.

The report's job is to be trustworthy, not impressive. Every limit that could
make a reader draw a wrong conclusion is stated on the page, not in a footnote.
"""

from __future__ import annotations

import pandas as pd


def _table(df: pd.DataFrame, max_rows: int = 25) -> str:
    if df.empty:
        return "_No group met the minimum sample size._\n"
    return df.head(max_rows).to_markdown(index=False) + "\n"


def render_report(tables: dict[str, pd.DataFrame], provenance: dict) -> str:
    """Build the complete report as one Markdown string."""
    season_table = tables["by_season"]
    rates = {
        int(row["season"]): row["success_rate"] * 100
        for _, row in season_table.iterrows()
    }
    drop = rates.get(2024, 0) - rates.get(2025, 0)

    parts: list[str] = []

    parts.append("# Baylor Offensive Play-Call Analysis — 2024 and 2025\n")
    parts.append(
        "**Audience:** analytics staff. **Scope:** 2024 and 2025 offensive "
        "snaps only.\n"
    )

    parts.append("\n## The headline\n")
    parts.append(
        f"Offensive success rate fell from **{rates.get(2024, 0):.1f}%** in 2024 "
        f"to **{rates.get(2025, 0):.1f}%** in 2025 — a drop of "
        f"**{drop:.1f} points**.\n"
    )
    if provenance.get("same_coordinator"):
        parts.append(
            "\nThe offensive coordinator did not change between these seasons. "
            "The drop is therefore not explained by a change of play-caller, "
            "and has to be read as scheme, personnel or execution under one "
            "system.\n"
        )
    parts.append("\n" + _table(season_table))

    parts.append("\n## How much to trust this\n")
    parts.append(
        f"- Charting rows matched to PFF plays: "
        f"**{provenance['match_rate'] * 100:.1f}%**. Unmatched rows are "
        "excluded from any cut that needs PFF fields.\n"
    )
    missing = provenance.get("designed_run_missing", 0)
    if missing:
        parts.append(
            f"- **{missing}** designed run plays appear in PFF with no charting "
            "row. Success rates are computed on the charted plays only, so the "
            "denominator is incomplete by that amount.\n"
        )
    else:
        parts.append(
            "- No designed run play was found in PFF without a charting row. "
            "The charted denominator is complete.\n"
        )
    parts.append(
        "- **Seasons 2021 to 2023 are excluded.** Those files carry no down, "
        "distance, yardage or field position, so success rate cannot be "
        "computed for them at all.\n"
    )
    parts.append(
        "- Rates are suppressed where fewer than 15 graded plays support them.\n"
    )
    parts.append(
        "- **This report contains no EPA.** Expected points needs a model fitted "
        "on a large play-by-play corpus, which this project does not yet have. "
        "Nothing here is a proxy for EPA.\n"
    )
    parts.append(
        "- Coverage is charted by PFF on dropbacks only. Run plays carry "
        "defensive personnel instead. The two are never pooled.\n"
    )
    parts.append(
        "- 2025's own defensive charting is essentially absent (`Front` 0% "
        "filled, `Cover Family` 0.4%). All 2025 defensive context here comes "
        "from PFF.\n"
    )

    section_titles = {
        "by_play_type": "Success by play type",
        "by_concept": "Success by concept",
        "by_formation": "Success by formation family",
        "by_personnel": "Success by personnel",
        "by_down_distance": "Success by down and distance",
        "by_field_zone": "Success by field zone",
        "by_run_pass": "Run versus pass",
        "by_qb": "Success by quarterback",
        "vs_defense_coverage": "Dropback success by coverage",
        "vs_defense_package": "Run success by defensive personnel",
        "vs_defense_box": "Success by box count",
    }
    parts.append("\n## Where the offense won and lost\n")
    for key, title in section_titles.items():
        if key in tables:
            parts.append(f"\n### {title}\n\n{_table(tables[key])}")

    tendency_keys = [k for k in tables if k.startswith("tendency_")]
    if tendency_keys:
        parts.append("\n## Coordinator tendency profile\n")
        parts.append(
            "Call frequency and success rate together. A high share with a low "
            "success rate is a predictable call that is not paying for its "
            "predictability.\n"
        )
        for key in sorted(tendency_keys):
            label = key.removeprefix("tendency_").replace("_", " by ")
            parts.append(f"\n### {label}\n\n{_table(tables[key])}")

    return "".join(parts)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/pytest tests/test_report.py -v
```

Expected: all PASS.

- [ ] **Step 5: Render the real report**

```bash
.venv/bin/python -c "
import glob, os
import pandas as pd
from src.playcalls.report import render_report

tables = {
    os.path.basename(p)[:-4]: pd.read_csv(p)
    for p in sorted(glob.glob('outputs/tables/*.csv'))
}

match = pd.read_csv('outputs/match_report.csv')
overall = match['matched'].sum() / match['charted_plays'].sum()

unmatched = pd.read_csv('outputs/unmatched_classification.csv')
missing = int((unmatched['classification'] == 'designed_run_missing').sum())

text = render_report(tables, {
    'match_rate': overall,
    'designed_run_missing': missing,
    'same_coordinator': True,
    'seasons': '2024-2025',
})
open('outputs/REPORT.md', 'w').write(text)
print(f'wrote outputs/REPORT.md ({len(text):,} chars)')
"
```

- [ ] **Step 6: Read the report and sanity-check every headline number**

Open `outputs/REPORT.md`. For at least three claims, trace the number back to its table and to the join. A number you cannot trace does not ship.

- [ ] **Step 7: Run the full test suite**

```bash
.venv/bin/pytest -v
```

Expected: everything passes.

- [ ] **Step 8: Commit**

```bash
git add src/playcalls/report.py tests/test_report.py outputs/REPORT.md
git commit -m "Render the Phase 1 report

The 'How much to trust this' section is not boilerplate. It carries the join
match rate, the count of designed runs PFF saw that the chart did not, the
2021-2023 exclusion, the suppression threshold, and an explicit statement that
nothing here is EPA. Tests assert those disclosures are present, because a
report that quietly drops its own limits is worse than no report."
```

---

## Task 10: Publish the report as an HTML artifact

**Files:**
- Create: `outputs/report.html`

**Interfaces:**
- Consumes: `outputs/REPORT.md`.
- Produces: a published artifact URL.

- [ ] **Step 1: Build the HTML from the Markdown**

Generate `outputs/report.html` from `outputs/REPORT.md`. Do not rewrite the content by hand — the Markdown is the single source of truth and the two must not drift.

Requirements for the page:
- A `<title>` naming the report — a short, distinctive noun phrase.
- Theme-aware: full light palette on bare `:root`, dark overrides under both `@media (prefers-color-scheme: dark)` guarded as `:root:not([data-theme="light"])` and `:root[data-theme="dark"]`. `body` gets an explicit token background.
- Responsive to 400px, with at least a 16px side gutter. Every table wrapped in its own `overflow-x: auto` container.
- No `<!DOCTYPE>`, `<html>`, `<head>` or `<body>` tags — the publish step wraps the file.

**Before writing the page, load the `artifact-design` skill.**

- [ ] **Step 2: Publish**

Call the Artifact tool with `file_path: outputs/report.html`, a one-sentence `description`, and a `favicon`.

- [ ] **Step 3: Commit**

```bash
git add outputs/report.html
git commit -m "Publish the report as a shareable HTML artifact

Generated from outputs/REPORT.md so the two cannot drift. The Markdown stays
the source of truth; this exists so the analytics staff get a link instead of
a file in a private repo."
```

---

## Task 11: Update the repo's agent guidance

The `CLAUDE.md` and `AGENTS.md` written before this work are now incomplete: they describe the CSVs but not the PFF join, the derived crosswalk, or the two gates.

**Files:**
- Modify: `CLAUDE.md`, `AGENTS.md`

- [ ] **Step 1: Add a "How this project actually works" section to both files**

Both files must gain, in their own words but with identical substance:

- The PFF DuckDB path, that it is opened read-only, and that `PFF_Data_Project` owns ingest.
- That `run.py` rebuilds everything from the CSVs plus `pff.db`.
- The two gates: the 95% join match rate, and the `designed_run_missing` count.
- That the `Play Type` crosswalk in `outputs/playtype_crosswalk.csv` is derived from evidence and reviewed, not authoritative football knowledge.
- That success rates exclude `Efficiency` values `X` and blank.
- That `MIN_SAMPLE = 15` suppresses thin cells.
- The reminder that these two files are kept in sync by editing both and are never symlinked.

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md AGENTS.md
git commit -m "Document the join, the gates and the crosswalk in the agent guides

Both files described the CSVs and stopped there. A future session would not
have known that pff.db is the other half of the data, that two gates protect
the numbers, or that the Play Type crosswalk is derived evidence rather than
football fact."
```

---

## Self-Review

**Spec coverage.**

| Spec section | Task |
|---|---|
| §3.2 missing premium categories | 1 |
| §4.1 repository boundary, read-only | 1, 3 |
| §5 the join, §5.4 the 95% gate | 4 |
| §6.1 rushing gap resolution | 5 |
| §6.2 crosswalk derived from evidence | 6 |
| §6.3 QB and coordinator confounds | 7 (`by_qb`), 9 (disclosure) |
| §6.3 2025 defensive charting collapse | 8 (`attach_coverage`), 9 |
| §6.4 cleaning rules | 2 |
| §7A success-rate profile | 7 |
| §7B situational profile | 7 (`situational_buckets`) |
| §7C versus-defence profile | 8 |
| §7D tendency profile | 8 (`tendency_by`) |
| §7E 2024 vs 2025 | 6 (crosswalk), 7 (`season` grouping), 9 |
| §8 no EPA claimed | 9 (`test_report_never_claims_epa`) |
| §9 verification, match report artefact | 4, 9 |
| §10 report format: Markdown + artifact | 9, 10 |

No spec section is unimplemented.

**Placeholder scan.** No TBD, no "add error handling", no "similar to Task N". Every code step carries runnable code. Task 1 step 6 deliberately says to read `--help` rather than guessing flag names, and Task 5 step 3 says to inspect real column names before writing predicates against them — those are instructions to verify, not placeholders.

**Type consistency.**
- `load_season(path) -> DataFrame` — defined Task 2, used Tasks 4, 6, 7.
- `success_rate(df) -> float` — defined Task 2, used Task 2's tests.
- `SUCCESS_RATE_EXCLUDED` — defined Task 2, imported by Task 7 and Task 8.
- `load_category(game_id, category, db_path)` / `load_plays(game_id, db_path)` / `baylor_games(season, db_path)` — defined Task 3, used Tasks 4, 5, 8.
- `map_games(season) -> dict[str, str]` — defined Task 4, used Tasks 4, 8.
- `join_game(chart_df, plays_df) -> (DataFrame, DataFrame)` and `match_rate(joined, chart_df) -> float` — defined Task 4, used Tasks 4, 5.
- `classify_unmatched(unmatched, rushing, passing)` and `CLASSIFICATIONS` — defined Task 5, used Task 5.
- `normalise_concept(value) -> str`, `derive_playtype_crosswalk(df_2024, df_2025, concept_column)` — defined Task 6, used Tasks 6, 7.
- `MIN_SAMPLE`, `rate_by(df, *columns, min_sample)`, `situational_buckets(df)` — defined Task 7, used Tasks 7, 8.
- `attach_coverage(joined, quarterback_charting, rushing)`, `tendency_by(df, situation_column, call_column, min_sample)` — defined Task 8, used Task 8.
- `render_report(tables, provenance) -> str` — defined Task 9, used Task 9.

Column names are consistent across tasks: `efficiency`, `explosive`, `run_pass`, `play_type`, `form_fam`, `personnel`, `down`, `distance`, `yards_to_goal`, `box_count`, `qb`, `play_id`, `season`, `game_code`, `play_no`.

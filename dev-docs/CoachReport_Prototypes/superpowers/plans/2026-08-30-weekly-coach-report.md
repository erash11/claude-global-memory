# Weekly Coach Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the approved Prototype A/B report into a weekly product that runs from one command with zero hand-edits.

**Architecture:** Four layers with one direction of flow — *fetch* (`sources/`) → *resolve* (`resolve.py`, picks the week and opponents from the schedule) → *derive* (`payload.py`, `metrics.py`, `flags.py`, the only layer with product logic and therefore the only layer with heavy tests) → *render* (`render.py`, `fonts.py`, `pdf.py`, which inject a JSON payload into an otherwise untouched template). The templates are the reviewed prototypes, moved not rewritten.

**Tech Stack:** Python 3.12+ managed by `uv`; `requests`, `duckdb`, `python-dotenv`, `pytest`. Rendering by headless Google Chrome. No JS build step, no framework — the deliverable is one self-contained HTML file per edition.

**Spec:** `~/DEV/Football/CoachReport_Prototypes/SPEC.md` (reads with `PRODUCT.md` and `DESIGN.md` in the same folder). Read all three before Task 1.

## Global Constraints

- **Zero weekly hand-edits.** No opponent name, date, week number, season label or PFF team id may be a literal anywhere except `config.py`. Enforced by gate G6.
- **Print is primary.** US Letter portrait, `8.5in × 11in` per sheet, one sheet = one page, `@page { size: letter; margin: 0 }`. Nothing may live only in a hover state.
- **`--out` (`#b8433a`) means one thing:** outside the reference range. Derived/ranking marks use `--neutral` (`#6b7a76`).
- **Voice:** descriptive, never a verdict on a person. No tier labels (`elite`, `poor`, `weak`, `bad`, `underperform`). Enforced by gate G10.
- **One spine per quantity.** `box_snaps` is computed once and copied to the second edition, never recomputed.
- **`seasonType == "regular"`** is filtered exactly once, in `sources/cfbd.py`. Nothing downstream re-filters.
- **Flag rule constants are frozen:** `SPREAD_FLOOR = 4.0`, `ABS_FLOOR = 6`, `ABSENT_AT = 2`, `ABSENT_MED = 10`, Tukey `k = 1.5`. DESIGN.md documents the reasoning; changing a constant without changing DESIGN.md makes the design doc a lie.
- **Credentials are read at runtime, never copied.** `CFBD_API_KEY` from `~/DEV/CFB_Analytics_Lab/.env`. PFF DuckDB at `~/DEV/Football/PFF_Data_Project/data/pff.db`, opened **read-only** — it holds 175,559 grades and 4.7M stat rows and must never be rebuilt.
- **Commit after every task.**

## File Structure

| File | Responsibility |
|---|---|
| `src/coachreport/config.py` | The only place constants live: `TEAM`, `P4`, position→group maps, paths |
| `src/coachreport/resolve.py` | Season, week, game id, opponent, next opponent — all from the schedule |
| `src/coachreport/sources/cfbd.py` | CFBD HTTP; applies the `seasonType` filter |
| `src/coachreport/sources/pff.py` | PFF DuckDB read-only; resolves team id |
| `src/coachreport/snapshot.py` | Orchestrates both sources into one cacheable `snapshot.json` |
| `src/coachreport/metrics.py` | `quantile`, `percentile_of`, `band_rows` — the reference-range maths |
| `src/coachreport/flags.py` | The player out-of-range rule |
| `src/coachreport/payload.py` | `build_meta` + payload A/B assembly |
| `src/coachreport/fonts.py` | Idempotent inline `@font-face` embedding |
| `src/coachreport/render.py` | Payload → self-contained HTML |
| `src/coachreport/pdf.py` | Headless Chrome → PDF, plus the render-time gates |
| `src/coachreport/cli.py` | `coachreport run` |

---

### Task 1: Repo scaffold and config

**Files:**
- Create: `~/DEV/Football/WeeklyCoachReport/pyproject.toml`
- Create: `~/DEV/Football/WeeklyCoachReport/src/coachreport/__init__.py`
- Create: `~/DEV/Football/WeeklyCoachReport/src/coachreport/config.py`
- Create: `~/DEV/Football/WeeklyCoachReport/tests/test_config.py`
- Create: `~/DEV/Football/WeeklyCoachReport/.gitignore`

**Interfaces:**
- Consumes: nothing.
- Produces: `config.TEAM: str`, `config.P4: set[str]`, `config.SEASON_START_MONTH: int`, `config.GROUP: dict[str, str]`, `config.SIDE: dict[str, str]`, `config.CFBD_ENV_PATH: Path`, `config.PFF_DB: Path`, `config.REPO: Path`, `config.OUT: Path`, `config.TEMPLATES: Path`, `config.FONTS: Path`.

- [ ] **Step 1: Create the repo and move the durable docs**

```bash
mkdir -p ~/DEV/Football/WeeklyCoachReport/{src/coachreport/sources,templates,fonts,tests/fixtures,out}
cd ~/DEV/Football/WeeklyCoachReport
git init
P=~/DEV/Football/CoachReport_Prototypes
cp "$P/PRODUCT.md" "$P/DESIGN.md" "$P/SPEC.md" .
cp "$P/prototype_a_analytics.tpl.html" templates/coaches.tpl.html
cp "$P/prototype_b_demand.tpl.html"    templates/performance.tpl.html
cp "$P/prototype_pipeline/fonts/"*.woff2 fonts/
cp "$P/prototype_pipeline/fixtures/snapshot.json"   tests/fixtures/snapshot_2025w06.json
cp "$P/prototype_pipeline/fixtures/wp.json"         tests/fixtures/wp_2025w06.json
cp "$P/prototype_pipeline/fixtures/payload_a.json"  tests/fixtures/expected_payload_a.json
cp "$P/prototype_pipeline/fixtures/payload_b.json"  tests/fixtures/expected_payload_b.json
```

- [ ] **Step 2: Write `pyproject.toml`**

```toml
[project]
name = "coachreport"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["requests>=2.32", "duckdb>=1.0", "python-dotenv>=1.0"]

[project.scripts]
coachreport = "coachreport.cli:main"

[dependency-groups]
dev = ["pytest>=8.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/coachreport"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Write `.gitignore`**

```gitignore
out/
.venv/
__pycache__/
*.pyc
.env
```

`out/` is ignored because it holds athlete-named PDFs (FERPA, see PRODUCT.md).

- [ ] **Step 4: Write the failing test**

```python
# tests/test_config.py
from coachreport import config


def test_team_is_the_only_team_constant():
    assert config.TEAM == "Baylor"


def test_power_four_is_the_comparison_set():
    assert config.P4 == {"SEC", "Big Ten", "Big 12", "ACC"}


def test_position_groups_cover_every_pff_position_seen():
    seen = ["QB", "HB", "FB", "WR", "TE", "T", "G", "C",
            "DI", "ED", "DE", "DT", "NT", "LB", "CB", "S", "FS", "SS",
            "K", "P", "LS"]
    for pos in seen:
        assert pos in config.GROUP, f"{pos} has no group"
        assert config.GROUP[pos] in config.SIDE


def test_paths_point_at_real_things():
    assert config.PFF_DB.exists()
    assert config.TEMPLATES.is_dir()
```

- [ ] **Step 5: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport'`

- [ ] **Step 6: Write `config.py`**

```python
"""The only module allowed to contain literals. Gate G6 enforces that."""
from pathlib import Path

TEAM = "Baylor"
P4 = {"SEC", "Big Ten", "Big 12", "ACC"}
SEASON_START_MONTH = 8          # August; before it, the season is the previous year

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "templates"
FONTS = REPO / "fonts"
OUT = REPO / "out"

CFBD_ENV_PATH = Path.home() / "DEV/CFB_Analytics_Lab/.env"
PFF_DB = Path.home() / "DEV/Football/PFF_Data_Project/data/pff.db"

# PFF position -> group. Taken from the prototype; every position observed in the
# 2025 grade rows is covered, and an unseen position falls back to "ST".
GROUP = {
    "QB": "QB", "WR": "WR", "TE": "TE", "LB": "LB",
    "T": "OL", "G": "OL", "C": "OL",
    "DI": "DL", "ED": "DL", "DE": "DL", "DT": "DL", "NT": "DL",
    "CB": "DB", "S": "DB", "FS": "DB", "SS": "DB",
    "HB": "RB", "FB": "RB",
    "K": "ST", "P": "ST", "LS": "ST",
}
SIDE = {"OL": "off", "QB": "off", "RB": "off", "WR": "off", "TE": "off",
        "DL": "def", "LB": "def", "DB": "def", "ST": "st"}

EDITIONS = {
    "coaches": "coaches.tpl.html",
    "performance": "performance.tpl.html",
}


def group_of(position: str) -> str:
    return GROUP.get(position, "ST")


def side_of(position: str) -> str:
    return SIDE.get(group_of(position), "st")
```

- [ ] **Step 7: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`
Expected: 4 passed

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat: scaffold WeeklyCoachReport repo, config, and reviewed docs"
```

---

### Task 2: Week resolution — the zero-hand-edits core

This is the task that makes the product different from the prototype. The prototype hardcodes `YEAR`, `WEEK`, `GAME_ID`, `OPP` and `NEXT_OPP`; all five come from the schedule here.

**Files:**
- Create: `src/coachreport/resolve.py`
- Create: `tests/test_resolve.py`

**Interfaces:**
- Consumes: `config.TEAM`, `config.SEASON_START_MONTH`.
- Produces:
  - `current_season(now: datetime | None = None) -> int`
  - `class ResolvedWeek` — frozen dataclass with fields `season: int`, `week: int`, `game_id: int`, `opponent: str`, `home: bool`, `next_opponent: str | None`, `next_week: int | None`, `next_home: bool | None`
  - `resolve_week(games: list[dict], team: str, season: int, week: int | None = None) -> ResolvedWeek`
  - `class NoCompletedGame(RuntimeError)`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_resolve.py
import json
from datetime import datetime

import pytest

from coachreport import config
from coachreport.resolve import (NoCompletedGame, ResolvedWeek,
                                 current_season, resolve_week)


def g(week, home, away, hp=None, ap=None, season_type="regular", gid=None):
    return {"id": gid or week * 1000, "week": week, "seasonType": season_type,
            "homeTeam": home, "awayTeam": away, "homePoints": hp, "awayPoints": ap}


SCHEDULE = [
    g(1, "Baylor", "Auburn", 38, 24),
    g(2, "SMU", "Baylor", 20, 17),
    g(6, "Baylor", "Kansas State", 35, 34, gid=401756911),
    g(8, "TCU", "Baylor"),               # not played yet
    g(9, "Baylor", "Cincinnati"),
]


def test_current_season_rolls_over_in_august():
    assert current_season(datetime(2026, 8, 30)) == 2026
    assert current_season(datetime(2026, 1, 12)) == 2025
    assert current_season(datetime(2026, 7, 31)) == 2025


def test_resolves_the_latest_completed_game():
    r = resolve_week(SCHEDULE, "Baylor", 2025)
    assert r.week == 6
    assert r.game_id == 401756911
    assert r.opponent == "Kansas State"
    assert r.home is True


def test_resolves_the_next_scheduled_opponent():
    r = resolve_week(SCHEDULE, "Baylor", 2025)
    assert r.next_opponent == "TCU"
    assert r.next_week == 8
    assert r.next_home is False


def test_postseason_row_never_wins_the_week():
    # CFBD relabels a postseason row with a regular-season week number.
    poisoned = SCHEDULE + [g(1, "Baylor", "Phantom Bowl", 3, 0, season_type="postseason")]
    r = resolve_week(poisoned, "Baylor", 2025)
    assert r.week == 6 and r.opponent == "Kansas State"


def test_explicit_week_override():
    r = resolve_week(SCHEDULE, "Baylor", 2025, week=1)
    assert r.week == 1 and r.opponent == "Auburn" and r.home is True


def test_away_game_reads_the_opponent_off_the_home_slot():
    r = resolve_week(SCHEDULE, "Baylor", 2025, week=2)
    assert r.opponent == "SMU" and r.home is False


def test_no_completed_game_raises_rather_than_guessing():
    with pytest.raises(NoCompletedGame):
        resolve_week([g(1, "Baylor", "Auburn")], "Baylor", 2025)


def test_last_game_of_season_has_no_next_opponent():
    r = resolve_week([g(15, "Baylor", "Houston", 21, 14)], "Baylor", 2025)
    assert r.next_opponent is None and r.next_week is None


def test_resolves_against_the_real_saved_snapshot():
    snap = json.loads((config.REPO / "tests/fixtures/snapshot_2025w06.json").read_text())
    # The fixture's schedule is already normalised; rebuild CFBD-shaped rows from it.
    rows = [{"id": snap["meta"]["game_id"] if s["week"] == 6 else s["week"] * 1000,
             "week": s["week"], "seasonType": "regular",
             "homeTeam": "Baylor" if s["home"] else s["opponent"],
             "awayTeam": s["opponent"] if s["home"] else "Baylor",
             "homePoints": (s["pf"] if s["home"] else s["pa"]),
             "awayPoints": (s["pa"] if s["home"] else s["pf"])}
            for s in snap["schedule"]]
    r = resolve_week(rows, "Baylor", 2025, week=6)
    assert r.game_id == snap["meta"]["game_id"]
    assert r.opponent == "Kansas State"
    assert r.next_opponent == "TCU"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_resolve.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.resolve'`

- [ ] **Step 3: Write `resolve.py`**

```python
"""Derives every weekly variable from the schedule.

The predecessor report died of hand-editing: the opponent, the week and the next
game were typed in every Monday. Nothing in this module accepts a typed value
except an explicit `--week` override for rebuilding an old week.
"""
from dataclasses import dataclass
from datetime import datetime

from . import config


class NoCompletedGame(RuntimeError):
    """No finished regular-season game to report on — a bye, or the season hasn't started."""


@dataclass(frozen=True)
class ResolvedWeek:
    season: int
    week: int
    game_id: int
    opponent: str
    home: bool
    next_opponent: str | None
    next_week: int | None
    next_home: bool | None


def current_season(now: datetime | None = None) -> int:
    now = now or datetime.now()
    return now.year if now.month >= config.SEASON_START_MONTH else now.year - 1


def _regular(games: list[dict]) -> list[dict]:
    return [g for g in games if g.get("seasonType", "regular") == "regular"]


def _played(game: dict) -> bool:
    return game.get("homePoints") is not None and game.get("awayPoints") is not None


def resolve_week(games: list[dict], team: str, season: int,
                 week: int | None = None) -> ResolvedWeek:
    reg = _regular(games)
    done = [g for g in reg if _played(g)]

    if week is None:
        if not done:
            raise NoCompletedGame(
                f"{team} has no completed regular-season game in {season}. "
                "Nothing to report — this is a bye week or the season has not started.")
        game = max(done, key=lambda g: g["week"])
    else:
        game = next((g for g in done if g["week"] == week), None)
        if game is None:
            raise NoCompletedGame(
                f"{team} has no completed regular-season game in week {week} of {season}.")

    home = game["homeTeam"] == team
    opponent = game["awayTeam"] if home else game["homeTeam"]

    later = [g for g in reg if g["week"] > game["week"]]
    nxt = min(later, key=lambda g: g["week"]) if later else None

    return ResolvedWeek(
        season=season,
        week=game["week"],
        game_id=game["id"],
        opponent=opponent,
        home=home,
        next_opponent=(nxt["awayTeam"] if nxt["homeTeam"] == team else nxt["homeTeam"])
        if nxt else None,
        next_week=nxt["week"] if nxt else None,
        next_home=(nxt["homeTeam"] == team) if nxt else None,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_resolve.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: derive season, week, game and opponents from the schedule"
```

---

### Task 3: CFBD source with the seasonType filter applied once

**Files:**
- Create: `src/coachreport/sources/__init__.py` (empty)
- Create: `src/coachreport/sources/cfbd.py`
- Create: `tests/test_cfbd.py`

**Interfaces:**
- Consumes: `config.CFBD_ENV_PATH`.
- Produces:
  - `api_key() -> str`
  - `regular_only(rows)` — passes non-list payloads through untouched
  - `class Client` with `get(path: str, **params)` and a `calls: int` counter

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cfbd.py
import pytest

from coachreport.sources import cfbd


class FakeResponse:
    def __init__(self, payload):
        self._p = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._p


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.seen = []

    def get(self, url, headers=None, params=None, timeout=None):
        self.seen.append((url, params))
        return FakeResponse(self.payload)


def test_regular_only_drops_postseason_rows():
    rows = [{"week": 1, "seasonType": "regular"},
            {"week": 1, "seasonType": "postseason"}]
    assert cfbd.regular_only(rows) == [{"week": 1, "seasonType": "regular"}]


def test_regular_only_keeps_rows_with_no_season_type():
    rows = [{"team": "Baylor"}]
    assert cfbd.regular_only(rows) == rows


def test_regular_only_passes_through_a_dict_payload():
    assert cfbd.regular_only({"a": 1}) == {"a": 1}


def test_client_filters_every_response_and_counts_calls():
    session = FakeSession([{"week": 1, "seasonType": "regular"},
                           {"week": 1, "seasonType": "postseason"}])
    c = cfbd.Client(key="test-key", session=session)
    out = c.get("/games", year=2025, team="Baylor")
    assert out == [{"week": 1, "seasonType": "regular"}]
    assert c.calls == 1
    assert session.seen[0][1] == {"year": 2025, "team": "Baylor"}


def test_missing_key_fails_loudly(monkeypatch, tmp_path):
    monkeypatch.delenv("CFBD_API_KEY", raising=False)
    monkeypatch.setattr(cfbd.config, "CFBD_ENV_PATH", tmp_path / "nope.env")
    with pytest.raises(RuntimeError, match="CFBD_API_KEY"):
        cfbd.api_key()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cfbd.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.sources'`

- [ ] **Step 3: Write `cfbd.py`**

```python
"""CFBD REST access.

CFBD mixes a postseason row into a season query, relabelled with a regular-season
week number, which shows up downstream as a phantom duplicate week. The filter
lives here and only here: nothing past this module ever sees a postseason row, and
nothing past this module re-filters.
"""
import os

import requests
from dotenv import dotenv_values

from .. import config

BASE = "https://api.collegefootballdata.com"


def api_key() -> str:
    key = os.environ.get("CFBD_API_KEY")
    if not key and config.CFBD_ENV_PATH.exists():
        key = dotenv_values(config.CFBD_ENV_PATH).get("CFBD_API_KEY")
    if not key:
        raise RuntimeError(
            f"CFBD_API_KEY not found in the environment or {config.CFBD_ENV_PATH}")
    return key


def regular_only(rows):
    """Drop postseason rows. Non-list payloads pass through untouched."""
    if not isinstance(rows, list):
        return rows
    return [r for r in rows
            if not isinstance(r, dict) or r.get("seasonType", "regular") == "regular"]


class Client:
    def __init__(self, key: str | None = None, session=None):
        self.key = key or api_key()
        self.session = session or requests.Session()
        self.calls = 0

    def get(self, path: str, **params):
        self.calls += 1
        r = self.session.get(BASE + path,
                             headers={"Authorization": f"Bearer {self.key}"},
                             params=params, timeout=60)
        r.raise_for_status()
        return regular_only(r.json())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cfbd.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: CFBD client that filters postseason rows at the data layer"
```

---

### Task 4: PFF source with a derived team id

The prototype writes `BAY_TID = "118"`. Verified against the live database: `select team_id from teams where is_baylor` returns `118`, and `team_id` equals `franchise_id` for that row. The literal is unnecessary and is removed.

**Files:**
- Create: `src/coachreport/sources/pff.py`
- Create: `tests/test_pff.py`

**Interfaces:**
- Consumes: `config.PFF_DB`, `config.TEAM`.
- Produces:
  - `connect(db: Path | None = None)` — read-only DuckDB connection
  - `team_id(con) -> str`
  - `game_grades(con, season: int, week: int) -> list[dict]` with keys `name, position, unit, grade_type, grade, snaps, team_id`
  - `season_snap_rows(con, season: int, team_id: str, through_week: int) -> list[dict]` with keys `name, position, week, snaps`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pff.py
import pytest

from coachreport import config
from coachreport.sources import pff

pytestmark = pytest.mark.skipif(not config.PFF_DB.exists(),
                                reason="PFF database not present on this machine")


@pytest.fixture(scope="module")
def con():
    c = pff.connect()
    yield c
    c.close()


def test_team_id_is_derived_not_typed(con):
    assert pff.team_id(con) == "118"


def test_connection_is_read_only(con):
    with pytest.raises(Exception):
        con.execute("create table should_not_exist (x int)")


def test_season_snap_rows_stop_at_the_requested_week(con):
    rows = pff.season_snap_rows(con, 2025, pff.team_id(con), through_week=6)
    assert rows, "expected 2025 Baylor snap rows through week 6"
    assert max(r["week"] for r in rows) <= 6
    assert all(r["snaps"] >= 0 for r in rows)


def test_game_grades_carry_both_teams(con):
    rows = pff.game_grades(con, 2025, 6)
    assert rows
    assert len({r["team_id"] for r in rows}) >= 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_pff.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.sources.pff'`

- [ ] **Step 3: Write `pff.py`**

```python
"""PFF DuckDB access — read-only, always.

The database is already backfilled: 175,559 game grades and 4.7M stat rows for
2023-2025. It is never written to and never rebuilt from here.
"""
from pathlib import Path

import duckdb

from .. import config


def connect(db: Path | None = None):
    return duckdb.connect(str(db or config.PFF_DB), read_only=True)


def team_id(con) -> str:
    """Baylor's PFF team id, derived. Verified equal to franchise_id ('118')."""
    row = con.execute("select team_id from teams where is_baylor limit 1").fetchone()
    if not row:
        raise RuntimeError("PFF database has no team row flagged is_baylor")
    return str(row[0])


def game_grades(con, season: int, week: int) -> list[dict]:
    rows = con.execute("""
        select p.name, gr.position, gr.unit, gr.grade_type,
               gr.grade_value, gr.snap_count, gr.team_id
        from pff_grades gr
        join players p on p.pff_player_id = gr.pff_player_id
        join games g on g.game_id = gr.game_id
        where g.is_baylor_game and gr.season = ? and gr.week = ?
    """, [season, week]).fetchall()
    return [{"name": r[0], "position": r[1], "unit": r[2], "grade_type": r[3],
             "grade": r[4], "snaps": r[5], "team_id": str(r[6])} for r in rows]


def season_snap_rows(con, season: int, team_id: str, through_week: int) -> list[dict]:
    rows = con.execute("""
        select p.name, gr.position, gr.week, max(gr.snap_count) snaps
        from pff_grades gr
        join players p on p.pff_player_id = gr.pff_player_id
        join games g on g.game_id = gr.game_id
        where g.is_baylor_game and gr.season = ? and gr.team_id = ? and gr.week <= ?
        group by 1, 2, 3
    """, [season, team_id, through_week]).fetchall()
    return [{"name": r[0], "position": r[1], "week": int(r[2]),
             "snaps": int(r[3] or 0)} for r in rows]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_pff.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: PFF source with derived team id, read-only"
```

---

### Task 5: Snapshot assembly

Reproduces `pull_snapshot.py`'s output shape exactly, because the saved fixture — and therefore the golden test in Task 8 — depends on it.

**Files:**
- Create: `src/coachreport/snapshot.py`
- Create: `tests/test_snapshot.py`

**Interfaces:**
- Consumes: `resolve.ResolvedWeek`, `cfbd.Client`, `pff` module, `config.P4`.
- Produces:
  - `build_snapshot(client, con, rw: ResolvedWeek) -> dict` with top-level keys `meta, game, schedule, ppa_games, ppa_team_season, ppa_next_opp, adv_games_baylor, adv_game, adv_season_next_opp, adv_season_baylor, p4, drives, plays, next_opp_ppa_games, next_opp_adv_games, pff_grades, pff_season_snaps, winprob_raw`
  - `p4_distributions(all_season_adv, conf_by_team) -> dict` with keys `n_teams, median, dist`
  - `P4_METRICS: dict[str, tuple]` — the metric key → JSON path map

- [ ] **Step 1: Write the failing test**

```python
# tests/test_snapshot.py
import json

from coachreport import config
from coachreport.snapshot import P4_METRICS, dig, p4_distributions


def test_dig_walks_nested_paths_and_survives_missing_keys():
    row = {"offense": {"havoc": {"total": 0.21}}}
    assert dig(row, "offense", "havoc", "total") == 0.21
    assert dig(row, "offense", "missing", "total") is None
    assert dig(row, "defense", "ppa") is None


def test_p4_metrics_cover_both_sides_of_the_ball():
    assert sum(1 for k in P4_METRICS if k.startswith("off_")) == 8
    assert sum(1 for k in P4_METRICS if k.startswith("def_")) == 6


def test_p4_distributions_only_include_power_four_teams():
    rows = [{"team": "Baylor", "offense": {"successRate": 0.5}},
            {"team": "Rice", "offense": {"successRate": 0.1}}]
    conf = {"Baylor": "Big 12", "Rice": "American Athletic"}
    d = p4_distributions(rows, conf)
    assert d["n_teams"] == 1
    assert d["dist"]["off_success"] == [0.5]


def test_snapshot_fixture_still_has_the_shape_we_build_to():
    snap = json.loads((config.REPO / "tests/fixtures/snapshot_2025w06.json").read_text())
    for key in ("meta", "game", "schedule", "ppa_games", "adv_games_baylor",
                "adv_game", "p4", "drives", "plays", "pff_grades",
                "pff_season_snaps"):
        assert key in snap, f"fixture missing {key}"
    assert set(snap["p4"]) >= {"n_teams", "median", "dist"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_snapshot.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.snapshot'`

- [ ] **Step 3: Write `snapshot.py`**

```python
"""One raw, cacheable pull. Everything derived happens downstream of this file."""
import statistics as st

from . import config
from .resolve import ResolvedWeek
from .sources import pff

P4_METRICS = {
    "off_success":    ("offense", "successRate"),
    "off_explosive":  ("offense", "explosiveness"),
    "off_ppa":        ("offense", "ppa"),
    "off_rush_ppa":   ("offense", "rushingPlays", "ppa"),
    "off_pass_ppa":   ("offense", "passingPlays", "ppa"),
    "off_line_yards": ("offense", "lineYards"),
    "off_stuff":      ("offense", "stuffRate"),
    "off_havoc":      ("offense", "havoc", "total"),
    "def_success":    ("defense", "successRate"),
    "def_explosive":  ("defense", "explosiveness"),
    "def_ppa":        ("defense", "ppa"),
    "def_havoc":      ("defense", "havoc", "total"),
    "def_line_yards": ("defense", "lineYards"),
    "def_stuff":      ("defense", "stuffRate"),
}


def dig(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def p4_distributions(all_season_adv: list[dict], conf_by_team: dict) -> dict:
    rows = [r for r in all_season_adv if conf_by_team.get(r["team"]) in config.P4]
    dist = {k: [dig(r, *path) for r in rows] for k, path in P4_METRICS.items()}
    return {
        "n_teams": len(rows),
        "median": {k: (round(st.median([v for v in vs if v is not None]), 4)
                       if any(v is not None for v in vs) else None)
                   for k, vs in dist.items()},
        "dist": {k: [round(v, 4) for v in vs if v is not None] for k, vs in dist.items()},
    }


def build_snapshot(client, con, rw: ResolvedWeek) -> dict:
    team, season, week = config.TEAM, rw.season, rw.week

    games = client.get("/games", year=season, team=team)
    game = next(g for g in games if g["id"] == rw.game_id)

    snap = {
        "meta": {"year": season, "week": week, "team": team,
                 "opponent": rw.opponent, "next_opponent": rw.next_opponent,
                 "game_id": rw.game_id},
        "game": {"date": game["startDate"], "venue": game.get("venue"),
                 "home": game["homeTeam"], "away": game["awayTeam"],
                 "home_points": game["homePoints"], "away_points": game["awayPoints"],
                 "excitement": game.get("excitementIndex")},
        "schedule": [
            {"week": g["week"],
             "opponent": g["awayTeam"] if g["homeTeam"] == team else g["homeTeam"],
             "home": g["homeTeam"] == team,
             "pf": g["homePoints"] if g["homeTeam"] == team else g["awayPoints"],
             "pa": g["awayPoints"] if g["homeTeam"] == team else g["homePoints"]}
            for g in sorted(games, key=lambda z: z["week"])],
    }

    snap["ppa_games"] = client.get("/ppa/games", year=season, team=team)
    snap["ppa_team_season"] = client.get("/ppa/teams", year=season, team=team)
    snap["adv_games_baylor"] = client.get("/stats/game/advanced", year=season, team=team)
    snap["adv_game"] = [r for r in snap["adv_games_baylor"] if r.get("gameId") == rw.game_id]
    snap["adv_season_baylor"] = client.get("/stats/season/advanced", year=season, team=team)
    snap["drives"] = client.get("/drives", year=season, week=week, team=team)
    snap["plays"] = client.get("/plays", year=season, week=week, team=team)
    snap["winprob_raw"] = client.get("/metrics/wp", gameId=rw.game_id)

    if rw.next_opponent:
        snap["ppa_next_opp"] = client.get("/ppa/teams", year=season, team=rw.next_opponent)
        snap["adv_season_next_opp"] = client.get("/stats/season/advanced", year=season,
                                                 team=rw.next_opponent)
        snap["next_opp_ppa_games"] = client.get("/ppa/games", year=season,
                                                team=rw.next_opponent)
        snap["next_opp_adv_games"] = client.get("/stats/game/advanced", year=season,
                                                team=rw.next_opponent)
    else:
        snap["ppa_next_opp"] = snap["adv_season_next_opp"] = []
        snap["next_opp_ppa_games"] = snap["next_opp_adv_games"] = []

    all_adv = client.get("/stats/season/advanced", year=season)
    conf = {t["school"]: t.get("conference")
            for t in client.get("/teams/fbs", year=season)}
    snap["p4"] = p4_distributions(all_adv, conf)
    snap["baylor_season_adv"] = snap["adv_season_baylor"][0] if snap["adv_season_baylor"] else {}
    snap["next_opp_season_adv"] = (snap["adv_season_next_opp"][0]
                                   if snap["adv_season_next_opp"] else {})

    tid = pff.team_id(con)
    snap["meta"]["pff_team_id"] = tid
    snap["pff_grades"] = pff.game_grades(con, season, week)
    snap["pff_season_snaps"] = pff.season_snap_rows(con, season, tid, through_week=week)
    return snap
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_snapshot.py -v`
Expected: 4 passed

- [ ] **Step 5: Upgrade the salvaged fixture to the new snapshot shape**

The salvaged `snapshot_2025w06.json` was written by the prototype's
`pull_snapshot.py` and does **not** match what `build_snapshot` now produces.
Three measured differences, all of which would crash or mislead the golden test in
Task 8:

| Fixture (old) | `build_snapshot` (new) |
|---|---|
| no `winprob_raw` — win probability lived in a separate `wp.json` | `snap["winprob_raw"]` |
| `meta.pff_game_id` | `meta.pff_team_id` |
| `pff_season_snaps` holds **1197 rows for both teams** — the old SQL had no team filter, and the prototype re-queried DuckDB separately to get Baylor only | `pff_season_snaps` is already filtered to Baylor |

Upgrade the fixture once, in place, and check the result in. Do not adapt it inside
the test — a fixture that needs a shim is a fixture that lies about the contract.

```python
# tests/fixtures/upgrade_snapshot.py — run once, then delete or keep as provenance
import json
from pathlib import Path

from coachreport.sources import pff

HERE = Path(__file__).parent
snap = json.loads((HERE / "snapshot_2025w06.json").read_text())

# 1. fold the separate win-probability file in
snap["winprob_raw"] = json.loads((HERE / "wp_2025w06.json").read_text())

# 2. pff_team_id replaces pff_game_id
con = pff.connect()
tid = pff.team_id(con)
snap["meta"]["pff_team_id"] = tid
snap["meta"].pop("pff_game_id", None)

# 3. season snaps, filtered to Baylor the way the prototype's second query did
snap["pff_season_snaps"] = pff.season_snap_rows(con, 2025, tid, through_week=6)
con.close()

(HERE / "snapshot_2025w06.json").write_text(json.dumps(snap, default=str))
print("winprob_raw:", len(snap["winprob_raw"]),
      "| pff_team_id:", tid,
      "| season snap rows:", len(snap["pff_season_snaps"]), "(was 1197, both teams)")
```

Run: `uv run python tests/fixtures/upgrade_snapshot.py`
Expected: `winprob_raw: 162 | pff_team_id: 118 | season snap rows: <fewer than 1197>`

- [ ] **Step 6: Add a fixture-shape guard so this cannot silently regress**

```python
# append to tests/test_snapshot.py
def test_fixture_matches_the_current_snapshot_shape():
    snap = json.loads((config.REPO / "tests/fixtures/snapshot_2025w06.json").read_text())
    assert "winprob_raw" in snap and snap["winprob_raw"], "fixture predates winprob_raw"
    assert "pff_team_id" in snap["meta"], "fixture predates pff_team_id"
    assert "pff_game_id" not in snap["meta"], "fixture still carries the old key"
```

Run: `uv run pytest tests/test_snapshot.py -v`
Expected: 5 passed

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: snapshot assembly, and upgrade the salvaged fixture to its shape"
```

---

### Task 6: Reference-range maths

**Files:**
- Create: `src/coachreport/metrics.py`
- Create: `tests/test_metrics.py`

**Interfaces:**
- Consumes: `snapshot.dig`.
- Produces:
  - `quantile(sorted_vals: list[float], q: float) -> float | None`
  - `percentile_of(sorted_vals: list[float], x: float) -> float | None`
  - `band_rows(row: dict, p4_dist: dict) -> list[dict]` — each row carries `key, label, side, unit, direction, value, p10, p25, p50, p75, p90, lo, hi, pctl, flag`
  - `PATHS: dict[str, tuple[tuple, str, str, str, int]]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_metrics.py
from coachreport.metrics import PATHS, band_rows, percentile_of, quantile


def test_quantile_interpolates():
    v = [1, 2, 3, 4, 5]
    assert quantile(v, 0.0) == 1
    assert quantile(v, 0.5) == 3
    assert quantile(v, 1.0) == 5
    assert quantile(v, 0.25) == 2


def test_quantile_of_empty_is_none():
    assert quantile([], 0.5) is None


def test_percentile_counts_values_below():
    assert percentile_of([1, 2, 3, 4], 3) == 50.0
    assert percentile_of([1, 2, 3, 4], 0) == 0.0
    assert percentile_of([1, 2, 3, 4], 9) == 100.0
    assert percentile_of([1, 2], None) is None


def test_direction_flips_percentile_so_higher_is_always_better():
    # off_stuff is "stuffed rate": lower is better, direction -1.
    dist = {"off_stuff": [0.10, 0.20, 0.30, 0.40]}
    rows = band_rows({"offense": {"stuffRate": 0.10}}, dist)
    row = next(r for r in rows if r["key"] == "off_stuff")
    assert row["direction"] == -1
    assert row["pctl"] == 100.0        # rawest value, best score
    assert row["flag"] == "high"


def test_metrics_missing_from_the_row_are_skipped_not_zeroed():
    dist = {"off_success": [0.3, 0.4, 0.5]}
    assert band_rows({"offense": {}}, dist) == []


def test_every_path_declares_a_direction_and_a_unit():
    for key, (path, label, side, unit, direction) in PATHS.items():
        assert side in ("off", "def")
        assert unit in ("pct", "dec")
        assert direction in (1, -1)
        assert label and not label.isupper()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_metrics.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.metrics'`

- [ ] **Step 3: Write `metrics.py`**

```python
"""Reference ranges. The chart grammar needs real quantiles, not just a percentile.

`direction` is +1 where higher is better and -1 where lower is better. `pctl` is
already polarity-corrected here so the template never re-orients an axis: on the
sheet, further right is always better, including on defensive rows.
"""
from .snapshot import dig

PATHS = {
    "off_success":    (("offense", "successRate"), "Success rate", "off", "pct", 1),
    "off_explosive":  (("offense", "explosiveness"), "Explosiveness", "off", "dec", 1),
    "off_ppa":        (("offense", "ppa"), "EPA per play", "off", "dec", 1),
    "off_rush_ppa":   (("offense", "rushingPlays", "ppa"), "EPA per rush", "off", "dec", 1),
    "off_pass_ppa":   (("offense", "passingPlays", "ppa"), "EPA per pass", "off", "dec", 1),
    "off_line_yards": (("offense", "lineYards"), "Line yards", "off", "dec", 1),
    "off_stuff":      (("offense", "stuffRate"), "Stuffed rate", "off", "pct", -1),
    "off_havoc":      (("offense", "havoc", "total"), "Havoc allowed", "off", "pct", -1),
    "def_success":    (("defense", "successRate"), "Success rate allowed", "def", "pct", -1),
    "def_explosive":  (("defense", "explosiveness"), "Explosiveness allowed", "def", "dec", -1),
    "def_ppa":        (("defense", "ppa"), "EPA per play allowed", "def", "dec", -1),
    "def_havoc":      (("defense", "havoc", "total"), "Havoc created", "def", "pct", 1),
    "def_line_yards": (("defense", "lineYards"), "Line yards allowed", "def", "dec", -1),
    "def_stuff":      (("defense", "stuffRate"), "Stuff rate", "def", "pct", 1),
}


def quantile(sorted_vals, q):
    if not sorted_vals:
        return None
    i = q * (len(sorted_vals) - 1)
    lo, hi = int(i), min(int(i) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (i - lo)


def percentile_of(sorted_vals, x):
    if x is None or not sorted_vals:
        return None
    below = sum(1 for v in sorted_vals if v < x)
    return round(100 * below / len(sorted_vals), 1)


def band_rows(row: dict, p4_dist: dict) -> list[dict]:
    out = []
    for key, (path, label, side, unit, direction) in PATHS.items():
        vals = sorted(v for v in p4_dist.get(key, []) if v is not None)
        v = dig(row, *path)
        if v is None or not vals:
            continue
        raw_p = percentile_of(vals, v)
        good_p = raw_p if direction == 1 else 100 - raw_p
        out.append({
            "key": key, "label": label, "side": side, "unit": unit,
            "direction": direction, "value": round(v, 4),
            "p10": round(quantile(vals, .10), 4), "p25": round(quantile(vals, .25), 4),
            "p50": round(quantile(vals, .50), 4), "p75": round(quantile(vals, .75), 4),
            "p90": round(quantile(vals, .90), 4),
            "lo": round(vals[0], 4), "hi": round(vals[-1], 4),
            "pctl": round(good_p, 1),
            "flag": "high" if good_p >= 90 else "low" if good_p <= 10 else None,
        })
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_metrics.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: reference-range metrics with polarity-corrected percentiles"
```

---

### Task 7: The player out-of-range rule

DESIGN.md documents this rule and the reasoning behind every constant. The code and the doc must agree.

**Files:**
- Create: `src/coachreport/flags.py`
- Create: `tests/test_flags.py`

**Interfaces:**
- Consumes: `metrics.quantile`.
- Produces:
  - `SPREAD_FLOOR = 4.0`, `ABS_FLOOR = 6`, `ABSENT_AT = 2`, `ABSENT_MED = 10`, `K = 1.5`
  - `RULE: dict` — the payload's `flag_rule` block
  - `band_for(prior: list[int]) -> dict | None`
  - `classify(this_week: int, band: dict | None) -> str | None` returning `"high" | "low" | "absent" | None`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_flags.py
from coachreport.flags import (ABS_FLOOR, ABSENT_AT, ABSENT_MED, K,
                               SPREAD_FLOOR, band_for, classify)


def test_constants_match_the_design_document():
    assert (SPREAD_FLOOR, ABS_FLOOR, ABSENT_AT, ABSENT_MED, K) == (4.0, 6, 2, 10, 1.5)


def test_fewer_than_three_prior_weeks_gives_no_band():
    assert band_for([40, 42]) is None
    assert classify(70, None) is None


def test_band_carries_both_triggers():
    b = band_for([40, 42, 44, 46, 48])
    assert b["med"] == 44
    assert b["trigger_hi"] >= b["hi"]
    assert b["trigger_lo"] <= b["lo"]


def test_one_snap_past_a_five_game_maximum_does_not_flag():
    # This is the exact case the old min/max rule got wrong.
    b = band_for([40, 42, 44, 46, 48])
    assert classify(49, b) is None


def test_a_real_jump_flags_high():
    b = band_for([40, 42, 44, 46, 48])
    assert classify(62, b) == "high"


def test_a_real_drop_flags_low():
    b = band_for([40, 42, 44, 46, 48])
    assert classify(24, b) == "low"


def test_a_metronome_does_not_flag_on_a_wobble():
    # Zero spread; the floor of 4 snaps keeps the fence from collapsing onto the median.
    b = band_for([50, 50, 50, 50, 50])
    assert b["spread"] == SPREAD_FLOOR
    assert classify(55, b) is None


def test_near_zero_snaps_for_a_regular_reads_as_absent_not_low():
    b = band_for([40, 42, 44, 46, 48])
    assert classify(1, b) == "absent"


def test_near_zero_snaps_for_a_bit_player_is_not_absent():
    b = band_for([3, 4, 5, 6, 7])
    assert classify(0, b) is None


def test_absent_wins_over_low_when_both_could_apply():
    b = band_for([40, 42, 44, 46, 48])
    assert classify(2, b) == "absent"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_flags.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.flags'`

- [ ] **Step 3: Write `flags.py`**

```python
"""What counts as out of range, for a player's weekly snap count.

A threshold that fires on noise gets ignored, and then the real one gets ignored
with it. This rule takes the STRICTER of two tests, because each alone fails a
real case:

  - the observed range alone flags one snap past a five-game maximum;
  - the spread fence alone flags a very consistent player for a game he has
    already played, and misses a large jump by a volatile one.

Three guards make it usable on five data points:
  SPREAD_FLOOR  a metronome must not flag on a small wobble
  ABS_FLOOR     a change must clear a real number of snaps, not just a ratio
  ABSENT_*      near-zero snaps for a regular is an AVAILABILITY fact, not a
                workload deviation, and is reported as such

These constants are documented in DESIGN.md. Changing one here without changing
the document makes the document a lie.
"""
from .metrics import quantile

K = 1.5              # Tukey fence multiplier, drawn on the sheet as a dashed rule
SPREAD_FLOOR = 4.0   # snaps
ABS_FLOOR = 6        # snaps away from his own median
ABSENT_AT = 2        # snaps this week
ABSENT_MED = 10      # ...against a prior median of at least this

RULE = {"k": K, "spread_floor": SPREAD_FLOOR, "abs_floor": ABS_FLOOR,
        "absent_at": ABSENT_AT, "absent_med": ABSENT_MED}


def band_for(prior: list[int]) -> dict | None:
    """The player's own reference range, from his own prior weeks. None under 3 games."""
    prior = sorted(v for v in prior if v > 0)
    if len(prior) < 3:
        return None
    p25, med, p75 = (round(quantile(prior, q), 1) for q in (.25, .50, .75))
    spread = max(p75 - p25, SPREAD_FLOOR)
    band = {"lo": prior[0], "p25": p25, "med": med, "p75": p75, "hi": prior[-1],
            "iqr": round(p75 - p25, 1), "spread": round(spread, 1),
            "fence_lo": round(med - K * spread, 1),
            "fence_hi": round(med + K * spread, 1)}
    band["trigger_hi"] = round(max(band["hi"], band["fence_hi"]), 1)
    band["trigger_lo"] = round(min(band["lo"], band["fence_lo"]), 1)
    return band


def classify(this_week: int, band: dict | None) -> str | None:
    if not band:
        return None
    if this_week <= ABSENT_AT and band["med"] >= ABSENT_MED:
        return "absent"
    if abs(this_week - band["med"]) < ABS_FLOOR:
        return None
    if this_week > band["trigger_hi"]:
        return "high"
    if this_week < band["trigger_lo"]:
        return "low"
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_flags.py -v`
Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: player out-of-range rule with stability guards"
```

---

### Task 8: Payload assembly and the golden regression test

The most important task. `build_meta` is the answer to "zero weekly hand-edits", and the golden test pins the whole derive layer against a week a human reviewed.

**Files:**
- Create: `src/coachreport/payload.py`
- Create: `tests/test_payload.py`

**Interfaces:**
- Consumes: `resolve.ResolvedWeek`, `metrics.band_rows`, `flags.band_for/classify/RULE`, `config.group_of/side_of`.
- Produces:
  - `build_meta(snap: dict, rw: ResolvedWeek) -> dict` — all keys listed in SPEC.md §3.1
  - `build_payloads(snap: dict, rw: ResolvedWeek) -> tuple[dict, dict]` returning `(coaches, performance)`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_payload.py
import json

import pytest

from coachreport import config
from coachreport.payload import build_meta, build_payloads
from coachreport.resolve import ResolvedWeek

RW = ResolvedWeek(season=2025, week=6, game_id=401756911, opponent="Kansas State",
                  home=True, next_opponent="TCU", next_week=8, next_home=False)


@pytest.fixture(scope="module")
def snap():
    return json.loads((config.REPO / "tests/fixtures/snapshot_2025w06.json").read_text())


@pytest.fixture(scope="module")
def built(snap):
    return build_payloads(snap, RW)


def test_meta_has_every_key_a_sheet_prints(snap):
    m = build_meta(snap, RW)
    for key in ("team", "opponent", "next_opponent", "season", "week", "date",
                "date_short", "venue", "team_score", "opp_score", "result", "home",
                "excitement", "next_week", "next_home", "next_game", "next_short",
                "week_label", "season_range", "baseline_range",
                "baseline_range_prose"):
        assert key in m, f"meta missing {key}"
        assert m[key] is not None, f"meta[{key}] is None"


def test_meta_labels_are_derived_not_typed(snap):
    m = build_meta(snap, RW)
    assert m["week_label"] == "week 6"
    assert m["season_range"] == "weeks 1–6"
    assert m["baseline_range"] == "weeks 1–5"
    assert m["next_game"] == "Week 8 · at TCU"
    assert m["next_short"] == "Wk 8 at TCU"
    assert m["result"] == "W"


def test_no_next_opponent_says_so_rather_than_crashing(snap):
    last = ResolvedWeek(2025, 6, 401756911, "Kansas State", True, None, None, None)
    m = build_meta(snap, last)
    assert m["next_game"] == "No further games"


def test_both_editions_quote_the_same_snap_count(built):
    a, b = built
    assert a["box_snaps"] == b["box_snaps"]
    assert a["box_snaps"]["off"] > 0


def test_both_editions_share_one_meta(built):
    a, b = built
    assert a["meta"] == b["meta"]


def test_no_week_appears_twice_anywhere(built):
    a, b = built
    for rows, key in ((a["epa_by_week"], "week"), (b["season_tempo"], "week")):
        weeks = [r[key] for r in rows]
        assert len(weeks) == len(set(weeks)), f"duplicate week in {weeks}"


def test_players_short_of_three_prior_weeks_are_kept_with_a_null_band(built):
    _, b = built
    thin = [p for p in b["season_players"] if p["band"] is None]
    assert all(p["flag"] is None for p in thin)


def test_golden_coaches_payload_matches_the_reviewed_week(built):
    a, _ = built
    expected = json.loads(
        (config.REPO / "tests/fixtures/expected_payload_a.json").read_text())
    assert a["bands"] == expected["bands"]
    assert a["box_snaps"] == expected["box_snaps"]
    assert a["score_events"] == expected["score_events"]
    assert a["pff_offense"] == expected["pff_offense"]
    assert a["pff_defense"] == expected["pff_defense"]


def test_golden_performance_payload_matches_the_reviewed_week(built):
    _, b = built
    expected = json.loads(
        (config.REPO / "tests/fixtures/expected_payload_b.json").read_text())
    assert b["group_totals"] == expected["group_totals"]
    assert b["flag_rule"] == expected["flag_rule"]
    assert ([(p["name"], p["flag"]) for p in b["season_players"] if p["flag"]]
            == [(p["name"], p["flag"]) for p in expected["season_players"] if p["flag"]])


def test_the_flagged_set_is_the_five_players_the_review_saw(built):
    _, b = built
    assert len([p for p in b["season_players"] if p["flag"]]) == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_payload.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.payload'`

- [ ] **Step 3: Write `payload.py`**

```python
"""Payload assembly. The payload is the frozen interface to the templates.

Every weekly variable a sheet prints is derived once, here, into `meta`. No
opponent name, date, week number or season label may be typed into markup — that
is the failure that killed the 2024 report. The same rule covers computed prose:
a claim like "the widest gap of the season" is generated from the rows rendered
beside it, never written down.
"""
from collections import defaultdict
from datetime import datetime

from . import config, flags
from .metrics import band_rows
from .resolve import ResolvedWeek


def build_meta(snap: dict, rw: ResolvedWeek) -> dict:
    game = snap["game"]
    dt = datetime.fromisoformat(str(game["date"]).replace("Z", "+00:00"))
    home = game["home"] == config.TEAM

    meta = {
        "team": config.TEAM,
        "opponent": rw.opponent,
        "next_opponent": rw.next_opponent,
        "season": rw.season,
        "week": rw.week,
        "date": dt.strftime("%B %-d, %Y"),
        "date_short": dt.strftime("%d %b %Y"),
        "venue": game["venue"],
        "team_score": game["home_points"] if home else game["away_points"],
        "opp_score": game["away_points"] if home else game["home_points"],
        "excitement": round(game["excitement"], 2) if game.get("excitement") else None,
        "home": home,
    }
    meta["result"] = "W" if meta["team_score"] > meta["opp_score"] else "L"

    if rw.next_opponent:
        vs = "vs" if rw.next_home else "at"
        meta["next_week"] = rw.next_week
        meta["next_home"] = rw.next_home
        meta["next_game"] = f"Week {rw.next_week} · {vs} {rw.next_opponent}"
        meta["next_short"] = f"Wk {rw.next_week} {vs} {rw.next_opponent}"
    else:
        meta["next_week"] = meta["next_home"] = None
        meta["next_game"] = meta["next_short"] = "No further games"

    prior = list(range(1, rw.week))
    meta["week_label"] = f"week {rw.week}"
    meta["season_range"] = f"weeks {prior[0]}–{rw.week}" if prior else f"week {rw.week}"
    if len(prior) > 1:
        meta["baseline_range"] = f"weeks {prior[0]}–{prior[-1]}"
        meta["baseline_range_prose"] = f"weeks {prior[0]} to {prior[-1]}"
    elif prior:
        meta["baseline_range"] = meta["baseline_range_prose"] = f"week {prior[0]}"
    else:
        meta["baseline_range"] = meta["baseline_range_prose"] = "no prior games"
    return meta


def _tempo(drives: list[dict]) -> dict:
    plays = sum(d["plays"] for d in drives)
    secs = sum(d["elapsed"]["minutes"] * 60 + d["elapsed"]["seconds"] for d in drives)
    yards = sum(d["yards"] for d in drives)
    n = len(drives)
    return {"drives": n, "plays": plays, "yards": yards, "sec": secs,
            "plays_per_drive": round(plays / n, 2) if n else 0,
            "sec_per_play": round(secs / plays, 1) if plays else 0,
            "yards_per_drive": round(yards / n, 1) if n else 0,
            "scoring_drives": sum(1 for d in drives if d["scoring"]),
            "three_and_outs": sum(1 for d in drives
                                  if d["plays"] <= 3 and not d["scoring"])}


def build_payloads(snap: dict, rw: ResolvedWeek) -> tuple[dict, dict]:
    team, week = config.TEAM, rw.week
    meta = build_meta(snap, rw)
    dist = snap["p4"]["dist"]

    # ---------------------------------------------------------- shared spine
    # One definition of the week's snap count, computed once and copied. Two
    # editions computing this separately is how they drifted apart the first time.
    bx = next((g for g in snap["adv_games_baylor"] if g["week"] == week), None)
    box_snaps = ({"off": bx["offense"]["plays"], "def": bx["defense"]["plays"],
                  "off_drives": bx["offense"]["drives"],
                  "def_drives": bx["defense"]["drives"]} if bx else None)

    drives = snap["drives"]
    tempo = {"baylor_off": _tempo([d for d in drives if d["offense"] == team]),
             "baylor_def": _tempo([d for d in drives if d["offense"] != team])}
    drive_log = [{"num": d["driveNumber"],
                  "off": "BU" if d["offense"] == team else "OPP",
                  "plays": d["plays"], "yards": d["yards"], "result": d["driveResult"],
                  "start_ytg": d["startYardsToGoal"],
                  "elapsed": d["elapsed"]["minutes"] * 60 + d["elapsed"]["seconds"],
                  "period": d["startPeriod"]}
                 for d in sorted(drives, key=lambda z: z["driveNumber"])]

    # per-player game snaps: max across grade types is the true snap count
    snaps, grade_map = {}, defaultdict(dict)
    for g in snap["pff_grades"]:
        k = (g["team_id"], g["name"], g["position"])
        snaps[k] = max(snaps.get(k, 0), g["snaps"] or 0)
        grade_map[k][g["grade_type"]] = g["grade"]

    tid = snap["meta"]["pff_team_id"]
    bay_rows = []
    for (t, name, pos), gm in grade_map.items():
        if t != tid:
            continue
        row = {"name": name, "position": pos, "group": config.group_of(pos),
               "side": config.side_of(pos), "snaps": snaps[(t, name, pos)]}
        row.update({k: round(v, 1) for k, v in gm.items() if v is not None})
        bay_rows.append(row)

    # ------------------------------------------------------ coaches edition
    wp = snap["winprob_raw"]
    winprob = [{"p": w["playNumber"], "wp": round(w["homeWinProbability"], 4),
                "hs": w["homeScore"], "as": w["awayScore"]} for w in wp]
    events = []
    for prev, cur in zip(wp, wp[1:]):
        if cur["homeScore"] != prev["homeScore"] or cur["awayScore"] != prev["awayScore"]:
            events.append({"p": cur["playNumber"], "hs": cur["homeScore"],
                           "as": cur["awayScore"],
                           "wp": round(cur["homeWinProbability"], 3),
                           "swing": round(cur["homeWinProbability"]
                                          - prev["homeWinProbability"], 3),
                           "text": (cur.get("playText") or "")[:96]})

    A = {
        "meta": meta,
        "p4_n": snap["p4"]["n_teams"],
        "bands": band_rows(snap["baylor_season_adv"], dist),
        "next_bands": band_rows(snap["next_opp_season_adv"], dist),
        "winprob": winprob,
        "score_events": events,
        "box": {"offense": snap["adv_game"][0]["offense"],
                "defense": snap["adv_game"][0]["defense"]},
        "ppa_game": next((g for g in snap["ppa_games"]
                          if g["gameId"] == rw.game_id), None),
        "ppa_season": snap["ppa_team_season"][0] if snap["ppa_team_season"] else {},
        "epa_by_week": [{"week": g["week"], "opponent": g["opponent"],
                         "off": g["offense"]["overall"], "def": g["defense"]["overall"]}
                        for g in sorted(snap["ppa_games"], key=lambda z: z["week"])],
        "drive_log": drive_log,
        "tempo": tempo,
        "box_snaps": box_snaps,
        "pff_offense": sorted(
            [{k: r[k] for k in ("name", "position", "group", "snaps", "offense")}
             for r in bay_rows if r.get("offense") is not None and r["snaps"] >= 15],
            key=lambda z: -z["offense"])[:11],
        "pff_defense": sorted(
            [{k: r[k] for k in ("name", "position", "group", "snaps", "defense")}
             for r in bay_rows if r.get("defense") is not None and r["snaps"] >= 15],
            key=lambda z: -z["defense"])[:11],
    }

    # -------------------------------------------------- performance edition
    q_off, q_def = defaultdict(int), defaultdict(int)
    for p in snap["plays"]:
        (q_off if p["offense"] == team else q_def)[p["period"]] += 1

    def tempo_rows(adv):
        return [{"week": g["week"], "opponent": g["opponent"],
                 "off_plays": g["offense"]["plays"], "def_plays": g["defense"]["plays"],
                 "off_drives": g["offense"]["drives"],
                 "def_drives": g["defense"]["drives"]}
                for g in sorted(adv, key=lambda z: z["week"]) if g["week"] <= week]

    grp = defaultdict(lambda: {"snaps": 0, "n": 0})
    for r in bay_rows:
        grp[r["group"]]["snaps"] += r["snaps"]
        grp[r["group"]]["n"] += 1

    series, pos = defaultdict(dict), {}
    for r in snap["pff_season_snaps"]:
        series[r["name"]][int(r["week"])] = int(r["snaps"] or 0)
        pos[r["name"]] = r["position"]
    weeks = sorted({int(r["week"]) for r in snap["pff_season_snaps"]})

    season_players = []
    for name, by_week in series.items():
        prior = [v for w, v in by_week.items() if w < week and v > 0]
        this = by_week.get(week, 0)
        band = flags.band_for(prior)
        base = sum(prior) / len(prior) if prior else 0
        season_players.append({
            "name": name, "position": pos[name],
            "group": config.group_of(pos[name]), "side": config.side_of(pos[name]),
            "by_week": {str(w): by_week.get(w, 0) for w in weeks},
            "total": sum(by_week.values()),
            "games": len([v for v in by_week.values() if v > 0]),
            "this_week": this, "baseline": round(base, 1), "band": band,
            "delta_pct": round(100 * (this - base) / base, 1) if base else None,
            "dev": round(this - band["med"], 1) if band else None,
            "flag": flags.classify(this, band),
        })

    B = {
        "meta": meta,
        "tempo": tempo,
        "snaps_by_quarter": [{"q": q, "off": q_off.get(q, 0), "def": q_def.get(q, 0)}
                             for q in sorted(set(q_off) | set(q_def))],
        "drive_log": drive_log,
        "season_tempo": tempo_rows(snap["adv_games_baylor"]),
        "next_opp_tempo": tempo_rows(snap["next_opp_adv_games"]),
        "box_snaps": box_snaps,          # copied from A, never recomputed
        "group_totals": [{"group": g, "side": config.SIDE.get(g, "st"),
                          "snaps": v["snaps"], "players": v["n"],
                          "avg": round(v["snaps"] / v["n"], 1)}
                         for g, v in sorted(grp.items(), key=lambda kv: -kv[1]["snaps"])],
        "weeks": weeks,
        "flag_rule": flags.RULE,
        "season_players": sorted(season_players, key=lambda z: -z["this_week"]),
    }
    return A, B
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_payload.py -v`
Expected: 10 passed

If a golden assertion fails, the difference is real: either the refactor changed a
number, or the prototype had a bug the refactor fixed. Do not loosen the assertion
to make it pass. Diff the two payloads, decide which is right, and if the new one
is right, regenerate the fixture in the same commit with a message saying why.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: payload assembly with derived meta and golden regression"
```

---

### Task 9: Font embedding

**Files:**
- Create: `src/coachreport/fonts.py`
- Create: `tests/test_fonts.py`

**Interfaces:**
- Consumes: `config.FONTS`, `config.TEMPLATES`.
- Produces:
  - `FACES: list[tuple[str, str, tuple[int, int]]]`
  - `font_style_block(cache_dir=None) -> str` — a complete `<style>` element
  - `embed(html: str, cache_dir=None) -> str` — idempotent

- [ ] **Step 1: Write the failing test**

```python
# tests/test_fonts.py
import pytest

from coachreport import config, fonts

pytestmark = pytest.mark.skipif(
    not list(config.FONTS.glob("*.woff2")),
    reason="font cache not present")


def test_block_embeds_all_three_families_as_data_uris():
    block = fonts.font_style_block()
    for pretty, _slug, _w in fonts.FACES:
        assert f"font-family:'{pretty}'" in block
    assert "data:font/woff2;base64," in block
    assert "fonts.gstatic.com" not in block


def test_each_family_is_embedded_once_with_a_weight_range():
    block = fonts.font_style_block()
    assert block.count("@font-face") == 3
    assert block.count("font-weight:400 700") == 3


def test_embed_is_idempotent():
    html = "<head><style>/* x */</style>__FONTS__</head>"
    once = fonts.embed(html)
    twice = fonts.embed(once)
    assert once == twice
    assert twice.count("@font-face") == 3


def test_embed_replaces_a_google_fonts_link_block():
    html = ('<head><link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=X">'
            '</head>')
    out = fonts.embed(html)
    assert "fonts.googleapis.com" not in out
    assert "@font-face" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_fonts.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.fonts'`

- [ ] **Step 3: Write `fonts.py`**

```python
"""Self-host the three typefaces as inline @font-face data URIs.

PRODUCT.md requires a single self-contained file that survives being emailed and
re-rendered. A <link> to fonts.googleapis.com does not meet that: offline, the
pages fall back to Arial Narrow / system mono / system sans and the design
collapses.

All three families are variable fonts, so every requested weight returns a
byte-identical file. Embed each family ONCE with a weight range, not once per
weight: 78 KB raw across all three instead of 189 KB.

The .woff2 files are checked into the repo, so a build never needs the network.
Idempotent: re-running replaces the block it wrote last time.
"""
import base64
import re
import subprocess

from . import config

FACES = [
    ("Archivo Narrow", "Archivo+Narrow", (400, 700)),
    ("JetBrains Mono", "JetBrains+Mono", (400, 700)),
    ("Source Sans 3", "Source+Sans+3", (400, 700)),
]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
RANGE = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
         "U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
MARK = "/* Self-hosted: the sheets must render identically with no network. */"

SLOT = re.compile(r"__FONTS__")
LINKS = re.compile(
    r'(?:<link rel="preconnect" href="https://fonts\.[a-z]+\.com"[^>]*>\s*)*'
    r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]+">')
EXISTING = re.compile(r"<style>\s*" + re.escape(MARK) + r".*?</style>", re.S)


def _fetch(url: str) -> bytes:
    return subprocess.run(["curl", "-sSL", "-A", UA, url],
                          capture_output=True, check=True).stdout


def _woff2(slug: str, w_lo: int, w_hi: int, cache_dir) -> bytes:
    cached = cache_dir / f"{slug}.woff2"
    if cached.exists():
        return cached.read_bytes()
    css = _fetch(f"https://fonts.googleapis.com/css2?family={slug}"
                 f":wght@{w_lo};{w_hi}&display=swap").decode()
    latin = next(f for f in re.findall(r"@font-face\s*\{[^}]*\}", css)
                 if "U+0000-00FF" in f)
    url = re.search(r"url\((https://[^)]+\.woff2)\)", latin).group(1)
    data = _fetch(url)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(data)
    return data


def font_style_block(cache_dir=None) -> str:
    cache_dir = cache_dir or config.FONTS
    blocks = []
    for pretty, slug, (w_lo, w_hi) in FACES:
        b64 = base64.b64encode(_woff2(slug, w_lo, w_hi, cache_dir)).decode()
        blocks.append(
            f"@font-face{{font-family:'{pretty}';font-style:normal;"
            f"font-weight:{w_lo} {w_hi};font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
            f"unicode-range:{RANGE};}}")
    return "<style>\n" + MARK + "\n" + "\n".join(blocks) + "\n</style>"


def embed(html: str, cache_dir=None) -> str:
    block = font_style_block(cache_dir)
    for pattern in (EXISTING, LINKS, SLOT):
        if pattern.search(html):
            html = pattern.sub(lambda _: block, html, count=1)
            break
    else:
        raise RuntimeError("no font block, font link or __FONTS__ slot in the template")
    if "fonts.googleapis.com" in html or "fonts.gstatic.com" in html:
        raise RuntimeError("template still references a font host after embedding")
    return html
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_fonts.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: idempotent offline font embedding"
```

---

### Task 10: Render payload into the templates

**Files:**
- Create: `src/coachreport/render.py`
- Create: `tests/test_render.py`

**Interfaces:**
- Consumes: `config.TEMPLATES`, `config.EDITIONS`, `fonts.embed`.
- Produces:
  - `inject(template_html: str, payload: dict) -> str`
  - `render_edition(edition: str, payload: dict, out_dir: Path) -> Path`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_render.py
import json

import pytest

from coachreport import config, render


def test_inject_replaces_the_placeholder():
    out = render.inject("<script>const D=__PAYLOAD__;</script>__FONTS__", {"a": 1})
    assert '{"a":1}' in out or '{"a": 1}' in out
    assert "__PAYLOAD__" not in out


def test_inject_escapes_a_closing_script_tag_in_the_data():
    payload = {"text": "sack </script> forced fumble"}
    out = render.inject("<script>const D=__PAYLOAD__;</script>__FONTS__", payload)
    assert "</script> forced" not in out
    assert "<\\/script>" in out


def test_inject_fails_loudly_when_the_template_has_no_slot():
    with pytest.raises(AssertionError):
        render.inject("<html>no slot</html>", {})


def test_every_declared_edition_has_a_template_on_disk():
    for name in config.EDITIONS.values():
        assert (config.TEMPLATES / name).exists(), f"missing template {name}"


def test_rendered_file_is_self_contained(tmp_path):
    payload = json.loads(
        (config.REPO / "tests/fixtures/expected_payload_a.json").read_text())
    out = render.render_edition("coaches", payload, tmp_path)
    html = out.read_text()
    assert "fonts.googleapis.com" not in html
    assert "fonts.gstatic.com" not in html
    assert "__PAYLOAD__" not in html
    assert "<script src=\"http" not in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.render'`

- [ ] **Step 3: Write `render.py`**

```python
"""Inject a payload into a template. The template is never edited by hand."""
import json
from pathlib import Path

from . import config, fonts

SLOT = "__PAYLOAD__"


def inject(template_html: str, payload: dict) -> str:
    assert SLOT in template_html, f"no {SLOT} placeholder in template"
    data = json.dumps(payload, separators=(",", ":"), default=str)
    # keep a play description containing </script> from closing the block
    data = data.replace("</", "<\\/")
    return template_html.replace(SLOT, data)


def render_edition(edition: str, payload: dict, out_dir: Path) -> Path:
    template = config.TEMPLATES / config.EDITIONS[edition]
    html = fonts.embed(inject(template.read_text(), payload))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{edition}.html"
    out.write_text(html)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_render.py -v`
Expected: 5 passed

If `test_inject_replaces_the_placeholder` fails because the moved template has no
`__PAYLOAD__` slot, add the slot to `templates/*.tpl.html` — the prototype templates
carry it, but confirm rather than assume.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: render payloads into self-contained editions"
```

---

### Task 11: PDF export and the render-time gates

**Files:**
- Create: `src/coachreport/pdf.py`
- Create: `tests/test_pdf.py`

**Interfaces:**
- Consumes: rendered HTML paths.
- Produces:
  - `CHROME: str` — path to Google Chrome
  - `to_pdf(html_path: Path, pdf_path: Path, offline: bool = True) -> Path`
  - `page_count(pdf_path: Path) -> int`
  - `page_size_inches(pdf_path: Path) -> tuple[float, float]`
  - `check_gates(html_path: Path, pdf_path: Path) -> list[str]` — returns failure strings, empty when clean

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pdf.py
import json
from pathlib import Path

import pytest

from coachreport import config, pdf, render

pytestmark = pytest.mark.skipif(not Path(pdf.CHROME).exists(),
                                reason="Google Chrome not installed")


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    d = tmp_path_factory.mktemp("render")
    out = {}
    for edition, fixture in (("coaches", "expected_payload_a.json"),
                             ("performance", "expected_payload_b.json")):
        payload = json.loads((config.REPO / "tests/fixtures" / fixture).read_text())
        html = render.render_edition(edition, payload, d)
        out[edition] = (html, pdf.to_pdf(html, d / f"{edition}.pdf"))
    return out


def test_each_edition_is_five_pages(rendered):
    for edition, (_html, p) in rendered.items():
        assert pdf.page_count(p) == 5, f"{edition} is not 5 pages"


def test_pages_are_true_us_letter(rendered):
    for edition, (_html, p) in rendered.items():
        w, h = pdf.page_size_inches(p)
        assert round(w, 2) == 8.50 and round(h, 2) == 11.00, f"{edition} is {w}x{h}in"


def test_no_gate_fails(rendered):
    for edition, (html, p) in rendered.items():
        failures = pdf.check_gates(html, p)
        assert failures == [], f"{edition}: {failures}"


def test_the_probe_actually_reads_the_page(rendered):
    # A probe that returns nothing makes G2/G3/G4 pass vacuously. Prove it reports.
    html, _p = rendered["coaches"]
    reading = pdf.probe(html)
    assert reading["sheets"] == 5
    assert reading["fonts"] == [True, True, True]
    assert reading["bad"] == 0


def test_a_broken_page_makes_the_gates_fail(tmp_path):
    # A gate that cannot fail is not a gate.
    bad = tmp_path / "broken.html"
    bad.write_text(
        "<html><body>"
        "<div class='sheet' style='height:2400px'>NaN undefined</div>"
        "</body></html>")
    bad_pdf = pdf.to_pdf(bad, tmp_path / "broken.pdf")
    failures = pdf.check_gates(bad, bad_pdf)
    joined = " ".join(failures)
    assert "G1" in joined, "page-count gate did not fire"
    assert "G2" in joined, "overflow gate did not fire"
    assert "G3" in joined, "undefined/NaN gate did not fire"
    assert "G4" in joined, "offline-font gate did not fire"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_pdf.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.pdf'`

- [ ] **Step 3: Write `pdf.py`**

```python
"""Headless Chrome export, plus the gates that decide whether a run may ship.

Three traps this module exists to avoid:
  - Chrome stamps a file:/// path into the footer by default. --no-pdf-header-footer.
  - Byte size proves nothing. Page COUNT and page BOX are the arbiters, and a
    sheet that silently spilled onto a sixth page looks fine until it is printed.
  - `--evaluate-on-new-document` is a Puppeteer API, NOT a Chrome CLI flag. Chrome
    ignores unknown flags in silence, so a probe written that way returns nothing
    and every gate built on it passes vacuously. The probe below injects its script
    into a temporary copy of the document and reads the answer back out of
    <title> via --dump-dom, which does work from the command line.

The /Type/Pages and /MediaBox extraction below was verified against the two
known-good prototype PDFs: both report 5 pages at 8.5 x 11.0 in.
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OFFLINE_FLAGS = ["--host-resolver-rules=MAP * 0.0.0.0"]
BASE_FLAGS = ["--headless=new", "--disable-gpu", "--no-sandbox",
              "--no-pdf-header-footer", "--virtual-time-budget=8000"]


def _run(args: list[str]) -> str:
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"chrome failed: {r.stderr[-800:]}")
    return r.stdout


def to_pdf(html_path: Path, pdf_path: Path, offline: bool = True) -> Path:
    flags = BASE_FLAGS + (OFFLINE_FLAGS if offline else [])
    _run([CHROME, *flags, f"--print-to-pdf={pdf_path}", f"file://{html_path}"])
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"no PDF produced at {pdf_path}")
    return pdf_path


def page_count(pdf_path: Path) -> int:
    raw = pdf_path.read_bytes()
    counts = [int(m) for m in re.findall(rb"/Type\s*/Pages[^>]*?/Count\s+(\d+)", raw)]
    if counts:
        return max(counts)
    return len(re.findall(rb"/Type\s*/Page[^s]", raw))


def page_size_inches(pdf_path: Path) -> tuple[float, float]:
    raw = pdf_path.read_bytes()
    m = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", raw)
    if not m:
        raise RuntimeError("no /MediaBox in the PDF")
    x0, y0, x1, y1 = (float(v) for v in m.groups())
    return round((x1 - x0) / 72, 2), round((y1 - y0) / 72, 2)


# Appended to a TEMPORARY copy of the document. It writes its answer into the
# title, because --dump-dom is the only channel Chrome gives us from the CLI.
_PROBE_JS = """
<script>
document.fonts.ready.then(() => {
  const sheets = [...document.querySelectorAll('.sheet')];
  document.title = 'PROBE:' + JSON.stringify({
    sheets: sheets.length,
    tall: sheets.map((s, i) => [i, s.scrollHeight]).filter(([, h]) => h > 1056),
    fonts: ['Archivo Narrow', 'JetBrains Mono', 'Source Sans 3']
             .map(f => document.fonts.check('12px "' + f + '"')),
    bad: (document.body.innerText.match(/undefined|NaN/g) || []).length,
  });
});
</script>
"""


class ProbeFailed(RuntimeError):
    """The probe did not report. Never treat this as 'no problems found'."""


def probe(html_path: Path) -> dict:
    """Measure the rendered document with the network blackholed.

    Raises rather than returning {} — a silent empty probe is how G2/G3/G4 turn
    into gates that cannot fail.
    """
    with tempfile.TemporaryDirectory() as d:
        probed = Path(d) / html_path.name
        probed.write_text(html_path.read_text() + _PROBE_JS)
        out = _run([CHROME, *BASE_FLAGS, *OFFLINE_FLAGS, "--dump-dom",
                    f"file://{probed}"])
    m = re.search(r"<title>PROBE:(.*?)</title>", out, re.S)
    if not m:
        raise ProbeFailed(f"probe produced no reading for {html_path.name}")
    return json.loads(m.group(1))


def check_gates(html_path: Path, pdf_path: Path) -> list[str]:
    fails = []
    html = html_path.read_text()

    n = page_count(pdf_path)
    if n != 5:
        fails.append(f"G1 page count is {n}, expected 5")
    w, h = page_size_inches(pdf_path)
    if (w, h) != (8.5, 11.0):
        fails.append(f"G1 page box is {w}x{h}in, expected 8.5x11.0")

    for host in ("fonts.googleapis.com", "fonts.gstatic.com"):
        if host in html:
            fails.append(f"G5 output references {host}")

    try:
        p = probe(html_path)
    except ProbeFailed as e:
        return fails + [f"G2/G3/G4 could not be measured: {e}"]

    if p.get("tall"):
        fails.append(f"G2 sheets over one page: {p['tall']}")
    if p.get("bad"):
        fails.append(f"G3 {p['bad']} undefined/NaN in rendered text")
    if not all(p.get("fonts", [])):
        fails.append(f"G4 fonts not loaded offline: {p.get('fonts')}")
    return fails
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_pdf.py -v`
Expected: 5 passed

`test_a_broken_page_makes_the_gates_fail` is the important one. The first version of
this module used `--evaluate-on-new-document`, which is a Puppeteer API rather than a
Chrome CLI flag; Chrome ignored it silently and three of the five gates passed on
every input, including a deliberately broken one.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: PDF export with page-count, offline-font and overflow gates"
```

---

### Task 12: The Monday command

**Files:**
- Create: `src/coachreport/cli.py`
- Create: `src/coachreport/audit.py`
- Create: `tests/test_audit.py`
- Create: `README.md`

**Interfaces:**
- Consumes: everything above.
- Produces:
  - `audit.no_hardcoded_weekly_values(paths) -> list[str]`
  - `audit.no_tier_language(payload: dict) -> list[str]`
  - `cli.main(argv=None) -> int`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_audit.py
from coachreport import audit, config


def test_flags_a_hardcoded_year(tmp_path):
    f = tmp_path / "bad.html"
    f.write_text("<p>Week 6, 2025 vs Kansas State</p>")
    hits = audit.no_hardcoded_weekly_values([f])
    assert any("2025" in h for h in hits)
    assert any("Week 6" in h or "week number" in h for h in hits)
    assert any("Kansas State" in h for h in hits)


def test_passes_a_slot_driven_template(tmp_path):
    f = tmp_path / "good.html"
    f.write_text("<p data-slot='week_label'></p><p data-slot='opponent'></p>")
    assert audit.no_hardcoded_weekly_values([f]) == []


def test_config_is_exempt():
    assert audit.no_hardcoded_weekly_values(
        [config.REPO / "src/coachreport/config.py"]) == []


def test_tier_language_is_caught():
    payload = {"note": "an elite week from the front seven"}
    assert audit.no_tier_language(payload)


def test_neutral_language_passes():
    payload = {"note": "above his own range for weeks 1 to 5"}
    assert audit.no_tier_language(payload) == []


def test_a_year_inside_a_url_is_not_a_hardcode(tmp_path):
    f = tmp_path / "svg.html"
    f.write_text('const NS = "http://www.w3.org/2000/svg";')
    assert audit.no_hardcoded_weekly_values([f]) == []


def test_an_opponent_named_only_in_a_comment_is_not_a_hardcode(tmp_path):
    f = tmp_path / "brief.html"
    f.write_text("<!-- design brief: what TCU demands in week 8 -->\n<p></p>")
    assert audit.no_hardcoded_weekly_values([f]) == []


def test_the_font_unicode_range_is_not_a_year(tmp_path):
    f = tmp_path / "fonts.html"
    f.write_text("<style>\n/* Self-hosted: x */\n"
                 "@font-face{unicode-range:U+2000-206F,U+2074;}\n</style>")
    assert audit.no_hardcoded_weekly_values([f]) == []


def test_the_shipped_templates_are_clean():
    # Verified before this plan was written: both prototype templates scan clean
    # once comments, the font block and URLs are stripped.
    hits = audit.no_hardcoded_weekly_values(sorted(config.TEMPLATES.glob("*.html")))
    assert hits == [], hits


def test_the_source_tree_is_clean():
    # SPEC G6 covers src/ too. audit.py exempts config.py (where TEAM lives) and
    # itself (where the opponent list lives).
    hits = audit.no_hardcoded_weekly_values(
        sorted((config.REPO / "src/coachreport").rglob("*.py")))
    assert hits == [], hits
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_audit.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'coachreport.audit'`

- [ ] **Step 3: Write `audit.py`**

```python
"""Gates G6 and G10 — the two rules that are easy to break by accident.

G6 is the zero-hand-edits rule made checkable. G10 keeps the voice descriptive:
DESIGN.md forbids tier labels, and a standing reviewer preference forbids
blame-implying rationale.

Three sources of false positives were MEASURED on the real templates and are
stripped before scanning. Without the strip the audit reports four hits on two
genuinely clean files, and an audit that cries wolf gets switched off:
  - the embedded font CSS carries `U+2000-206F` and `U+2074`, which read as years;
  - the SVG namespace `http://www.w3.org/2000/svg` reads as the year 2000;
  - the design brief at the top of each template is an HTML comment and names the
    week's opponent in prose. A comment is not printed, so it is not a hand-edit.

With these three strips, both prototype templates scan CLEAN, and a file containing
`<p>Week 6, 2025 vs Kansas State</p>` is still caught on all three counts. Both
facts were verified before this plan was written.
"""
import json
import re
from pathlib import Path

COMMENT = re.compile(r"<!--.*?-->", re.S)
FONT_STYLE = re.compile(r"<style>\s*/\* Self-hosted:.*?</style>", re.S)
URL = re.compile(r"https?://\S+")
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
WEEK = re.compile(r"\bWeek\s+\d+\b", re.I)
# Big 12 opponents plus the non-conference names on the 2025 card. Config-free:
# any of these appearing as a literal in markup is a hand-edit waiting to happen.
OPPONENTS = [
    "Kansas State", "Kansas", "TCU", "Texas Tech", "Oklahoma State", "Iowa State",
    "Cincinnati", "Houston", "BYU", "Utah", "Arizona", "Arizona State", "Colorado",
    "UCF", "West Virginia", "Auburn", "SMU", "Samford", "Arkansas",
]
TIER_WORDS = ["elite", "poor", "weak", "bad", "underperform", "disappointing",
              "worst", "lazy", "soft"]
EXEMPT = {"config.py", "audit.py"}


def no_hardcoded_weekly_values(paths) -> list[str]:
    hits = []
    for p in (Path(x) for x in paths):
        if p.name in EXEMPT:
            continue
        text = p.read_text(errors="ignore")
        text = URL.sub("", FONT_STYLE.sub("", COMMENT.sub("", text)))
        for m in YEAR.findall(text):
            hits.append(f"{p.name}: hardcoded year {m}")
        for m in WEEK.findall(text):
            hits.append(f"{p.name}: hardcoded {m}")
        for name in OPPONENTS:
            if re.search(rf"\b{re.escape(name)}\b", text):
                hits.append(f"{p.name}: hardcoded opponent {name}")
    return sorted(set(hits))


def no_tier_language(payload: dict) -> list[str]:
    text = json.dumps(payload, default=str).lower()
    return [w for w in TIER_WORDS if re.search(rf"\b{w}", text)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_audit.py -v`
Expected: 10 passed

`test_the_shipped_templates_are_clean` should pass on the moved prototype
templates — that was measured, not assumed. If it ever fails later, the template
has acquired a hand-edit: replace the literal with a `meta` slot. Never weaken the
audit to make it pass.

- [ ] **Step 5: Write `cli.py`**

```python
"""The Monday command.

    uv run coachreport run
    uv run coachreport run --week 6 --season 2025
    uv run coachreport run --offline
"""
import argparse
import json
import sys
from datetime import datetime

from . import audit, config, payload, render, pdf, snapshot
from .resolve import NoCompletedGame, current_season, resolve_week
from .sources import cfbd, pff


def _out_dir(season: int, week: int):
    return config.OUT / str(season) / f"wk{week:02d}"


def run(season=None, week=None, offline=False, force=False) -> int:
    season = season or current_season()

    if offline:
        cached = sorted(config.OUT.glob(f"{season}/wk*/snapshot.json"))
        if not cached:
            print(f"no cached snapshot for {season}", file=sys.stderr)
            return 2
        snap = json.loads(cached[-1].read_text())
        rw = resolve_week([], config.TEAM, season, week=snap["meta"]["week"]) \
            if False else None
    client = con = None
    if not offline:
        client = cfbd.Client()
        try:
            games = client.get("/games", year=season, team=config.TEAM)
            rw = resolve_week(games, config.TEAM, season, week=week)
        except NoCompletedGame as e:
            print(e, file=sys.stderr)
            return 3
        con = pff.connect()
        snap = snapshot.build_snapshot(client, con, rw)
        con.close()
    else:
        from .resolve import ResolvedWeek
        m = snap["meta"]
        rw = ResolvedWeek(m["year"], m["week"], m["game_id"], m["opponent"], True,
                          m.get("next_opponent"), None, None)

    out = _out_dir(rw.season, rw.week)
    if out.exists() and not force and not week:
        print(f"{out} already exists — week {rw.week} is already built. "
              f"Re-run with --force to rebuild.", file=sys.stderr)
        return 4

    out.mkdir(parents=True, exist_ok=True)
    (out / "snapshot.json").write_text(json.dumps(snap, default=str))

    A, B = payload.build_payloads(snap, rw)
    failures = []
    for edition, data, name in (("coaches", A, "payload_a.json"),
                                ("performance", B, "payload_b.json")):
        (out / name).write_text(json.dumps(data, separators=(",", ":"), default=str))
        tiers = audit.no_tier_language(data)
        if tiers:
            failures.append(f"G10 {edition}: tier language {tiers}")
        html = render.render_edition(edition, data, out)
        pdf_path = pdf.to_pdf(html, out / f"{edition}.pdf")
        failures += [f"{edition}: {f}" for f in pdf.check_gates(html, pdf_path)]

    # SPEC G6 covers templates AND source. audit.py exempts config.py and itself.
    failures += audit.no_hardcoded_weekly_values(
        sorted(config.TEMPLATES.glob("*.html"))
        + sorted((config.REPO / "src/coachreport").rglob("*.py")))

    print(f"\n{config.TEAM} {rw.season} week {rw.week} "
          f"{'vs' if rw.home else 'at'} {rw.opponent}")
    print(f"next: {rw.next_opponent or 'none'}")
    print(f"wrote {out}")
    if failures:
        print("\nFAILED GATES:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("all gates passed")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="coachreport")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="build this week's two editions")
    r.add_argument("--season", type=int, default=None)
    r.add_argument("--week", type=int, default=None)
    r.add_argument("--offline", action="store_true",
                   help="rebuild from the cached snapshot, no API calls")
    r.add_argument("--force", action="store_true", help="rebuild a week already built")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run(a.season, a.week, a.offline, a.force)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Simplify the offline branch**

The offline branch above is written twice over. Collapse it so the snapshot is
loaded in exactly one place and `ResolvedWeek` is constructed in exactly one place:

```python
def _load_or_pull(season, week, offline):
    """Return (snapshot, ResolvedWeek). One path builds, one path reloads."""
    from .resolve import ResolvedWeek
    if offline:
        cached = sorted(config.OUT.glob(f"{season}/wk*/snapshot.json"))
        if not cached:
            raise NoCompletedGame(f"no cached snapshot for {season}")
        snap = json.loads(cached[-1].read_text())
        m = snap["meta"]
        nxt = m.get("next_opponent")
        return snap, ResolvedWeek(m["year"], m["week"], m["game_id"], m["opponent"],
                                  snap["game"]["home"] == config.TEAM,
                                  nxt, None, None)
    client = cfbd.Client()
    games = client.get("/games", year=season, team=config.TEAM)
    rw = resolve_week(games, config.TEAM, season, week=week)
    con = pff.connect()
    try:
        return snapshot.build_snapshot(client, con, rw), rw
    finally:
        con.close()
```

Then `run()` starts:

```python
def run(season=None, week=None, offline=False, force=False) -> int:
    season = season or current_season()
    try:
        snap, rw = _load_or_pull(season, week, offline)
    except NoCompletedGame as e:
        print(e, file=sys.stderr)
        return 3
```

Note that in the offline path `next_week`/`next_home` are unavailable, so
`meta["next_game"]` degrades to `"No further games"`. That is honest — an offline
rebuild is for checking a render, not for handing to a coach.

- [ ] **Step 7: Write `README.md`**

````markdown
# Weekly Coach Report

Two editions of one weekly football report for Baylor — a coaches edition and a
performance/medical edition — built from CFBD and PFF, printed and handed out.

Read `PRODUCT.md` (why), `DESIGN.md` (how it looks and what the charts may claim),
and `SPEC.md` (how it is built) before changing anything.

## Monday

```bash
cd ~/DEV/Football/WeeklyCoachReport
uv run coachreport run
```

It resolves the week itself. Output lands in `out/<season>/wk<NN>/`:
`coaches.pdf`, `performance.pdf`, both `.html`, both payloads, and the raw snapshot.

Exit codes: `0` clean · `1` a gate failed (do not print it) · `3` no completed game
(bye week) · `4` the week is already built (add `--force`).

## When it fails

| Symptom | Cause | Fix |
|---|---|---|
| `CFBD_API_KEY not found` | `~/DEV/CFB_Analytics_Lab/.env` moved | Restore the file; never paste the key into code |
| `no team row flagged is_baylor` | PFF database moved or replaced | Check `~/DEV/Football/PFF_Data_Project/data/pff.db` |
| `G1 page count is 6` | A sheet overflowed | `pdf.probe()` names the sheet; shorten it, do not shrink the type |
| `G4 fonts not loaded offline` | Font cache missing | `fonts/*.woff2` must be checked in |
| `G6 hardcoded opponent` | Someone typed a name into a template | Replace with a `meta` slot |
| exit 3 on a game week | CFBD has not posted the result yet | Wait; do not pass `--week` to force it |

## Tests

```bash
uv run pytest -v
```

The golden test rebuilds 2025 week 6 from a saved snapshot and compares against the
payload a human reviewed. If it fails, a number changed — find out which and why
before touching the fixture.
````

- [ ] **Step 8: Run the whole suite**

Run: `uv run pytest -v`
Expected: all tests pass

- [ ] **Step 9: Run the real command end to end**

Run: `uv run coachreport run --season 2025 --week 6 --force`
Expected: exit 0, `all gates passed`, four files in `out/2025/wk06/`

- [ ] **Step 10: Commit**

```bash
git add -A && git commit -m "feat: coachreport run — the Monday command, with all gates"
```

---

## After the plan

1. **Run one verdict pass on the templates before the first real week ships.** The
   fixes made after the prototype's last verdict were never re-reviewed. Do not
   assume a clean bill.
2. **Archive the prototypes.** `~/DEV/Football/CoachReport_Prototypes/` stays on disk
   as the reference rendering. Nothing new is added to it.
3. **Phase 2, not this season:** a launchd agent calling `coachreport run` on Monday
   morning plus a failure notification. No code change needed.
4. **Project 2 is a separate plan.** The year-over-year team-state report for S&C and
   medical needs its own brainstorming pass — see SPEC.md §8.

## Self-review notes

- **Spec coverage:** §1.1 → Tasks 2, 4, 12 (audit); §1.2 → Task 2 + CLI exit 3/4;
  §1.3 → Task 3; §2 layout → all tasks; §3.1 `meta` → Task 8; §3.2/§3.3 payloads →
  Task 8; §4 script fates → Tasks 3–10; §5 running → Task 12; §6 gates G1–G5 → Task
  11, G6/G10 → Task 12, G7 → Task 8, G8 → Task 8, G9 → Tasks 3 and 8; §7 open items →
  "After the plan"; §8 → out of scope by design.
- **Type consistency:** `ResolvedWeek` fields are used identically in Tasks 2, 5, 8
  and 12. `band_for`/`classify` signatures match between Tasks 7 and 8.
  `box_snaps` keys (`off`, `def`, `off_drives`, `def_drives`) match between Task 8
  and the SPEC. `check_gates` returns a list of strings in both Task 11 and Task 12.
- **Measured, not assumed.** Five facts in this plan were checked against the real
  artifacts before it was written, rather than reasoned about:
  1. PFF `team_id` for Baylor is derivable — `select team_id from teams where
     is_baylor` returns `118`, equal to `franchise_id`. The literal in
     `build_payloads.py` is unnecessary and Task 4 removes it.
  2. Both prototype templates carry the `__PAYLOAD__` slot.
  3. Both scan CLEAN under the G6 audit once comments, the font block and URLs are
     stripped, while a file with a real hardcode is still caught on all three
     counts. The strips remove three measured false positives (`U+2000-206F`,
     `U+2074`, and the SVG namespace URL) — they are not a loosening.
  4. The `/Type/Pages` and `/MediaBox` extraction in Task 11 was run against the two
     known-good prototype PDFs: both report 5 pages at 8.5 x 11.0 in.
  5. The salvaged fixture does **not** match the new snapshot shape — it has no
     `winprob_raw`, carries `pff_game_id` instead of `pff_team_id`, and its
     `pff_season_snaps` holds 1197 rows for both teams. Task 5 Step 5 upgrades it,
     and Task 5 Step 6 guards against the mismatch returning.
- **Two defects were found and fixed during self-review**, both of which would have
  cost an executor a debugging session: the Task 8 golden test would have raised
  `KeyError` on the un-upgraded fixture, and the Task 11 probe used
  `--evaluate-on-new-document`, a Puppeteer API that Chrome ignores in silence,
  which made G2, G3 and G4 pass on any input at all.

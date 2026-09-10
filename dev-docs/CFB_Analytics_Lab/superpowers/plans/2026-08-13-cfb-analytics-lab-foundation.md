# CFB Analytics Lab Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the data foundation and first lesson of a stateful learning workspace that applies techniques from Eager & Erickson's *Football Analytics with Python and R* to CollegeFootballData play-by-play.

**Architecture:** A budget-guarded CFBD puller writes immutable per-week Parquet to `data/raw/`. A deliberately thin `cfblab` package handles only fetching, loading, and classification filtering; all analytical transformation happens in notebooks, because in a learning project the transformation is the lesson. DuckDB queries Parquet directly so 1.3M plays never need to fit in memory.

**Tech Stack:** Python 3.14.6 (uv-managed venv), pandas 3.0.5, pyarrow, duckdb, statsmodels, scikit-learn, matplotlib, PyMC 6.3.0 + ArviZ, nbformat, pytest, requests.

**Spec:** `docs/superpowers/specs/2026-08-13-cfb-analytics-lab-design.md`

## Global Constraints

Every task's requirements implicitly include this section. Values are copied verbatim from the spec.

- Python **3.14.6** at `/opt/homebrew/bin/python3`; PEP 668-managed, so **venvs only** — never `pip install` globally.
- `uv` **0.11.6** at `~/.local/bin/uv` manages the venv and dependencies.
- CFBD base URL is **`https://api.collegefootballdata.com`**. Do not use `apinext` — it serves a byte-identical spec.
- Auth is `Authorization: Bearer <CFBD_API_KEY>`. Key is read from `~/DEV/CFB_Victory_Model/.env`.
- CFBD tier is **Free, 1,000 calls/month, reset `2026-09-01T00:00:00Z`**. 928 remaining as of 2026-08-13. CFB and CBB share one pool.
- **`/plays` requires an explicit `week` for BOTH `regular` and `postseason`.** Omitting it returns HTTP 400. Per-week iteration is mandatory.
- **Truncation tripwire: a response of exactly 2000 or exactly 100 rows is an error**, not data. `/plays/stats` silently caps at 2000; `/games/media` appears to cap at 100.
- Requests are **serial with a 1.0-second delay**. This is a free community API.
- **Never commit `.env`, `data/raw/`, `data/curated/`, or `data/call_ledger.csv`.** Already in `.gitignore`.
- pandas resolves to **3.0.5**; the book targets 1.x/2.x. Copy-on-write semantics differ. Expect small adaptations to book code.
- `/plays` returns **FBS and FCS games**. Store as returned; filter to FBS explicitly at analysis time.

---

### Task 1: Project scaffolding and environment

**Files:**
- Create: `pyproject.toml`
- Create: `src/cfblab/__init__.py`
- Create: `.env`
- Create: `tests/__init__.py`
- Create: `tests/test_smoke.py`

**Interfaces:**
- Consumes: nothing (first task)
- Produces: an importable `cfblab` package with `cfblab.__version__` (str), and a working `.venv` at the repo root.

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "cfblab"
version = "0.1.0"
description = "Learning workspace applying football-analytics techniques to college football data"
requires-python = ">=3.14"
dependencies = [
    "requests>=2.32",
    "pandas>=3.0",
    "pyarrow>=17",
    "duckdb>=1.1",
    "numpy>=2.0",
    "scipy>=1.14",
    "statsmodels>=0.14",
    "scikit-learn>=1.5",
    "matplotlib>=3.9",
    "seaborn>=0.13",
    "pymc>=6.0",
    "arviz>=0.20",
    "nbformat>=5.10",
    "jupyter>=1.1",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-mock>=3.14"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/cfblab"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create the package skeleton**

```bash
mkdir -p src/cfblab tests lessons learning-records data
```

Write `src/cfblab/__init__.py`:

```python
"""CFB Analytics Lab — thin data layer for the lesson notebooks."""

__version__ = "0.1.0"
```

Write `tests/__init__.py` as an empty file:

```bash
touch tests/__init__.py
```

- [ ] **Step 3: Write the failing smoke test**

Write `tests/test_smoke.py`:

```python
import cfblab


def test_package_imports_and_has_version():
    assert isinstance(cfblab.__version__, str)
    assert cfblab.__version__ == "0.1.0"
```

- [ ] **Step 4: Create the venv and install**

```bash
cd ~/DEV/CFB_Analytics_Lab
~/.local/bin/uv venv --python 3.14 .venv
~/.local/bin/uv pip install --python .venv/bin/python -e ".[dev]"
```

Expected: resolves and installs, including `pymc` and `pytensor`. This was verified on 2026-08-13; if PyMC fails to resolve, stop and report rather than pinning a different Python.

- [ ] **Step 5: Run the smoke test**

Run: `.venv/bin/pytest tests/test_smoke.py -v`
Expected: PASS

- [ ] **Step 6: Create `.env` from the existing key**

```bash
grep '^CFBD_API_KEY=' ~/DEV/CFB_Victory_Model/.env > ~/DEV/CFB_Analytics_Lab/.env
chmod 600 ~/DEV/CFB_Analytics_Lab/.env
```

Verify it is ignored by git:

```bash
git check-ignore -v .env
```

Expected: prints a line showing `.gitignore` matched `.env`. If it prints nothing, STOP — the key would be committed.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/cfblab/__init__.py tests/__init__.py tests/test_smoke.py
git commit -m "feat: project scaffolding and uv environment"
```

---

### Task 2: Budget guard and call ledger

The expensive failure mode is a pull that burns the monthly budget and locks the project out until Sept 1. This task builds the guard that prevents it. It is deliberately separate from `pull.py` so the guard is independently testable without touching the network.

**Files:**
- Create: `src/cfblab/budget.py`
- Test: `tests/test_budget.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `BudgetError(RuntimeError)`
  - `API_BASE: str` — `"https://api.collegefootballdata.com"`
  - `load_api_key(env_path: Path | None = None) -> str`
  - `get_info(api_key: str) -> dict` — GET `/info`, returns the parsed JSON dict
  - `check_budget(estimated_calls: int, info: dict, margin: float = 1.2) -> None` — raises `BudgetError` when `info["remainingCalls"] < estimated_calls * margin`
  - `log_call(ledger_path: Path, endpoint: str, status: int, rows: int) -> None` — appends one CSV row
  - `LEDGER_HEADER: list[str]` — `["timestamp", "endpoint", "status", "rows"]`

- [ ] **Step 1: Write the failing tests**

Write `tests/test_budget.py`:

```python
import csv
from pathlib import Path

import pytest

from cfblab.budget import (
    LEDGER_HEADER,
    BudgetError,
    check_budget,
    load_api_key,
    log_call,
)


def test_check_budget_passes_when_ample():
    info = {"remainingCalls": 928, "monthlyLimit": 1000}
    check_budget(estimated_calls=125, info=info)


def test_check_budget_raises_when_short():
    info = {"remainingCalls": 100, "monthlyLimit": 1000}
    with pytest.raises(BudgetError) as exc:
        check_budget(estimated_calls=125, info=info)
    assert "125" in str(exc.value)
    assert "100" in str(exc.value)


def test_check_budget_enforces_margin():
    # 125 calls * 1.2 margin = 150 required; 130 remaining is not enough.
    info = {"remainingCalls": 130, "monthlyLimit": 1000}
    with pytest.raises(BudgetError):
        check_budget(estimated_calls=125, info=info)


def test_load_api_key_reads_env_file(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text('CFBD_API_KEY="abc123"\n')
    assert load_api_key(env) == "abc123"


def test_load_api_key_raises_when_missing(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("SOMETHING_ELSE=1\n")
    with pytest.raises(RuntimeError):
        load_api_key(env)


def test_log_call_appends_with_header(tmp_path: Path):
    ledger = tmp_path / "call_ledger.csv"
    log_call(ledger, "/plays", 200, 18837)
    log_call(ledger, "/info", 200, 1)

    with ledger.open() as fh:
        rows = list(csv.reader(fh))

    assert rows[0] == LEDGER_HEADER
    assert len(rows) == 3
    assert rows[1][1] == "/plays"
    assert rows[1][3] == "18837"
    assert rows[2][1] == "/info"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_budget.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'cfblab.budget'`

- [ ] **Step 3: Write the implementation**

Write `src/cfblab/budget.py`:

```python
"""Budget guard and call ledger for the CFBD free tier.

The CFBD free tier allows 1,000 calls per month with a hard reset on the 1st.
A pull that dies halfway through burns calls with nothing to show for it, so
every pull runs a pre-flight check and every request is logged durably.
"""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

import requests

API_BASE = "https://api.collegefootballdata.com"
DEFAULT_ENV = Path.home() / "DEV" / "CFB_Analytics_Lab" / ".env"
LEDGER_HEADER = ["timestamp", "endpoint", "status", "rows"]


class BudgetError(RuntimeError):
    """Raised when a pull would exceed the remaining monthly call budget."""


def load_api_key(env_path: Path | None = None) -> str:
    """Read CFBD_API_KEY out of a KEY=VALUE file."""
    path = Path(env_path) if env_path is not None else DEFAULT_ENV
    if not path.exists():
        raise RuntimeError(f"No env file at {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == "CFBD_API_KEY":
            return value.strip().strip('"').strip("'")
    raise RuntimeError(f"CFBD_API_KEY not found in {path}")


def get_info(api_key: str) -> dict:
    """GET /info — tier, monthly limit, remaining calls, reset timestamp."""
    response = requests.get(
        f"{API_BASE}/info",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def check_budget(estimated_calls: int, info: dict, margin: float = 1.2) -> None:
    """Refuse to start a pull that could strand the budget.

    Raises BudgetError unless remaining calls cover the estimate plus margin.
    """
    remaining = int(info["remainingCalls"])
    required = int(estimated_calls * margin)
    if remaining < required:
        raise BudgetError(
            f"Refusing to pull: needs {estimated_calls} calls "
            f"({required} with {margin}x margin) but only {remaining} remain. "
            f"Budget resets {info.get('resetAt', 'on the 1st')}."
        )


def log_call(ledger_path: Path, endpoint: str, status: int, rows: int) -> None:
    """Append one request to the durable call ledger."""
    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if is_new:
            writer.writerow(LEDGER_HEADER)
        writer.writerow(
            [dt.datetime.now(dt.UTC).isoformat(), endpoint, status, rows]
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_budget.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/cfblab/budget.py tests/test_budget.py
git commit -m "feat: budget guard and call ledger for CFBD free tier"
```

---

### Task 3: Play-by-play puller with truncation tripwire

**Files:**
- Create: `src/cfblab/pull.py`
- Test: `tests/test_pull.py`

**Interfaces:**
- Consumes: `cfblab.budget.API_BASE`, `check_budget`, `get_info`, `load_api_key`, `log_call`, `BudgetError`
- Produces:
  - `TruncationError(RuntimeError)`
  - `SUSPECT_ROW_COUNTS: frozenset[int]` — `frozenset({100, 2000})`
  - `REQUEST_DELAY_SECONDS: float` — `1.0`
  - `MAX_REGULAR_WEEKS: int` — `20`
  - `MAX_POSTSEASON_WEEKS: int` — `3`
  - `fetch_plays(api_key: str, year: int, week: int, season_type: str) -> list[dict]`
  - `estimate_calls(years: list[int]) -> int`
  - `week_path(root: Path, year: int, season_type: str, week: int) -> Path`
  - `pull_years(years: list[int], root: Path, api_key: str, ledger_path: Path) -> dict[str, int]` — returns `{"fetched": int, "skipped": int}`

- [ ] **Step 1: Write the failing tests**

Write `tests/test_pull.py`:

```python
from pathlib import Path

import pytest

from cfblab.pull import (
    SUSPECT_ROW_COUNTS,
    TruncationError,
    estimate_calls,
    fetch_plays,
    week_path,
)


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_suspect_counts_are_the_documented_caps():
    assert SUSPECT_ROW_COUNTS == frozenset({100, 2000})


def test_fetch_plays_returns_rows(monkeypatch):
    payload = [{"gameId": 1, "playType": "Rush"}] * 137
    monkeypatch.setattr(
        "cfblab.pull.requests.get", lambda *a, **k: FakeResponse(payload)
    )
    rows = fetch_plays("KEY", 2025, 5, "regular")
    assert len(rows) == 137


def test_fetch_plays_raises_on_truncation(monkeypatch):
    # Exactly 2000 rows is the documented silent cap, never real data.
    payload = [{"gameId": 1}] * 2000
    monkeypatch.setattr(
        "cfblab.pull.requests.get", lambda *a, **k: FakeResponse(payload)
    )
    with pytest.raises(TruncationError) as exc:
        fetch_plays("KEY", 2025, 5, "regular")
    assert "2000" in str(exc.value)


def test_fetch_plays_allows_empty(monkeypatch):
    # Empty is the postseason termination signal, not an error.
    monkeypatch.setattr(
        "cfblab.pull.requests.get", lambda *a, **k: FakeResponse([])
    )
    assert fetch_plays("KEY", 2024, 9, "postseason") == []


def test_estimate_calls_covers_regular_and_postseason():
    # 20 regular-week probes + 3 postseason probes per season.
    assert estimate_calls([2024]) == 23
    assert estimate_calls([2019, 2020]) == 46


def test_week_path_is_partitioned(tmp_path: Path):
    p = week_path(tmp_path, 2025, "regular", 5)
    assert p.parent.name == "season=2025"
    assert p.name == "regular-week=05.parquet"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_pull.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'cfblab.pull'`

- [ ] **Step 3: Write the implementation**

Write `src/cfblab/pull.py`:

```python
"""CFBD play-by-play puller.

Writes immutable per-week Parquet under data/raw/plays/season=YYYY/.
Resumable: any week already on disk is skipped, so a crash costs nothing.

Two API facts drive this design, both verified 2026-08-13:
  * /plays requires an explicit week for BOTH regular and postseason.
    There is no whole-season call; per-week iteration sets the cost floor.
  * A response of exactly 2000 or exactly 100 rows is a silent cap, not data.
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

from cfblab.budget import API_BASE, check_budget, get_info, log_call

SUSPECT_ROW_COUNTS = frozenset({100, 2000})
REQUEST_DELAY_SECONDS = 1.0
MAX_REGULAR_WEEKS = 20
MAX_POSTSEASON_WEEKS = 3


class TruncationError(RuntimeError):
    """Raised when a response row count matches a known silent cap."""


def estimate_calls(years: list[int]) -> int:
    """Upper bound on calls for a pull: probe every possible week."""
    return len(years) * (MAX_REGULAR_WEEKS + MAX_POSTSEASON_WEEKS)


def week_path(root: Path, year: int, season_type: str, week: int) -> Path:
    return Path(root) / f"season={year}" / f"{season_type}-week={week:02d}.parquet"


def fetch_plays(api_key: str, year: int, week: int, season_type: str) -> list[dict]:
    """Fetch one week of plays. Raises TruncationError on a silent cap."""
    response = requests.get(
        f"{API_BASE}/plays",
        headers={"Authorization": f"Bearer {api_key}"},
        params={"year": year, "week": week, "seasonType": season_type},
        timeout=120,
    )
    response.raise_for_status()
    rows = response.json()
    if len(rows) in SUSPECT_ROW_COUNTS:
        raise TruncationError(
            f"/plays returned exactly {len(rows)} rows for {year} "
            f"{season_type} week {week} — that is a known silent cap, "
            f"not real data. Narrow the query and retry."
        )
    return rows


def pull_years(
    years: list[int],
    root: Path,
    api_key: str,
    ledger_path: Path,
) -> dict[str, int]:
    """Pull every week of every year. Idempotent and resumable."""
    check_budget(estimate_calls(years), get_info(api_key))

    root = Path(root)
    fetched = skipped = 0

    for year in years:
        for season_type, max_weeks in (
            ("regular", MAX_REGULAR_WEEKS),
            ("postseason", MAX_POSTSEASON_WEEKS),
        ):
            for week in range(1, max_weeks + 1):
                target = week_path(root, year, season_type, week)
                if target.exists():
                    skipped += 1
                    continue

                rows = fetch_plays(api_key, year, week, season_type)
                log_call(ledger_path, "/plays", 200, len(rows))
                time.sleep(REQUEST_DELAY_SECONDS)

                if not rows:
                    # Empty week terminates this season_type for this year.
                    break

                target.parent.mkdir(parents=True, exist_ok=True)
                pd.json_normalize(rows).to_parquet(target, index=False)
                fetched += 1

    return {"fetched": fetched, "skipped": skipped}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_pull.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/cfblab/pull.py tests/test_pull.py
git commit -m "feat: play-by-play puller with truncation tripwire and resume"
```

---

### Task 4: Classification filters and COVID flag

`/plays` returns FBS **and** FCS games. An FBS-vs-FCS blowout leaking into a completion-percentage-over-expected model corrupts it, so classification must be an explicit, visible act — never a hidden default.

**Files:**
- Create: `src/cfblab/filters.py`
- Test: `tests/test_filters.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `COVID_SEASONS: frozenset[int]` — `frozenset({2020})`
  - `add_covid_flag(plays: pd.DataFrame, season_col: str = "season") -> pd.DataFrame`
  - `attach_classification(plays: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame` — adds `homeClassification` and `awayClassification` by joining on `gameId`
  - `fbs_only(plays: pd.DataFrame) -> pd.DataFrame` — keeps rows where both classifications are `"fbs"`

- [ ] **Step 1: Write the failing tests**

Write `tests/test_filters.py`:

```python
import pandas as pd

from cfblab.filters import COVID_SEASONS, add_covid_flag, attach_classification, fbs_only


def test_covid_seasons_is_2020_only():
    assert COVID_SEASONS == frozenset({2020})


def test_add_covid_flag_marks_2020():
    plays = pd.DataFrame({"season": [2019, 2020, 2021]})
    out = add_covid_flag(plays)
    assert out["covid_season"].tolist() == [False, True, False]


def test_attach_classification_joins_on_gameid():
    plays = pd.DataFrame({"gameId": [1, 1, 2], "playType": ["Rush", "Pass", "Rush"]})
    games = pd.DataFrame(
        {
            "id": [1, 2],
            "homeClassification": ["fbs", "fbs"],
            "awayClassification": ["fbs", "fcs"],
        }
    )
    out = attach_classification(plays, games)
    assert out["awayClassification"].tolist() == ["fbs", "fbs", "fcs"]


def test_fbs_only_drops_fcs_matchups():
    plays = pd.DataFrame(
        {
            "gameId": [1, 2],
            "homeClassification": ["fbs", "fbs"],
            "awayClassification": ["fbs", "fcs"],
        }
    )
    out = fbs_only(plays)
    assert out["gameId"].tolist() == [1]


def test_fbs_only_does_not_mutate_input():
    plays = pd.DataFrame(
        {
            "gameId": [1, 2],
            "homeClassification": ["fbs", "fbs"],
            "awayClassification": ["fbs", "fcs"],
        }
    )
    fbs_only(plays)
    assert len(plays) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_filters.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'cfblab.filters'`

- [ ] **Step 3: Write the implementation**

Write `src/cfblab/filters.py`:

```python
"""Explicit classification and season filtering.

/plays ships FCS games alongside FBS. Filtering is deliberately a separate,
visible step rather than a default, so a notebook never silently analyses a
different population than its author thinks it does.
"""

from __future__ import annotations

import pandas as pd

COVID_SEASONS = frozenset({2020})


def add_covid_flag(plays: pd.DataFrame, season_col: str = "season") -> pd.DataFrame:
    """Mark COVID-affected seasons rather than dropping them.

    2020 was shortened, the Big Ten and Pac-12 played partial schedules, and
    non-conference play nearly vanished. Lesson 0001 uses this flag to show
    why year-over-year correlations spanning 2020 misbehave.
    """
    out = plays.copy()
    out["covid_season"] = out[season_col].isin(COVID_SEASONS)
    return out


def attach_classification(plays: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame:
    """Join division classification onto each play via gameId."""
    lookup = games[["id", "homeClassification", "awayClassification"]].rename(
        columns={"id": "gameId"}
    )
    return plays.merge(lookup, on="gameId", how="left")


def fbs_only(plays: pd.DataFrame) -> pd.DataFrame:
    """Keep only plays from games where BOTH teams are FBS."""
    mask = (plays["homeClassification"] == "fbs") & (
        plays["awayClassification"] == "fbs"
    )
    return plays.loc[mask].copy()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_filters.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/cfblab/filters.py tests/test_filters.py
git commit -m "feat: explicit FBS classification and COVID season flag"
```

---

### Task 5: Parquet and DuckDB loaders

**Files:**
- Create: `src/cfblab/io.py`
- Test: `tests/test_io.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `DEFAULT_RAW: Path` — `Path("data/raw/plays")`
  - `plays_glob(root: Path, years: list[int] | None = None) -> str`
  - `load_plays(root: Path, years: list[int] | None = None, columns: list[str] | None = None) -> pd.DataFrame`
  - `query(sql: str, root: Path) -> pd.DataFrame` — runs DuckDB SQL with a `plays` view registered over the Parquet
  - `load_victory_model_csv(name_glob: str) -> pd.DataFrame` — reads from `~/DEV/CFB_Victory_Model/data/cfbd/`, used by Lesson 0001

- [ ] **Step 1: Write the failing tests**

Write `tests/test_io.py`:

```python
from pathlib import Path

import pandas as pd

from cfblab.io import load_plays, plays_glob, query


def _seed(root: Path, year: int, week: int, rows: int) -> None:
    d = root / f"season={year}"
    d.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {"gameId": range(rows), "season": [year] * rows, "yardsGained": [3] * rows}
    ).to_parquet(d / f"regular-week={week:02d}.parquet", index=False)


def test_plays_glob_all_years(tmp_path: Path):
    assert plays_glob(tmp_path).endswith("season=*/*.parquet")


def test_plays_glob_single_year(tmp_path: Path):
    assert "season=2025" in plays_glob(tmp_path, [2025])


def test_load_plays_reads_all_partitions(tmp_path: Path):
    _seed(tmp_path, 2024, 1, 10)
    _seed(tmp_path, 2025, 1, 5)
    df = load_plays(tmp_path)
    assert len(df) == 15
    assert set(df["season"].unique()) == {2024, 2025}


def test_load_plays_filters_years(tmp_path: Path):
    _seed(tmp_path, 2024, 1, 10)
    _seed(tmp_path, 2025, 1, 5)
    df = load_plays(tmp_path, years=[2025])
    assert len(df) == 5


def test_query_runs_sql_over_parquet(tmp_path: Path):
    _seed(tmp_path, 2025, 1, 12)
    out = query("SELECT COUNT(*) AS n FROM plays", tmp_path)
    assert out["n"].iloc[0] == 12
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_io.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'cfblab.io'`

- [ ] **Step 3: Write the implementation**

Write `src/cfblab/io.py`:

```python
"""Loading helpers.

DuckDB reads the Parquet partitions directly so the notebooks can work with
1.3M plays without holding them all in pandas.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

DEFAULT_RAW = Path("data/raw/plays")
VICTORY_MODEL_CFBD = Path.home() / "DEV" / "CFB_Victory_Model" / "data" / "cfbd"


def plays_glob(root: Path, years: list[int] | None = None) -> str:
    """Build a glob covering the requested seasons."""
    root = Path(root)
    if years is None:
        return str(root / "season=*" / "*.parquet")
    if len(years) == 1:
        return str(root / f"season={years[0]}" / "*.parquet")
    joined = ",".join(str(y) for y in years)
    return str(root / f"season={{{joined}}}" / "*.parquet")


def load_plays(
    root: Path,
    years: list[int] | None = None,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Read plays into pandas. Pass `columns` to avoid loading everything."""
    select = ", ".join(columns) if columns else "*"
    pattern = plays_glob(root, years)
    return duckdb.sql(
        f"SELECT {select} FROM read_parquet('{pattern}')"  # noqa: S608
    ).df()


def query(sql: str, root: Path, years: list[int] | None = None) -> pd.DataFrame:
    """Run DuckDB SQL against a `plays` view over the Parquet partitions."""
    pattern = plays_glob(root, years)
    con = duckdb.connect()
    try:
        con.execute(
            f"CREATE VIEW plays AS SELECT * FROM read_parquet('{pattern}')"  # noqa: S608
        )
        return con.execute(sql).df()
    finally:
        con.close()


def load_victory_model_csv(name_glob: str) -> pd.DataFrame:
    """Concatenate matching CSVs from the existing CFB_Victory_Model pull.

    Lesson 0001 runs entirely on this already-downloaded data — no API calls.
    """
    paths = sorted(VICTORY_MODEL_CFBD.glob(name_glob))
    if not paths:
        raise FileNotFoundError(
            f"No CSVs matching {name_glob!r} in {VICTORY_MODEL_CFBD}"
        )
    return pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_io.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/cfblab/io.py tests/test_io.py
git commit -m "feat: Parquet and DuckDB loaders"
```

---

### Task 6: Teach-workspace documents

Mirrors `~/DEV/Terminal_Fluency` so the workspace is self-describing and resumable: `cd` in, read `MISSION.md` then `NOTES.md`, then the newest `learning-records/` entry. Do not re-interview about the mission.

**Files:**
- Create: `MISSION.md`
- Create: `NOTES.md`
- Create: `GLOSSARY.md`
- Create: `RESOURCES.md`
- Create: `README.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the resume protocol every later session depends on.

- [ ] **Step 1: Write `MISSION.md`**

```markdown
# Mission

Fluency in applying data-science techniques to football data — specifically the
methods in *Football Analytics with Python and R* (Eric A. Eager & Richard A.
Erickson, O'Reilly, 2023), transposed from the book's NFL/nflfastR data onto
college football data from the CollegeFootballData API.

## What fluency means here

Not "I ran the notebook." Fluency is: given a football question, choose an
appropriate method, fit it, and explain both what it says and where it breaks.

Each lesson ends in a drill completed unaided. The drill is the evidence.

## Scope

**In:** over-expected metrics (CPOE/RYOE), GLMs (logistic + Poisson), stability
analysis, clustering + PCA, tree ensembles, Bayesian hierarchical models.

**Out:** beating the betting market, Baylor coaching deliverables, and any change
to `~/DEV/CFB_Victory_Model` (which has a hard weekly cron dependency).

Bayesian methods are **not** in the book. Lesson 0007 is a deliberate extension
past the source material and is the steepest part of the curriculum.

## Why college data rather than the book's NFL data

The methods port directly — CFBD's `/plays` schema maps nearly one-to-one onto
nflfastR, and CFBD ships `ppa` per play where nflfastR ships `epa`. But college
football has a far wider talent spread (136 FBS teams plus FCS opponents), which
makes partial pooling genuinely more interesting here than in the NFL.
```

- [ ] **Step 2: Write `NOTES.md`**

```markdown
# Notes

## Resume protocol

1. `cd ~/DEV/CFB_Analytics_Lab`
2. Read `MISSION.md`, then this file.
3. Read the newest file in `learning-records/`.
4. Build the next lesson **only** if the previous drill has been reported.

Do not re-interview about the mission. This workspace is self-describing.

## Teaching preferences

- One lesson at a time. Never batch-generate notebooks — that produces reading
  material, not fluency.
- Glossary terms are promoted to `GLOSSARY.md` only after Eric *uses* them
  correctly, never on introduction.
- Drills are completed unaided. A drill Eric cannot do is the signal for what the
  next lesson covers.

## Verified environment (2026-08-13)

- Python 3.14.6, uv-managed venv at `.venv`. PEP 668 — never install globally.
- pandas resolves to **3.0.5**; the book targets 1.x/2.x. Copy-on-write semantics
  differ, so occasional book code needs small adaptations. This is expected.
- R is **not** installed and is not needed — PyMC covers hierarchical models.
- PyMC 6.3.0 / PyTensor 3.2.4 verified to resolve on Python 3.14.

## CFBD budget

Free tier: **1,000 calls/month**, reset on the 1st. CFB and CBB share the pool.
Check remaining with `/info` before any pull. `data/call_ledger.csv` is the
durable record; `/info/usage` only covers a rolling 7 days.

## Lesson ledger

| # | Lesson | Built | Drill reported |
|---|---|---|---|
| 0001 | Stability / year-over-year | pending | pending |
```

- [ ] **Step 3: Write `GLOSSARY.md`**

```markdown
# Glossary

Terms are added here only after Eric has *used* them correctly — not when they
are first introduced in a lesson.

_(empty — lesson 0001 not yet drilled)_
```

- [ ] **Step 4: Write `RESOURCES.md`**

```markdown
# Resources

Per the teach protocol, every resource listed here must be fetched and confirmed
before it is cited in a lesson. Do not cite from parametric memory.

## Primary text

**Football Analytics with Python and R: Learning Data Science Through the Lens of
Sports** — Eric A. Eager & Richard A. Erickson, O'Reilly Media, 2023.
Uses nflfastR / `nfl_data_py` (NFL). Not yet ingested into the SecondBrain
library; `Knowledge/library/advisors/` currently holds only
`strength-and-conditioning.md`.

## Data

- CollegeFootballData API — `https://api.collegefootballdata.com`
- OpenAPI spec — `https://api.collegefootballdata.com/api-docs.json` (74 paths)
- Existing local pull — `~/DEV/CFB_Victory_Model/data/cfbd/` (101 CSVs, 58 MB,
  2019–2026; no play-by-play)

## Verified API constraints

See `docs/superpowers/specs/2026-08-13-cfb-analytics-lab-design.md` for the full
probe results, including the `/plays/stats` 2000-row silent truncation and the
mandatory `week` parameter.
```

- [ ] **Step 5: Write `README.md`**

```markdown
# CFB Analytics Lab

A learning workspace applying data-science techniques from *Football Analytics
with Python and R* to college football play-by-play data.

Start with `MISSION.md`, then `NOTES.md`.

## Setup

```bash
~/.local/bin/uv venv --python 3.14 .venv
~/.local/bin/uv pip install --python .venv/bin/python -e ".[dev]"
grep '^CFBD_API_KEY=' ~/DEV/CFB_Victory_Model/.env > .env
```

## Pull the data

```bash
.venv/bin/python -m cfblab.cli pull --years 2019 2020 2021 2022 2023 2024 2025
```

Budget-guarded: refuses to start if the monthly CFBD allowance cannot cover it.
Resumable: re-running skips weeks already on disk.

## Run the tests

```bash
.venv/bin/pytest -v
```

## Layout

| Path | What it is |
|---|---|
| `lessons/` | Notebooks, one per technique. Each ends in a drill. |
| `learning-records/` | Drill results. The evidence of fluency. |
| `src/cfblab/` | Thin data layer — pull, load, filter. Nothing analytical. |
| `data/raw/` | Immutable Parquet from CFBD. Gitignored, regenerable. |
| `docs/superpowers/` | Spec and implementation plan. |
```

- [ ] **Step 6: Commit**

```bash
git add MISSION.md NOTES.md GLOSSARY.md RESOURCES.md README.md
git commit -m "docs: teach-workspace mission, notes, glossary, resources"
```

---

### Task 7: CLI entry point and live data pull

This task spends real API calls. The budget guard runs first; if it refuses, stop and report rather than lowering the margin.

**Files:**
- Create: `src/cfblab/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `cfblab.budget.load_api_key`, `cfblab.pull.pull_years`, `estimate_calls`
- Produces: `main(argv: list[str] | None = None) -> int` and a `python -m cfblab.cli pull --years ...` entry point.

- [ ] **Step 1: Write the failing test**

Write `tests/test_cli.py`:

```python
from cfblab.cli import build_parser


def test_parser_accepts_years():
    args = build_parser().parse_args(["pull", "--years", "2024", "2025"])
    assert args.command == "pull"
    assert args.years == [2024, 2025]


def test_parser_defaults_to_full_range():
    args = build_parser().parse_args(["pull"])
    assert args.years == [2019, 2020, 2021, 2022, 2023, 2024, 2025]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'cfblab.cli'`

- [ ] **Step 3: Write the implementation**

Write `src/cfblab/cli.py`:

```python
"""Command-line entry point for the CFBD pull."""

from __future__ import annotations

import argparse
from pathlib import Path

from cfblab.budget import BudgetError, get_info, load_api_key
from cfblab.pull import estimate_calls, pull_years

DEFAULT_YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cfblab")
    sub = parser.add_subparsers(dest="command", required=True)

    pull = sub.add_parser("pull", help="Pull play-by-play from CFBD")
    pull.add_argument("--years", type=int, nargs="+", default=DEFAULT_YEARS)
    pull.add_argument("--root", type=Path, default=Path("data/raw/plays"))
    pull.add_argument("--ledger", type=Path, default=Path("data/call_ledger.csv"))

    sub.add_parser("budget", help="Show remaining CFBD call budget")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    api_key = load_api_key()

    if args.command == "budget":
        info = get_info(api_key)
        print(
            f"{info['tierName']}: {info['remainingCalls']}/{info['monthlyLimit']} "
            f"remaining, resets {info['resetAt']}"
        )
        return 0

    print(f"Estimated cost: {estimate_calls(args.years)} calls (upper bound)")
    try:
        result = pull_years(args.years, args.root, api_key, args.ledger)
    except BudgetError as exc:
        print(f"ABORTED: {exc}")
        return 1

    print(f"Fetched {result['fetched']} weeks, skipped {result['skipped']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_cli.py -v`
Expected: 2 passed

- [ ] **Step 5: Check the budget before spending anything**

Run: `.venv/bin/python -m cfblab.cli budget`
Expected: prints something like `Free: 927/1000 remaining, resets 2026-09-01T00:00:00.000Z`

If remaining is under 200, STOP and report — do not proceed with the pull.

- [ ] **Step 6: Run the live pull**

Run: `.venv/bin/python -m cfblab.cli pull`
Expected: ~125 weeks fetched over roughly 3–4 minutes (1s delay per call). Watch for `TruncationError` — if one fires, stop and report rather than retrying.

- [ ] **Step 7: Verify what landed**

```bash
.venv/bin/python -c "
from cfblab.io import load_plays, query
df = query('SELECT season, COUNT(*) AS plays FROM plays GROUP BY season ORDER BY season', 'data/raw/plays')
print(df)
print('total:', df['plays'].sum())
"
du -sh data/raw/plays
wc -l data/call_ledger.csv
```

Expected: 7 seasons, roughly 1.2–1.4M total plays, 200–300 MB on disk. 2020 should show a visibly lower count than its neighbours — that is the COVID season, and it is expected.

- [ ] **Step 8: Commit**

```bash
git add src/cfblab/cli.py tests/test_cli.py
git commit -m "feat: CLI entry point and budget-guarded live pull"
```

---

### Task 8: Cross-validation against CFBD's own aggregates

The check that matters most. Silent join bugs are the likeliest way this project produces confident nonsense: a plausible number that is simply wrong. This asserts that play-level data aggregated up matches what CFBD reports directly.

> **Deviation from the spec, deliberate.** The spec calls for aggregating to a
> *player*-season and comparing against `/stats/player/season` (Sawyer Robertson,
> playerId 4432759). That is not achievable from `/plays` alone: `/plays` carries
> no structured player attribution — athlete names appear only inside the free-text
> `playText` field. Structured per-player attribution lives in `/plays/stats`, which
> silently truncates at 2000 rows and would need one call per game (~950/season) to
> pull safely — far beyond the monthly budget. This plan therefore cross-validates at
> **team-season** level against `/stats/season`, which exercises the same joins and
> catches the same class of bug at a fraction of the cost. Update the spec to match.

**Files:**
- Create: `tests/test_crossvalidation.py`

**Interfaces:**
- Consumes: `cfblab.io.load_plays`, `cfblab.budget.load_api_key`, `API_BASE`
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Write the test**

Write `tests/test_crossvalidation.py`:

```python
"""Cross-validate derived play-level aggregates against CFBD's own endpoints.

Skipped unless the raw pull is present, so the unit suite stays offline.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import requests

from cfblab.budget import API_BASE, load_api_key
from cfblab.io import query

RAW = Path("data/raw/plays")

pytestmark = pytest.mark.skipif(
    not (RAW / "season=2025").exists(),
    reason="raw pull not present; run `python -m cfblab.cli pull` first",
)


def test_play_counts_are_plausible():
    df = query(
        "SELECT season, COUNT(*) AS n FROM plays GROUP BY season ORDER BY season",
        RAW,
    )
    assert len(df) == 7, "expected 7 seasons, 2019-2025"
    # A full FBS+FCS season is well over 100k plays.
    assert df["n"].min() > 80_000
    # 2020 was shortened; it should be the smallest season.
    assert df.loc[df["season"] == 2020, "n"].iloc[0] == df["n"].min()


def test_no_season_hit_the_truncation_cap():
    df = query(
        "SELECT season, COUNT(*) AS n FROM plays GROUP BY season",
        RAW,
    )
    assert 2000 not in set(df["n"]), "a season totalling exactly 2000 means truncation"


def test_baylor_2025_rush_attempts_match_cfbd_season_stats():
    """Aggregate plays up to a team-season and compare against /stats/season."""
    derived = query(
        """
        SELECT COUNT(*) AS rushes
        FROM plays
        WHERE season = 2025 AND offense = 'Baylor' AND playType = 'Rush'
        """,
        RAW,
    )["rushes"].iloc[0]

    response = requests.get(
        f"{API_BASE}/stats/season",
        headers={"Authorization": f"Bearer {load_api_key()}"},
        params={"year": 2025, "team": "Baylor"},
        timeout=60,
    )
    response.raise_for_status()
    stats = {row["statName"]: row["statValue"] for row in response.json()}
    reported = stats["rushingAttempts"]

    # Play-type labelling differs slightly from box-score conventions
    # (sacks, kneels, scrambles), so allow 15% drift. A larger gap means
    # the join or the filter is wrong, not a labelling nuance.
    assert abs(derived - reported) / reported < 0.15, (
        f"derived {derived} vs CFBD {reported} — investigate the join"
    )
```

- [ ] **Step 2: Run the cross-validation**

Run: `.venv/bin/pytest tests/test_crossvalidation.py -v`
Expected: 3 passed. If the Baylor comparison fails by more than 15%, STOP — do not adjust the tolerance to make it pass. Investigate whether `pull_years` dropped weeks or `json_normalize` mangled a column.

- [ ] **Step 3: Run the whole suite**

Run: `.venv/bin/pytest -v`
Expected: all tests pass (smoke, budget, pull, filters, io, cli, crossvalidation).

- [ ] **Step 4: Commit**

```bash
git add tests/test_crossvalidation.py
git commit -m "test: cross-validate play aggregates against CFBD season stats"
```

---

### Task 9: Lesson 0001 — Stability / year-over-year

Runs entirely on the existing `CFB_Victory_Model` CSVs — **no API calls**. This is deliberately the first lesson because it needs no pull and because knowing which metrics are noise changes how every later model is read.

**Files:**
- Create: `scripts/build_lesson_0001.py`
- Create: `lessons/0001-stability.ipynb` (generated)
- Create: `learning-records/0001-starting-floor.md`

**Interfaces:**
- Consumes: `cfblab.io.load_victory_model_csv`
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Write the notebook builder**

Notebooks are generated from a script so they stay reviewable in git diffs.

Write `scripts/build_lesson_0001.py`:

```python
"""Build lessons/0001-stability.ipynb via nbformat."""

from pathlib import Path

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell("""\
# Lesson 0001 — Stability: which stats are real?

**Prerequisite:** none. This lesson uses CSVs already on disk from
`CFB_Victory_Model`. It makes **no API calls**.

## The idea

Eric Eager's signature theme is that a statistic is only useful if it is
*repeatable*. A metric that swings wildly from season to season is mostly noise —
it describes what happened, but predicts nothing.

The test is simple: correlate a team's metric in year *N* with the same team's
metric in year *N+1*. High correlation means the metric measures something
durable about the team. Low correlation means you are measuring variance.

This reframes everything that follows. When a later model says a team is good at
something, the first question is: is that thing stable?
"""))

cells.append(nbf.v4.new_code_cell("""\
import pandas as pd
import matplotlib.pyplot as plt

from cfblab.io import load_victory_model_csv

season = load_victory_model_csv("season_advanced_*.csv")
print(season.shape)
season.head()
"""))

cells.append(nbf.v4.new_markdown_cell("""\
## Building year-over-year pairs

To correlate year *N* against *N+1* we self-join the table on team, shifting the
season by one. Every team-season that has a successor contributes one pair.
"""))

cells.append(nbf.v4.new_code_cell("""\
def yoy_pairs(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    \"\"\"Pair each team's metric in season N with the same team in N+1.\"\"\"
    cur = df[["season", "team", metric]].copy()
    nxt = cur.copy()
    nxt["season"] = nxt["season"] - 1
    return cur.merge(
        nxt, on=["season", "team"], suffixes=("_y1", "_y2")
    ).dropna()

# Inspect what columns are actually available before choosing metrics.
[c for c in season.columns if "offense" in c][:20]
"""))

cells.append(nbf.v4.new_markdown_cell("""\
## Stability of several metrics

Pick a handful of offensive metrics and compare their year-over-year correlation.
The ordering is the point — not the absolute values.
"""))

cells.append(nbf.v4.new_code_cell("""\
metrics = [
    "offense.successRate",
    "offense.explosiveness",
    "offense.ppa",
    "offense.rushingPlays.successRate",
    "offense.passingPlays.successRate",
]

results = []
for m in metrics:
    if m not in season.columns:
        print(f"skip (absent): {m}")
        continue
    pairs = yoy_pairs(season, m)
    r = pairs[f"{m}_y1"].corr(pairs[f"{m}_y2"])
    results.append({"metric": m, "r": r, "n_pairs": len(pairs)})

stability = pd.DataFrame(results).sort_values("r", ascending=False)
stability
"""))

cells.append(nbf.v4.new_markdown_cell("""\
## The COVID problem

2020 was shortened, the Big Ten and Pac-12 played partial schedules, and
non-conference play nearly vanished. Any pair spanning 2020 is comparing a normal
season against a strange one.

Recompute with 2020 pairs excluded and see how much the ordering moves.
"""))

cells.append(nbf.v4.new_code_cell("""\
clean = season[~season["season"].isin([2019, 2020])]

results_clean = []
for m in metrics:
    if m not in season.columns:
        continue
    pairs = yoy_pairs(clean, m)
    if len(pairs) < 20:
        continue
    results_clean.append({
        "metric": m,
        "r_excl_covid": pairs[f"{m}_y1"].corr(pairs[f"{m}_y2"]),
        "n_pairs": len(pairs),
    })

comparison = stability.merge(
    pd.DataFrame(results_clean)[["metric", "r_excl_covid"]], on="metric", how="left"
)
comparison["delta"] = comparison["r_excl_covid"] - comparison["r"]
comparison
"""))

cells.append(nbf.v4.new_markdown_cell("""\
## Regression to the mean, seen directly

Split teams into quintiles by year-1 performance and plot their average year-2
performance. If the metric were pure skill the line would be flat at the
identity; the flatter it slopes toward the overall mean, the more of year 1 was luck.
"""))

cells.append(nbf.v4.new_code_cell("""\
m = stability.iloc[0]["metric"]  # the most stable metric found above
pairs = yoy_pairs(season, m)
pairs["quintile"] = pd.qcut(pairs[f"{m}_y1"], 5, labels=False)

summary = pairs.groupby("quintile")[[f"{m}_y1", f"{m}_y2"]].mean()

ax = summary.plot(marker="o", figsize=(7, 4))
ax.set_title(f"Regression to the mean: {m}")
ax.set_xlabel("Year-1 quintile (0 = worst)")
ax.set_ylabel(m)
plt.tight_layout()
plt.show()

summary
"""))

cells.append(nbf.v4.new_markdown_cell("""\
---

## Drill 0001

Complete this **unaided** and write your answers to
`learning-records/0001-drill-result.md`.

1. Rank five team metrics of your choosing by year-over-year stability. Show the
   correlations and the number of pairs behind each.
2. For the **least** stable metric, explain in two or three sentences why it might
   be unstable. Is it a small-sample problem, a schedule problem, or is the thing
   it measures genuinely not a durable team trait?
3. One of your five will change rank when 2020 pairs are excluded. Which, and why?
4. Answer in your own words: a coach tells you his team was 3rd nationally in
   explosiveness last year and expects the same this year. What do you say?

You are done when someone reading your file could reproduce the ranking without
rerunning your code.
"""))

nb["cells"] = cells
out = Path("lessons/0001-stability.ipynb")
out.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, out)
print(f"wrote {out}")
```

- [ ] **Step 2: Build the notebook**

```bash
mkdir -p scripts
.venv/bin/python scripts/build_lesson_0001.py
```

Expected: `wrote lessons/0001-stability.ipynb`

- [ ] **Step 3: Execute the notebook end to end**

```bash
.venv/bin/jupyter execute lessons/0001-stability.ipynb --inplace
```

Expected: runs without error. If `season_advanced_*.csv` column names differ from
the `offense.successRate` style used above, fix the metric list in the builder
script and rebuild — do not hand-edit the `.ipynb`.

- [ ] **Step 4: Write the starting-floor record**

Write `learning-records/0001-starting-floor.md`:

```markdown
# 0001 — Starting floor

**Date:** 2026-08-13

## Claimed floor

Eric has an existing CFB Victory Model project (regression-based game forecasting,
evaluated against market lines 2019–2025) and works as a sport scientist at Baylor
Athletics Applied Performance, where he routinely handles force-plate, GPS, and
athlete-monitoring data.

Recorded as a **claim not yet corroborated**. The Drill 0001 result is what
confirms or supersedes it.

## What this predicts

Comfortable with: correlation, descriptive statistics, pandas dataframes, reading
a model's output.

Unknown: whether the *stability* framing — treating year-over-year correlation as
a filter on which metrics deserve attention at all — is already part of how he
reads data, or is new.

## Supersede this file when

Drill 0001 is reported. Write `learning-records/0001-drill-result.md` and update
the lesson ledger in `NOTES.md`.
```

- [ ] **Step 5: Update the lesson ledger**

In `NOTES.md`, change the ledger row for 0001 from `pending | pending` to
`built | pending`.

- [ ] **Step 6: Commit**

```bash
git add scripts/build_lesson_0001.py lessons/0001-stability.ipynb \
        learning-records/0001-starting-floor.md NOTES.md
git commit -m "feat: lesson 0001 stability analysis with drill"
```

---

## Done criteria

- [ ] `.venv/bin/pytest -v` passes, including cross-validation against CFBD.
- [ ] `data/raw/plays/` holds 7 seasons, ~1.2–1.4M plays, 200–300 MB.
- [ ] `data/call_ledger.csv` shows the pull cost and is gitignored.
- [ ] `.venv/bin/python -m cfblab.cli budget` shows remaining calls comfortably above zero.
- [ ] `lessons/0001-stability.ipynb` executes end to end.
- [ ] `git status` is clean and no `.env` or `data/` file is tracked.
- [ ] Eric has the Drill 0001 prompt and knows lesson 0002 is built only after he reports it.

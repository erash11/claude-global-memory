# CMJ Recovery Monitoring Report — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `scripts/generate_recovery_report.py` — a standalone script that reads `data/master_data.csv` and produces `output/recovery_report_YYYY-MM-DD.html` showing each athlete's pre-practice CMJ values across N consecutive sessions, colored to reveal session-to-session decline and deviation from personal window average.

**Architecture:** Six athlete×session metric grids (one per CMJ metric) stacked vertically in a self-contained HTML report. Each cell is colored by the worst of two signals: (1) session-to-session delta vs config thresholds, and (2) deviation from the athlete's personal window average. A summary table assigns each athlete a Recovered/Watch/At Risk badge across the full window. Reuses `calc_pct_change` and `get_metric_color` from `utils.py` and all thresholds from `config.yaml` — no changes to existing files.

**Tech Stack:** Python 3.10+, pandas, PyYAML, Jinja2 — same as existing scripts.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `scripts/generate_recovery_report.py` | **Create** | Data loading, grid building, badge assignment, CLI entrypoint |
| `templates/recovery_report_template.html` | **Create** | Jinja2 HTML template; self-contained, offline-safe, Baylor dark theme |
| `tests/test_recovery_report.py` | **Create** | Unit tests for all logic functions |
| `scripts/utils.py` | **Read-only** | Reuse `calc_pct_change`, `get_metric_color`, `format_pct` |
| `config.yaml` | **Read-only** | Thresholds, roster, column mapping |
| `data/master_data.csv` | **Read-only** | Source data |

**No other files are modified.**

---

## Shared Constants (used across multiple tasks)

These constants live in `generate_recovery_report.py` and mirror those in `generate_report.py`:

```python
METRIC_COLS = [
    "jump_height_cm",
    "rsi_modified",
    "mean_propulsive_force_n",
    "ecc_braking_rfd_ns",
    "time_to_takeoff_ms",
    "cm_depth_cm",
]

COL_TO_THRESHOLD_KEY = {
    "jump_height_cm": "jump_height",
    "rsi_modified": "rsi_modified",
    "mean_propulsive_force_n": "mean_propulsive_force",
    "ecc_braking_rfd_ns": "ecc_braking_rfd",
    "time_to_takeoff_ms": "time_to_takeoff",
    "cm_depth_cm": "countermovement_depth",
}

COLOR_RANK = {"red": 3, "yellow": 2, "green": 1, "grey": 0}
```

---

## Task 1: Data Loading — `load_pre_data` and `get_session_dates`

**Files:**
- Create: `tests/test_recovery_report.py`
- Create: `scripts/generate_recovery_report.py` (skeleton + data loading functions)

### What these functions do

`load_pre_data(master_path, end_date, n_sessions)` — reads master CSV, keeps only `session_tag == "pre"` rows, finds all unique dates ≤ end_date, takes the N most recent, returns all rows for those dates as a DataFrame.

`get_session_dates(pre_data)` — extracts unique dates from the pre_data DataFrame and returns them sorted ascending.

---

- [ ] **Step 1.1: Create the test file with data loading tests**

Create `tests/test_recovery_report.py`:

```python
"""Tests for generate_recovery_report.py"""
import io
import sys
from pathlib import Path
import pandas as pd
import pytest

# Add scripts/ to path so we can import without installing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from generate_recovery_report import load_pre_data, get_session_dates


# ─── Shared test fixture ───────────────────────────────────────────────────────

SAMPLE_CSV = """athlete_name,test_date,test_time,session_tag,jump_height_cm,rsi_modified,mean_propulsive_force_n,ecc_braking_rfd_ns,time_to_takeoff_ms,cm_depth_cm,source_file,import_timestamp
Alice,2026-03-02,2:00 PM,pre,40.0,0.60,1500,6000,700,-35.0,test.csv,2026-03-02
Alice,2026-03-02,4:00 PM,post,37.0,0.55,1400,5500,750,-38.0,test.csv,2026-03-02
Alice,2026-03-05,2:00 PM,pre,39.0,0.59,1480,5900,710,-34.0,test.csv,2026-03-05
Alice,2026-03-05,4:00 PM,post,36.0,0.53,1380,5400,760,-37.0,test.csv,2026-03-05
Bob,2026-03-05,2:00 PM,pre,45.0,0.70,1600,7000,680,-30.0,test.csv,2026-03-05
Alice,2026-03-09,2:00 PM,pre,38.0,0.57,1460,5800,720,-35.5,test.csv,2026-03-09
Bob,2026-03-09,2:00 PM,pre,44.0,0.68,1580,6900,690,-31.0,test.csv,2026-03-09
Alice,2026-03-16,2:00 PM,pre,35.0,0.52,1400,5300,740,-37.0,test.csv,2026-03-16
"""


@pytest.fixture
def master_csv(tmp_path):
    p = tmp_path / "master_data.csv"
    p.write_text(SAMPLE_CSV)
    return p


# ─── load_pre_data ─────────────────────────────────────────────────────────────

def test_load_pre_data_returns_only_pre_rows(master_csv):
    df = load_pre_data(master_csv, "2026-03-20", n_sessions=6)
    assert (df["session_tag"] == "pre").all()


def test_load_pre_data_respects_end_date(master_csv):
    df = load_pre_data(master_csv, "2026-03-09", n_sessions=6)
    assert "2026-03-16" not in df["test_date"].values


def test_load_pre_data_respects_n_sessions(master_csv):
    df = load_pre_data(master_csv, "2026-03-20", n_sessions=2)
    dates = df["test_date"].unique()
    assert len(dates) == 2
    # Should be the 2 most recent: 2026-03-09 and 2026-03-16
    assert set(dates) == {"2026-03-09", "2026-03-16"}


def test_load_pre_data_counts_sessions_by_unique_date(master_csv):
    # Even though Bob has no pre row on 2026-03-02, that date still
    # counts as a session because Alice does
    df = load_pre_data(master_csv, "2026-03-20", n_sessions=3)
    dates = df["test_date"].unique()
    assert len(dates) == 3


# ─── get_session_dates ─────────────────────────────────────────────────────────

def test_get_session_dates_returns_sorted_ascending(master_csv):
    df = load_pre_data(master_csv, "2026-03-20", n_sessions=6)
    dates = get_session_dates(df)
    assert dates == sorted(dates)


def test_get_session_dates_no_duplicates(master_csv):
    df = load_pre_data(master_csv, "2026-03-20", n_sessions=6)
    dates = get_session_dates(df)
    assert len(dates) == len(set(dates))
```

- [ ] **Step 1.2: Run tests — verify they fail (module not found)**

```bash
python -m pytest tests/test_recovery_report.py -v
```

Expected: `ModuleNotFoundError: No module named 'generate_recovery_report'`

- [ ] **Step 1.3: Create `scripts/generate_recovery_report.py` skeleton + implement data loading**

```python
"""
generate_recovery_report.py — CMJ pre-session recovery trend report.

Shows each athlete's pre-practice CMJ values across N sessions with
session-to-session delta coloring and personal window average deviation.

Usage:
    python scripts/generate_recovery_report.py
    python scripts/generate_recovery_report.py --date 2026-03-20 --sessions 4
    python scripts/generate_recovery_report.py --config config.yaml --master data/master_data.csv
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_CONFIG = PROJECT_ROOT / "config.yaml"
DEFAULT_MASTER = PROJECT_ROOT / "data" / "master_data.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

sys.path.insert(0, str(SCRIPT_DIR))
from utils import calc_pct_change, get_metric_color, format_pct

# ─── Constants ────────────────────────────────────────────────────────────────

METRIC_COLS = [
    "jump_height_cm",
    "rsi_modified",
    "mean_propulsive_force_n",
    "ecc_braking_rfd_ns",
    "time_to_takeoff_ms",
    "cm_depth_cm",
]

COL_TO_THRESHOLD_KEY = {
    "jump_height_cm": "jump_height",
    "rsi_modified": "rsi_modified",
    "mean_propulsive_force_n": "mean_propulsive_force",
    "ecc_braking_rfd_ns": "ecc_braking_rfd",
    "time_to_takeoff_ms": "time_to_takeoff",
    "cm_depth_cm": "countermovement_depth",
}

COLOR_RANK = {"red": 3, "yellow": 2, "green": 1, "grey": 0}


# ─── Data Loading ─────────────────────────────────────────────────────────────

def load_pre_data(master_path: Path, end_date: str, n_sessions: int) -> pd.DataFrame:
    """
    Return a filtered DataFrame of pre-practice rows for the N most recent
    sessions up to end_date.

    A "session" is a unique test_date with at least one pre row. Dates are
    collected from the pre-filtered subset, sorted descending, and the N most
    recent are kept; all rows for those dates are returned.
    """
    df = pd.read_csv(master_path, dtype=str)
    df["test_date"] = pd.to_datetime(df["test_date"]).dt.strftime("%Y-%m-%d")
    pre = df[df["session_tag"] == "pre"].copy()

    all_dates = sorted(
        pre[pre["test_date"] <= end_date]["test_date"].unique(),
        reverse=True,
    )
    window_dates = set(all_dates[:n_sessions])
    return pre[pre["test_date"].isin(window_dates)].copy()


def get_session_dates(pre_data: pd.DataFrame) -> list:
    """Return sorted ascending list of unique test_date values from pre_data."""
    return sorted(pre_data["test_date"].unique())
```

- [ ] **Step 1.4: Run data loading tests — verify they pass**

```bash
python -m pytest tests/test_recovery_report.py -v -k "load_pre_data or session_dates"
```

Expected: All 6 tests PASS.

- [ ] **Step 1.5: Commit**

```bash
git add scripts/generate_recovery_report.py tests/test_recovery_report.py
git commit -m "feat: add recovery report skeleton with data loading functions"
```

---

## Task 2: Window Baseline — `compute_window_baseline`

**Files:**
- Modify: `tests/test_recovery_report.py` (add tests)
- Modify: `scripts/generate_recovery_report.py` (add function)

### What this function does

`compute_window_baseline(values)` — returns the mean of non-null values. Used once per athlete per metric before the per-cell loop in `build_metric_grid`.

---

- [ ] **Step 2.1: Add baseline tests to `tests/test_recovery_report.py`**

Add these tests after the existing ones:

```python
from generate_recovery_report import compute_window_baseline


def test_compute_window_baseline_basic():
    assert compute_window_baseline([40.0, 38.0, 36.0]) == pytest.approx(38.0)


def test_compute_window_baseline_single_value():
    assert compute_window_baseline([40.0]) == pytest.approx(40.0)


def test_compute_window_baseline_ignores_none():
    # None values (absent sessions) must not affect the mean
    result = compute_window_baseline([40.0, None, 36.0])
    assert result == pytest.approx(38.0)


def test_compute_window_baseline_all_none_returns_none():
    assert compute_window_baseline([None, None]) is None
```

- [ ] **Step 2.2: Run — verify new tests fail**

```bash
python -m pytest tests/test_recovery_report.py -v -k "baseline"
```

Expected: `ImportError` or `AttributeError` (function not yet defined).

- [ ] **Step 2.3: Implement `compute_window_baseline` in `generate_recovery_report.py`**

Add after `get_session_dates`:

```python
def compute_window_baseline(values: list) -> float:
    """
    Return the mean of non-None, non-NaN values.
    Returns None if no valid values exist.
    """
    valid = [v for v in values if v is not None and not (isinstance(v, float) and pd.isna(v))]
    if not valid:
        return None
    return sum(valid) / len(valid)
```

- [ ] **Step 2.4: Run — verify baseline tests pass**

```bash
python -m pytest tests/test_recovery_report.py -v -k "baseline"
```

Expected: 4 tests PASS.

- [ ] **Step 2.5: Commit**

```bash
git add scripts/generate_recovery_report.py tests/test_recovery_report.py
git commit -m "feat: add compute_window_baseline function"
```

---

## Task 3: Grid Building — `build_metric_grid`

**Files:**
- Modify: `tests/test_recovery_report.py` (add grid tests)
- Modify: `scripts/generate_recovery_report.py` (add helper + grid function)

### What this function does

`build_metric_grid(pre_data, metric_col, session_dates, config, roster_map)` — for one metric, returns a list of per-athlete row dicts. Each row dict has `name`, `number`, `position`, and a `cells` list. Each cell dict has `session_date`, `value`, `absent`, `display_value`, `pct_change_s1_display`, `s2_indicator`, and `color`.

**Cell color algorithm:**
1. Compute baseline for this athlete/metric (once, before the cell loop)
2. For each session date:
   - If athlete has no pre row → absent cell (grey, excluded from counts)
   - If value is non-numeric → N/A grey cell
   - Signal 1: `calc_pct_change(prev_value, current_value)` if prev_value exists and prev session was not absent → `get_metric_color()` → s1_color. If no prior (first session or prev was absent) → s1_color = None
   - Signal 2: `calc_pct_change(baseline, current_value)` → `get_metric_color()` → s2_color. Set s2_indicator based on magnitude.
   - Final color: `max(s1_color, s2_color, key=COLOR_RANK)`. If both None → "grey".

---

- [ ] **Step 3.1: Add grid tests to `tests/test_recovery_report.py`**

Add these imports at the top:

```python
from generate_recovery_report import build_metric_grid, compute_window_baseline
```

Add these tests:

```python
# ─── Shared config fixture for grid tests ─────────────────────────────────────

JUMP_HEIGHT_CFG = {
    "thresholds": {
        "jump_height": {
            "metric_label": "Jump Height",
            "short_label": "Jump Ht",
            "unit": "cm",
            "direction": "decrease_bad",
            "yellow_min": 5.0,
            "red_min": 10.0,
        }
    }
}

TTT_CFG = {
    "thresholds": {
        "time_to_takeoff": {
            "metric_label": "Time to Takeoff",
            "short_label": "Time-TO",
            "unit": "ms",
            "direction": "increase_bad",
            "yellow_min": 5.0,
            "red_min": 12.0,
        }
    }
}

ROSTER_MAP = {"alice": {"number": "1", "position": "Setter"}}


def _make_pre_data(rows: list) -> pd.DataFrame:
    """rows = list of (name, date, value_str) for jump_height_cm."""
    return pd.DataFrame([
        {
            "athlete_name": name,
            "test_date": date,
            "test_time": "2:00 PM",
            "session_tag": "pre",
            "jump_height_cm": val,
            "rsi_modified": "0.60",
            "mean_propulsive_force_n": "1500",
            "ecc_braking_rfd_ns": "6000",
            "time_to_takeoff_ms": "700",
            "cm_depth_cm": "-35.0",
        }
        for name, date, val in rows
    ])


def test_session_to_session_coloring():
    """Declining jump height produces yellow then red cells."""
    pre = _make_pre_data([
        ("Alice", "2026-03-02", "40.0"),   # baseline included
        ("Alice", "2026-03-05", "37.5"),   # -6.25% vs prior → yellow
        ("Alice", "2026-03-09", "30.0"),   # -20.0% vs prior → red
    ])
    session_dates = ["2026-03-02", "2026-03-05", "2026-03-09"]
    grid = build_metric_grid(pre, "jump_height_cm", session_dates, JUMP_HEIGHT_CFG, ROSTER_MAP)

    alice = next(r for r in grid if r["name"] == "Alice")
    assert alice["cells"][0]["color"] in ("green", "grey")  # first session, no S1
    assert alice["cells"][1]["color"] == "yellow"
    assert alice["cells"][2]["color"] == "red"


def test_first_session_has_no_signal1_color():
    """First session in window has no S1 delta — color comes from S2 or grey."""
    pre = _make_pre_data([("Alice", "2026-03-02", "40.0")])
    grid = build_metric_grid(pre, "jump_height_cm", ["2026-03-02"], JUMP_HEIGHT_CFG, ROSTER_MAP)
    alice = next(r for r in grid if r["name"] == "Alice")
    # S1 is neutral; S2 vs own baseline of 40.0 is 0% → green
    assert alice["cells"][0]["color"] == "green"
    assert alice["cells"][0]["pct_change_s1_display"] == "—"


def test_absent_session_is_grey_and_excluded():
    """Athlete with no data for a session gets an absent/grey cell."""
    pre = _make_pre_data([
        ("Alice", "2026-03-02", "40.0"),
        ("Alice", "2026-03-09", "38.0"),
        # Alice has no row for 2026-03-05
    ])
    session_dates = ["2026-03-02", "2026-03-05", "2026-03-09"]
    grid = build_metric_grid(pre, "jump_height_cm", session_dates, JUMP_HEIGHT_CFG, ROSTER_MAP)
    alice = next(r for r in grid if r["name"] == "Alice")
    assert alice["cells"][1]["absent"] is True
    assert alice["cells"][1]["color"] == "grey"


def test_post_absent_cell_has_no_signal1():
    """Cell immediately after an absent session has no S1 (treat like first session)."""
    pre = _make_pre_data([
        ("Alice", "2026-03-02", "40.0"),
        # Alice absent on 2026-03-05
        ("Alice", "2026-03-09", "38.0"),
    ])
    session_dates = ["2026-03-02", "2026-03-05", "2026-03-09"]
    grid = build_metric_grid(pre, "jump_height_cm", session_dates, JUMP_HEIGHT_CFG, ROSTER_MAP)
    alice = next(r for r in grid if r["name"] == "Alice")
    # 2026-03-09 cell: prior (2026-03-05) was absent → no S1
    assert alice["cells"][2]["pct_change_s1_display"] == "—"


def test_rolling_baseline_deviation_decrease_bad():
    """A value well below window average on a decrease_bad metric fires S2 red."""
    pre = _make_pre_data([
        ("Alice", "2026-03-02", "40.0"),
        ("Alice", "2026-03-05", "40.0"),
        ("Alice", "2026-03-09", "40.0"),
        ("Alice", "2026-03-16", "20.0"),  # baseline=(40+40+40+20)/4=35; 20 vs 35 = -42.9% → red
    ])
    session_dates = ["2026-03-02", "2026-03-05", "2026-03-09", "2026-03-16"]
    grid = build_metric_grid(pre, "jump_height_cm", session_dates, JUMP_HEIGHT_CFG, ROSTER_MAP)
    alice = next(r for r in grid if r["name"] == "Alice")
    assert alice["cells"][3]["color"] == "red"
    assert alice["cells"][3]["s2_indicator"] == "↓↓"


def test_rolling_baseline_deviation_increase_bad():
    """A value well above window average on an increase_bad metric fires S2 red."""
    pre = pd.DataFrame([
        {"athlete_name": "Alice", "test_date": "2026-03-02", "test_time": "2:00 PM",
         "session_tag": "pre", "jump_height_cm": "40.0", "rsi_modified": "0.60",
         "mean_propulsive_force_n": "1500", "ecc_braking_rfd_ns": "6000",
         "time_to_takeoff_ms": "700", "cm_depth_cm": "-35.0"},
        {"athlete_name": "Alice", "test_date": "2026-03-05", "test_time": "2:00 PM",
         "session_tag": "pre", "jump_height_cm": "40.0", "rsi_modified": "0.60",
         "mean_propulsive_force_n": "1500", "ecc_braking_rfd_ns": "6000",
         "time_to_takeoff_ms": "700", "cm_depth_cm": "-35.0"},
        {"athlete_name": "Alice", "test_date": "2026-03-09", "test_time": "2:00 PM",
         "session_tag": "pre", "jump_height_cm": "40.0", "rsi_modified": "0.60",
         "mean_propulsive_force_n": "1500", "ecc_braking_rfd_ns": "6000",
         "time_to_takeoff_ms": "700", "cm_depth_cm": "-35.0"},
        {"athlete_name": "Alice", "test_date": "2026-03-16", "test_time": "2:00 PM",
         "session_tag": "pre", "jump_height_cm": "40.0", "rsi_modified": "0.60",
         "mean_propulsive_force_n": "1500", "ecc_braking_rfd_ns": "6000",
         "time_to_takeoff_ms": "850", "cm_depth_cm": "-35.0"},
        # time_to_takeoff: baseline=(700+700+700+850)/4=737.5
        # 850 vs 737.5: pct_change(737.5, 850)=+15.2% → red (red_min=12.0, increase_bad)
    ])
    session_dates = ["2026-03-02", "2026-03-05", "2026-03-09", "2026-03-16"]
    grid = build_metric_grid(pre, "time_to_takeoff_ms", session_dates, TTT_CFG, ROSTER_MAP)
    alice = next(r for r in grid if r["name"] == "Alice")
    assert alice["cells"][3]["color"] == "red"
    assert alice["cells"][3]["s2_indicator"] == "↑↑"
```

- [ ] **Step 3.2: Run — verify grid tests fail**

```bash
python -m pytest tests/test_recovery_report.py -v -k "grid or coloring or absent or baseline_deviation"
```

Expected: `ImportError` (function not yet defined).

- [ ] **Step 3.3: Implement helper `_worst_color` and `build_metric_grid` in `generate_recovery_report.py`**

Add after `compute_window_baseline`:

```python
def _worst_color(c1: str, c2: str) -> str:
    """Return the more severe of two colors. None inputs treated as grey."""
    c1 = c1 or "grey"
    c2 = c2 or "grey"
    return c1 if COLOR_RANK[c1] >= COLOR_RANK[c2] else c2


def _build_roster_map(config: dict) -> dict:
    """Return {lowercased_name: {number, position}} from config roster."""
    roster_map = {}
    for entry in config.get("roster", []):
        key = " ".join(entry["name"].strip().lower().split())
        roster_map[key] = {
            "number": str(entry.get("number", "")),
            "position": entry.get("position", ""),
        }
    return roster_map


def build_metric_grid(
    pre_data: pd.DataFrame,
    metric_col: str,
    session_dates: list,
    config: dict,
    roster_map: dict,
) -> list:
    """
    Build per-athlete rows for one metric grid.

    Returns list of dicts, one per athlete, sorted by position then name:
      {
        "name": str,
        "number": str,
        "position": str,
        "cells": [
          {
            "session_date": str,
            "value": float | None,
            "absent": bool,
            "display_value": str,        # "40.0" or "—" or "N/A"
            "pct_change_s1_display": str, # "-3.2%" or "—"
            "s2_indicator": str,          # "", "~", "↓↓", "↑↑"
            "color": str,                 # "green","yellow","red","grey"
          }
        ]
      }
    """
    threshold_key = COL_TO_THRESHOLD_KEY[metric_col]
    cfg = config["thresholds"][threshold_key]
    direction = cfg["direction"]

    # Gather all athletes present in any session
    athlete_names = sorted(pre_data["athlete_name"].unique())

    rows = []
    for name in athlete_names:
        roster_entry = roster_map.get(" ".join(name.strip().lower().split()), {})
        athlete_rows = pre_data[pre_data["athlete_name"] == name]

        # ── Collect raw values per session for baseline computation ──
        raw_values = {}
        for date in session_dates:
            day_rows = athlete_rows[athlete_rows["test_date"] == date]
            if day_rows.empty:
                raw_values[date] = None
            else:
                val_str = day_rows.sort_values("test_time").iloc[-1][metric_col]
                try:
                    raw_values[date] = float(val_str)
                except (ValueError, TypeError):
                    raw_values[date] = None

        # ── Compute window baseline ONCE before the cell loop ──
        baseline = compute_window_baseline(list(raw_values.values()))

        # ── Build cells ──
        cells = []
        prev_value = None   # None if prior session was absent or doesn't exist
        prev_was_absent = True  # treat first session as if prior was absent

        for date in session_dates:
            current_value = raw_values[date]
            absent = current_value is None

            if absent:
                cells.append({
                    "session_date": date,
                    "value": None,
                    "absent": True,
                    "display_value": "—",
                    "pct_change_s1_display": "—",
                    "s2_indicator": "",
                    "color": "grey",
                })
                prev_value = None
                prev_was_absent = True
                continue

            display_value = str(round(current_value, 1))

            # Signal 1: session-to-session delta
            # No S1 if first session OR if prior session was absent
            if prev_was_absent or prev_value is None:
                s1_color = None
                pct_s1_display = "—"
            else:
                pct_s1 = calc_pct_change(prev_value, current_value)
                s1_color = get_metric_color(pct_s1, cfg)
                pct_s1_display = format_pct(pct_s1)

            # Signal 2: deviation from window baseline
            if baseline is None:
                s2_color = None
                s2_indicator = ""
            else:
                pct_s2 = calc_pct_change(baseline, current_value)
                s2_color = get_metric_color(pct_s2, cfg)
                if s2_color == "red":
                    s2_indicator = "↓↓" if direction == "decrease_bad" else "↑↑"
                elif s2_color == "yellow":
                    s2_indicator = "~"
                else:
                    s2_indicator = ""

            final_color = _worst_color(s1_color, s2_color)

            cells.append({
                "session_date": date,
                "value": current_value,
                "absent": False,
                "display_value": display_value,
                "pct_change_s1_display": pct_s1_display,
                "s2_indicator": s2_indicator,
                "color": final_color,
            })

            prev_value = current_value
            prev_was_absent = False

        rows.append({
            "name": name,
            "number": roster_entry.get("number", ""),
            "position": roster_entry.get("position", ""),
            "cells": cells,
        })

    # Sort by position then name
    rows.sort(key=lambda r: (r["position"], r["name"]))
    return rows
```

- [ ] **Step 3.4: Run grid tests — verify they pass**

```bash
python -m pytest tests/test_recovery_report.py -v -k "grid or coloring or absent or baseline_deviation"
```

Expected: All 8 new tests PASS.

- [ ] **Step 3.5: Run full test suite — verify nothing broken**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS (existing tests + new tests).

- [ ] **Step 3.6: Commit**

```bash
git add scripts/generate_recovery_report.py tests/test_recovery_report.py
git commit -m "feat: implement build_metric_grid with Signal 1 + Signal 2 cell coloring"
```

---

## Task 4: Badge Assignment and Summary Helpers

**Files:**
- Modify: `tests/test_recovery_report.py` (add badge + summary tests)
- Modify: `scripts/generate_recovery_report.py` (add badge + summary functions)

### What these functions do

`assign_recovery_badge(athlete_name, all_grids)` — counts red and yellow cells across all 6 metric grids for one athlete (excluding absent cells), applies At Risk > Watch > Recovered cascade, identifies most affected metric, and computes last session trend.

Returns:
```python
{
    "badge": "at_risk" | "watch" | "recovered",
    "most_affected_metric_label": str,   # display label from config
    "last_session_trend": "↑" | "↓" | "→" | "—",
}
```

---

- [ ] **Step 4.1: Add badge and summary tests to `tests/test_recovery_report.py`**

Add this import at the top of the test file:
```python
from generate_recovery_report import assign_recovery_badge
```

Add these tests:

```python
# ─── assign_recovery_badge ────────────────────────────────────────────────────

def _make_grid_row(name: str, colors: list, session_dates: list, metric_key: str) -> list:
    """Build a minimal all_grids entry from a list of color strings."""
    cells = []
    for date, color in zip(session_dates, colors):
        cells.append({
            "session_date": date,
            "absent": color == "grey",
            "color": color,
            # s1_color mirrors color for trend calculation (simplification for tests)
            "pct_change_s1_display": "—" if color == "grey" else "-3.0%",
            "s1_color": None if color == "grey" else color,
        })
    return [{
        "name": name,
        "number": "1",
        "position": "Setter",
        "cells": cells,
    }]


DATES_4 = ["2026-03-02", "2026-03-05", "2026-03-09", "2026-03-16"]

METRIC_LABELS = {
    "jump_height": "Jump Height",
    "rsi_modified": "RSI-modified",
    "mean_propulsive_force": "Mean Propulsive Force",
    "ecc_braking_rfd": "Eccentric Braking RFD",
    "time_to_takeoff": "Time to Takeoff",
    "countermovement_depth": "Countermovement Depth",
}


def test_badge_at_risk_two_reds():
    all_grids = {
        "jump_height": _make_grid_row("Alice", ["green", "green", "red", "red"], DATES_4, "jump_height"),
        "rsi_modified": _make_grid_row("Alice", ["green"] * 4, DATES_4, "rsi_modified"),
        "mean_propulsive_force": _make_grid_row("Alice", ["green"] * 4, DATES_4, "mean_propulsive_force"),
        "ecc_braking_rfd": _make_grid_row("Alice", ["green"] * 4, DATES_4, "ecc_braking_rfd"),
        "time_to_takeoff": _make_grid_row("Alice", ["green"] * 4, DATES_4, "time_to_takeoff"),
        "countermovement_depth": _make_grid_row("Alice", ["green"] * 4, DATES_4, "countermovement_depth"),
    }
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["badge"] == "at_risk"


def test_badge_at_risk_three_plus_yellow_red():
    # 3 yellows = 3+ (yellow+red) → At Risk
    all_grids = {
        "jump_height": _make_grid_row("Alice", ["green", "yellow", "yellow", "yellow"], DATES_4, "jump_height"),
        "rsi_modified": _make_grid_row("Alice", ["green"] * 4, DATES_4, "rsi_modified"),
        "mean_propulsive_force": _make_grid_row("Alice", ["green"] * 4, DATES_4, "mean_propulsive_force"),
        "ecc_braking_rfd": _make_grid_row("Alice", ["green"] * 4, DATES_4, "ecc_braking_rfd"),
        "time_to_takeoff": _make_grid_row("Alice", ["green"] * 4, DATES_4, "time_to_takeoff"),
        "countermovement_depth": _make_grid_row("Alice", ["green"] * 4, DATES_4, "countermovement_depth"),
    }
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["badge"] == "at_risk"


def test_badge_watch_two_yellows():
    all_grids = {
        "jump_height": _make_grid_row("Alice", ["green", "green", "yellow", "yellow"], DATES_4, "jump_height"),
        "rsi_modified": _make_grid_row("Alice", ["green"] * 4, DATES_4, "rsi_modified"),
        "mean_propulsive_force": _make_grid_row("Alice", ["green"] * 4, DATES_4, "mean_propulsive_force"),
        "ecc_braking_rfd": _make_grid_row("Alice", ["green"] * 4, DATES_4, "ecc_braking_rfd"),
        "time_to_takeoff": _make_grid_row("Alice", ["green"] * 4, DATES_4, "time_to_takeoff"),
        "countermovement_depth": _make_grid_row("Alice", ["green"] * 4, DATES_4, "countermovement_depth"),
    }
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["badge"] == "watch"


def test_badge_watch_one_red():
    all_grids = {
        "jump_height": _make_grid_row("Alice", ["green", "green", "green", "red"], DATES_4, "jump_height"),
        "rsi_modified": _make_grid_row("Alice", ["green"] * 4, DATES_4, "rsi_modified"),
        "mean_propulsive_force": _make_grid_row("Alice", ["green"] * 4, DATES_4, "mean_propulsive_force"),
        "ecc_braking_rfd": _make_grid_row("Alice", ["green"] * 4, DATES_4, "ecc_braking_rfd"),
        "time_to_takeoff": _make_grid_row("Alice", ["green"] * 4, DATES_4, "time_to_takeoff"),
        "countermovement_depth": _make_grid_row("Alice", ["green"] * 4, DATES_4, "countermovement_depth"),
    }
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["badge"] == "watch"


def test_badge_recovered():
    all_grids = {k: _make_grid_row("Alice", ["green"] * 4, DATES_4, k)
                 for k in ["jump_height", "rsi_modified", "mean_propulsive_force",
                           "ecc_braking_rfd", "time_to_takeoff", "countermovement_depth"]}
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["badge"] == "recovered"


def test_badge_cascade_at_risk_beats_watch():
    # 2 reds AND 2 yellows — At Risk must win
    all_grids = {
        "jump_height": _make_grid_row("Alice", ["red", "red", "yellow", "yellow"], DATES_4, "jump_height"),
        "rsi_modified": _make_grid_row("Alice", ["green"] * 4, DATES_4, "rsi_modified"),
        "mean_propulsive_force": _make_grid_row("Alice", ["green"] * 4, DATES_4, "mean_propulsive_force"),
        "ecc_braking_rfd": _make_grid_row("Alice", ["green"] * 4, DATES_4, "ecc_braking_rfd"),
        "time_to_takeoff": _make_grid_row("Alice", ["green"] * 4, DATES_4, "time_to_takeoff"),
        "countermovement_depth": _make_grid_row("Alice", ["green"] * 4, DATES_4, "countermovement_depth"),
    }
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["badge"] == "at_risk"


def test_most_affected_metric():
    # jump_height has 2 yellow+red, rsi has 1 — jump_height should be most affected
    all_grids = {
        "jump_height": _make_grid_row("Alice", ["green", "yellow", "yellow", "green"], DATES_4, "jump_height"),
        "rsi_modified": _make_grid_row("Alice", ["green", "yellow", "green", "green"], DATES_4, "rsi_modified"),
        "mean_propulsive_force": _make_grid_row("Alice", ["green"] * 4, DATES_4, "mean_propulsive_force"),
        "ecc_braking_rfd": _make_grid_row("Alice", ["green"] * 4, DATES_4, "ecc_braking_rfd"),
        "time_to_takeoff": _make_grid_row("Alice", ["green"] * 4, DATES_4, "time_to_takeoff"),
        "countermovement_depth": _make_grid_row("Alice", ["green"] * 4, DATES_4, "countermovement_depth"),
    }
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["most_affected_metric_label"] == "Jump Height"


def test_absent_cells_excluded_from_badge_counts():
    # One red cell and one absent cell — only the red counts
    all_grids = {
        "jump_height": _make_grid_row("Alice", ["green", "grey", "green", "red"], DATES_4, "jump_height"),
        "rsi_modified": _make_grid_row("Alice", ["green"] * 4, DATES_4, "rsi_modified"),
        "mean_propulsive_force": _make_grid_row("Alice", ["green"] * 4, DATES_4, "mean_propulsive_force"),
        "ecc_braking_rfd": _make_grid_row("Alice", ["green"] * 4, DATES_4, "ecc_braking_rfd"),
        "time_to_takeoff": _make_grid_row("Alice", ["green"] * 4, DATES_4, "time_to_takeoff"),
        "countermovement_depth": _make_grid_row("Alice", ["green"] * 4, DATES_4, "countermovement_depth"),
    }
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["badge"] == "watch"  # 1 red = Watch, not At Risk


def test_last_session_trend_declining():
    # Last session: all 6 metrics red → ↓
    last_colors = ["red", "red", "red", "red", "red", "red"]
    metrics = ["jump_height", "rsi_modified", "mean_propulsive_force",
               "ecc_braking_rfd", "time_to_takeoff", "countermovement_depth"]
    all_grids = {}
    for i, m in enumerate(metrics):
        all_grids[m] = _make_grid_row(
            "Alice",
            ["green", "green", "green", last_colors[i]],
            DATES_4, m
        )
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["last_session_trend"] == "↓"


def test_last_session_trend_improving():
    # Last session: all 6 metrics green → ↑
    metrics = ["jump_height", "rsi_modified", "mean_propulsive_force",
               "ecc_braking_rfd", "time_to_takeoff", "countermovement_depth"]
    all_grids = {m: _make_grid_row("Alice", ["yellow", "yellow", "red", "green"], DATES_4, m)
                 for m in metrics}
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["last_session_trend"] == "↑"


def test_last_session_trend_absent_returns_dash():
    # Athlete absent last session
    all_grids = {
        "jump_height": _make_grid_row("Alice", ["green", "green", "green", "grey"], DATES_4, "jump_height"),
        "rsi_modified": _make_grid_row("Alice", ["green", "green", "green", "grey"], DATES_4, "rsi_modified"),
        "mean_propulsive_force": _make_grid_row("Alice", ["green"] * 3 + ["grey"], DATES_4, "mean_propulsive_force"),
        "ecc_braking_rfd": _make_grid_row("Alice", ["green"] * 3 + ["grey"], DATES_4, "ecc_braking_rfd"),
        "time_to_takeoff": _make_grid_row("Alice", ["green"] * 3 + ["grey"], DATES_4, "time_to_takeoff"),
        "countermovement_depth": _make_grid_row("Alice", ["green"] * 3 + ["grey"], DATES_4, "countermovement_depth"),
    }
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["last_session_trend"] == "—"


def test_last_session_trend_no_prior_returns_arrow():
    # Athlete has only one session (first and last) → no S1 → →
    DATES_1 = ["2026-03-16"]
    all_grids = {m: _make_grid_row("Alice", ["green"], DATES_1, m)
                 for m in ["jump_height", "rsi_modified", "mean_propulsive_force",
                           "ecc_braking_rfd", "time_to_takeoff", "countermovement_depth"]}
    result = assign_recovery_badge("Alice", all_grids, METRIC_LABELS)
    assert result["last_session_trend"] == "→"
```

- [ ] **Step 4.2: Run — verify new tests fail**

```bash
python -m pytest tests/test_recovery_report.py -v -k "badge or trend or most_affected or absent_cells"
```

Expected: `ImportError` (function not yet defined).

- [ ] **Step 4.3: Implement `assign_recovery_badge` in `generate_recovery_report.py`**

Add after `build_metric_grid`:

```python
def assign_recovery_badge(athlete_name: str, all_grids: dict, metric_labels: dict) -> dict:
    """
    Compute recovery badge (at_risk/watch/recovered), most affected metric,
    and last session trend for one athlete across all 6 metric grids.

    all_grids: dict[metric_key, list[athlete_row_dict]]
      Each athlete_row_dict: {"name": str, "cells": [{"absent": bool, "color": str, "s1_color": str|None, ...}]}
    metric_labels: dict[metric_key, display_label_str]
    """
    red_count = 0
    yellow_count = 0
    metric_yr_counts = {}

    # Gather last-session cells for trend calculation
    last_session_cells = {}  # metric_key → cell dict for last session

    for metric_key, grid in all_grids.items():
        athlete_row = next((r for r in grid if r["name"] == athlete_name), None)
        metric_yr = 0

        if athlete_row:
            for cell in athlete_row["cells"]:
                if cell["absent"]:
                    continue
                if cell["color"] == "red":
                    red_count += 1
                    metric_yr += 1
                elif cell["color"] == "yellow":
                    yellow_count += 1
                    metric_yr += 1

            # Track the last (most recent) cell for trend
            if athlete_row["cells"]:
                last_session_cells[metric_key] = athlete_row["cells"][-1]

        metric_yr_counts[metric_key] = metric_yr

    # ── Badge cascade: At Risk > Watch > Recovered ──
    if red_count >= 2 or (red_count + yellow_count) >= 3:
        badge = "at_risk"
    elif yellow_count >= 2 or red_count == 1:
        badge = "watch"
    else:
        badge = "recovered"

    # ── Most Affected Metric ──
    if metric_yr_counts:
        most_affected_key = max(metric_yr_counts, key=metric_yr_counts.get)
        most_affected_label = metric_labels.get(most_affected_key, most_affected_key)
        if metric_yr_counts[most_affected_key] == 0:
            most_affected_label = "None"
    else:
        most_affected_label = "None"

    # ── Last Session Trend (Signal 1 only) ──
    trend = _compute_trend(last_session_cells)

    return {
        "badge": badge,
        "most_affected_metric_label": most_affected_label,
        "last_session_trend": trend,
    }


def _compute_trend(last_session_cells: dict) -> str:
    """
    Given the last session cell for each metric, compute ↑ / ↓ / → / —.

    Rules:
    - If all 6 last cells are absent → "—"
    - If last cell has no Signal 1 (s1_color is None) → treat as neutral
    - ↑ if 4+ metrics have s1_color == "green"
    - ↓ if 4+ metrics have s1_color in ("yellow", "red")
    - → otherwise
    """
    if not last_session_cells:
        return "→"

    # If athlete absent for every metric in the last session → "—"
    if all(cell.get("absent", False) for cell in last_session_cells.values()):
        return "—"

    green_count = 0
    bad_count = 0

    for cell in last_session_cells.values():
        if cell.get("absent", False):
            continue
        s1 = cell.get("s1_color")
        if s1 is None:
            # No prior (first session or post-absent) → insufficient data → neutral
            continue
        if s1 == "green":
            green_count += 1
        elif s1 in ("yellow", "red"):
            bad_count += 1

    if green_count >= 4:
        return "↑"
    if bad_count >= 4:
        return "↓"
    return "→"
```

**Important:** `build_metric_grid` cell dicts currently store `pct_change_s1_display` but not `s1_color` directly. Update `build_metric_grid` to also store `s1_color` in each cell. Find the cell construction inside `build_metric_grid` and add `"s1_color": s1_color` to the non-absent cell dict. The s1_color variable already exists in that scope.

In `build_metric_grid`, change the non-absent cell dict from:
```python
cells.append({
    "session_date": date,
    "value": current_value,
    "absent": False,
    "display_value": display_value,
    "pct_change_s1_display": pct_s1_display,
    "s2_indicator": s2_indicator,
    "color": final_color,
})
```
To:
```python
cells.append({
    "session_date": date,
    "value": current_value,
    "absent": False,
    "display_value": display_value,
    "pct_change_s1_display": pct_s1_display,
    "s1_color": s1_color,       # ← add this
    "s2_indicator": s2_indicator,
    "color": final_color,
})
```

- [ ] **Step 4.4: Run badge tests — verify they pass**

```bash
python -m pytest tests/test_recovery_report.py -v -k "badge or trend or most_affected or absent_cells"
```

Expected: All 13 new tests PASS.

- [ ] **Step 4.5: Run full test suite**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 4.6: Commit**

```bash
git add scripts/generate_recovery_report.py tests/test_recovery_report.py
git commit -m "feat: add assign_recovery_badge with badge cascade, most affected metric, and trend"
```

---

## Task 5: HTML Template

**Files:**
- Create: `templates/recovery_report_template.html`

### What this template renders

Jinja2 template receiving this context dict:

```python
{
    "report_date": str,              # "March 23, 2026"
    "date_range": str,               # "March 02 – March 20, 2026"
    "n_sessions": int,               # 6
    "at_risk_count": int,
    "watch_count": int,
    "recovered_count": int,
    "session_dates_display": list,   # ["Mar 2", "Mar 5", ...] for column headers
    "metric_grids": [                # 6 grids in order
        {
            "metric_label": str,     # "Jump Height"
            "unit": str,             # "cm"
            "rows": list,            # build_metric_grid output
        }
    ],
    "summary_rows": [                # one per athlete
        {
            "name": str,
            "number": str,
            "position": str,
            "badge": str,            # "at_risk" | "watch" | "recovered"
            "badge_label": str,      # "At Risk" | "Watch" | "Recovered"
            "most_affected_metric_label": str,
            "last_session_trend": str,
        }
    ],
    "footer_text": str,
}
```

---

- [ ] **Step 5.1: Create `templates/recovery_report_template.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Baylor Volleyball - CMJ Recovery Report - {{ report_date }}</title>
<style>
  :root {
    --baylor-green: #003015;
    --baylor-gold: #FFB81C;
    --bg: #0A0F0D;
    --surface: #111916;
    --surface-2: #182420;
    --border: #1E2E28;
    --text: #E8EDE9;
    --text-muted: #7A8E82;
    --green: #22C55E;
    --green-bg: rgba(34,197,94,0.08);
    --green-border: rgba(34,197,94,0.2);
    --yellow: #D4A800;
    --yellow-text: #FACC15;
    --yellow-bg: rgba(250,204,21,0.08);
    --yellow-border: rgba(250,204,21,0.25);
    --red: #EF4444;
    --red-bg: rgba(239,68,68,0.08);
    --red-border: rgba(239,68,68,0.2);
    --grey-bg: rgba(120,120,120,0.08);
    --grey-border: rgba(120,120,120,0.2);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  /* ─── Header ─── */
  .header {
    background: linear-gradient(180deg, var(--baylor-green) 0%, var(--bg) 100%);
    padding: 32px 40px 48px;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
  }
  .header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(255,184,28,0.08) 0%, transparent 70%);
    border-radius: 50%;
  }
  .header-brand { display: flex; align-items: center; gap: 14px; margin-bottom: 8px; }
  .header-logo {
    width: 42px; height: 42px;
    background: var(--baylor-gold);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; color: var(--baylor-green); font-weight: 900;
  }
  .header-org { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
  .header-title { font-size: 26px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
  .header-subtitle { font-size: 14px; color: var(--text-muted); }

  /* ─── Team Summary Badges ─── */
  .summary-bar {
    display: flex; gap: 16px; margin-top: 24px; flex-wrap: wrap;
  }
  .summary-badge {
    padding: 8px 18px; border-radius: 8px; font-size: 14px; font-weight: 600;
    display: flex; align-items: center; gap: 8px;
  }
  .badge-at-risk  { background: var(--red-bg);    border: 1px solid var(--red-border);    color: var(--red); }
  .badge-watch    { background: var(--yellow-bg);  border: 1px solid var(--yellow-border);  color: var(--yellow-text); }
  .badge-recovered { background: var(--green-bg); border: 1px solid var(--green-border); color: var(--green); }

  /* ─── Main content ─── */
  .content { padding: 32px 40px; max-width: 1400px; margin: 0 auto; }

  /* ─── Section header ─── */
  .section-title {
    font-size: 16px; font-weight: 700; color: var(--baylor-gold);
    text-transform: uppercase; letter-spacing: 1px;
    margin: 36px 0 12px;
    padding-bottom: 8px; border-bottom: 1px solid var(--border);
  }

  /* ─── Metric Grid ─── */
  .metric-grid-wrap { margin-bottom: 40px; overflow-x: auto; }
  .metric-grid-label { font-size: 13px; color: var(--text-muted); margin-bottom: 8px; }
  .metric-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .metric-table th {
    padding: 8px 12px; text-align: center;
    background: var(--surface-2); border: 1px solid var(--border);
    color: var(--text-muted); font-weight: 600; white-space: nowrap;
  }
  .metric-table th.athlete-col { text-align: left; min-width: 160px; }
  .metric-table td {
    padding: 8px 10px; border: 1px solid var(--border);
    text-align: center; vertical-align: middle;
  }
  .metric-table td.athlete-info { text-align: left; background: var(--surface); }
  .athlete-name { font-weight: 600; font-size: 13px; }
  .athlete-meta { font-size: 11px; color: var(--text-muted); }

  /* Cell colors */
  .cell-green  { background: var(--green-bg);  border-color: var(--green-border)  !important; }
  .cell-yellow { background: var(--yellow-bg); border-color: var(--yellow-border) !important; }
  .cell-red    { background: var(--red-bg);    border-color: var(--red-border)    !important; }
  .cell-grey   { background: var(--grey-bg);   border-color: var(--grey-border)   !important; color: var(--text-muted); }

  .cell-value { font-weight: 600; font-size: 13px; display: block; }
  .cell-delta { font-size: 11px; color: var(--text-muted); display: block; margin-top: 2px; }
  .cell-indicator { font-size: 11px; display: block; margin-top: 1px; }
  .cell-green  .cell-indicator { color: var(--green); }
  .cell-yellow .cell-indicator { color: var(--yellow-text); }
  .cell-red    .cell-indicator { color: var(--red); }
  .absent-label { font-size: 10px; color: var(--text-muted); display: block; margin-top: 2px; letter-spacing: 0.5px; }

  /* ─── Summary Table ─── */
  .summary-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .summary-table th {
    padding: 10px 14px; text-align: left;
    background: var(--surface-2); border: 1px solid var(--border);
    color: var(--text-muted); font-weight: 600; text-transform: uppercase;
    font-size: 11px; letter-spacing: 0.5px;
  }
  .summary-table td { padding: 10px 14px; border: 1px solid var(--border); vertical-align: middle; }
  .summary-table tr:nth-child(even) td { background: var(--surface); }

  .status-pill {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 12px; font-weight: 700;
  }
  .status-at_risk   { background: var(--red-bg);    border: 1px solid var(--red-border);    color: var(--red); }
  .status-watch     { background: var(--yellow-bg);  border: 1px solid var(--yellow-border);  color: var(--yellow-text); }
  .status-recovered { background: var(--green-bg);   border: 1px solid var(--green-border);   color: var(--green); }

  .trend-symbol { font-size: 16px; font-weight: 700; }
  .trend-up   { color: var(--green); }
  .trend-down { color: var(--red); }
  .trend-flat { color: var(--text-muted); }

  /* ─── Legend ─── */
  .legend {
    display: flex; gap: 20px; flex-wrap: wrap;
    margin-top: 32px; padding: 16px 20px;
    background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
    font-size: 12px; color: var(--text-muted);
  }
  .legend-item { display: flex; align-items: center; gap: 8px; }
  .legend-dot {
    width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
  }
  .dot-green  { background: var(--green); }
  .dot-yellow { background: var(--yellow-text); }
  .dot-red    { background: var(--red); }
  .dot-grey   { background: #555; }

  /* ─── Footer ─── */
  .footer {
    text-align: center; padding: 24px;
    color: var(--text-muted); font-size: 11px;
    border-top: 1px solid var(--border); margin-top: 48px;
  }
</style>
</head>
<body>

<!-- ─── Header ─── -->
<div class="header">
  <div class="header-brand">
    <div class="header-logo">BU</div>
    <div>
      <div class="header-org">Baylor Volleyball · Applied Performance</div>
    </div>
  </div>
  <div class="header-title">CMJ Recovery Monitoring Report</div>
  <div class="header-subtitle">Pre-Practice Trend · {{ date_range }} · {{ n_sessions }} Sessions</div>
  <div class="summary-bar">
    <div class="summary-badge badge-at-risk">At Risk &nbsp;<strong>{{ at_risk_count }}</strong></div>
    <div class="summary-badge badge-watch">Watch &nbsp;<strong>{{ watch_count }}</strong></div>
    <div class="summary-badge badge-recovered">Recovered &nbsp;<strong>{{ recovered_count }}</strong></div>
  </div>
</div>

<!-- ─── Main Content ─── -->
<div class="content">

  <!-- ─── Metric Grids ─── -->
  {% for grid in metric_grids %}
  <div class="section-title">{{ grid.metric_label }} <span style="font-weight:400;font-size:12px;color:var(--text-muted)">({{ grid.unit }})</span></div>
  <div class="metric-grid-wrap">
    <table class="metric-table">
      <thead>
        <tr>
          <th class="athlete-col">Athlete</th>
          {% for date_label in session_dates_display %}
          <th>{{ date_label }}</th>
          {% endfor %}
        </tr>
      </thead>
      <tbody>
        {% for row in grid.rows %}
        <tr>
          <td class="athlete-info">
            <span class="athlete-name">
              {% if row.number %}#{{ row.number }} · {% endif %}{{ row.name }}
            </span>
            {% if row.position %}
            <span class="athlete-meta">{{ row.position }}</span>
            {% endif %}
          </td>
          {% for cell in row.cells %}
          <td class="cell-{{ cell.color }}">
            {% if cell.absent %}
            <span class="cell-value">—</span>
            <span class="absent-label">Absent</span>
            {% else %}
            <span class="cell-value">{{ cell.display_value }}</span>
            <span class="cell-delta">{{ cell.pct_change_s1_display }}</span>
            {% if cell.s2_indicator %}
            <span class="cell-indicator">{{ cell.s2_indicator }}</span>
            {% endif %}
            {% endif %}
          </td>
          {% endfor %}
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% endfor %}

  <!-- ─── Recovery Status Summary ─── -->
  <div class="section-title">Recovery Status Summary</div>
  <table class="summary-table">
    <thead>
      <tr>
        <th>Athlete</th>
        <th>Pos</th>
        <th>#</th>
        <th>Status</th>
        <th>Most Affected Metric</th>
        <th>Last Session Trend</th>
      </tr>
    </thead>
    <tbody>
      {% for row in summary_rows %}
      <tr>
        <td><strong>{{ row.name }}</strong></td>
        <td>{{ row.position }}</td>
        <td>{{ row.number }}</td>
        <td>
          <span class="status-pill status-{{ row.badge }}">{{ row.badge_label }}</span>
        </td>
        <td>{{ row.most_affected_metric_label }}</td>
        <td>
          {% if row.last_session_trend == "↑" %}
          <span class="trend-symbol trend-up">↑</span>
          {% elif row.last_session_trend == "↓" %}
          <span class="trend-symbol trend-down">↓</span>
          {% elif row.last_session_trend == "—" %}
          <span class="trend-symbol trend-flat">—</span>
          {% else %}
          <span class="trend-symbol trend-flat">→</span>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <!-- ─── Legend ─── -->
  <div class="legend">
    <div class="legend-item"><div class="legend-dot dot-green"></div> Green — Within thresholds vs prior session and window average</div>
    <div class="legend-item"><div class="legend-dot dot-yellow"></div> Yellow — ≥yellow_min decline vs prior session or window average</div>
    <div class="legend-item"><div class="legend-dot dot-red"></div> Red — ≥red_min decline vs prior session or window average</div>
    <div class="legend-item"><div class="legend-dot dot-grey"></div> Grey — Absent or first session (no prior to compare)</div>
    <div class="legend-item">~ = moderate deviation from window average &nbsp;|&nbsp; ↓↓/↑↑ = large deviation from window average</div>
  </div>

</div>

<!-- ─── Footer ─── -->
<div class="footer">{{ footer_text }}</div>

</body>
</html>
```

- [ ] **Step 5.2: Verify the template file exists and has correct Jinja2 syntax**

```bash
python -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'), autoescape=True)
t = env.get_template('recovery_report_template.html')
print('Template OK:', t.name)
"
```

Expected: `Template OK: recovery_report_template.html`

- [ ] **Step 5.3: Commit**

```bash
git add templates/recovery_report_template.html
git commit -m "feat: add recovery report Jinja2 HTML template"
```

---

## Task 6: CLI Entrypoint and End-to-End Integration

**Files:**
- Modify: `scripts/generate_recovery_report.py` (add `render_recovery_report`, `main`, helper to build context)

### What `main()` does

1. Parse CLI args (`--date`, `--sessions`, `--config`, `--master`)
2. Load config → build roster map and metric labels dict
3. Call `load_pre_data` → `get_session_dates`
4. For each of the 6 metrics, call `build_metric_grid` → collect into `all_grids`
5. For each athlete, call `assign_recovery_badge`
6. Build Jinja2 context dict
7. Call `render_recovery_report` → write output HTML

---

- [ ] **Step 6.1: Implement `render_recovery_report` and `main()` in `generate_recovery_report.py`**

Add at the end of the file:

```python
# ─── Config Helpers ───────────────────────────────────────────────────────────

def load_config(config_path: Path) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def build_metric_labels(config: dict) -> dict:
    """Return {threshold_key: metric_label} from config thresholds."""
    return {
        key: cfg["metric_label"]
        for key, cfg in config["thresholds"].items()
    }


# ─── Render ───────────────────────────────────────────────────────────────────

def render_recovery_report(context: dict, templates_dir: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
    )
    template = env.get_template("recovery_report_template.html")
    return template.render(**context)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate CMJ Recovery Monitoring Report"
    )
    parser.add_argument(
        "--date",
        default=datetime.today().strftime("%Y-%m-%d"),
        help="End date for session window (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--sessions",
        type=int,
        default=6,
        help="Number of most recent sessions to include (default: 6)",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--master", type=Path, default=DEFAULT_MASTER)
    args = parser.parse_args()

    # Validate date
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(f"Error: --date must be YYYY-MM-DD. Got: {args.date}")
        sys.exit(1)

    # Load config
    if not args.config.exists():
        print(f"Error: Config not found at {args.config}")
        sys.exit(1)
    config = load_config(args.config)
    roster_map = _build_roster_map(config)
    metric_labels = build_metric_labels(config)

    # Load data
    if not args.master.exists():
        print(f"Error: master_data.csv not found at {args.master}")
        sys.exit(1)

    print(f"Loading pre-practice data (last {args.sessions} sessions up to {args.date})...")
    pre_data = load_pre_data(args.master, args.date, args.sessions)

    if pre_data.empty:
        print(f"Error: No pre-practice data found up to {args.date}.")
        sys.exit(1)

    session_dates = get_session_dates(pre_data)
    print(f"Sessions: {', '.join(session_dates)}")

    # Build all metric grids
    all_grids = {}
    metric_grid_context = []
    for metric_col in METRIC_COLS:
        threshold_key = COL_TO_THRESHOLD_KEY[metric_col]
        cfg = config["thresholds"][threshold_key]
        grid_rows = build_metric_grid(pre_data, metric_col, session_dates, config, roster_map)
        all_grids[threshold_key] = grid_rows
        metric_grid_context.append({
            "metric_label": cfg["metric_label"],
            "unit": cfg["unit"],
            "rows": grid_rows,
        })

    # Build per-athlete summary
    athlete_names = sorted({row["name"] for rows in all_grids.values() for row in rows})
    summary_rows = []
    for name in athlete_names:
        badge_result = assign_recovery_badge(name, all_grids, metric_labels)
        # Get number/position from any grid row
        any_row = next(
            (r for rows in all_grids.values() for r in rows if r["name"] == name),
            {}
        )
        badge_labels = {
            "at_risk": "At Risk",
            "watch": "Watch",
            "recovered": "Recovered",
        }
        summary_rows.append({
            "name": name,
            "number": any_row.get("number", ""),
            "position": any_row.get("position", ""),
            "badge": badge_result["badge"],
            "badge_label": badge_labels[badge_result["badge"]],
            "most_affected_metric_label": badge_result["most_affected_metric_label"],
            "last_session_trend": badge_result["last_session_trend"],
        })

    # Sort summary: at_risk first, then watch, then recovered
    badge_order = {"at_risk": 0, "watch": 1, "recovered": 2}
    summary_rows.sort(key=lambda r: (badge_order[r["badge"]], r["name"]))

    # Counts for header
    at_risk_count = sum(1 for r in summary_rows if r["badge"] == "at_risk")
    watch_count = sum(1 for r in summary_rows if r["badge"] == "watch")
    recovered_count = sum(1 for r in summary_rows if r["badge"] == "recovered")

    # Date display helpers
    report_date_display = datetime.strptime(args.date, "%Y-%m-%d").strftime("%B %d, %Y")
    start_date_display = datetime.strptime(session_dates[0], "%Y-%m-%d").strftime("%B %d")
    end_date_display = datetime.strptime(session_dates[-1], "%Y-%m-%d").strftime("%B %d, %Y")
    date_range = f"{start_date_display} – {end_date_display}"
    session_dates_display = [
        datetime.strptime(d, "%Y-%m-%d").strftime("%b %d").replace(" 0", " ")
        for d in session_dates
    ]

    context = {
        "report_date": report_date_display,
        "date_range": date_range,
        "n_sessions": len(session_dates),
        "at_risk_count": at_risk_count,
        "watch_count": watch_count,
        "recovered_count": recovered_count,
        "session_dates_display": session_dates_display,
        "metric_grids": metric_grid_context,
        "summary_rows": summary_rows,
        "footer_text": config["report"]["footer_text"],
    }

    # Render and save
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DEFAULT_OUTPUT_DIR / f"recovery_report_{args.date}.html"

    print(f"\nRendering report...")
    html = render_recovery_report(context, TEMPLATES_DIR)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report saved: {output_path}")
    print(f"  At Risk: {at_risk_count}  Watch: {watch_count}  Recovered: {recovered_count}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6.2: Run the full test suite one final time**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 6.3: Smoke test against real data**

```bash
python scripts/generate_recovery_report.py --date 2026-03-20 --sessions 6
```

Expected output (approximately):
```
Loading pre-practice data (last 6 sessions up to 2026-03-20)...
Sessions: 2026-03-02, 2026-03-05, 2026-03-06, 2026-03-09, 2026-03-16, ...
Rendering report...
Report saved: output\recovery_report_2026-03-20.html
  At Risk: X  Watch: X  Recovered: X
```

Open `output/recovery_report_2026-03-20.html` in a browser and verify:
- [ ] Header shows correct date range and session count
- [ ] Six metric grids are visible with athlete rows and colored cells
- [ ] Absent sessions (athletes missing from a date) show grey "—" cells
- [ ] Recovery Status Summary table renders with correct badges and trend arrows
- [ ] Page is self-contained (no external network requests needed)

- [ ] **Step 6.4: Commit**

```bash
git add scripts/generate_recovery_report.py
git commit -m "feat: add recovery report CLI entrypoint and render function"
```

---

## Done

The recovery monitoring report is complete. Summary of what was built:

| File | Purpose |
|---|---|
| `scripts/generate_recovery_report.py` | Complete standalone script with all logic |
| `templates/recovery_report_template.html` | Self-contained HTML template, Baylor dark theme |
| `tests/test_recovery_report.py` | 30+ unit tests covering all logic paths |

Run anytime with:
```bash
python scripts/generate_recovery_report.py
python scripts/generate_recovery_report.py --date 2026-03-20 --sessions 4
```

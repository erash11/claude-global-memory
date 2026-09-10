# CMJ Recovery Monitoring Report — Design Spec
**Baylor Volleyball | Applied Performance**
Date: 2026-03-23

---

## Problem Statement

After each practice, the daily CMJ traffic-light report shows fatigue within that session (pre vs post). The coaching question this report addresses is different: **"Is the previous session's fatigue affecting pre-session jump output in subsequent sessions?"** — i.e., are athletes recovering between practices, or are their pre-practice values declining over time?

---

## Goal

A standalone HTML report (`output/recovery_report_YYYY-MM-DD.html`) that shows each athlete's pre-practice CMJ values across N consecutive sessions, colored to reveal session-to-session decline and deviation from personal window average.

---

## CLI Interface

```bash
# Default: last 6 sessions up to today (today = script execution date)
python scripts/generate_recovery_report.py

# Override end date and window size
python scripts/generate_recovery_report.py --date 2026-03-20 --sessions 4

# Optional flags (same as generate_report.py)
python scripts/generate_recovery_report.py --config config.yaml --master data/master_data.csv
```

| Argument | Default | Description |
|---|---|---|
| `--date` | `datetime.today()` (script execution date) | End date for the session window (YYYY-MM-DD). Output filename reflects this date. |
| `--sessions` | 6 | Number of most recent sessions to include |
| `--config` | config.yaml | Path to config file |
| `--master` | data/master_data.csv | Path to master data CSV |

Output file: `output/recovery_report_YYYY-MM-DD.html` (date = `--date` value or today if omitted)

---

## Report Layout

### 1. Header
- Title, date range covered, number of sessions
- Team summary: count of athletes per recovery badge (Recovered / Watch / At Risk)

### 2. Six Metric Grids (stacked vertically)
One grid per metric, in this order:
1. Jump Height
2. RSI-modified
3. Mean Propulsive Force
4. Eccentric Braking RFD
5. Time to Takeoff
6. Countermovement Depth

Each grid is an **athlete × session** table. Rows = athletes (sorted by roster position then name). Columns = session dates in chronological order.

**Athlete population:** The union of all athletes who appear in at least one pre-practice row within the window. Athletes not in the roster are displayed without number/position (same behavior as `generate_report.py`).

Each cell displays:
- The raw pre-practice value with unit
- A percent-change indicator vs the prior session (e.g., `-3.2%`)
- A window-average deviation indicator (`~` for yellow-range, `↓↓` / `↑↑` for red-range, per metric direction)
- Traffic-light background color (see Cell Coloring Logic below)

### 3. Recovery Status Summary Table
Final table: one row per athlete, columns: Athlete · Position · # · Status Badge · Most Affected Metric · Last Session Trend

---

## Cell Coloring Logic

Each cell color is the **worst (most severe) of two signals**. Color precedence: red > yellow > green > grey.

### Signal 1 — Session-to-Session Delta

Compare `pre[session N]` vs `pre[session N-1]` using the existing `calc_pct_change(pre, post)` and `get_metric_color(pct_change, cfg)` from `utils.py`. Thresholds come from `config.yaml` (`yellow_min`, `red_min`, `direction` per metric). Direction (`decrease_bad` / `increase_bad`) is respected as in the daily report.

- Green: change within green threshold
- Yellow: change ≥ yellow_min in bad direction
- Red: change ≥ red_min in bad direction

### Signal 2 — Window Average Deviation

**Personal baseline** = mean of the athlete's non-null pre values across **all sessions in the window** (including the current session). This is computed once per athlete per metric for the full window and held constant — it is a fixed window reference, not recomputed per cell.

Deviation is evaluated by calling `calc_pct_change(baseline, current_session_value)` fed into `get_metric_color()` with the metric's `direction` config key. This ensures `increase_bad` metrics (Time to Takeoff, CM Depth) are colored correctly: a pre value *above* baseline triggers yellow/red, not below.

- Within threshold → no additional indicator
- ≥ yellow_min deviation in bad direction → `~` indicator added; cell is yellow at minimum
- ≥ red_min deviation in bad direction → `↓↓` (decrease_bad) or `↑↑` (increase_bad) indicator; cell is red at minimum

### Combined Rule
Worst of Signal 1 and Signal 2 determines cell color (red > yellow > green).

### Special Cell States
| State | Display |
|---|---|
| First session in window (no prior to compare for Signal 1) | Signal 1 = neutral (no color contribution); Signal 2 still applies; final color from Signal 2 only |
| Immediately after an absent session (no prior pre row to compare) | Same as first session: Signal 1 = neutral; Signal 2 still applies; final color from Signal 2 only; percent-change indicator displays "—" (no prior value) |
| Athlete absent for that session | Grey cell; "—" text; "Absent" label; excluded from Signal 1, Signal 2, and badge color counts entirely |
| Missing/non-numeric value | Grey cell; "N/A" |

Note: "First session" and "post-absent" cells can still be yellow or red if Signal 2 fires. Only **truly absent cells** (no athlete data for that date) are always grey and excluded from all counts.

---

## Recovery Status Badge Logic

Computed per athlete across all 6 metrics and all sessions in the window. **Only absent cells (grey "—" cells) are excluded from badge color counts.** First-session and post-absent cells are included if Signal 2 produces a color. Badge rules are evaluated in cascade order: At Risk first, then Watch, then Recovered.

| Badge | Criteria |
|---|---|
| **At Risk** (red) | 2+ red cells OR 3+ (yellow + red) cells across all metrics and sessions |
| **Watch** (yellow) | 2–3 yellow cells OR 1 red cell across all metrics and sessions (and does not meet At Risk) |
| **Recovered** (green) | Does not meet At Risk or Watch |

**Most Affected Metric**: the metric column with the highest count of yellow + red cells for that athlete across the window.

**Last Session Trend**: computed by applying `get_metric_color()` to each metric's session-to-session delta for the most recent session transition (Signal 1 only), then counting the resulting colors:
- `↑` if 4 or more metrics are green (improving or stable)
- `↓` if 4 or more metrics are yellow or red (declining)
- `→` otherwise (mixed signals)

If the athlete was absent for the most recent session, display `—`.

If the most recent session transition has no Signal 1 (i.e., it is a first-session or post-absent cell), display `→` (insufficient data to determine direction).

---

## Reused Without Changes

| File | What is reused |
|---|---|
| `scripts/utils.py` | `calc_pct_change`, `get_metric_color` |
| `config.yaml` | All thresholds, roster, column mapping — no new config keys needed |

Note: `assign_overall_color` from `utils.py` is **not** used in this report. The recovery badge logic (multi-session, multi-metric counts) is a different computation and is implemented directly in `generate_recovery_report.py`.

---

## New Files

| File | Purpose |
|---|---|
| `scripts/generate_recovery_report.py` | Main script: data loading, grid building, badge assignment, render |
| `templates/recovery_report_template.html` | Jinja2 template; self-contained HTML (matches daily report visual style) |

## Not Modified

- `scripts/generate_report.py` — daily report unchanged
- `scripts/run_pipeline.py` — recovery report is run separately, not chained automatically
- `scripts/import_data.py` — no changes

---

## Key Functions in `generate_recovery_report.py`

| Function | Signature | Purpose |
|---|---|---|
| `load_pre_data` | `(master_path, end_date, n_sessions) -> DataFrame` | Returns a filtered DataFrame of **rows** (not just dates) from master CSV containing only pre-tagged records for the N most recent sessions up to end_date. A "session" is a unique `test_date` with at least one pre row. Unique dates are collected from the pre-filtered subset, sorted descending, and the N most recent are kept; then all rows for those dates are returned. |
| `get_session_dates` | `(pre_data: DataFrame) -> list[str]` | Extracts and returns a sorted (ascending) list of unique `test_date` values from the already-filtered DataFrame returned by `load_pre_data`. This function is a simple downstream helper — it does not re-filter or re-scope dates. |
| `compute_window_baseline` | `(values: list[float]) -> float` | Mean of non-null pre values for one athlete/metric across the window |
| `build_metric_grid` | `(pre_data, metric_col, session_dates, config, roster_map) -> list[dict]` | Build per-athlete rows for one metric grid with Signal 1, Signal 2, combined color, and indicators. Per athlete/metric, `compute_window_baseline` must be called **once before iterating over session columns**, using that athlete's full set of non-null values across the window — not inside the per-cell loop. |
| `assign_recovery_badge` | `(athlete_name, all_grids: dict[str, list[dict]]) -> dict` | Apply At Risk > Watch > Recovered cascade across all 6 metric grids for one athlete. `all_grids` is a dict mapping metric key (e.g., `"jump_height"`) to the `list[dict]` returned by `build_metric_grid` for that metric. Each dict in the list has at least `{"name": str, "cells": list[{"color": str, ...}]}`. |
| `render_recovery_report` | `(context, templates_dir) -> str` | Jinja2 render |

---

## Testing

Extend existing test suite with `tests/test_recovery_report.py`:

- `test_session_to_session_coloring` — verify cell colors for known pre-value sequences (decrease_bad metric declining across sessions)
- `test_rolling_baseline_deviation_decrease_bad` — verify `~` / `↓↓` indicators trigger correctly for a `decrease_bad` metric (e.g., Jump Height below window average)
- `test_rolling_baseline_deviation_increase_bad` — verify `↑↑` indicators trigger for an `increase_bad` metric (e.g., Time to Takeoff or CM Depth *above* window average triggers yellow/red, not below)
- `test_absent_handling` — verify absent sessions show grey/dash; cell immediately after absent session gets neutral grey with no Signal 1 color; absent sessions are excluded from badge counts
- `test_recovery_badge_assignment` — verify At Risk / Watch / Recovered thresholds using known grid color counts; confirm At Risk > Watch > Recovered cascade order
- `test_most_affected_metric` — verify correct metric identified when one has most yellow+red cells
- `test_last_session_trend` — verify ↑ / ↓ / → calculation given known per-metric delta colors; include edge cases: (a) athlete with only one session in window (most recent = first session → displays `→`), (b) athlete absent for most recent session (displays `—`), (c) athlete whose most recent prior session was absent (displays `→`)

---

## Visual Style

Matches the existing daily report: dark Baylor theme (`#003015` green, `#FFB81C` gold), same CSS custom properties, same font stack. Self-contained HTML (no external dependencies) so it works offline.

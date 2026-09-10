# Post-Session Coach Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A one-page coach-facing HTML+PDF post-session report (planned vs actual, max-velocity exposure, SPC over/under-dose flags) generated read-only from `gps_report/data/gps_history.duckdb`.

**Architecture:** New `coach_report/` package, pure consumer of the existing DuckDB. Pipeline: load session rows → infer day-type from session name → compute planned range from historical medians (override file wins) → compute max-vel exposure lists → compute XmR control limits per athlete → render Jinja2 HTML with inline SVG sparklines → export PDF via headless Chrome.

**Tech Stack:** Python 3.12, duckdb, pandas, PyYAML, Jinja2, pytest. Chrome/Edge headless for PDF. Same dependency set as `gps_report/` (no new deps).

## Global Constraints

- DB opened with `duckdb.connect(path, read_only=True)` — never write to `gps_history.duckdb`.
- Default DB path resolves relative to repo root: `gps_report/data/gps_history.duckdb`; `--db` flag overrides (needed when running from a worktree).
- Metrics (exact DB columns): `total_player_load`, `player_load_per_minute`, `explosive_efforts`, `max_velocity_ms`, `total_duration_s`.
- Units: velocity stored m/s, displayed mph (× 2.23694). Player Load unitless (note: DB stores Catapult `average_player_load`).
- SPC: XmR — sigma = mean(|moving range|)/1.128, UCL/LCL = CL ± 3σ, LCL floored at 0, min 10 prior sessions, baseline = last 20 non-game sessions before report date.
- Max vel: exposure threshold 0.90 × PB, opportunity window 10 days (both in `coach_config.yaml`).
- Day-type regexes in config, first match wins; unmatched → `other`, never dropped.
- Output: `coach_report/Reports/coach/YYYY-MM-DD/coach_report.html` (+ `.pdf`).
- All HTML self-contained (inline CSS + SVG; no external requests).

---

### Task 1: Config + day-type inference (`day_types.py`)

**Files:**
- Create: `coach_report/coach_config.yaml`
- Create: `coach_report/src/__init__.py`, `coach_report/src/day_types.py`
- Test: `coach_report/tests/test_day_types.py`

**Interfaces:**
- Produces: `infer_day_type(session_name: str, rules: list[dict]) -> str` where rules = `[{pattern, day_type}]` from config key `day_types`; `load_config(path) -> dict`.

- [x] Write failing tests: name→type table (`"SP26 - P15 - 04.25.26"→"practice"`, `"SP26 - Walk Thru #10 - 04.22.26"→"walk_thru"`, `"AUBURN - G1 - 08.29.25"→"game"`, `"SP26 - 4TH QTR #4 - 03.06.26"→"conditioning"`, `"Lift Group A"→"other"`); case-insensitivity.
- [x] Run to verify failure; implement; verify pass.
- [x] Config content: `day_types` rules (walk.?thru→walk_thru, scrimmage→scrimmage, 4th\s*qtr→conditioning, `-\s*P\d+`→practice, `-\s*G\d+`→game), `metrics` display names, `maxvel: {threshold_pct: 0.90, window_days: 10}`, `spc: {baseline_sessions: 20, min_sessions: 10, sigma_mult: 3.0, sparkline_sessions: 15, metrics: [total_player_load, player_load_per_minute]}`, `plan: {lookback_days: 365, on_target_band: [lower=q25, upper=q75]}`, `report: {timezone: America/Chicago, title}`.
- [x] Commit.

### Task 2: Data access (`data.py`)

**Files:**
- Create: `coach_report/src/data.py`
- Test: `coach_report/tests/test_data.py` (fixture builds a tiny in-memory DuckDB with same schema)

**Interfaces:**
- Produces:
  - `connect(db_path) -> duckdb.Connection` (read_only)
  - `sessions_on(con, date) -> pd.DataFrame` (session_id, session_name, session_date, start_time, end_time)
  - `athlete_rows(con, session_ids) -> pd.DataFrame` (athlete_id, name, position_group, metrics… joined to athletes)
  - `history(con, before_date, lookback_days) -> pd.DataFrame` (athlete_id, session_id, session_date, session_name, metrics) — all athlete_sessions joined to sessions in window, excluding report date
  - `personal_bests(con) -> pd.DataFrame` (athlete_id, pb_max_velocity_ms) over full history

- [x] Failing tests with 3-athlete fixture DB; implement; pass; commit.

### Task 3: Planned vs actual (`plan.py` — folded into day_types? No: separate)

**Files:**
- Create: `coach_report/src/plan.py`
- Create: `coach_report/plan_overrides.yaml` (documented, empty mapping)
- Test: `coach_report/tests/test_plan.py`

**Interfaces:**
- Produces: `planned_targets(hist: pd.DataFrame, day_type: str, metrics: list[str]) -> dict[metric] = {planned_lo(q25), planned_med, planned_hi(q75), n_sessions}` using per-session team medians of same day-type; `apply_overrides(targets, overrides: dict, date) -> (targets, note, forced_day_type)`; `compare(actual_team_median, targets) -> {delta_pct, badge in {over, on, under, no_plan}}`.
- Badge: `on` if within [planned_lo, planned_hi]; over/under outside.

- [x] Failing tests: q25/q75 from synthetic history; override wins; empty history → `no_plan`. Implement; pass; commit.

### Task 4: Max velocity (`maxvel.py`)

**Files:**
- Create: `coach_report/src/maxvel.py`
- Test: `coach_report/tests/test_maxvel.py`

**Interfaces:**
- Produces: `exposure_lists(today: pd.DataFrame, hist: pd.DataFrame, pbs: pd.DataFrame, threshold_pct, window_days, report_date) -> {hit_today: [...], needs_opportunity: [...], not_present: [...]}`; rows carry name, position_group, today_mph, pb_mph, pct_of_pb, days_since_exposure.
- `needs_opportunity` = athletes present today (or in window) whose best pct-of-PB in window < threshold; sorted days_since_exposure desc (None → "10+").

- [x] Failing tests: athlete at 92% PB today → hit; 85% for 12 days → needs; absent from window → not_present. Implement; pass; commit.

### Task 5: SPC (`spc.py`)

**Files:**
- Create: `coach_report/src/spc.py`
- Test: `coach_report/tests/test_spc.py`

**Interfaces:**
- Produces: `xmr_limits(values: list[float]) -> {cl, ucl, lcl, sigma}` and `spc_flags(today, hist, config, day_type) -> {flags: [FlagRow], excluded: [(name, n_sessions)]}`; FlagRow = {athlete_id, name, position_group, metric, value, cl, ucl, lcl, sigma_dev, direction in {over, under}, series: last-N [(date, value)] incl. today}.
- Baseline excludes `game` day-type rows when today's day_type != game; flags sorted |sigma_dev| desc, grouped by direction.

- [x] Failing tests: hand-computed XmR fixture (values [10,12,11,13,12,11,12,13,11,12] → CL=11.7, sigma=mean MR/1.128; verify UCL/LCL to 3 decimals); over-flag when today > UCL; under-flag; <10 sessions excluded. Implement; pass; commit.

### Task 6: Render + PDF (`render.py`, template, CLI)

**Files:**
- Create: `coach_report/src/render.py`, `coach_report/templates/coach_report.html.j2`, `coach_report/coach_report.py`
- Test: `coach_report/tests/test_render.py` (smoke: renders with fixture context, contains athlete names, no Jinja errors; sparkline SVG function unit-tested for coordinate scaling)

**Interfaces:**
- Consumes all prior modules. `sparkline_svg(series, cl, ucl, lcl, width=220, height=48) -> str`; `render_html(context) -> str`; `export_pdf(html_path, pdf_path)` — finds `chrome.exe`/`msedge.exe`, runs `--headless=new --disable-gpu --print-to-pdf=...`; missing browser → warn, HTML only.
- CLI: `coach_report.py --date today|YYYY-MM-DD [--db PATH] [--session ID] [--no-pdf]`; exit 3 when no sessions (print 5 nearest session dates).
- Template sections per spec: header, planned-vs-actual KPI tiles + position-group table, max-vel two lists, SPC flag tables with sparklines, footer. Inline CSS; follow dataviz skill guidance (load before writing template).

- [x] Smoke tests; implement; pass; commit.

### Task 7: End-to-end validation

- [x] Run `python coach_report.py --date 2026-04-25 --db <main checkout db>` and a walk-thru date (2026-04-22).
- [x] Cross-check: team median total_player_load for 2026-04-25 vs direct SQL; one athlete's XmR limits recomputed by hand in a scratch script.
- [x] Export PDF; visual check of HTML (Read screenshot optional).
- [x] Commit; update repo CLAUDE.md with a short coach_report section.

## Self-Review

- Spec coverage: day-types (T1), read-only data (T2), planned vs actual + overrides (T3), max vel (T4), SPC (T5), layout/PDF/CLI/error handling (T6), validation (T7). Multiple-sessions aggregation handled in T6 CLI (practices aggregated; `--session` to pick). ✓
- No placeholders; interfaces named consistently (`planned_targets`, `exposure_lists`, `spc_flags`, `sparkline_svg`). ✓

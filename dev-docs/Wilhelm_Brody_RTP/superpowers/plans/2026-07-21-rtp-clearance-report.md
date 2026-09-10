# RTP Clearance Report (Wilhelm) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One-page ACL RTP clearance report for Brody Wilhelm (TE, surgery 2025-10-01): criteria chips + four time-series panels (GPS velocity, GPS workload, CMJ, strength), TE IQR band + pre-injury baseline on every panel, delivered as print PDF + private artifact link.

**Architecture:** `pull_data.py` (Catapult CLI subprocess + two DuckDB reads → `data/report_data.json`) → `charts.py` (matplotlib → four SVGs) → `build_report.py` (HTML shell, inline SVGs → headless Edge PDF). Same HTML publishes as the artifact.

**Tech Stack:** Python 3 (`C:\Users\eric_rash\AppData\Local\Python\bin\python.exe`), duckdb 1.5.1, matplotlib, pyyaml, pypdf (install), `catapult-openfield-connect-pp-cli`, headless Edge.

## Global Constraints

- Working dir: the `build` worktree of `C:\Users\eric_rash\Desktop\DEV\SpecialRequests\Wilhelm_Brody_RTP` (own git repo, no remote — commit locally, no PR).
- PDF must be exactly ONE US-letter page — fail loudly otherwise (spec).
- No dual-axis charts (dataviz rule): panels 3–4 are stacked small-multiples sharing the x-axis.
- Palette (dataviz reference, light mode): series blue `#2a78d6`; TE band fill `#f0efec` w/ median line `#c3c2b7`; pre-injury dashed `#0b0b0b`; threshold dotted `#898781`; status good `#0ca30c` / warning `#fab219` / serious `#ec835a`; ink `#0b0b0b`/`#52514e`/muted `#898781`; grid `#e1e0d9`; surface `#fcfcfb`. Text never wears series color. Report commits to the light look (print parity).
- Criteria chip logic: **Met** ≥ target; **Approaching** ≥ target−5 pts; **Not met** below; **No data** when no post-op measurement exists (never a fake status).
- Data facts (verified 2026-07-21): VALD `forceplate.db` is DuckDB, long format (`metric_name`/`metric_value`); Brody CMJ classified rows end 2026-06-08 (only 2 post-op tests), IMTP ends 2026-06-10, **no L/R split in IMTP** → symmetry criterion uses CMJ `Eccentric Braking Impulse Asymmetry` / `classified_athletes.asymmetry_pct`. Perch `perch_1rm` ends 2026-04-27, has no position column (TE membership joined from VALD TE name list). Catapult profile `velocity_max` = 8.62961 m/s (pre-injury max reference). Catapult local `statistics` table covers ONLY 2026-04-15→28; live `statistics` command needs `--timeout 120s`+, JSON-array args:
  `statistics --parameters '["total_player_load","max_vel","total_distance"]' --group-by '["athlete","activity"]' --filters '[{"name":"athlete_name","comparison":"=","values":["Brody Wilhelm"]},{"name":"date","comparison":">=","values":["2026-04-01"]}]' --agent`
  Response envelope: `{"meta":{"source":...},"results":[...]}`. **Fallback if live stats unavailable:** local statistics rows (Apr 27–28: max_vel 4.16, 852 m) + profile velocity_max; GPS panels annotate "limited GPS — live pull unavailable" and workload criterion = No data.

---

### Task 1: Scaffold + params

**Files:**
- Create: `params.yaml`, `.gitignore`, `src/`, `data/`, `out/`

**Interfaces:**
- Produces: `params.yaml` consumed by all `src/*` via `yaml.safe_load`.

- [ ] **Step 1: Write `.gitignore`** — `out/`, `data/`, `__pycache__/`
- [ ] **Step 2: Write `params.yaml`:**

```yaml
athlete:
  name: "Brody Wilhelm"
  catapult_id: "dfa0b5c5-0b89-49ff-89c9-2123090651d6"
  perch_name: "brody wilhelm"
  position: "Tight End"
surgery_date: "2025-10-01"
report_date: "2026-07-21"
preinjury_window: ["2025-06-01", "2025-09-30"]
catapult_profile_velocity_max: 8.62961
te_gps_window_weeks: 6
paths:
  forceplate_db: "C:/Users/eric_rash/Desktop/DEV/ForcePlate_DecisionSystem/data/forceplate.db"
  perch_db: "C:/Users/eric_rash/Desktop/DEV/PlayerProfiles_FB_03-28-2026/data/perch.duckdb"
  catapult_cli: "C:/Users/eric_rash/go/bin/catapult-openfield-connect-pp-cli.exe"
  catapult_local_db: "C:/Users/eric_rash/.local/share/catapult-openfield-connect-pp-cli/data.db"
  thresholds_yaml: "C:/Users/eric_rash/Desktop/DEV/ForcePlate_DecisionSystem/config/thresholds.yaml"
thresholds:
  velocity_pct_preinjury: 90
  mrsi_pct_baseline: 90
  asym_caution: 10
  imtp_pct_preinjury: 90
  strength_pct_preinjury: 90
  workload_pct_te_median: 85
  approaching_margin: 5
```

- [ ] **Step 3: `pip install pypdf`** (page-count check): `& C:\Users\eric_rash\AppData\Local\Python\bin\python.exe -m pip install pypdf --quiet`
- [ ] **Step 4: Commit** `chore: scaffold params + gitignore`

### Task 2: `src/pull_data.py`

**Files:** Create: `src/pull_data.py`

**Interfaces:**
- Produces: `data/report_data.json` with keys `as_of`, `gps` (`brody_sessions` [{date,max_vel,total_player_load,total_distance}], `preinjury_max_vel`, `te_weekly_band` [{week_start,p25,p50,p75}], `gps_note`), `cmj` (`tests` [{date,mrsi,asym,jump_height_cm}], `baseline_mrsi`, `te_band` {mrsi:{p25,p50,p75}, jh:{...}}), `imtp` (`tests` [{date,peak_force_n}], `preinjury_best`, `te_band`), `strength` (`lifts` [{date,e1rm_lbs}], `exercise`, `preinjury_best`, `te_band`), `criteria` [{id,label,value_text,target_text,status}].

- [ ] **Step 1: Implement.** Key logic (VALD via duckdb read_only; percentiles via `statistics.quantiles`):
  - `pull_vald(p)`: Brody rows from `classified_athletes` (test_date, asymmetry_pct, mrsi, baseline_mrsi); jump height from `raw_tests` where `metric_name='Jump Height (Imp-Mom)'`; IMTP `Peak Vertical Force` from `imtp_tests`. TE band: latest 2026 test per other TE (`WHERE position='Tight End' AND athlete_name != 'Brody Wilhelm' AND test_date >= DATE '2026-01-01'`) → p25/p50/p75 across athletes for mrsi, jump height, IMTP PVF. Also return the TE athlete-name list for the Perch join.
  - `pull_perch(p)`: Brody `perch_1rm` rows for the lower-body lift with the longest Brody history (expected `Back Squat`); `preinjury_best` = max one_rm_lbs where test_date < surgery_date; TE band from rows whose `name_normalized` is in the lowercased VALD TE list, latest per athlete.
  - `pull_catapult(p)`: subprocess CLI `statistics` (syntax in Global Constraints) for (a) Brody pre-injury window, (b) Brody surgery→report_date, (c) TE names trailing-6-week window (one query, multiple `values`). Parse `.results`. On failure/timeout (retry once, 180s): fall back to local sqlite `statistics` table + set `gps_note`. `preinjury_max_vel` = max(profile velocity_max, observed pre-injury session max).
  - `compute_criteria(...)` → six chips: sprint velocity ≥90% pre-injury; weekly PL ≥85% TE median; CMJ asym within ±10%; mRSI ≥90% baseline; IMTP PVF ≥90% pre-injury best; Back Squat e1RM ≥90% pre-injury. Latest post-op value each; No data when absent.
- [ ] **Step 2: Run + sanity check:** `python src/pull_data.py` with assertions in main: cmj tests ≥ 8, imtp dates ≥ 10, perch lifts ≥ 5, every criterion status ∈ {met,approaching,not_met,no_data}; print one summary line per source.
- [ ] **Step 3: Commit** `feat: data pull layer -> report_data.json`

### Task 3: `src/charts.py`

**Files:** Create: `src/charts.py`

**Interfaces:**
- Consumes: `data/report_data.json`.
- Produces: `out/panel1.svg`…`out/panel4.svg`, each ~7.2×1.55 in via `fig.savefig(..., format='svg')`, Agg backend, rcParams: palette + `font.family: 'Segoe UI'`, `svg.fonttype: 'none'`.

- [ ] **Step 1: Implement four builders** sharing `_style_ax(ax)` (y-grid `#e1e0d9`, spines off except bottom `#c3c2b7`, muted 7pt ticks) and `_band(ax, p25, p50, p75)` (axhspan `#f0efec`, median dashed `#c3c2b7`). X-domain 2025-06-01→2026-07-21, vertical surgery marker + label on every panel.
  - `panel1`: Brody session `max_vel` (m/s) line+dots blue; dashed black pre-injury best; dotted gray 90% line; TE band.
  - `panel2`: weekly summed `total_player_load` thin bars (blue, rounded ends); TE weekly IQR band; `gps_note` annotated top-left muted italic when set.
  - `panel3`: 2 stacked axes sharex — (a) mRSI dots+line, baseline dashed, TE band; (b) asymmetry % dots, ±10 caution bounds shaded; direct-label the latest point of each.
  - `panel4`: 2 stacked axes sharex — (a) IMTP Peak Vertical Force (N), pre-injury dashed, TE band; (b) Back Squat e1RM (lbs), pre-injury dashed, TE band.
  - Sparse-data honesty: points always drawn; no line interpolation across the surgery gap.
- [ ] **Step 2: Run; confirm 4 SVGs exist, each > 2 KB.**
- [ ] **Step 3: Commit** `feat: four report panels`

### Task 4: `src/build_report.py`

**Files:** Create: `src/build_report.py`

**Interfaces:**
- Consumes: `data/report_data.json`, `out/panel*.svg`.
- Produces: `out/report.html`, `out/Wilhelm_Brody_RTP_2026-07-21.pdf` (exactly 1 page).

- [ ] **Step 1: Implement.** f-string HTML: header row (name/position left; DOS, months post-op, report date right), criteria chip row (6 chips: colored dot + label + value vs target; "No data" gray), four panel sections each with 8pt title + one-line caption, footer with per-source as-of dates + threshold sources ("house thresholds.yaml; VALD 2024-25 NFL/NCAA normative report"). CSS: `@page { size: letter portrait; margin: 0.35in }`, body 9pt Segoe UI, `svg { width:100% }`, `-webkit-print-color-adjust: exact`.
- [ ] **Step 2: PDF:** subprocess `"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=<abs pdf> file:///<abs html>`; `pypdf.PdfReader` page count — raise if ≠ 1 (shrink panel heights once and retry).
- [ ] **Step 3: Run end-to-end; visually inspect** by Reading the PDF (renders pages) — label collisions/overflow per dataviz step 7 + anti-patterns.
- [ ] **Step 4: Commit** `feat: html shell + one-page pdf build`

### Task 5: Deliver

- [ ] **Step 1:** Publish `out/report.html` as private artifact (favicon 🏈, title "Wilhelm RTP Clearance Report").
- [ ] **Step 2:** `SendUserFile` the PDF.
- [ ] **Step 3:** Merge `build` → `main` locally; final summary with `result:` line (no remote → no PR; say where the repo is).

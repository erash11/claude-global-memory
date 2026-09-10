# ForcePlate Decision System — Design Spec

**Date:** 2026-03-20
**Project:** ForcePlate_DecisionSystem
**Status:** Approved (v2 — post spec review)

---

## Overview

A Python-based data pipeline and dashboard that operationalizes the Pentheny CMJ Force Plate Decision Framework for a collegiate Football program. The system ingests CMJ test data from the VALD ForceDecks REST API, stores it in DuckDB, classifies athletes using the 4-step hybrid pipeline, and surfaces results via an interactive Streamlit dashboard and a weekly PDF/HTML report.

---

## Problem & Motivation

The performance staff collects CMJ force plate data via VALD ForceDecks but currently has no automated way to:
- Classify athletes into training groups (Gold/Purple/White) using validated thresholds
- Detect longitudinal readiness flags (yellow/orange/red) based on individual baselines
- Generate consistent weekly reports for coaching and medical staff

This system closes that gap with a reproducible, single-command pipeline.

---

## Architecture

```
VALD REST API (OAuth2 / Auth0)
    ↓
src/ingest/vald_client.py     ← OAuth2 token cache + REST calls
    ↓
src/ingest/pipeline.py        ← filter to Football team, 42 metrics, date ≥ 2026-01-01
                              ← pivot long→wide per test_id before classification
    ↓
data/forceplate.db (DuckDB)   ← raw_tests | classified_athletes | athlete_baselines
    ↓
src/classify/engine.py        ← 4-step Pentheny classification
    ↓
src/report/dashboard.py       ← Streamlit interactive dashboard
src/report/pdf_report.py      ← Jinja2 → WeasyPrint → PDF + HTML
```

---

## Directory Structure

```
ForcePlate_DecisionSystem/
├── .env                          # VALD_CLIENT_ID, VALD_CLIENT_SECRET, VALD_REGION_URL, VALD_TEAM_ID
├── .gitignore                    # excludes .env, data/*.db, reports/
├── requirements.txt
├── run_pipeline.py               # CLI entry point
├── config/
│   └── thresholds.yaml           # all P25/P50/P75 per metric per position group
├── src/
│   ├── __init__.py
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── vald_client.py
│   │   └── pipeline.py
│   ├── classify/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── asymmetry.py
│   │   ├── mrsi.py
│   │   ├── eccentric.py
│   │   └── p1p2.py
│   └── report/
│       ├── __init__.py
│       ├── dashboard.py
│       ├── pdf_report.py
│       └── components/
│           ├── radar_chart.py
│           ├── phase_profile.py
│           └── roster_table.py
├── templates/
│   └── weekly_report.html
├── data/                         # gitignored
│   └── forceplate.db
├── reports/                      # gitignored (contains athlete PII)
├── docs/
│   └── superpowers/specs/
│       └── 2026-03-20-forceplate-decision-system-design.md
└── ContextBackgroundInfo/        # reference PDFs (existing)
```

---

## Component Specifications

### 1. VALD API Client (`src/ingest/vald_client.py`)

**Authentication:** OAuth2 client credentials flow (Auth0).

- Token endpoint: `https://auth.prd.vald.com/oauth/token` (hard-coded; not region-specific)
- Required request body fields: `client_id`, `client_secret`, `audience="vald-api-external"`, `grant_type="client_credentials"`
- Token cached in memory; auto-refreshed when JWT `exp` claim is within 60 seconds of expiry (parsed with `PyJWT`)
- Data endpoints use `VALD_REGION_URL` as the base (region-specific, from `.env`)

**`VALDClient` reads `VALD_TEAM_ID` from `.env` internally.** The `get_tests()` method uses it by default; the team_id can also be passed explicitly for `--dry-run` discovery. This ensures all callers use the configured team without re-reading `.env` outside the client.

**Interface:**
```python
class VALDClient:
    def get_teams(self) -> list[dict]
    def get_profiles(self, team_id: str | None = None) -> list[dict]  # defaults to VALD_TEAM_ID
    def get_tests(self, from_date: str, test_type: str = "CMJ") -> list[dict]  # uses VALD_TEAM_ID
    def get_result_definitions(self) -> dict  # metric_name → unit; cached after first call
```

**Config (from `.env`):**
- `VALD_CLIENT_ID`
- `VALD_CLIENT_SECRET`
- `VALD_REGION_URL` — e.g., `https://prd-use-api-forcedecks.valdperformance.com`
- `VALD_TEAM_ID` — Football team identifier in VALD system

**Metric filtering:** API returns all metrics per test. After retrieval, `pipeline.py` filters to the 42 target metric names defined in `config/thresholds.yaml` under `target_metrics`.

---

### 2. Data Pivoting (in `src/ingest/pipeline.py`)

`raw_tests` stores one row per `(test_id, metric_name)` — up to 42 rows per test. Before classification, `pipeline.py` is responsible for pivoting these long-format rows into a wide-format dict per test:

```python
# Pseudocode in pipeline.py
for test_id, group in raw_tests_df.groupby("test_id"):
    metrics_dict = dict(zip(group["metric_name"], group["metric_value"]))
    position_group = group["position_group"].iloc[0]
    baseline = get_baseline(athlete_id)
    result = classify_test(metrics_dict, position_group, thresholds, baseline)
    upsert_classified(result)
```

This pivot is the explicit responsibility of `pipeline.py`, not `engine.py`. The classification engine receives only the wide-format dict.

---

### 3. DuckDB Schema (`data/forceplate.db`)

**`raw_tests`** — append-only; upsert by `(test_id, metric_name)` to avoid duplicates
```sql
CREATE TABLE IF NOT EXISTS raw_tests (
    test_id         VARCHAR NOT NULL,
    athlete_id      VARCHAR NOT NULL,
    athlete_name    VARCHAR,
    position        VARCHAR,
    position_group  VARCHAR,   -- 'skill' | 'big'
    test_date       DATE,
    metric_name     VARCHAR,
    metric_value    DOUBLE,
    metric_unit     VARCHAR,
    pulled_at       TIMESTAMP DEFAULT now(),
    PRIMARY KEY (test_id, metric_name)
);
```

**`classified_athletes`** — recomputed on each pipeline run (INSERT OR REPLACE)
```sql
CREATE TABLE IF NOT EXISTS classified_athletes (
    test_id           VARCHAR PRIMARY KEY,
    athlete_id        VARCHAR,
    athlete_name      VARCHAR,
    position_group    VARCHAR,
    test_date         DATE,
    asymmetry_pct     DOUBLE,
    asymmetry_flag    VARCHAR,   -- 'pass' | 'caution' | 'flag'
    mrsi              DOUBLE,
    mrsi_group        VARCHAR,   -- 'gold' | 'purple' | 'white'
    ecc_peak_power_bm DOUBLE,
    ecc_profile       VARCHAR,   -- 'gold_confirm' | 'purple' | 'ecc_flag'
    final_group       VARCHAR,   -- 'gold' | 'purple' | 'white'
    concentric_impulse DOUBLE,
    p1_impulse        DOUBLE,
    p2_impulse        DOUBLE,
    p1p2_quadrant     VARCHAR,   -- 'low_p1' | 'low_p2' | 'balanced' | 'low_bw'
    ci_quartile       INTEGER,   -- 1–4
    baseline_mrsi     DOUBLE,
    mrsi_pct_change   DOUBLE,
    readiness_flag    VARCHAR,   -- 'green' | 'yellow' | 'orange' | 'red'
    classified_at     TIMESTAMP DEFAULT now()
);
```

**`athlete_baselines`** — baseline update rules:
- **Set on first occurrence:** When an athlete appears in the system for the first time, their first test's mRSI becomes the baseline.
- **Never auto-updated:** Baselines do not change automatically. They require an explicit manual override via CLI flag `--reset-baseline <athlete_id>` or `--reset-all-baselines`.
- **Rationale:** Prevents a declining athlete from having their flag thresholds silently drift downward. Intentional clinical decision to update baselines.

```sql
CREATE TABLE IF NOT EXISTS athlete_baselines (
    athlete_id    VARCHAR PRIMARY KEY,
    baseline_mrsi DOUBLE,
    baseline_date DATE,
    updated_at    TIMESTAMP DEFAULT now()
);
```

---

### 4. Classification Engine

**Entry point:** `src/classify/engine.py` — `classify_test(test_metrics: dict, position_group: str, thresholds: dict, baseline_mrsi: float | None) -> dict`

**Step 1 — Asymmetry Screen** (`asymmetry.py`):
| Asymmetry % | Flag | Action |
|---|---|---|
| < 10% | `pass` | Proceed normally |
| 10–15% | `caution` | Flag for review; continue classification |
| > 15% | `flag` | Restrict bilateral high-load work; clinical eval within 48h |

**Step 2 — mRSI Primary Classification** (`mrsi.py`):
Thresholds from `thresholds.yaml` per `position_group`. Returns `gold`, `purple`, or `white`. White group exits early (skip Steps 3 & 4).

**Step 3 — Eccentric Profile Confirmation** (`eccentric.py`):
- `EPF/BM > 2.5x` AND `Peak Power/BM ≥ gold threshold` → `gold_confirm`
- `EPF/BM 2.0–2.5x` OR `Peak Power/BM` in purple range → `purple`
- `EPF/BM < 2.0x` → `ecc_flag` (clinical flag + Purple group)
- `Countermovement Depth` > position threshold → SSC coupling note appended

**Step 4 — P1/P2 Concentric Impulse Quadrant** (`p1p2.py`):
- Sort into Q1–Q4 by total concentric impulse against YAML quartile thresholds
- Within quartile: compare P1 and P2 to quartile median → `low_p1` | `low_p2` | `balanced` | `low_bw`
- Attach training prescription text from a prescription lookup dict (keyed by `final_group + p1p2_quadrant`)

**Longitudinal flags** (computed against `athlete_baselines.baseline_mrsi`):
- **Consecutive test definition:** "2 consecutive tests" means the 2 most recent tests by `test_date` for that athlete, regardless of time gap between them. A gap > 21 days resets the consecutive-test counter to 1 (prevents stale comparisons from triggering false flags).
- Yellow: mRSI drop > 5% vs. baseline, present in both of the last 2 consecutive tests
- Orange: mRSI drop > 10% vs. baseline, present in both of the last 2 consecutive tests
- Red: mRSI drop > 15% vs. baseline, OR single-test drop > 10% vs. baseline
- Asymmetry Alert: current asymmetry > (baseline asymmetry + 5%)

---

### 5. Streamlit Dashboard (`src/report/dashboard.py`)

**Views:**

**A. Team Roster View**
- Sortable/filterable table: athlete name, position, group badge (color-coded), readiness flag dot, mRSI, Peak Power/BM, EDRFD/BM, Asymmetry%
- Click row → navigate to Individual Profile

**B. Individual Athlete Profile**
- Radar chart (Plotly `go.Scatterpolar`): percentile profile across metric clusters vs. team and normative benchmarks
- Phase Profile cards: Braking / Propulsive / Landing (Deficit → Adequate → Strength)
- Movement Strategy panel: Tier 3 metrics (depth, stiffness, timing ratios)
- Longitudinal trend: mRSI line chart (last 8 tests) with colored flag threshold bands
- Training prescription card: derived from `final_group` + `p1p2_quadrant`
- Clinical notes: asymmetry alerts, ECC flags, SSC depth flags

**C. Risk Cluster Panel** — CMJ-only metrics (v1 scope):
1. **Deceleration Deficit:** Low EDRFD/BM + Low Braking Net Impulse + High CM Depth
2. **Low Relative Power:** Peak Power/BM < P25 + mRSI < P25 + Conc. Impulse Q1
3. **ECC Deficit:** Ecc Peak Power/BM < P25 + EPF/BM < 2.0x + Asymmetry Braking Impulse > 10%
4. **SSC Coupling Deficit:** CM Depth > position threshold + Low LL Stiffness + Low FV0/BM

*Note: NordBord-dependent clusters (Nordic asymmetry, Calf ISO) are deferred to v2 when NordBord data is integrated.*

**Sidebar controls:** Date range picker, position group filter, show/hide White Group

---

### 6. PDF/HTML Report (`src/report/pdf_report.py`)

Triggered by `python run_pipeline.py --report`. Renders `templates/weekly_report.html` via Jinja2:

- **Executive summary:** team readiness distribution bar, count by group, # flagged
- **Risk alerts:** athletes in red/orange state with metric details
- **Athlete cards:** one per athlete — radar chart as PNG (Plotly `write_image` via `kaleido`), key metrics table (color-coded), prescription text
- **Trend movers:** athletes who changed group since previous week's report

Output: `reports/YYYY-MM-DD_football_cmj_report.pdf` + `.html`
(`reports/` directory is gitignored — contains athlete PII)

**PDF conversion:** `weasyprint` (actively maintained, pip-installable, no external binary required). Replaces `pdfkit`/`wkhtmltopdf`, which is EOL as of 2024.

**Chart image export:** Plotly `write_image()` via `kaleido`. Kaleido v1.x requires **Google Chrome or Chromium** installed on the machine (not bundled). This is a hard prerequisite for PDF chart rendering.

---

### 7. Configuration (`config/thresholds.yaml`)

Top-level keys:
- `target_metrics` — list of 42 VALD metric names to extract
- `position_map` — position abbreviation → position group (`skill` | `big`)
- `position_groups` — per-group thresholds (P25/P50/P75/elite) for all primary + secondary metrics
- `concentric_impulse_quartiles` — Q1/Q2/Q3/Q4 boundaries per position group
- `prescriptions` — lookup dict: `group.quadrant` → prescription text

**NFL/NCAA normative data is fully available** from `ContextBackgroundInfo/VALD Normative Data Report – 2024-25 NFL and NCAA Football Report.pdf`. The YAML will be seeded with football-specific norms at implementation time — no placeholder data. Position groups map directly to the 10 positions in the report (Defensive Back, Defensive Line, Linebacker, Offensive Line, Quarterback, Running Back, Tight End, Wide Receiver, Special Teams, Kicker/Punter).

**Available percentiles per position (NFL and NCAA):** P5, P25, Median (P50), P75, P95 for all CMJ metrics listed in the target_metrics list.

**Position group mapping for classification thresholds:**
- `skill` group: Defensive Back, Linebacker, Quarterback, Running Back, Wide Receiver, Tight End, Special Teams, Kicker/Punter
- `big` group: Defensive Line, Offensive Line

Each position uses its **own position-specific percentile column** from the normative report for classification — not a pooled "skill" or "big" average. The `position_groups` config key maps to individual position entries.

---

### 8. Pipeline Entry Point (`run_pipeline.py`)

```
Usage:
  python run_pipeline.py                          # pull + classify
  python run_pipeline.py --dry-run                # list teams/athletes, no DB writes
  python run_pipeline.py --report                 # pull + classify + generate PDF/HTML
  python run_pipeline.py --from-date YYYY-MM-DD   # override start date
  python run_pipeline.py --reset-baseline <id>    # manually reset one athlete's baseline
  python run_pipeline.py --reset-all-baselines    # reset all baselines (e.g. new season)
```

Steps:
1. Load `.env`
2. `--dry-run`: call `get_teams()` + `get_profiles()`, print summary, exit
3. Pull CMJ tests from Football team, `from_date=2026-01-01` (or CLI override)
4. Filter to 42 target metrics
5. Upsert into `raw_tests` (skip existing `(test_id, metric_name)` pairs)
6. Pivot long→wide per test_id
7. Run classification engine on all new tests
8. Upsert into `classified_athletes`
9. Set baseline for athletes appearing for the first time in `athlete_baselines`
10. Print: X athletes, Y new tests, Z flags
11. If `--report`: generate PDF/HTML to `reports/`

---

## Tech Stack

| Layer | Library | Notes |
|-------|---------|-------|
| API client | `requests` | Direct REST; no SDK |
| Auth token parsing | `PyJWT` | JWT `exp` claim check |
| Env config | `python-dotenv` | |
| Data store | `duckdb` | |
| Data wrangling | `pandas` | |
| Config | `pyyaml` | |
| Dashboard | `streamlit`, `plotly` | |
| PDF export | `jinja2`, `weasyprint` | weasyprint replaces EOL pdfkit/wkhtmltopdf |
| PDF chart images | `kaleido` | Requires Chrome/Chromium installed |

---

## Information Required at Implementation Start

**Hard prerequisites (system cannot run without these):**

1. **`.env` file** — `VALD_CLIENT_ID`, `VALD_CLIENT_SECRET`, `VALD_REGION_URL`, `VALD_TEAM_ID`
2. **Google Chrome or Chromium** — installed on Windows machine (required by Kaleido for chart image export in PDF)

**Available and ready to use:**

3. **NFL/NCAA normative data** — All P5/P25/P50/P75/P95 values for all 10 positions extracted from `ContextBackgroundInfo/VALD Normative Data Report – 2024-25 NFL and NCAA Football Report.pdf`. Will be seeded directly into `config/thresholds.yaml` at implementation time.

**Required before full accuracy (can run pipeline without, but classifications will be wrong):**

4. **Position field confirmation** — verify VALD athlete profile returns position field, or provide a CSV mapping `athlete_id → position`

---

## Verification Plan

1. `python run_pipeline.py --dry-run` → prints team name + athlete count (confirms auth + team ID)
2. Full pull → inspect `raw_tests` row count in DuckDB; verify 42 metrics present per test
3. Classification spot-check: manually verify 2–3 athlete classifications against threshold tables
4. `streamlit run src/report/dashboard.py` → Team Roster view renders, athlete drill-down loads
5. `python run_pipeline.py --report` → PDF opens correctly, radar chart PNGs render, athlete cards present

---

## Out of Scope (v1)

- Automated scheduling (Windows Task Scheduler setup)
- Multi-sport support (other programs beyond Football)
- Real-time VALD webhook integration
- User authentication on the Streamlit dashboard
- NordBord or ForceFrame data (CMJ only) — NordBord-dependent risk clusters deferred to v2

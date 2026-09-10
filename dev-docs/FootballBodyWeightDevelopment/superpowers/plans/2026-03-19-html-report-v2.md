# HTML Report v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `scripts/05_html_report_v2.py` that generates `output/report/weight_gain_analysis_report_v2.html` — a redesigned, self-contained Baylor-branded HTML report with a dashboard hero section, tabbed recommendation tables, embedded charts, and improved typography, without touching any original files.

**Architecture:** The new script mirrors the structure of `scripts/05_html_report.py` — modular section-builder functions assembled in `generate_html()`. New additions are a `build_hero()` function, a `build_css_v2()` replacing the CSS block, a `build_recommendation_tabs()` replacing `build_recommendation_tables()`, and inline JS for tab switching and expand/collapse. All images embedded as base64 data URIs via the existing `embed_image()` pattern.

**Tech Stack:** Python 3, pandas, base64 (stdlib), pathlib (stdlib). No new dependencies. Vanilla JS only (no libraries). Output is a single `.html` file.

**Spec:** `docs/superpowers/specs/2026-03-19-html-report-v2-design.md`

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Create | `scripts/05_html_report_v2.py` | New generator — all v2 HTML/CSS/JS |
| Output | `output/report/weight_gain_analysis_report_v2.html` | Generated file (not committed) |
| Read-only | `scripts/05_html_report.py` | Reference only — do not modify |
| Read-only | `scripts/config.py` | Source of `POSITION_ORDER`, `TIME_WINDOWS`, colors, paths |
| Read-only | `output/data/*.csv` | Data sources |
| Read-only | `output/charts/gain_distribution_by_position.png` | Embedded in hero |
| Read-only | `output/charts/gain_rate_diminishing_returns.png` | Embedded in diminishing returns |

---

## Task 1: Scaffold the new script with data loading and utilities

**Files:**
- Create: `scripts/05_html_report_v2.py`

- [ ] **Step 1.1: Create the file with imports, constants, and utility functions**

Copy the utility layer from `05_html_report.py` — these functions are unchanged in v2:

```python
"""
Step 5 (v2): HTML Report Generation — Redesigned
Self-contained Baylor-branded HTML report with dashboard hero, tabbed
recommendation tables, embedded charts, and improved typography.
Preserves all original files. Outputs weight_gain_analysis_report_v2.html.
"""

import base64
import pandas as pd
import numpy as np
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    PROJECT_ROOT, DATA_OUT_DIR, REPORT_DIR, POSITION_ORDER, TIME_WINDOWS,
    MIN_WEIGHINS, ROLLING_WINDOW_DAYS, MAX_GAP_DAYS, MIN_GAIN_LBS,
    MIN_GAIN_DURATION_DAYS, NOISE_THRESHOLD_LBS, MAX_RATE_LBS_PER_WEEK,
    BAYLOR_GREEN, BAYLOR_GOLD,
)

LOGO_PATH = PROJECT_ROOT / "Baylor Sport Lockups-Football.png"
CHART_GAIN_DIST = PROJECT_ROOT / "output" / "charts" / "gain_distribution_by_position.png"
CHART_DIM_RETURNS = PROJECT_ROOT / "output" / "charts" / "gain_rate_diminishing_returns.png"
OUTPUT_FILENAME = "weight_gain_analysis_report_v2.html"


def load_data():
    rec = pd.read_csv(DATA_OUT_DIR / "recommendation_table.csv")
    gain = pd.read_csv(DATA_OUT_DIR / "gain_periods.csv", parse_dates=["START_DATE", "END_DATE"])
    summary = pd.read_csv(DATA_OUT_DIR / "player_summary.csv")
    cleaned = pd.read_csv(DATA_OUT_DIR / "cleaned_data.csv", parse_dates=["DATE"])
    dim_path = DATA_OUT_DIR / "diminishing_returns.csv"
    dim = pd.read_csv(dim_path) if dim_path.exists() else pd.DataFrame()
    return rec, gain, summary, cleaned, dim


def embed_image(path):
    """Return base64 data URI for an image, or empty string if missing."""
    if not Path(path).exists():
        return ""
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def chart_html(path, caption, css_class="report-chart"):
    """Return <img> tag with base64 src, or .chart-missing placeholder."""
    uri = embed_image(path)
    if not uri:
        return f'<div class="chart-missing">Chart not available: {Path(path).name}</div>'
    return f'<img class="{css_class}" src="{uri}" alt="{caption}"><p class="chart-caption">{caption}</p>'


def window_label(w):
    labels = {
        30: "30 Days (~4 Weeks)",
        60: "60 Days (~8 Weeks)",
        90: "90 Days (~12 Weeks)",
        120: "120 Days (~16 Weeks)",
        180: "180 Days (~26 Weeks)",
        "offseason": "Offseason (Summer)",
        "annual": "Full Year",
    }
    return labels.get(w, str(w))


def window_tab_label(w):
    labels = {30: "30d", 60: "60d", 90: "90d", 120: "120d", 180: "180d",
              "offseason": "Offseason", "annual": "Annual"}
    return labels.get(w, str(w))


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
```

- [ ] **Step 1.2: Run the file to verify it imports cleanly**

```bash
cd "c:/Users/Eric_Rash/Desktop/DEV/Football/FootballBodyWeightDevelopment"
python scripts/05_html_report_v2.py
```

Since the file has no `main()` yet it will execute the module body (imports + function definitions) and exit. Expected: no output, no errors. If you see an `ImportError`, check that `scripts/config.py` exports the expected names (POSITION_ORDER, TIME_WINDOWS, BAYLOR_GREEN, BAYLOR_GOLD, DATA_OUT_DIR, REPORT_DIR, PROJECT_ROOT).

---

## Task 2: Build the CSS block

**Files:**
- Modify: `scripts/05_html_report_v2.py`

- [ ] **Step 2.1: Add `build_css_v2()` after the utility functions**

```python
def build_css_v2():
    return f"""
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            color: #333;
            background: #fff;
            line-height: 1.6;
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 20px 40px 20px;
            font-size: 15px;
        }}

        /* ── Header ── */
        .header {{
            background: #fff;
            text-align: center;
            padding: 36px 20px 20px 20px;
            border-bottom: 4px solid {BAYLOR_GOLD};
        }}
        .header img.logo {{
            max-width: 340px;
            height: auto;
            margin-bottom: 16px;
        }}
        .header h1 {{
            color: {BAYLOR_GREEN};
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 13px;
        }}

        /* ── Hero ── */
        .hero {{
            margin: 28px 0 0 0;
            padding-bottom: 28px;
            border-bottom: 2px solid {BAYLOR_GOLD};
        }}
        .hero-cards {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 22px;
        }}
        .hero-card {{
            background: #fff;
            border: 1px solid #e0e0e0;
            border-top: 4px solid {BAYLOR_GREEN};
            border-radius: 4px;
            padding: 16px 12px;
            text-align: center;
        }}
        .hero-card.gold-accent {{
            border-top-color: {BAYLOR_GOLD};
        }}
        .hero-card .card-value {{
            font-size: 26px;
            font-weight: 700;
            color: {BAYLOR_GREEN};
            line-height: 1.2;
        }}
        .hero-card .card-label {{
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }}
        .report-chart {{
            width: 100%;
            max-width: 100%;
            height: auto;
            display: block;
            border-radius: 4px;
        }}
        .chart-caption {{
            font-size: 12px;
            color: #888;
            text-align: center;
            margin-top: 6px;
            font-style: italic;
        }}
        .chart-missing {{
            background: #f5f5f5;
            border: 1px dashed #ccc;
            color: #999;
            text-align: center;
            padding: 24px;
            border-radius: 4px;
            font-size: 13px;
        }}

        /* ── Section headings ── */
        h2 {{
            color: {BAYLOR_GREEN};
            font-size: 20px;
            margin: 36px 0 12px 0;
            padding-bottom: 6px;
            border-bottom: 2px solid {BAYLOR_GOLD};
        }}
        h3 {{
            color: {BAYLOR_GREEN};
            font-size: 16px;
            margin: 24px 0 8px 0;
        }}

        /* ── Callout boxes ── */
        .callout {{
            background: #fffbee;
            border: 1px solid {BAYLOR_GOLD};
            padding: 14px 18px;
            margin: 16px 0;
            border-radius: 4px;
        }}
        .callout strong {{ color: {BAYLOR_GREEN}; }}

        .callout-green {{
            background: #f0f7f3;
            border: 1px solid {BAYLOR_GREEN};
            padding: 14px 18px;
            margin: 16px 0;
            border-radius: 4px;
        }}
        .warning {{
            background: #fffbee;
            border: 1px solid {BAYLOR_GOLD};
            padding: 10px 14px;
            margin: 8px 0;
            font-size: 13px;
            border-radius: 4px;
        }}
        .warning strong {{ color: #b07d00; }}

        /* ── Tables ── */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0 20px 0;
            font-size: 14px;
        }}
        thead th {{
            background: {BAYLOR_GREEN};
            color: #fff;
            font-weight: 600;
            padding: 10px 12px;
            text-align: center;
            border: 1px solid {BAYLOR_GREEN};
        }}
        thead th:first-child {{ text-align: left; }}
        tbody td {{
            padding: 8px 12px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        tbody td:first-child {{
            text-align: left;
            font-weight: 600;
            color: {BAYLOR_GREEN};
        }}
        tbody tr:nth-child(even) {{ background: #f8f9f5; }}
        tbody tr:hover {{ background: #eef5e8; }}
        .small-n {{ color: #b07d00; font-weight: bold; }}

        /* ── Tabs ── */
        .tab-bar {{
            display: flex;
            gap: 0;
            border-bottom: 2px solid #e0e0e0;
            position: sticky;
            top: 0;
            z-index: 100;
            background: #fff;
            padding-top: 8px;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            font-family: inherit;
            color: #555;
            font-weight: 500;
            margin-bottom: -2px;
            white-space: nowrap;
        }}
        .tab-btn:hover {{ color: {BAYLOR_GREEN}; background: #f8f9f5; }}
        .tab-btn.active {{
            color: {BAYLOR_GREEN};
            font-weight: 700;
            border-bottom-color: {BAYLOR_GOLD};
        }}
        .tab-btn:disabled {{
            color: #bbb;
            cursor: not-allowed;
        }}
        .tab-panel {{ display: none; padding-top: 8px; }}
        .tab-panel.active {{ display: block; }}

        /* ── Details/Summary ── */
        details {{
            margin: 10px 0;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            overflow: hidden;
        }}
        details[open] {{
            border-left: 3px solid {BAYLOR_GOLD};
        }}
        summary {{
            background: #f8f9f5;
            padding: 12px 16px;
            cursor: pointer;
            font-weight: 600;
            color: {BAYLOR_GREEN};
            font-size: 16px;
        }}
        summary:hover {{ background: #eef5e8; }}
        details .detail-body {{ padding: 12px 16px; }}

        /* ── Expand/Collapse button ── */
        .expand-btn {{
            background: none;
            border: 1px solid {BAYLOR_GREEN};
            color: {BAYLOR_GREEN};
            padding: 6px 14px;
            border-radius: 4px;
            font-size: 13px;
            cursor: pointer;
            font-family: inherit;
            margin-bottom: 12px;
        }}
        .expand-btn:hover {{ background: #eef5e8; }}

        /* ── Trend indicators ── */
        .trend-down {{ color: {BAYLOR_GREEN}; font-weight: 600; }}
        .trend-up {{ color: #c0392b; font-weight: 600; }}

        /* ── Overview grid (Data Overview section) ── */
        .overview-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin: 16px 0;
        }}
        .overview-card {{
            background: #f8f9f5;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        .overview-card .number {{
            font-size: 28px;
            font-weight: 700;
            color: {BAYLOR_GREEN};
        }}
        .overview-card .label {{
            font-size: 12px;
            color: #666;
            margin-top: 2px;
        }}

        /* ── How-to steps ── */
        .howto-step {{
            display: flex;
            align-items: flex-start;
            margin: 12px 0;
        }}
        .step-number {{
            background: {BAYLOR_GREEN};
            color: #fff;
            font-weight: 700;
            min-width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 14px;
            flex-shrink: 0;
            font-size: 15px;
        }}
        .step-text {{ padding-top: 6px; }}

        /* ── Lists ── */
        ul, ol {{ padding-left: 24px; margin: 8px 0; }}
        li {{ margin: 4px 0; }}

        /* ── Footer ── */
        .footer {{
            margin-top: 40px;
            padding-top: 16px;
            border-top: 2px solid {BAYLOR_GREEN};
            text-align: center;
            font-size: 11px;
            color: #999;
        }}

        /* ── Print ── */
        @media print {{
            body {{ max-width: 100%; padding: 0 10px; font-size: 13px; }}
            .tab-bar {{ display: none !important; }}
            .tab-panel {{ display: block !important; }}
            .tab-panel + .tab-panel {{ page-break-before: always; }}
            .tab-panel-heading {{ display: block !important; }}
            details {{ open; border-left: none; }}
            .expand-btn {{ display: none; }}
            .no-print {{ display: none; }}
            table {{ page-break-inside: avoid; font-size: 11px; }}
        }}
    </style>
"""
```

---

## Task 3: Build the header and hero sections

**Files:**
- Modify: `scripts/05_html_report_v2.py`

- [ ] **Step 3.1: Add `build_header_v2()` — logo, title, gold border**

```python
def build_header_v2(cleaned):
    date_min = cleaned["DATE"].min().strftime("%B %d, %Y")
    date_max = cleaned["DATE"].max().strftime("%B %d, %Y")
    logo_html = ""
    if LOGO_PATH.exists():
        logo_uri = embed_image(LOGO_PATH)
        logo_html = f'<img class="logo" src="{logo_uri}" alt="Baylor Football">'
    return f"""
    <div class="header">
        {logo_html}
        <h1>Weight Gain Analysis Report</h1>
        <div class="subtitle">Data-Driven Bodyweight Expectations by Position &nbsp;|&nbsp; {date_min} – {date_max}</div>
    </div>
"""
```

- [ ] **Step 3.2: Add `build_hero()` — 4 metric cards + gain distribution chart**

```python
def build_hero(summary, cleaned):
    n_players = len(summary[summary["ELIGIBLE"]]) if "ELIGIBLE" in summary.columns else len(summary)
    n_weighins = len(cleaned)
    date_min = cleaned["DATE"].min().strftime("%b %Y")
    date_max = cleaned["DATE"].max().strftime("%b %Y")
    n_positions = len(POSITION_ORDER)

    chart = chart_html(
        CHART_GAIN_DIST,
        "Weight Gain Distribution by Position Group (lbs gained per period)",
    )

    return f"""
    <div class="hero">
        <div class="hero-cards">
            <div class="hero-card">
                <div class="card-value">{n_players:,}</div>
                <div class="card-label">Players Analyzed</div>
            </div>
            <div class="hero-card">
                <div class="card-value">{n_weighins:,}</div>
                <div class="card-label">Total Weigh-ins</div>
            </div>
            <div class="hero-card">
                <div class="card-value" style="font-size:18px;">{date_min}–{date_max}</div>
                <div class="card-label">Date Range</div>
            </div>
            <div class="hero-card gold-accent">
                <div class="card-value">{n_positions}</div>
                <div class="card-label">Position Groups</div>
            </div>
        </div>
        {chart}
    </div>
"""
```

---

## Task 4: Build the tabbed recommendation tables

**Files:**
- Modify: `scripts/05_html_report_v2.py`

This is the largest change. The 7 stacked tables become a tabbed interface with one table per tab. The 90-day tab is active by default.

- [ ] **Step 4.1: Add `build_recommendation_tabs(rec)`**

```python
def build_recommendation_tabs(rec):
    all_windows = list(TIME_WINDOWS) + ["offseason", "annual"]

    # Build tab buttons
    tab_buttons = ""
    for w in all_windows:
        w_str = str(w)
        subset = rec[rec["WINDOW"] == w_str]
        label = window_tab_label(w)
        star = " &#9733;" if w == 90 else ""
        if subset.empty:
            tab_buttons += f'<button class="tab-btn" disabled title="No data available">{label}{star}</button>'
        else:
            active = ' active' if w == 90 else ''
            tab_buttons += f'<button class="tab-btn{active}" onclick="showTab(\'{w_str}\')" id="tab-btn-{w_str}">{label}{star}</button>'

    # Build tab panels
    tab_panels = ""
    for w in all_windows:
        w_str = str(w)
        subset = rec[rec["WINDOW"] == w_str]
        if subset.empty:
            continue

        label = window_label(w)
        active = ' active' if w == 90 else ''

        rows_html = ""
        has_small_n = False
        for pos in POSITION_ORDER:
            row = subset[subset["POS_GROUP"] == pos]
            if row.empty:
                continue
            r = row.iloc[0]
            n_val = int(r["N_GAINERS"])
            small_n = ""
            if n_val < 15:
                small_n = ' <span class="small-n">*</span>'
                has_small_n = True
            rows_html += f"""
                <tr>
                    <td>{pos}</td>
                    <td>{r['REALISTIC_LBS']:.1f}</td>
                    <td>{r['AGGRESSIVE_LBS']:.1f}</td>
                    <td>{r['EXCEPTIONAL_LBS']:.1f}</td>
                    <td>{r['PCT_GAINING']:.0f}%</td>
                    <td>{n_val}{small_n}</td>
                </tr>"""

        footnote = ""
        if has_small_n:
            footnote = '<div class="callout" style="margin-top:8px;font-size:13px;"><span class="small-n">*</span> Small sample size (N &lt; 15). Interpret with caution.</div>'

        tab_panels += f"""
        <div class="tab-panel{active}" id="tab-{w_str}">
            <h3 class="tab-panel-heading" style="display:none;">{label}</h3>
            <p style="color:#666; font-size:13px; margin-bottom:12px;">
                All values in pounds (lbs). Tiers are computed among players who gained weight in this window.
                N = number of positive-gain observations.
            </p>
            <table>
                <thead>
                    <tr>
                        <th>Position</th>
                        <th>Realistic<br><span style="font-weight:normal;font-size:11px;">(50th %ile)</span></th>
                        <th>Aggressive<br><span style="font-weight:normal;font-size:11px;">(75th %ile)</span></th>
                        <th>Exceptional<br><span style="font-weight:normal;font-size:11px;">(90th %ile)</span></th>
                        <th>% Gaining</th>
                        <th>N</th>
                    </tr>
                </thead>
                <tbody>{rows_html}
                </tbody>
            </table>
            {footnote}
        </div>"""

    return f"""
    <h2>Weight Gain Expectations by Position &amp; Time Window</h2>
    <div class="tab-bar">{tab_buttons}</div>
    {tab_panels}
"""
```

---

## Task 5: Build the key findings section with Expand All button

**Files:**
- Modify: `scripts/05_html_report_v2.py`

- [ ] **Step 5.1: Add `build_key_findings_v2(rec, gain)`**

Copy `build_key_findings` from v1 and add the expand/collapse button:

```python
def build_key_findings_v2(rec, gain):
    html = """
    <h2>Key Findings by Position Group</h2>
    <button class="expand-btn no-print" onclick="toggleAll()">Expand All</button>
    <div id="findings-container">
"""

    for pos in POSITION_ORDER:
        pos_gains = gain[gain["POS_GROUP"] == pos]
        pos_rec_90 = rec[(rec["POS_GROUP"] == pos) & (rec["WINDOW"] == "90")]
        pos_rec_180 = rec[(rec["POS_GROUP"] == pos) & (rec["WINDOW"] == "180")]

        if pos_gains.empty:
            continue

        median_gain = pos_gains["TOTAL_GAIN_LBS"].median()
        p90_gain = pos_gains["TOTAL_GAIN_LBS"].quantile(0.90)
        median_duration = pos_gains["DURATION_DAYS"].median()
        median_rate = pos_gains["GAIN_PER_WEEK"].median()
        n_periods = len(pos_gains)
        n_players = pos_gains["NAME"].nunique()

        bullets = f"""
            <li><strong>{n_periods} gain periods</strong> detected across <strong>{n_players} players</strong></li>
            <li>Median gain per period: <strong>{median_gain:.1f} lbs</strong> over
                <strong>{median_duration:.0f} days</strong> ({median_rate:.1f} lbs/week)</li>
            <li>90th percentile gain: <strong>{p90_gain:.1f} lbs</strong> per period</li>
"""
        if not pos_rec_90.empty:
            r90 = pos_rec_90.iloc[0]
            bullets += f"""
            <li>In 90 days: typical gainer adds <strong>{r90['REALISTIC_LBS']:.1f} lbs</strong>,
                aggressive target is <strong>{r90['AGGRESSIVE_LBS']:.1f} lbs</strong></li>"""
        if not pos_rec_180.empty:
            r180 = pos_rec_180.iloc[0]
            bullets += f"""
            <li>In 180 days: typical gainer adds <strong>{r180['REALISTIC_LBS']:.1f} lbs</strong>,
                aggressive target is <strong>{r180['AGGRESSIVE_LBS']:.1f} lbs</strong></li>"""

        big_gains = pos_gains[pos_gains["TOTAL_GAIN_LBS"] >= 10]
        pct_big = 100 * len(big_gains) / n_periods if n_periods > 0 else 0
        if pct_big < 5:
            bullets += f"""
            <li style="color:#b07d00;"><strong>&#9888; 10+ lb gains are rare</strong> — only {len(big_gains)}
                of {n_periods} gain periods ({pct_big:.1f}%) reached 10 lbs"""
            if len(big_gains) > 0:
                bullets += f" (median duration: {big_gains['DURATION_DAYS'].median():.0f} days)"
            bullets += "</li>"
        elif len(big_gains) > 0:
            med_dur = big_gains["DURATION_DAYS"].median()
            bullets += f"""
            <li>10+ lb gains: {len(big_gains)} instances ({pct_big:.0f}% of periods),
                median duration <strong>{med_dur:.0f} days</strong></li>"""

        html += f"""
        <details>
            <summary>{pos}</summary>
            <div class="detail-body">
                <ul>{bullets}
                </ul>
            </div>
        </details>"""

    html += "\n    </div>"
    return html
```

---

## Task 6: Build the diminishing returns section with chart

**Files:**
- Modify: `scripts/05_html_report_v2.py`

- [ ] **Step 6.1: Add `build_diminishing_returns_v2(dim)`**

Based on v1 but adds the chart above the table and uses labeled trend spans:

```python
def build_diminishing_returns_v2(dim):
    chart = chart_html(
        CHART_DIM_RETURNS,
        "Gain Rate: First 30 Days vs. Next 30 Days by Position Group (lbs/week)",
    )

    if dim.empty:
        return f"""
    <h2>Diminishing Returns: Do Gains Slow Down?</h2>
    {chart}
    <p><em>Insufficient data for analysis.</em></p>
"""

    dim_agg = dim.groupby("POS_GROUP").agg(
        first_30=("GAIN_RATE_FIRST_30", "median"),
        next_30=("GAIN_RATE_NEXT_30", "median"),
        n=("GAIN_RATE_FIRST_30", "count"),
    ).reindex([p for p in POSITION_ORDER if p in dim["POS_GROUP"].values])
    dim_agg = dim_agg.dropna()

    rows_html = ""
    for pos, row in dim_agg.iterrows():
        change_pct = ((row["next_30"] - row["first_30"]) / row["first_30"] * 100
                      if row["first_30"] != 0 else 0)
        if row["next_30"] < row["first_30"]:
            direction = f'<span class="trend-down">&#8595; Slowing ({abs(change_pct):.0f}%)</span>'
        else:
            direction = f'<span class="trend-up">&#8593; Accelerating ({abs(change_pct):.0f}%)</span>'

        rows_html += f"""
            <tr>
                <td>{pos}</td>
                <td>{row['first_30']:.2f}</td>
                <td>{row['next_30']:.2f}</td>
                <td>{direction}</td>
                <td>{int(row['n'])}</td>
            </tr>"""

    small_n_note = '<div class="callout" style="font-size:13px;margin-top:8px;"><span class="small-n">*</span> Positions with N &lt; 15 gain periods should be interpreted with caution — small samples produce less stable rate estimates.</div>'

    return f"""
    <h2>Diminishing Returns: Do Gains Slow Down?</h2>
    {chart}
    <p style="font-size:13px; color:#666; margin-bottom:12px;">
        For gain periods lasting 60+ days, gain rates in the first 30 days vs. the next 30 days.
        <span class="trend-down">Green = slowing (expected/healthy)</span> &nbsp;|&nbsp;
        <span class="trend-up">Red = accelerating (flag for review)</span>
    </p>
    <table>
        <thead>
            <tr>
                <th>Position</th>
                <th>First 30 Days<br>(lbs/wk)</th>
                <th>Next 30 Days<br>(lbs/wk)</th>
                <th>Change</th>
                <th>N</th>
            </tr>
        </thead>
        <tbody>{rows_html}
        </tbody>
    </table>
    {small_n_note}
    <div class="callout">
        <strong>Interpretation:</strong> Across nearly all position groups, the rate of gain slows
        substantially after the first month. Coaches should expect the most visible progress
        in the first 4 weeks, with a natural plateau afterward — <em>this does not mean the player
        has stopped working</em>.
    </div>
"""
```

---

## Task 7: Copy remaining sections unchanged, add JS, assemble and run

**Files:**
- Modify: `scripts/05_html_report_v2.py`

These sections are structurally identical to v1 — copy them verbatim from `05_html_report.py`:
- `build_executive_summary(summary, cleaned)` — no changes needed
- `build_data_overview(summary, cleaned, gain)` — no changes needed
- `build_methodology_summary()` — no changes needed
- `build_howto()` — step badge size is handled by CSS (36px in v2 CSS); no Python changes needed
- `build_footer()` — no changes needed
- `build_rare_gains(gain)` — no changes needed (callout style handled by updated CSS)

- [ ] **Step 7.1: Copy the 6 unchanged section-builder functions from v1**

Copy these functions as-is from `scripts/05_html_report.py`:
- `build_executive_summary`
- `build_data_overview`
- `build_methodology_summary`
- `build_howto`
- `build_footer`
- `build_rare_gains`

- [ ] **Step 7.2: Add `build_js()` — tab switching, expand/collapse, and print handling**

Note: `<details>` elements cannot be opened via CSS. A `window.onbeforeprint` handler opens them all
before printing and restores state after.

```python
def build_js():
    return """
    <script>
    function showTab(windowKey) {
        document.querySelectorAll('.tab-btn').forEach(function(btn) {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.tab-panel').forEach(function(panel) {
            panel.classList.remove('active');
        });
        var btn = document.getElementById('tab-btn-' + windowKey);
        var panel = document.getElementById('tab-' + windowKey);
        if (btn) btn.classList.add('active');
        if (panel) panel.classList.add('active');
    }

    function toggleAll() {
        var container = document.getElementById('findings-container');
        var details = container.querySelectorAll('details');
        var btn = document.querySelector('.expand-btn');
        var anyOpen = false;
        details.forEach(function(d) { if (!d.open) anyOpen = true; });
        details.forEach(function(d) { d.open = anyOpen; });
        btn.textContent = anyOpen ? 'Collapse All' : 'Expand All';
    }

    // For print: open all details, restore state after
    var _detailsStateBeforePrint = [];
    window.onbeforeprint = function() {
        _detailsStateBeforePrint = [];
        document.querySelectorAll('details').forEach(function(d) {
            _detailsStateBeforePrint.push(d.open);
            d.open = true;
        });
    };
    window.onafterprint = function() {
        document.querySelectorAll('details').forEach(function(d, i) {
            d.open = _detailsStateBeforePrint[i] || false;
        });
    };

    document.addEventListener('DOMContentLoaded', function() {
        showTab('90');
    });
    </script>
"""
```

- [ ] **Step 7.3: Add `generate_html_v2()` and `main()`**

```python
def generate_html_v2(rec, gain, summary, cleaned, dim):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baylor Football — Weight Gain Analysis Report v2</title>
    {build_css_v2()}
</head>
<body>
    {build_header_v2(cleaned)}
    {build_hero(summary, cleaned)}
    {build_executive_summary(summary, cleaned)}
    {build_data_overview(summary, cleaned, gain)}
    {build_howto()}
    {build_methodology_summary()}
    {build_recommendation_tabs(rec)}
    {build_key_findings_v2(rec, gain)}
    {build_diminishing_returns_v2(dim)}
    {build_rare_gains(gain)}
    {build_footer()}
    {build_js()}
</body>
</html>"""


def main():
    print("Step 5 (v2): HTML Report Generation\n")
    rec, gain, summary, cleaned, dim = load_data()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    print("Building HTML report v2...")
    html = generate_html_v2(rec, gain, summary, cleaned, dim)
    out_path = REPORT_DIR / OUTPUT_FILENAME
    out_path.write_text(html, encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024
    print(f"  Saved {out_path.name} ({size_kb:.0f} KB)")
    print(f"  Logo embedded: {'Yes' if LOGO_PATH.exists() else 'No'}")
    print(f"  Gain dist chart: {'Yes' if CHART_GAIN_DIST.exists() else 'Missing — placeholder rendered'}")
    print(f"  Dim returns chart: {'Yes' if CHART_DIM_RETURNS.exists() else 'Missing — placeholder rendered'}")
    print("\nDone. Open output/report/weight_gain_analysis_report_v2.html in a browser.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 7.4: Run the script**

```bash
cd "c:/Users/Eric_Rash/Desktop/DEV/Football/FootballBodyWeightDevelopment"
python scripts/05_html_report_v2.py
```

Expected output:
```
Step 5 (v2): HTML Report Generation

Building HTML report v2...
  Saved weight_gain_analysis_report_v2.html (XXXX KB)
  Logo embedded: Yes
  Gain dist chart: Yes
  Dim returns chart: Yes

Done. Open output/report/weight_gain_analysis_report_v2.html in a browser.
```

If you see a Python error, read the traceback — the most likely issues are a missing import or a mismatched function argument count.

---

## Task 8: Verify in browser

**Files:**
- Read: `output/report/weight_gain_analysis_report_v2.html`

- [ ] **Step 8.1: Open the report**

Open `output/report/weight_gain_analysis_report_v2.html` in a browser. Run through each verification check from the spec:

1. **Hero:** 4 metric cards visible; gain distribution chart renders below them
2. **Tabs:** Click all 7 tabs — correct table appears for each; 90-day tab is active by default with ★
3. **Sticky tab bar:** Scroll down — tab bar sticks to top of viewport
4. **Expand All:** Click the button — all 11 position details open; button changes to "Collapse All"; click again — all close
5. **Diminishing returns:** Chart renders above table; trend column shows "↓ Slowing" / "↑ Accelerating" text labels
6. **Print preview:** Tab bar hidden; all 7 tables visible as stacked sections

- [ ] **Step 8.2: Verify original report is unchanged**

```bash
cd "c:/Users/Eric_Rash/Desktop/DEV/Football/FootballBodyWeightDevelopment"
python -c "import hashlib; print(hashlib.md5(open('output/report/weight_gain_analysis_report.html','rb').read()).hexdigest())"
```

Record the hash. Re-run v2 script again. Re-run hash command. The two hashes must be identical.

- [ ] **Step 8.3: Test missing chart fallback**

```bash
# Temporarily rename the gain distribution chart
mv output/charts/gain_distribution_by_position.png output/charts/gain_distribution_by_position.png.bak
python scripts/05_html_report_v2.py
```

Open the regenerated report — hero should show "Chart not available" placeholder. Then restore:

```bash
mv output/charts/gain_distribution_by_position.png.bak output/charts/gain_distribution_by_position.png
```

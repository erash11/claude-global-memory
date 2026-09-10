# HTML Report v2 Design Spec

**Date:** 2026-03-19
**Project:** Baylor Football Body Weight Development
**Author:** Brainstorming session with Eric Rash

---

## Context

The current `weight_gain_analysis_report.html` is functionally complete but has several design weaknesses: no hero/dashboard section, 7 recommendation tables stacked vertically (hard to navigate), no embedded charts, limited typography, and a dated 960px max-width layout. The goal of v2 is to improve usability for a mixed audience of coaches (quick scan) and sports science/dietitian staff (deep reference), while retaining full Baylor branding and keeping the file self-contained for email distribution.

The original report and generator script are preserved. A new script `scripts/05_html_report_v2.py` outputs `output/report/weight_gain_analysis_report_v2.html`.

---

## Prerequisites

All pipeline steps 01–04 must have been run successfully before running `05_html_report_v2.py`.

**Required data files** (all in `output/data/`):
- `recommendation_table.csv` — columns: POS_GROUP, WINDOW, N_TOTAL, N_GAINERS, PCT_GAINING, REALISTIC_LBS, AGGRESSIVE_LBS, EXCEPTIONAL_LBS, NOTE — used in tabbed recommendation tables
- `gain_periods.csv` — columns: NAME, POS_GROUP, START_DATE, END_DATE, DURATION_DAYS, START_WEIGHT, END_WEIGHT, TOTAL_GAIN_LBS, GAIN_PER_WEEK — used in Data Overview, Key Findings, and Rare Gains sections
- `player_summary.csv` — used for hero card "Players Analyzed" count
- `cleaned_data.csv` — used for hero card "Total Weigh-ins" count and "Date Range" min/max
- `diminishing_returns.csv` — columns: NAME, POS_GROUP, GAIN_RATE_FIRST_30, GAIN_RATE_NEXT_30 — used in Diminishing Returns section

Note: `position_group_stats.csv` exists in `output/data/` but is not used in the v2 report (it was loaded but unused in v1 as well). Do not load it.

**Required chart files** (in `output/charts/`):
- `gain_distribution_by_position.png` (used in hero)
- `gain_rate_diminishing_returns.png` (used in diminishing returns section)

If a required chart file is missing, render a styled placeholder `<div class="chart-missing">Chart not available</div>` in its place rather than a broken `<img>` tag.

---

## Design Direction

**Hybrid — Dashboard Hero + Detail Sections**
Bold summary stats and key charts at the top, followed by clean detail sections. Coaches get an immediate read; staff can scroll into full depth.

---

## Page Structure

### 1. Baylor Header
- Unchanged: base64-embedded logo, report title, date range subtitle
- Slightly increased padding; 4px `#FFB81C` (gold) bottom border, replacing the current green border

### 2. Hero Section

Four metric cards in a single row. All values are **computed at report-generation time** from data files — never hardcoded:

| Card | Source | Accent |
|---|---|---|
| Players Analyzed | `len(player_summary_df)` | `#154734` green top-border |
| Total Weigh-ins | `len(cleaned_data_df)` | `#154734` green top-border |
| Date Range | `min(DATE)` – `max(DATE)` from `cleaned_data_df`, formatted as "Mon YYYY–Mon YYYY" | `#154734` green top-border |
| Position Groups | `len(POSITION_ORDER)` from `config.py` | `#FFB81C` gold top-border |

Below the cards: the **Gain Distribution by Position** chart (`output/charts/gain_distribution_by_position.png`) embedded as a base64 `<img>`, full-width with `max-width: 100%`, with a caption below it. If the chart file is missing, render the `.chart-missing` placeholder instead.

A 2px `#FFB81C` gold separator line appears below the entire hero section.

### 3. How to Use This Report
Kept structurally unchanged. Improved visual: larger step badges (36px diameter), slightly more whitespace (padding increased from 12px to 16px per step).

### 4. Weight Gain Expectations — Tabbed Interface

Tab bar with 7 tabs corresponding to all WINDOW values in `recommendation_table.csv`:

| Tab label | WINDOW value in CSV |
|---|---|
| 30d | `30` |
| 60d | `60` |
| 90d ★ | `90` (default active) |
| 120d | `120` |
| 180d | `180` |
| Offseason | `offseason` |
| Annual | `annual` |

**Tab bar behavior:**
- `position: sticky; top: 0; z-index: 100` — stays visible when scrolling the table below
- The Baylor header does **not** use `position: sticky` (it scrolls away), so `top: 0` is correct for the tab bar with no additional offset needed
- Active tab has a 3px `#FFB81C` gold bottom underline and bold text
- The 90-day tab renders a gold `★` star glyph after the label
- Inactive tab panels are hidden via `display: none`; active panel is `display: block`

**Tab switching (vanilla JS):**
```
function showTab(windowKey) {
  // hide all panels, deactivate all tabs
  // show panel matching windowKey, activate its tab button
}
// On DOMContentLoaded: showTab('90')
```

**Same table columns as current:** Position | Realistic (50th %ile) | Aggressive (75th %ile) | Exceptional (90th %ile) | % Gaining | N

**If a tab's data is missing** from the CSV (no rows for that WINDOW value): render the tab button as disabled (greyed out, no click handler) with a tooltip "No data available."

**Print styles (`@media print`):**
- Tab bar: `display: none`
- All tab panels: `display: block` (stacked tables)
- Each panel preceded by an `<h3>` heading showing the window label
- `page-break-before: always` on each panel after the first

### 5. Key Findings by Position Group
- 11 collapsible `<details>` sections (one per position group), unchanged data
- Styling improvements: `<summary>` font-size 16px, gold `3px solid #FFB81C` left-border when `<details>` is in `[open]` state
- **"Expand All / Collapse All" toggle button** above the section
  - Default label: **"Expand All"** (sections start collapsed)
  - Click behavior: if **any** section is currently closed (including partial-open state where the user has manually opened some) → open all and set label to "Collapse All"; if **all** are open → close all and set label to "Expand All". The check is: `if any details.open === false → open all; else → close all`.
  - Implemented in vanilla JS; no external dependencies

### 6. Diminishing Returns
- **Diminishing returns chart** (`output/charts/gain_rate_diminishing_returns.png`) embedded as base64 above the table, full-width with caption. Missing-chart fallback applies.
- Table unchanged in data; direction is computed per row: if `GAIN_RATE_NEXT_30 < GAIN_RATE_FIRST_30` → render `<span class="trend-down">↓ Slowing</span>`; otherwise → `<span class="trend-up">↑ Accelerating</span>`. Color mapping: `.trend-down` = `#154734` green (slowing is the expected/healthy outcome); `.trend-up` = `#c0392b` red (unexpectedly high late rate is a flag). Note: green = slowing is intentional — do not reverse the color assignment.
- Small-N asterisk footnote displayed in a full-card callout box (not inline text)

### 7. Positions Where 10+ lb Gains Are Rare
- Unchanged data and logic
- Callout box styling upgraded: border on all 4 sides (1px `#FFB81C`), background `#fffbee`, replacing left-border-only style

### 8. Footer
- Unchanged: generation timestamp, Baylor attribution

---

## Visual Design Changes

| Element | Current | v2 |
|---|---|---|
| Max-width | 960px | 1100px |
| Font stack | Segoe UI / Tahoma | `'Inter', 'Segoe UI', system-ui, sans-serif` |
| Body font size | 14px | 15px |
| Table font size | 13px | 14px |
| Header border | 4px `#154734` green bottom | 4px `#FFB81C` gold bottom |
| Hero | None | 4-card grid + computed metrics + chart |
| Recommendation nav | 7 stacked accordions | Sticky tabbed interface |
| Charts embedded | None | 2 (hero + diminishing returns section) |
| Chart fallback | Broken `<img>` | `.chart-missing` placeholder div |
| Expand all button | None | Added above position findings |
| Callout boxes | Left-border only | Full card (all 4 borders) |
| Print styles | Basic | Tab bar hidden; all panels stacked; page-breaks between tables |

---

## Constraints

- **Fully self-contained HTML** — no CDN, no external fonts, no external assets. `'Inter'` is included in the font stack as a preference for systems that have it installed, but it is not embedded — it will silently fall back to Segoe UI or system-ui on machines without Inter. No web font embedding is needed or expected.
- All images embedded as base64 data URIs (reuse `embed_image()` pattern from `05_html_report.py`)
- No external JS libraries — vanilla JS only
- Email-distributable (single `.html` file)
- Baylor brand colors: `#154734` (green), `#FFB81C` (gold) — unchanged from config
- Original files untouched:
  - `scripts/05_html_report.py` → preserved as-is
  - `output/report/weight_gain_analysis_report.html` → preserved as-is
- New files created:
  - `scripts/05_html_report_v2.py`
  - `output/report/weight_gain_analysis_report_v2.html`

---

## Verification

1. Run `python scripts/05_html_report_v2.py` — should complete without errors
2. Open `output/report/weight_gain_analysis_report_v2.html` in a browser
3. **Hero:** Confirm 4 metric cards show values derived from data (not hardcoded); confirm gain distribution chart renders
4. **Tabs:** Click each of the 7 tabs — confirm the correct table loads; confirm 90-day tab is active by default with `★` indicator
5. **Sticky tab bar:** Scroll down past the hero — confirm tab bar sticks to top of viewport
6. **Expand All:** Click "Expand All" in Key Findings — confirm all 11 position `<details>` open and button label changes to "Collapse All"; click again — all close
7. **Diminishing returns:** Confirm chart renders above the table; confirm trend labels read "↓ Slowing" / "↑ Accelerating" with text (not symbol alone)
8. **Print preview:** Confirm tab bar is hidden, all 7 tables are visible as stacked sections with headings
9. **Original preserved:** Confirm `output/report/weight_gain_analysis_report.html` is unchanged — run `python -c "import hashlib; print(hashlib.md5(open('output/report/weight_gain_analysis_report.html','rb').read()).hexdigest())"` before and after running the v2 script; the hash must be identical
10. **Missing chart fallback:** Temporarily rename a chart PNG, re-run script — confirm `.chart-missing` placeholder renders instead of broken image

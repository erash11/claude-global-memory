# Session Context — 2026-03-31

## Current State

V3 CMJ Hybrid Dashboard complete. 5-tab layout with SSC/plyo staging, phase composite bars, microcycle prescriptions, physio flags with localStorage notes, and a persistent squad-wide summary stats bar.

**Tests:** 120 total (unchanged — all passing)

## Changes (This Session)

### V3 Dashboard — 5-Tab Redesign

**Design reference:** `ContextBackgroundInfo/UpdateDesignPics/` (15 images showing V3 CMJ Hybrid Dashboard aesthetic and features)

#### Tab: Overview (updated)
- Added **Archetype badge** (Elastic / Typical / Grinder) to roster cards
- Added **SSC regime badge** (Fast SSC / Mixed SSC / Slow SSC) derived from Contraction Time
- Added **Plyo stage badge** (S1–S5) with red text when locked by SSC ceiling
- Filter chips abbreviated (EC / EE / BA / DEV) — same logic, shorter labels

#### Tab: Profiles (new)
- Flat alphabetical grid — all athletes, no position grouping
- Each card: mini radar SVG + 5 phase composite mini-bars (Perf / Strat / ECC / Brk / Land)
- Bars extend gold (right) for above-median, red (left) for below-median, centered at P50
- Delta values shown as normalized z-scores: `(value - P50) / (P75 - P25)`, clamped ±2

#### Tab: Training Rx (new)
- **Top section:** MD-3 station groups — athletes pooled by training station (4 stations: Fast ECC, ISO+Jumps, Short QCT, Weighted Plyo)
- **Bottom section:** Individual MD-1 through MD-4 microcycle prescription grid per athlete
- Station assignment and MD prescriptions come from `thresholds.yaml` prescription config

#### Tab: Plyo Stages (new)
- Athletes grouped by SSC regime (Fast → Mixed → Slow → Unknown)
- Within each regime: grouped by stage, sorted highest-to-lowest
- Ceiling badge shows stage cap for each regime
- Locked athletes (stage ≥ 4 with non-Fast SSC) show lock icon 🔒
- CT value shown in ms per athlete pill

#### Tab: Physio Flags (new)
- Shows only athletes with at least one exceeded physio threshold
- Flagged metrics: PLF/BM > `plf_bm_flag`, JH-rel PLF > `jh_rel_plf_flag`, Asym > caution threshold
- All thresholds are position-specific (added to `thresholds.yaml`)
- Physio notes textarea per athlete — saves to `localStorage` on blur, reloads on page init

#### Persistent Summary Stats Bar
- Always visible below tab nav regardless of active tab
- 8 squad-wide counters: Elite Conc / Explosive ECC / Balanced Ath / DEV / Braking Lim / Propulsive Lim / Landing Flag / Stage 3-5

### config/thresholds.yaml Changes
- Added `ssc_thresholds: {fast_ct_s: 0.150, slow_ct_s: 0.250}` at top of file
- Added `ft_ct` (p25/p50/p75) and `plf_bm` (p25/p50/p75) thresholds to all 10 positions
- Added `plf_bm_flag` and `jh_rel_plf_flag` scalar thresholds to all 10 positions
- **Restructured prescriptions** from flat strings (`gold.low_p1: "..."`) to nested dicts:
  ```yaml
  prescriptions:
    gold:
      low_p1:
        text: "..."         # legacy text field — p1p2.py reads this
        plyo_station: "..."
        md4: "..."
        md3: "..."
        md2: "..."
        md1: "..."
  ```

### src/classify/p1p2.py
- One-line fix: `prescriptions[group][quadrant]["text"]` instead of `prescriptions[f"{group}.{quadrant}"]`

### src/report/html_dashboard.py — New Functions
- `_ssc_regime(ct_seconds, cfg)` — Fast/Mixed/Slow SSC from CT and config thresholds
- `_plyo_stage(ssc, final_group, ci_quartile)` → `(stage: int, locked: bool)`
- `_archetype(ssc, movement_type)` → Elastic / Grinder / Typical
- `_phase_composites(metrics, pos_cfg)` → 5-item list for mini-bar chart; Landing inverted
- `_physio_flags(metrics, asymmetry_pct, pos_cfg)` → list of `{label, value, threshold, exceeded}`
- `_compute_summary_stats(athletes)` → 8-key dict for stats bar
- `_build_training_stations(athletes)` → ordered list of `{station_name, athletes}`
- `_build_plyo_stage_groups(athletes)` → grouped by regime then stage for Plyo Stages tab
- `build_athlete_context()` extended with 12 new fields: `contraction_time`, `ssc_regime`, `plyo_stage`, `plyo_locked`, `archetype`, `phase_composites`, `plyo_station`, `md4–md1`, `physio_flags`
- `render_dashboard()` passes: `summary_stats`, `training_stations`, `plyo_stage_groups`, `physio_athletes`

### tests/test_html_dashboard.py
- Updated one assertion: `"roster-view"` → `"tab-overview"` (ID changed in V3 template)

### docs/coaches_manual.md
- Full rewrite for V3: 4 parts (Sport Scientist, Coach Navigation, Interpreting Classifications, Best-Use Workflows)
- Original preserved as `docs/coaches_manual_v1.md`

## Key Files Modified
- `config/thresholds.yaml` — SSC thresholds, physio flag thresholds, restructured prescriptions
- `src/classify/p1p2.py` — prescription dict lookup fix
- `src/report/html_dashboard.py` — all V3 classification and aggregation logic
- `src/report/templates/dashboard.html.j2` — full 5-tab rewrite
- `tests/test_html_dashboard.py` — one assertion updated
- `docs/coaches_manual.md` — V3 rewrite
- `docs/coaches_manual_v1.md` — new file, original manual preserved
- `CLAUDE.md` — updated status, commands, dashboard description, new gotchas

## Known Considerations
- Movement type thresholds still produce ~93% Balanced — unchanged
- Physio notes are localStorage-only; they do not transfer between devices or staff members
- Plyo stage logic is heuristic (SSC ceiling + tier + CI quartile bump) — not validated against external progression criteria yet
- `ft_ct` and `plf_bm` position thresholds are estimated from NFL normative data; confirm against published VALD report before clinical use

---

# Session Context — 2026-03-23

## Current State

Baylor-branded dashboard redesign complete. Full visual rebrand with position-grouped roster, action-first athlete profiles, and enhanced radar charts with value labels.

**Tests:** 120 total (72 dashboard + 48 engine)

## Changes (This Session)

### Bodyweight Display — kg → lbs
- Bodyweight converted from kg to lbs in template only (`× 2.20462`)
- Two locations: roster card footer and athlete profile header
- Underlying data (`body_weight_kg`) unchanged in Python/DB

### Movement Strategy Badge Colors
- Each movement type now has a distinct badge color instead of uniform muted green
- Balanced (green), Fast-Deep (cyan/teal), Slow-Shallow (orange), Slow-Deep (purple), Unknown (gray)
- Implemented via CSS classes: `.badge-move-{{ type | lower | replace(' ', '-') }}`
- Applied on both roster cards and athlete profile headers

### Baylor Dashboard Redesign — Full Template Rewrite

**Design spec:** `docs/superpowers/specs/2026-03-22-baylor-dashboard-redesign-design.md`
**Implementation plan:** `docs/superpowers/plans/2026-03-22-baylor-dashboard-redesign.md`

#### Color System & Brand
- Page background: Baylor dark green `#001a0d`
- Card backgrounds: green gradient `#002a12` → `#001a0d`
- Primary accent / metric values: Baylor Gold `#FECB00`
- Body text: cream `#f0f0e8`, secondary: muted green `#7aab7a`
- Tier badges restyled: gold/purple/green/blue on dark matching backgrounds
- Flag colors unchanged (red/orange/yellow/green safety signals)

#### Roster View — Position-Grouped Layout
- Athletes grouped by full position name using `POSITION_ORDER` constant in `html_dashboard.py`
- Order: DB, LB, WR, RB, QB, TE, DL, OL, ST, K/P (skill first, then big, then special)
- Each group: gold label, athlete count badge, gold gradient stripe
- `render_dashboard()` builds `position_groups` list of `{position_name, athletes}` dicts
- Filter JS hides empty groups; sort reorders within each `.card-grid`
- Responsive: 4-col → 3-col (1200px) → 2-col (900px) → 1-col (600px)

#### Header
- Diagonal gold stripe pattern (CSS `repeating-linear-gradient` at -45deg)
- CSS-rendered "BU" circle logo (no image dependency)
- "BAYLOR FOOTBALL" in gold uppercase with letter-spacing
- `team_name` changed from "CMJ Force Plate Dashboard" to "Baylor Football"

#### Athlete Profile — Action-First Reorder
- **Row 2 (promoted):** Prescription (gold-bordered callout) + clinical notes + strengths/weaknesses (inline pill tags)
- **Row 3:** Radar chart (left) + trend vs baseline (right) — two-column
- **Row 4:** Phase profile + movement strategy — two-column (unchanged position)
- **Row 5 (demoted):** Key metrics in 5-column grid (was 2-col paired with radar)

#### Radar Chart Enhancements
- Baylor colors: gold polygon fill/stroke, dark green grid/axes, muted green labels
- SVG height increased from 360 to 400 (`_SVG_H = 400`) to prevent legend overlapping value labels
- Value labels at each vertex showing raw metric values in gold
- Formatting: `_TWO_DECIMAL_KEYS` = {RSI-modified, FT:CT} → 2 decimal places; all others → 1 decimal place
- Labels offset outward from polygon point along axis direction

### Encoding Fix — thresholds.yaml Prescriptions
- **Problem:** Foreign/garbled characters in prescription text on dashboard
- **Root cause:** En-dashes (U+2013) and em-dashes (U+2014) in `config/thresholds.yaml` rendered as mojibake
- **Fix:** Replaced all non-ASCII dashes with ASCII `-` in thresholds.yaml
- Also re-read from fixed YAML and updated stored DB prescription data via SQL

### New Tests (6 added, 66 → 72 dashboard tests)
- `TestRadarSvgValueLabels`: value labels present, absent when missing, 2-decimal formatting, 1-decimal formatting
- `TestPositionGrouping`: position groups in HTML output, position group ordering
- Updated existing color assertion tests for Baylor palette

### Template Backup
- Pre-redesign template preserved at `src/report/templates/dashboard.html.j2.bak`

## Key Files Modified
- `src/report/html_dashboard.py` — Baylor radar colors, value labels, position grouping, POSITION_ORDER, team_name
- `src/report/templates/dashboard.html.j2` — Complete rewrite: Baylor CSS, position-grouped roster, action-first profile, BU header
- `src/report/templates/dashboard.html.j2.bak` — New file, backup of pre-redesign template
- `tests/test_html_dashboard.py` — 6 new tests, updated color assertions
- `config/thresholds.yaml` — Replaced en-dash/em-dash with ASCII dashes in prescriptions
- `CLAUDE.md` — Updated test count, project structure, dashboard description, new gotchas
- `docs/superpowers/specs/2026-03-22-baylor-dashboard-redesign-design.md` — New file, design spec
- `docs/superpowers/plans/2026-03-22-baylor-dashboard-redesign.md` — New file, implementation plan

## Known Considerations
- Movement type thresholds still produce skewed distribution (~93% Balanced) — unchanged from prior session
- Windows `msys-2.0.dll` bash crashes still occur intermittently

---

# Session Context — 2026-03-21

## Current State

HTML dashboard fully implemented as a single self-contained HTML file generated by `run_pipeline.py --report` or `--report-only`. Replaced Streamlit dashboard and PDF report entirely.

**Tests:** 114 total (66 dashboard + 48 engine)

## Recent Changes (This Session)

### Filter Tabs Fix
- **Problem:** Clicking filter tabs didn't change the athlete listing
- **Root cause:** JS used `card.hidden` but CSS `.card { display: flex }` overrides the HTML `hidden` attribute
- **Fix:** Changed to `card.style.display = 'none'` in JS (`dashboard.html.j2:582`)

### Radar Chart Enhancements
- Enlarged SVG from 240×240 to 360×360 (radius 90→140), removed `max-width: 280px` CSS cap
- Added three-layer overlay:
  - **Green solid** — individual athlete values
  - **Orange dashed** — team positional average (computed from all athletes at same position)
  - **White dashed** — NFL P50 normative median (from `thresholds.yaml`)
- Legend at bottom of chart labels each line

### Baseline Trend (First-4-Test Average)
- **Previous:** Compared current test vs a single test from ~55 days ago — inconsistent, many athletes had no prior
- **New:** Averages the first 4 tests per athlete in the current season as baseline
- Athletes with <4 tests show "Establishing baseline (N/4 tests)" in orange
- Athletes with 0 prior tests show "No baseline" per metric
- Baseline never auto-updates — manual reset via `--reset-baseline` CLI flag

### Movement Type Fix
- **Problem:** All athletes showed "Balanced" regardless of actual movement strategy
- **Root causes:**
  1. Eccentric Duration thresholds were in milliseconds (450/600) but API returns **seconds** (0.450/0.600)
  2. Countermovement Depth thresholds expected positive values but API returns **negative cm**
- **Fix:** Converted thresholds to seconds, added `abs()` on depth
- Added "Unknown" label when either metric is missing (previously defaulted to "Balanced")
- Current distribution: ~93% Balanced, ~5% Slow-Deep, ~2% Fast-Deep — thresholds are intentionally strict
- Verified with DB query across all 56 athletes — distribution is genuine, not a bug

### Template Display Fixes
- **Ecc Duration:** Was showing raw seconds (e.g., "0 ms") in Movement Strategy panel — now converts `× 1000` to ms in template
- **CM Depth:** Was showing negative values (e.g., "-34.5 cm") — now uses `| abs` Jinja2 filter to display positive

### Coaches Manual
- Created `docs/coaches_manual.md` — comprehensive user guide
- **Part 1 (Sport Scientist):** Pipeline commands, report generation, distribution methods (email/shared drive/print), baseline resets, troubleshooting table
- **Part 2 (Coach):** How to read every dashboard element — roster cards, status dots, classification tiers, filter/sort, radar chart (three-layer explanation), phase profiles, movement strategy, trend vs baseline, strengths/weaknesses, prescriptions, clinical notes
- Includes quick-reference checklist for pre-practice and training design decisions

## Key Files Modified
- `src/report/html_dashboard.py` — radar SVG, movement type, baseline logic, team averages
- `src/report/templates/dashboard.html.j2` — filter tab JS, radar CSS, trend template, display unit conversions
- `tests/test_html_dashboard.py` — updated units in fixtures and movement type tests
- `CLAUDE.md` — updated test count, gotchas, documentation section
- `docs/coaches_manual.md` — new file, user manual for staff

## Known Considerations
- Movement type thresholds produce a skewed distribution — may want to adjust cutoffs for more granularity
- Windows `msys-2.0.dll` bash crashes occur intermittently — retry commands when this happens

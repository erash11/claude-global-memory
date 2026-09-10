# Baylor Dashboard Redesign — Design Spec

**Date:** 2026-03-22
**Status:** Approved
**Scope:** Visual redesign of `dashboard.html.j2` template and `html_dashboard.py` rendering logic

## Overview

Full visual rebrand of the CMJ Force Plate Dashboard with Baylor University identity, position-grouped roster layout, action-first athlete profile reordering, and enhanced radar chart with value labels. The old template is preserved before changes.

## 1. Color System & Brand

| Role | Color | Hex |
|------|-------|-----|
| Page background | Baylor dark green | `#001a0d` |
| Card background | Green gradient | `#002a12` → `#001a0d` |
| Header background | Deep green | `#003015` |
| Primary accent | Baylor Gold | `#FECB00` |
| Metric values | Gold | `#FECB00` |
| Body text | Cream/warm white | `#f0f0e8` |
| Secondary text | Muted green | `#7aab7a` |
| Card borders | Dark green | `#003a1a` |
| Hover/active borders | Gold | `#FECB00` |
| Geometric stripe accents | Gold at 6% opacity | `#FECB0010` |

**Tier badges:**
- ELITE CONCENTRIC — gold text (`#FECB00`) on dark gold bg (`#2e2a0a`), gold border
- EXPLOSIVE ECC — purple text (`#b07aff`) on dark purple bg (`#1a0d2e`)
- BALANCED ATHLETIC — green text (`#5adf7a`) on dark green bg (`#1a2e1a`)
- DEVELOPMENTAL — blue text (`#90a0ff`) on dark blue bg (`#0d0d1e`)

**Flag colors remain unchanged** (red/orange/yellow/green) — universal safety signals.

## 2. Roster View Layout

### Header
- Baylor green background with diagonal gold stripe pattern (uniform-inspired, `repeating-linear-gradient` at -45deg)
- Gold "BU" circle logo mark (CSS-rendered, no image dependency) + "BAYLOR FOOTBALL" in gold uppercase with letter-spacing
- "CMJ Force Plate Dashboard" subtitle in muted green
- Date + athlete count on the right

### Alert Strip
- No structural change — dark red background with red left border
- Only rendered when flagged athletes exist
- Positioned between header and position groups

### Position-Grouped Roster
- Athletes grouped by full position name (Defensive Back, Wide Receiver, Linebacker, etc.)
- Each group has:
  - Gold-labeled position name (uppercase, letter-spaced)
  - Athlete count badge (muted green text on dark green bg)
  - Gold gradient stripe extending to the right
- Group ordering: skill positions first (DB, LB, WR, RB, QB, TE), then big (DL, OL), then ST/K/P
- 4-column card grid within each group
- Responsive breakpoints: 3-col at 1200px, 2-col at 900px, 1-col at 600px

### Filter Tabs & Sort
- Same functionality, restyled: inactive tabs in dark green, active tab with gold text and gold border
- Sort dropdown in green/gold palette
- Filter hides individual cards within groups; if all cards in a group are filtered out, hide the group header too
- Sort reorders cards within their position group (not across groups)

### Athlete Cards
- Green gradient background (`linear-gradient(180deg, #002a12, #001a0d)`)
- Gold metric values (Power, Asym%, mRSI)
- Readiness dot: green glows, red pulses (CSS `@keyframes pulse`)
- Gold hover border with subtle gold box-shadow
- Red/orange left border for flagged athletes (unchanged)
- Card data attributes unchanged (for filter/sort JS)

## 3. Athlete Profile View — Action-First Reorder

### Current order → New order

| Current Row | Content | New Position |
|-------------|---------|-------------|
| — | Header (name, badges, meta) | Row 0 (unchanged) |
| — | Flag banner (if flagged) | Row 1 (unchanged) |
| Row 4+5 | Prescription, Clinical Notes, Strengths/Weaknesses | **Row 2 (promoted)** |
| Row 1 left | Radar chart | **Row 3 left** |
| Row 3 | Trend vs Baseline | **Row 3 right** |
| Row 2 | Phase Profile + Movement Strategy | **Row 4 (unchanged position)** |
| Row 1 right | Key Metrics (10 metrics) | **Row 5 (demoted)** |

### New Row 2: Action Panel
Single panel merging prescription, clinical notes, and strengths/weaknesses:
- **Prescription** in a gold-bordered callout (`border-left: 3px solid #FECB00`)
- **Clinical notes** below in muted text
- **Strengths** (green `+` pills) and **Weaknesses** (red `-` pills) displayed as inline tags/pills rather than a bulleted list, alongside the prescription

### New Row 3: Radar + Trend (two-col)
- Radar on left (see Section 4 for radar changes)
- Trend vs Baseline on right (was its own full-width row)
- Baseline status message ("Establishing baseline N/4") unchanged

### Row 4: Phase Profile + Movement Strategy (two-col)
- Same structure, Baylor colors applied
- Phase badges keep semantic colors (green/yellow/red for strong/monitor/deficit/high-risk)
- Metric labels in muted green, values in cream

### Row 5: Key Metrics (full-width)
- 2×5 grid (was 2-col paired with radar)
- Gold values, muted green labels
- Dark green cells with green border

## 4. Radar Chart Enhancement

### Color changes in `render_radar_svg()`
- Athlete polygon fill: `#FECB0022` (gold, transparent)
- Athlete polygon stroke: `#FECB00` (gold)
- Grid circles stroke: `#003a1a` (dark green)
- Axis spokes stroke: `#1a4a2a` (muted green)
- SVG background rect fill: `#001a0d` (page bg)
- Team avg polygon: `#f0a030` stroke (unchanged)
- NFL P50 polygon: `#ffffff` stroke (unchanged)
- Axis labels fill: `#7aab7a` (muted green, was `#888`)
- Legend text: `#7aab7a`

### Value labels (new)
- Small text (`font-size="9"`) placed adjacent to each vertex of the athlete polygon
- Shows the actual raw metric value (e.g., "0.74" for RSI-mod, "67.4" for Pk Power)
- Gold color (`#FECB00`)
- Offset slightly outward from the polygon point (same direction as axis label, ~12px offset)
- Only on the athlete polygon — team avg and NFL P50 do not get value labels (avoids clutter)
- Formatting: 2 decimal places for RSI-mod and FT:CT, 1 decimal place for everything else

### No structural changes
- 6-axis layout unchanged (Pk Power, Rel. Force, ECC Pw, Jump Ht, RSI-mod, FT:CT)
- Scoring algorithm unchanged (`_score_for_axis`)
- SVG dimensions unchanged (360×360, radius 140)

## 5. Files to Modify

| File | Changes |
|------|---------|
| `src/report/templates/dashboard.html.j2` | Full CSS restyle + HTML restructure (position groups, action-first profile) |
| `src/report/html_dashboard.py` | Radar SVG colors, value labels in `render_radar_svg()`, position grouping in `render_dashboard()`, action panel data in `build_athlete_context()` |

### Files to preserve
- Copy `dashboard.html.j2` to `dashboard.html.j2.bak` before modification
- Existing report file (`reports/2026-03-21_team_dashboard.html`) is already in `.gitignore`

## 6. Data Changes Required in `render_dashboard()`

### Position grouping
- Group athletes by `position` field before passing to template
- Pass as `position_groups` — list of `{position_name, athletes}` dicts
- Order: DB, LB, WR, RB, QB, TE, DL, OL, ST, K/P (hardcoded order list)

### Template context additions
- `position_groups`: replaces flat `athletes` list for roster view
- `athletes` list still passed (for profile views, filter/sort JS)

### Radar value labels
- `render_radar_svg()` gains value labels — needs the raw metric values passed through (already available in `metrics` dict)

## 7. Testing Considerations

- Existing 66 dashboard tests must continue passing
- Position grouping is a template-level change; `build_athlete_context()` output unchanged
- Radar SVG tests will need updated color assertions
- New test: verify position grouping order and completeness
- New test: verify radar SVG contains value label `<text>` elements

## 8. Out of Scope

- No changes to the classification pipeline or engine
- No changes to thresholds.yaml
- No changes to the database schema
- No new metrics or data pulls
- No logo image files (BU logo is CSS-rendered)

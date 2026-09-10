# RTP Clearance Report — Brody Wilhelm (TE) — Design

**Date:** 2026-07-21 · **Status:** Approved pending user spec review · **Deadline:** physician meeting today

## Context

Eric's PT colleague meets with team physicians today to discuss clearance of Brody Wilhelm (TE) returning from ACL reconstruction (surgery **2025-10-01**, ~9.5 months post-op). The report gives physicians a criteria-based, data-backed picture of rehab progression across GPS (Catapult), force plates (VALD), and weight-room strength (Perch).

## Deliverables

1. **Print-ready one-page PDF** (US letter) — the meeting handout.
2. **Private web link** (Claude artifact) — same layout, same charts, openable on any device. Link stays private; sharing is Eric's call (athlete performance/medical-adjacent data).

Both render from the **same HTML file** so they are visually identical.

## Approach (approved: "A2 hybrid")

- **Charts:** matplotlib renders each panel to SVG (correct date axes, shaded bands, dual axes from a real plotting library).
- **Layout:** a thin HTML shell (header, criteria chips, typography, print CSS `@page` letter) inlines the four SVGs.
- **PDF:** headless Chrome/Edge prints the HTML to a single-page PDF.
- **Link:** the same HTML is published as a private artifact.

Trade-off accepted: charts are static images on the web link (no hover). Chosen over pure-SVG-by-hand (higher chart-bug risk under deadline), full-matplotlib page (rough typography, second-class link), and extending PlayerProfiles_FB (unaudited renderer, highest same-day variance).

## Report purpose & framing (approved)

**Criteria-based clearance support** — each metric is anchored to an RTP benchmark with a Met / Approaching / Not-met status chip, alongside the time-series trends. No editorial paragraph; the physicians draw the conclusion.

## Comparison logic (approved)

Every panel shows **both**:
- **TE band** — IQR (25th–75th pct) of current Baylor TEs (excluding Brody) with median line, computed over a matched recent window (GPS: trailing 6 weeks of team training; VALD/Perch: most recent test per TE in 2026).
- **Pre-injury self** — dashed reference line at Brody's own pre-injury value (Jun–Sep 2025 window).

## Page layout (top to bottom)

1. **Header** — name, TE, DOS 2025-10-01, days/months post-op, report date, "Prepared for RTP clearance review".
2. **Criteria strip** — chips, thresholds cross-checked against `ForcePlate_DecisionSystem/config/thresholds.yaml` (house values win over the defaults below):
   - CMJ limb asymmetry ≤ 10% (Eccentric Braking Impulse Asymmetry — the limb-symmetry measure available in the data; IMTP has no L/R split, so an IMTP LSI is not computable — amended at implementation, 2026-07-21)
   - IMTP peak vertical force ≥ 90% of pre-injury best (replaces IMTP LSI per the data limitation above)
   - Sprint max velocity ≥ 90% of pre-injury best
   - Weekly workload within/above TE IQR (≥ 85% of TE median, matching Catapult CLI `rtp` default)
   - Lower-body strength ≥ 90% of pre-injury estimated 1RM
   - Chip logic: **Met** at threshold; **Approaching** within 5 points below; **Not met** otherwise. Any criterion with no post-op data shows **No data** rather than a false status.
3. **Four panels**, x-axis surgery → today, vertical marker at surgery date where pre-injury data is shown:
   1. **Return to sprinting** — session max velocity as % of pre-injury best (Catapult), threshold line at 90%, TE band.
   2. **Workload rebuild** — weekly Player Load (and/or high-speed running distance) vs TE weekly IQR band.
   3. **CMJ** — jump height trend + limb asymmetry % vs the 10% line (VALD), pre-injury baseline dashed.
   4. **Strength** — IMTP limb-symmetry % leading (clearance-relevant), Perch estimated-1RM trend secondary (approved).
4. **Footer** — per-source as-of dates (transparency on freshness): VALD, Perch, Catapult, plus threshold sources.

## Data sources (verified 2026-07-21)

| Source | Access | Brody's data | Freshness plan |
|---|---|---|---|
| Catapult GPS | `catapult-openfield-connect-pp-cli` (live API; `rtp`, `benchmark`, `pb` commands) | Roster confirmed; session history verified at implementation start | Live |
| VALD | `ForcePlate_DecisionSystem/data/forceplate.db` (DuckDB): `raw_tests` 328 rows 2025-06-23→2026-06-08; `imtp_tests` 40 rows →2026-06-10; `athlete_baselines` | Pre-injury + post-op through June | Timeboxed attempt to sync newer tests via the ForcePlate pipeline; else report as-of 2026-06-10 |
| Perch | `PlayerProfiles_FB_03-28-2026/data/perch.duckdb`: `perch_1rm` 36 rows 2025-08-01→2026-04-27 | Pre-injury + rehab strength work | Timeboxed re-run of `perch_ingest.py` for May–Jul; else as-of 2026-04-27 |

**Known risk:** Brody's post-op GPS volume is unverified — if he has little/no field GPS yet, panels 1–2 show whatever exists and the criteria chips say "No data" honestly. First implementation step verifies this.

## Architecture (one-off today, reusable-ready — approved)

```
SpecialRequests/Wilhelm_Brody_RTP/
  params.yaml          # athlete, position, surgery_date, as_of — the reuse seam
  src/pull_data.py     # Catapult CLI JSON + two DuckDB reads → data/report_data.json
  src/charts.py        # four panel functions (df, params) → SVG
  src/build_report.py  # HTML shell + inline SVGs → out/report.html → headless print → out/*.pdf
  data/ out/ docs/
```

No extra generalization work today beyond keeping athlete/position/dates in `params.yaml` and out of the code.

## Error handling

- Any source that fails to pull → panel renders with "data unavailable" note + criteria chip "No data"; report still ships.
- Name matching across systems ("Brody Wilhelm" / `brody wilhelm` normalized) asserted at pull time; hard fail with a clear message if a source has zero rows for him.
- PDF must be exactly one page — build step fails loudly if Chrome emits 2+ pages.

## Testing

Deadline-appropriate: pull-layer sanity assertions (row counts > 0, date ranges span pre/post-op), a visual check of the rendered HTML/PDF before delivery, and cross-checking 2–3 chart values against direct DB queries. No formal test suite today.

## Out of scope

- Editorial interpretation / recommendation text (explicitly declined in favor of criteria chips).
- Hover interactivity on the web link.
- Generalizing into a multi-athlete pipeline (future home would be PlayerProfiles_FB).

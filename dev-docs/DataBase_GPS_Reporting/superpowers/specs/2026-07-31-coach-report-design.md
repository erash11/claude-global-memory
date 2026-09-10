# Post-Session Coach Report — Design

**Date:** 2026-07-31
**Status:** Approved (design approved in session; recommended options accepted)
**Owner:** Eric Rash

## Purpose

A one-page, coach-facing post-session report answering: **what did we plan to do in practice vs what actually happened** — plus who needs attention. Distinct from the detailed post-session GPS report (AJ's report, produced by `gps_report/`): this is the high-level version Eric can text/email to coaches minutes after data lands, using the same metric context AJ reports on.

- **Volume:** Total Player Load
- **Intensity:** Player Load per Minute, Explosive Efforts
- **Max velocity:** who got their exposure, who needs the opportunity
- **Individual signal:** SPC (statistical process control) flags for over-/under-dosed athletes

## Architecture

New `coach_report/` folder inside `DataBase_GPS_Reporting`, **read-only** consumer of `gps_report/data/gps_history.duckdb`. Zero changes to the existing `gps_report/` pipeline; data freshness rides on its existing ingestion (nightly run / `run_report.py`).

```
coach_report/
  coach_report.py        # CLI entry: python coach_report.py --date today|YYYY-MM-DD
  coach_config.yaml      # day-type regexes, thresholds, metric display names
  plan_overrides.yaml    # optional per-date planned targets / day-type overrides
  src/
    data.py              # DuckDB read-only queries
    day_types.py         # session-name → day-type inference + historical norms
    spc.py               # XmR individuals charts, control limits, flags
    maxvel.py            # PB tracking, exposure lists
    render.py            # Jinja2 render + PDF export
  templates/coach_report.html.j2
  Reports/coach/YYYY-MM-DD/coach_report.html + .pdf
```

## Components

### Day-type inference (`day_types.py`)
Session names are highly regular. Regex table in `coach_config.yaml` (first match wins):

| Pattern | Day-type |
|---|---|
| `walk.?thru` (case-insens.) | `walk_thru` |
| `scrimmage` | `scrimmage` |
| `4th qtr` | `conditioning` |
| `- P\d+ -` | `practice` |
| `- G\d+ -` | `game` |
| no match | `other` (reported, never silently dropped) |

Fall-camp naming additions = one config line. Verified against 2024–2026 data: 183 practices, 57 walk-thrus, games all match `- G\d+`.

### Planned targets
"Planned" = historical **median ± IQR** per (day-type × position group × metric), computed at run time from `athlete_sessions` (not the stale `positional_norms` table, which is weekday-keyed and lacks PL/min + explosive efforts). Lookback window configurable (default 365 days).

`plan_overrides.yaml` per-date entries win over templates:
```yaml
2026-08-05:
  day_type: camp_practice        # force classification
  note: "Intentionally light — day after scrimmage"
  targets: { total_player_load: [400, 520] }   # optional explicit range
```

Team section shows planned range vs actual (team median), % delta, and an over/on/under-plan badge per metric: Player Load (volume), PL/min, Explosive Efforts (intensity).

### Max velocity (`maxvel.py`)
Personal best = max of `max_velocity_ms` over all history (display mph). Two lists:
- **Hit exposure today:** session max ≥ 90% of PB (threshold configurable)
- **Needs opportunity:** no session ≥ 90% PB in last 10 days (window configurable); sorted by days-since-last-exposure descending. Excludes athletes with no session in that window (not at practice ≠ needs sprint exposure — listed separately as "not present").

### SPC flags (`spc.py`)
Per athlete, per metric (Total Player Load, PL/min): **XmR individuals chart**.
- Baseline: last 20 sessions (excluding today); games excluded from practice baselines.
- Center line = mean; sigma = mean moving range / 1.128; UCL/LCL = CL ± 3σ (LCL floored at 0).
- Today above UCL → **overdosed signal**; below LCL → **underdosed signal**.
- Minimum 10 prior sessions to flag; below that, excluded with a count note.
- Output: ranked flag table (largest |deviation in σ| first), overdosed and underdosed grouped separately, each row with an inline SVG sparkline: last ~15 sessions, CL/UCL/LCL lines, today's point highlighted.

### Report layout (top → bottom)
1. **Header** — session name, date, day-type, duration, athlete count, plan-override note if any.
2. **Planned vs Actual** — KPI tiles per metric with badge + % delta; small per-position-group table.
3. **Max Velocity** — two compact lists (hit exposure / needs opportunity).
4. **SPC Flags** — overdosed table, underdosed table, sparklines; excluded-athlete note.
5. Footer — generated timestamp, data-as-of timestamp from DB.

### Output & PDF
HTML via Jinja2 (self-contained, inline CSS/SVG). PDF via headless Chrome (`--headless --print-to-pdf`), same mechanism as the html-to-pdf skill. Both written to `Reports/coach/YYYY-MM-DD/`.

## Error handling
- No session on requested date → clear message listing nearest session dates; exit 3.
- DB missing/locked → actionable message; open read-only to avoid contending with nightly ingest.
- Unknown day-type → report renders with "no plan template" note on the planned section rather than failing.
- Multiple sessions on one date → aggregate practices; `--session` flag to pick one.

## Testing
- Unit tests for `spc.py` (known-limit fixtures) and `day_types.py` (name → type table).
- End-to-end validation against 2026-04-25 (SP26 P15) and a walk-thru date; sanity-check team medians against direct DB queries.

## Out of scope (YAGNI)
- No new data ingestion; no Catapult API calls.
- No scheduling (can be added to the existing nightly run later).
- No ACWR/injury-risk modeling — SPC on the two agreed metrics only.

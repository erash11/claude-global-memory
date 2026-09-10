# Handoff — Tezino CampPrep Phase 4 Dashboard

Date: 2026-06-12

## Current State

The Phase 4 dashboard data contract and staff-facing static HTML dashboard are built.
The dashboard now leads with the Pulse Check First layout. The top section is driven by
`pulse_monitor` in `data/dashboard/dashboard_data.json` and shows selected process behavior
metrics before historical warning context. The next agent should not rebuild the data
plumbing unless the upstream CSV schemas change.

Run the full data chain from the project root:

```powershell
python scripts\refresh_dashboard.py
```

Primary dashboard input:

- `data/dashboard/dashboard_data.json`

Primary dashboard output:

- `data/dashboard/index.html`

Builders:

- `scripts/build_dashboard_data.py`
- `scripts/build_dashboard_html.py`
- `scripts/refresh_dashboard.py`

Tests:

- `tests/test_build_dashboard_data.py`
- `tests/test_build_dashboard_html.py`
- `tests/test_refresh_dashboard.py`

## Dashboard Data Contract

Top-level JSON keys:

- `schema_version`
- `generated_on`
- `project`
- `pulse_monitor`
- `current_ramp`
- `current_forceplate`
- `live_baseline`
- `warning_references`
- `spc_validation`
- `series`
- `caveats`

Current generated readback:

- 2026 GPS sessions: 8
- 2026 Perch training days: 6
- 2026 summer axial tonnage: 24,604.3 lb
- 2026 CMJ: 2 current-ramp tests through 2026-06-08; latest mRSI 0.5637, purple, green readiness
- 2026 IMTP: current-ramp rows through 2026-06-10; latest PVF/BM 31.14, RFD 100ms 4,825, RFD 200ms 5,333.75
- SPC validation overall: 11 early-warning series, 43 no-preinjury-signal series
- Chart-ready rows: 256 weekly exposure, 135 response, 44 SPC signal points

The static dashboard now renders `Tezino Morning Pulse Check` first, followed by the
Current Force Plate section from `current_forceplate`, live baseline context, and
historical warning references.

## Next Work

Use the dashboard manually for 2-3 weeks before adding scheduling/automation. Weekly flow:
run `python scripts\refresh_dashboard.py`, open `data/dashboard/index.html`, review
caveats/current-response values, and adjust staff-facing interpretation only if the data
changed enough to warrant it. Baseline-window choice is resolved as the first four weeks
of June 2026, with staff review after three weeks and provisional live limits until the
four-week window is complete.

Keep staff-facing language aligned with the process-behavior chart framing in
`docs/PROCESS-BEHAVIOR-CHARTS.md`: separate routine noise from meaningful process signals,
show the rule that triggered action, and do not overclaim injury prediction.

## Caveats to Preserve

- First four weeks of June 2026 selected as the live baseline; limits are provisional
  until the four-week window is complete.
- FC26 P1 is estimated as 2026-07-29 until the calendar is confirmed.
- Catapult tier-2 acceleration and HSR thresholds for a 290 lb DL are pending.
- Catapult tier-2 proxy rows remain review prompts, not locked foot-specific thresholds.
- SPC validation supports change detection, not a strong injury-prediction claim.

## Residual Environment Notes

- Browser QA used a local static server: `python -m http.server 8765 --bind 127.0.0.1`.
- `tmp4t9qaeqs` remains from an earlier sandbox temp-dir issue and is inaccessible.
- External Codex memory writes outside the project were blocked by the current sandbox.

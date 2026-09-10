# Dashboard UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 4 staff-facing HTML dashboard from `data/dashboard/dashboard_data.json`.

**Architecture:** Add one standard-library Python generator that reads the existing dashboard JSON contract and writes a self-contained `data/dashboard/index.html`. Keep source data in the JSON contract, render staff-facing copy and summary sections server-side, and use lightweight inline SVG/JavaScript only for chart rendering in the static file.

**Tech Stack:** Python standard library (`json`, `html`, `pathlib`, `datetime`), pytest/unittest, static HTML/CSS/JavaScript/SVG.

---

### Task 1: Add Dashboard HTML Tests

**Files:**
- Create: `tests/test_build_dashboard_html.py`
- Fixture input: `tests/fixtures/dashboard_data/`
- Target script: `scripts/build_dashboard_html.py`

- [x] **Step 1: Write failing tests**

Create tests that load `build_dashboard_html.py`, build a payload from the existing dashboard-data fixture, render HTML, and assert the staff-facing contract:

```python
def test_dashboard_html_contains_staff_sections():
    data_module = load_data_module()
    html_module = load_html_module()
    payload = data_module.build_dashboard_payload(FIXTURE)
    html = html_module.render_dashboard(payload)
    assert "Devonte Tezino" in html
    assert "Current 2026 Ramp" in html
    assert "Historical Warning References" in html
    assert "SPC Validation" in html
    assert "Process Behavior Chart Data" in html
    assert "2026 baseline window is not chosen yet" in html
```

Also assert the dashboard does not overclaim:

```python
def test_dashboard_html_preserves_caveats_and_avoids_prediction_claims():
    data_module = load_data_module()
    html_module = load_html_module()
    payload = data_module.build_dashboard_payload(FIXTURE)
    html = html_module.render_dashboard(payload)
    assert "change detection, not a strong injury-prediction claim" in html
    assert "safe limit" not in html.lower()
    assert "injury prediction" not in html.lower().replace("injury-prediction", "")
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests\test_build_dashboard_html.py -q -p no:cacheprovider`

Expected: FAIL because `scripts/build_dashboard_html.py` does not exist yet.

### Task 2: Implement Static Dashboard Generator

**Files:**
- Create: `scripts/build_dashboard_html.py`
- Output: `data/dashboard/index.html`

- [x] **Step 1: Implement formatting helpers**

Create helpers for HTML escaping, number formatting, date formatting, JSON embedding, and summarizing null values as `Data pending`.

- [x] **Step 2: Render staff-facing sections**

Render:
- Header with athlete, generated date, frame, and caveat strip.
- Current ramp KPI cards for GPS sessions, Perch training days, axial tonnage, and heavy axial reps.
- 2024 and 2025 warning-reference panels with injury date/mechanism and key summer/camp values.
- SPC validation summary with overall counts, by-ramp counts, early-warning list, and honest interpretation.
- Chart area for weekly exposure, response, and SPC signal points.

- [x] **Step 3: Add inline chart JavaScript**

Embed the payload as JSON and draw small SVG charts from `series.weekly_exposure`, `series.response`, and `series.spc_signal_points`. Use process-behavior language and display signal rule strings. Do not compute 2026 control limits.

- [x] **Step 4: Write output**

Write deterministic UTF-8 HTML to `data/dashboard/index.html` and print the relative path.

### Task 3: Generate, Verify, And Document

**Files:**
- Modify generated: `data/dashboard/index.html`
- Modify: `AGENTS.md`
- Modify: `docs/NARRATIVE-PLAN.md`
- Modify: `docs/HANDOFF-2026-06-11-night.md`

- [x] **Step 1: Run focused tests**

Run: `python -m pytest tests\test_build_dashboard_html.py -q -p no:cacheprovider`

- [x] **Step 2: Run all tests**

Run: `python -m pytest tests -q -p no:cacheprovider`

- [x] **Step 3: Run full refresh chain**

Run:

```powershell
python scripts\derive_perch_metrics.py
python scripts\build_ramp_datasets.py
python scripts\build_retrospective_panels.py
python scripts\build_spc_validation.py
python scripts\build_dashboard_data.py
python scripts\build_dashboard_html.py
```

- [x] **Step 4: Browser-check generated dashboard**

Open `data/dashboard/index.html` locally, verify desktop and mobile layout, confirm charts render, and confirm staff-facing caveats remain visible.

### Self-Review

- Spec coverage: Phase 4 dashboard UI is generated from the existing data contract and preserves caveats, current ramp cards, warning references, SPC validation, and chart sections.
- Placeholder scan: no unchosen 2026 baseline, control limits, target weight, or DL threshold is invented.
- Type consistency: source JSON keys match `scripts/build_dashboard_data.py`; generated HTML uses static strings only for labels and caveats.

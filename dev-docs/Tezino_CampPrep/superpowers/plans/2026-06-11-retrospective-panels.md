# Retrospective Panels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 3 retrospective exposure reconstruction from the existing ramp datasets.

**Architecture:** Add one pure-transform script that reads `data/ramps/ramps_all.csv` and writes tidy Phase 3 CSV panels to `data/retrospective/`. The script keeps tier labels explicit, anchors every row to camp and known injury dates, computes weekly exposure plus ramp-rate features, and separates response metrics from exposure metrics.

**Tech Stack:** Python standard library only (`csv`, `datetime`, `pathlib`, `collections`), pytest for regression tests.

---

### Task 1: Add Retrospective Builder Tests

**Files:**
- Create: `tests/test_build_retrospective_panels.py`
- Create: `tests/fixtures/retrospective_panels/ramps_all.csv`
- Create: `tests/fixtures/retrospective_panels/ramp_kpis.csv`

- [x] **Step 1: Write failing tests**

Test `build_weekly_exposure()` with fixture rows that include Perch, GPS, and response metrics. Assert weekly systemic and axial sums, session counts, injury anchoring, and ramp-rate columns.

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests\test_build_retrospective_panels.py -q -p no:cacheprovider`

Expected: FAIL because `scripts/build_retrospective_panels.py` does not exist yet.

### Task 2: Implement Retrospective Panel Builder

**Files:**
- Create: `scripts/build_retrospective_panels.py`
- Output: `data/retrospective/weekly_exposure.csv`
- Output: `data/retrospective/response_panel.csv`
- Output: `data/retrospective/injury_week_zoom.csv`

- [ ] **Step 1: Implement constants and CSV helpers**

Define camp anchors, injury anchors for 2024 and 2025, metric catalog, input/output paths, and read/write helpers.

- [ ] **Step 2: Implement weekly exposure aggregation**

Read ramp rows and aggregate weekly exposure by `ramp`, ISO week, `tier`, `surface`, and `metric`. Compute `week_start`, `week_end`, `days_to_camp_min`, `days_to_camp_max`, `days_to_injury_min`, `days_to_injury_max`, `value`, `wow_change`, and `vs_28d_avg`.

- [ ] **Step 3: Implement response panel**

Carry body weight, CMJ mRSI/asymmetry, IMTP, and CMJ tier detail as daily response rows with camp and injury anchors.

- [ ] **Step 4: Implement injury-week zoom**

Write daily rows for 2024 and 2025 within -14..+14 days of the July 10 injury anchors, keeping exposure and response metrics needed for the focused narrative.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests\test_build_retrospective_panels.py -q -p no:cacheprovider`

Expected: PASS.

### Task 3: Generate Full Phase 3 Outputs

**Files:**
- Modify generated CSVs under `data/retrospective/`

- [ ] **Step 1: Run upstream transforms**

Run:
```powershell
python scripts\derive_perch_metrics.py
python scripts\build_ramp_datasets.py
```

- [ ] **Step 2: Run retrospective builder**

Run:
```powershell
python scripts\build_retrospective_panels.py
```

Expected: printed row counts for `weekly_exposure.csv`, `response_panel.csv`, and `injury_week_zoom.csv`.

- [ ] **Step 3: Verify injury-week expectations**

Confirm 2024 has Perch training days through `2024-07-08` and no Perch training day after the `2024-07-10` fracture, while 2025 has Perch training days after `2025-07-10`.

### Self-Review

- Spec coverage: Phase 3 systemic exposure, foot-specific mechanical exposure, response panel, and injury-week zoom are covered.
- Placeholder scan: no task depends on unavailable Catapult thresholds; unavailable tier-2 Catapult fields are labeled as proxy metrics.
- Type consistency: all outputs use CSV scalar values and stable string identifiers.

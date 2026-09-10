# SPC Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate whether XmR control-chart signals on prior ramps would have appeared before the 2024-07-10 foot fracture and 2025-07-10 hip/groin strain.

**Architecture:** Add one pure-transform script that reads Phase 3 retrospective panels, derives SPC process variables, computes XmR limits from the 2023 healthy baseline, applies those limits to 2024 and 2025, and writes point-level and summary CSVs. The validation result is descriptive and honest; it does not gate the future live monitor.

**Tech Stack:** Python standard library only (`csv`, `datetime`, `pathlib`, `statistics`), pytest for regression tests.

---

### Task 1: Add SPC Validation Tests

**Files:**
- Create: `tests/test_build_spc_validation.py`
- Create: `tests/fixtures/spc_validation/weekly_exposure.csv`
- Create: `tests/fixtures/spc_validation/response_panel.csv`

- [x] **Step 1: Write failing tests**

Cover XmR limit calculation, exposure-rate series extraction, response raw series extraction, and injury lead-day summary.

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests\test_build_spc_validation.py -q -p no:cacheprovider`

Expected: FAIL because `scripts/build_spc_validation.py` does not exist yet.

### Task 2: Implement SPC Validation Builder

**Files:**
- Create: `scripts/build_spc_validation.py`
- Output: `data/spc_validation/spc_points.csv`
- Output: `data/spc_validation/spc_validation_summary.csv`
- Output: `data/spc_validation/spc_validation_notes.md`

- [ ] **Step 1: Implement XmR helpers**

Compute center line, moving ranges, MR-bar, sigma estimate (`MRbar / 1.128`), natural process limits, and signal flags for individual points outside limits.

- [ ] **Step 2: Build process-variable series**

Use exposure `wow_change` and `vs_28d_avg` from `weekly_exposure.csv`; use raw response values from `response_panel.csv`.

- [ ] **Step 3: Apply 2023 baseline limits to 2024/2025**

For each series key, compute limits from 2023 points where at least three baseline points exist, then score 2024/2025 points.

- [ ] **Step 4: Summarize injury-window validation**

For each 2024/2025 series, record whether any out-of-control signal occurred on or before injury day 0, earliest signal date, and lead days.

- [ ] **Step 5: Generate notes**

Write a short markdown file stating baseline choice, data limitations, and honest early-warning vs change-detection interpretation.

### Task 3: Generate and Verify Full Outputs

**Files:**
- Modify generated CSVs under `data/spc_validation/`
- Modify: `AGENTS.md`
- Modify: `docs/NARRATIVE-PLAN.md`
- Add memory note under `C:\Users\eric_rash\.codex\memories\extensions\ad_hoc\notes\`

- [ ] **Step 1: Run tests**

Run: `python -m pytest tests -q -p no:cacheprovider`

- [ ] **Step 2: Run full pipeline**

Run:
```powershell
python scripts\derive_perch_metrics.py
python scripts\build_ramp_datasets.py
python scripts\build_retrospective_panels.py
python scripts\build_spc_validation.py
```

- [ ] **Step 3: Verify validation claims**

Read `data/spc_validation/spc_validation_summary.csv` and report counts of pre-injury signals by ramp without overstating prediction.

### Self-Review

- Spec coverage: Phase 3b validation, honest validation reporting, and ADR-0001 framing are covered.
- Placeholder scan: no unavailable 2026 baseline or DL-specific Catapult thresholds are invented.
- Type consistency: output rows are long CSV rows keyed by stable `series_id`.

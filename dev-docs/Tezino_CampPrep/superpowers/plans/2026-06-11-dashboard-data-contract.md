# Dashboard Data Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a stable JSON data contract for the Phase 4 live monitor dashboard.

**Architecture:** Add one pure-transform script that reads generated CSV outputs from `data/ramps/`, `data/retrospective/`, and `data/spc_validation/`, then writes `data/dashboard/dashboard_data.json`. The JSON should separate dashboard metadata, current 2026 ramp status, retrospective warning references, SPC validation summary, chart-ready series, and explicit caveats.

**Tech Stack:** Python standard library only (`csv`, `json`, `datetime`, `pathlib`, `collections`), pytest for regression tests.

---

### Task 1: Add Dashboard Data Tests

**Files:**
- Create: `tests/test_build_dashboard_data.py`
- Create: `tests/fixtures/dashboard_data/` with small CSV fixtures.

- [x] **Step 1: Write failing tests**

Test that `build_dashboard_payload()` returns a versioned payload with `current_ramp`, `warning_references`, `spc_validation`, `series`, and `caveats`.

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests\test_build_dashboard_data.py -q -p no:cacheprovider`

Expected: FAIL because `scripts/build_dashboard_data.py` does not exist yet.

### Task 2: Implement Dashboard Data Builder

**Files:**
- Create: `scripts/build_dashboard_data.py`
- Output: `data/dashboard/dashboard_data.json`

- [ ] **Step 1: Implement CSV and scalar parsing helpers**

Read values safely, converting blank cells to `None` and numeric cells to numbers.

- [ ] **Step 2: Build current 2026 status**

Read `data/ramps/ramp_kpis.csv` and summarize 2026 camp anchor, GPS sessions, Perch training days, tonnage, and missing current response data.

- [ ] **Step 3: Build warning references**

Read 2024 and 2025 KPI rows and expose July-10 injury context, summer GPS sessions, Perch axial tonnage, heavy axial reps, camp availability, and key response-at-entry fields.

- [ ] **Step 4: Build SPC validation summary**

Read `spc_validation_summary.csv` and count interpretations overall and by ramp; include early-warning series details.

- [ ] **Step 5: Build chart-ready series**

Read compact subsets from `weekly_exposure.csv`, `response_panel.csv`, and `spc_points.csv` for dashboard panels.

- [ ] **Step 6: Write JSON output**

Write deterministic, indented JSON to `data/dashboard/dashboard_data.json`.

### Task 3: Generate and Verify

**Files:**
- Modify generated `data/dashboard/dashboard_data.json`
- Modify `AGENTS.md`
- Modify `docs/NARRATIVE-PLAN.md`
- Add/update project-local handoff if needed.

- [ ] **Step 1: Run tests**

Run: `python -m pytest tests -q -p no:cacheprovider`

- [ ] **Step 2: Run full pipeline**

Run:
```powershell
python scripts\derive_perch_metrics.py
python scripts\build_ramp_datasets.py
python scripts\build_retrospective_panels.py
python scripts\build_spc_validation.py
python scripts\build_dashboard_data.py
```

- [ ] **Step 3: Read back JSON contract**

Verify top-level keys, 2026 current status, SPC validation counts, and caveats.

### Self-Review

- Spec coverage: dashboard data contract includes current 2026 ramp, 2024/2025 warning references, SPC validation, chart series, and caveats.
- Placeholder scan: no UI or unchosen 2026 control limits are invented.
- Type consistency: JSON keys are stable and snake_case.

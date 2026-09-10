# Dashboard Refresh Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one manual command that refreshes all dashboard source artifacts and rewrites the staff-facing dashboard.

**Architecture:** Add a small Python orchestrator that runs the existing pure-transform scripts in dependency order, fails fast, and prints the final dashboard paths. Keep analytical logic in the existing builders; this command is operational glue only.

**Tech Stack:** Python standard library (`subprocess`, `sys`, `pathlib`, `argparse`), pytest/unittest.

---

### Task 1: Test The Refresh Command Contract

**Files:**
- Create: `tests/test_refresh_dashboard.py`
- Target script: `scripts/refresh_dashboard.py`

- [x] **Step 1: Write failing tests**

Test that the command exposes the exact refresh steps in order and can execute them through an injected runner:

```python
def test_refresh_steps_are_in_dependency_order():
    module = load_module("refresh_dashboard", SCRIPT_PATH)
    assert module.refresh_steps() == [
        "derive_perch_metrics.py",
        "build_ramp_datasets.py",
        "build_retrospective_panels.py",
        "build_spc_validation.py",
        "build_dashboard_data.py",
        "build_dashboard_html.py",
    ]

def test_run_refresh_invokes_each_step_with_current_python():
    module = load_module("refresh_dashboard_run", SCRIPT_PATH)
    calls = []
    result = module.run_refresh(runner=lambda cmd, cwd: calls.append((cmd, cwd)) or 0)
    assert result == 0
    assert [cmd[-1].name for cmd, _cwd in calls] == module.refresh_steps()
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests\test_refresh_dashboard.py -q -p no:cacheprovider`

Expected: FAIL because `scripts/refresh_dashboard.py` does not exist yet.

### Task 2: Implement The Refresh Command

**Files:**
- Create: `scripts/refresh_dashboard.py`

- [x] **Step 1: Add step list and injected runner interface**

Define `refresh_steps()` and `run_refresh(runner=None)`. The default runner should call `subprocess.run(cmd, cwd=PROJECT_ROOT).returncode`.

- [x] **Step 2: Add CLI entrypoint**

`main()` should call `run_refresh()`, print the output paths on success, and return the first failing step code on failure.

- [x] **Step 3: Run focused tests**

Run: `python -m pytest tests\test_refresh_dashboard.py -q -p no:cacheprovider`

Expected: PASS.

### Task 3: Wire The Operator Docs

**Files:**
- Modify: `AGENTS.md`
- Modify: `docs/NARRATIVE-PLAN.md`
- Modify: `docs/HANDOFF-2026-06-11-night.md`

- [x] **Step 1: Replace multi-command refresh guidance**

Document the manual operator command:

```powershell
python scripts\refresh_dashboard.py
```

- [x] **Step 2: Run full verification**

Run:

```powershell
python scripts\refresh_dashboard.py
python -m pytest tests -q -p no:cacheprovider
```

Expected: dashboard artifacts regenerate and all tests pass.

### Self-Review

- Spec coverage: one manual refresh command exists, uses the existing dependency order, and keeps scheduling/automation deferred.
- Placeholder scan: no analytical assumptions, baseline choices, or control limits are introduced.
- Type consistency: refresh command returns process-style integer exit codes and accepts an injected runner for tests.

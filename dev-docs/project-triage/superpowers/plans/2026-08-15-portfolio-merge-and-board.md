# Portfolio Merge + Board Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the two project registries into `portfolio.json`, then ship a local drag-and-drop board for managing it.

**Architecture:** Phase 1 is a one-shot merge module with a dry-run CLI; it adds a top-level `inbox` list that `validate()` deliberately does not police. Phase 2 adds pure mutation functions to a new `board_ops.py`, then a stdlib `http.server` in `board.py` that exposes them over localhost and serves one vanilla-JS page. All writes funnel through `portfolio.save_registry`, which validates and backs up.

**Tech Stack:** Python 3.11+, stdlib only (`http.server`, `json`, `pathlib`, `unittest`). No third-party packages, no JS build step, no CDN.

**Spec:** `docs/superpowers/specs/2026-08-15-portfolio-merge-and-browser-editor-design.md` (revision 4)

## Global Constraints

- **Stdlib only.** No pip installs, no npm, no CDN references in the HTML.
- **Run tests with:** `python3 -m unittest discover -s tests -v` from the repo root. 46 tests pass today; every task must leave them passing.
- **Test style:** `unittest`, `tempfile.TemporaryDirectory`, `import portfolio` directly. Follow `tests/test_portfolio.py`.
- **Vocabulary is owned by `portfolio.py`** — import `LANES`, `PROJECT_STATUSES`, `STAGES`. Never re-declare these lists.
  - `LANES = {"job", "side"}`
  - `PROJECT_STATUSES = {"active", "paused", "done", "dropped"}`
  - `STAGES = ["idea", "grilled", "spec", "planned", "building", "shipped"]`
- **`validate()` requires on every `projects` record:** `name`, `lane`, `rank` (int ≥ 1, unique per lane among `active`), `status`, `purpose` (str), `next_action` (str). `stage` is optional but must be a valid stage **if the key is present** — a present-but-`null` stage fails.
- **Never write a `stage` or `lane` key set to `null`.** Omit the key instead.
- **The merge reads the working-copy `portfolio.json`**, which carries 43 uncommitted lines. Never `git checkout` or `git stash` that file.
- **Bind only to `127.0.0.1`.** The board is never exposed to the network.
- `prototype/board.html` is reference only. Do not import from it or promote it.

---

## File Structure

| File | Responsibility |
|---|---|
| `merge_curation.py` | **create** — pure `merge()` plus a dry-run CLI. Used once, kept for the record. |
| `board_ops.py` | **create** — pure registry mutations: `reorder`, `promote`, `patch_project`, `delete_project`. No HTTP, no I/O. |
| `board.py` | **create** — `http.server` handler, token/Origin checks, static page serving, undo buffer. |
| `board.html` | **create** — the single page. Vanilla JS, fetches `/api/*`. |
| `portfolio.py` | **modify** — make `save_registry` atomic. |
| `tests/test_merge_curation.py` | **create** |
| `tests/test_board_ops.py` | **create** |
| `tests/test_board_server.py` | **create** |

`board_ops.py` is deliberately separate from `board.py`: the interesting logic (rank renumbering, promotion rules) is testable without starting a server.

---

# Phase 1 — Merge

### Task 1: Lock in that `inbox` survives validation and round-trips

The whole merge depends on `validate()` ignoring a top-level `inbox` key and `save_registry` preserving it. That is current behaviour, not guaranteed behaviour — pin it with tests before building on it.

**Files:**
- Test: `tests/test_merge_curation.py` (create)

**Interfaces:**
- Consumes: `portfolio.validate`, `portfolio.save_registry`, `portfolio.load_registry`
- Produces: `minimal_registry()` test helper reused by Task 2

- [ ] **Step 1: Write the failing test**

```python
# tests/test_merge_curation.py
import json
import tempfile
import unittest
from pathlib import Path

import portfolio


def minimal_registry():
    return {
        "meta": {"artifact_url": ""},
        "projects": [
            {"name": "Alpha", "lane": "job", "rank": 1, "status": "active",
             "purpose": "p", "next_action": "n", "dev_folder": "Alpha",
             "links": [], "updates": [], "curated_at": "2026-08-01T00:00:00"},
        ],
        "ideas": [],
    }


class TestInboxTier(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "portfolio.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_validate_ignores_inbox_key(self):
        data = minimal_registry()
        data["inbox"] = [{"name": "Bucket"}]
        portfolio.validate(data)  # must not raise

    def test_inbox_records_may_omit_required_project_fields(self):
        data = minimal_registry()
        data["inbox"] = [{"name": "Bucket", "status": "paused"}]
        portfolio.validate(data)  # no lane/rank/purpose/next_action — still fine

    def test_inbox_survives_save_and_load(self):
        data = minimal_registry()
        data["inbox"] = [{"name": "Bucket", "purpose": "vps experiment"}]
        portfolio.save_registry(self.path, data)
        back = portfolio.load_registry(self.path)
        self.assertEqual(back["inbox"], [{"name": "Bucket", "purpose": "vps experiment"}])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test**

Run: `python3 -m unittest tests.test_merge_curation -v`
Expected: PASS — these lock in existing behaviour. If any fail, stop: the spec's inbox tier is invalid and the design needs revisiting before continuing.

- [ ] **Step 3: Commit**

```bash
git add tests/test_merge_curation.py
git commit -m "test: pin inbox tier tolerance in validate and save_registry"
```

---

### Task 2: The `merge()` function

**Files:**
- Create: `merge_curation.py`
- Test: `tests/test_merge_curation.py` (extend)

**Interfaces:**
- Consumes: `portfolio.validate`
- Produces: `merge_curation.merge(port: dict, cur: dict, now: str) -> dict` — returns a new registry, does not mutate its arguments. `now` is an ISO-8601 string like `"2026-08-15T14:03:51"`.

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_merge_curation.py

import merge_curation

NOW = "2026-08-15T14:03:51"


class TestMerge(unittest.TestCase):
    def test_curation_status_wins_on_conflict(self):
        port = minimal_registry()                      # Alpha is active
        cur = {"Alpha": {"status_override": "pause"}}
        out = merge_curation.merge(port, cur, NOW)
        self.assertEqual(out["projects"][0]["status"], "paused")
        self.assertEqual(out["projects"][0]["curated_at"], NOW)

    def test_resume_maps_to_active(self):
        port = minimal_registry()
        port["projects"][0]["status"] = "paused"
        cur = {"Alpha": {"status_override": "resume"}}
        out = merge_curation.merge(port, cur, NOW)
        self.assertEqual(out["projects"][0]["status"], "active")

    def test_portfolio_purpose_is_kept_and_curation_purpose_becomes_an_update(self):
        port = minimal_registry()
        cur = {"Alpha": {"purpose": "a shorter phrasing"}}
        out = merge_curation.merge(port, cur, NOW)
        self.assertEqual(out["projects"][0]["purpose"], "p")
        self.assertIn("a shorter phrasing", out["projects"][0]["updates"][0]["note"])
        self.assertEqual(out["projects"][0]["updates"][0]["date"], "2026-08-15")

    def test_identical_purpose_adds_no_update(self):
        port = minimal_registry()
        cur = {"Alpha": {"purpose": "p"}}
        out = merge_curation.merge(port, cur, NOW)
        self.assertEqual(out["projects"][0]["updates"], [])

    def test_unknown_name_goes_to_inbox_without_lane_rank_or_stage(self):
        port = minimal_registry()
        cur = {"Football": {"status_override": "resume", "purpose": "force plate reporting"}}
        out = merge_curation.merge(port, cur, NOW)
        self.assertEqual(len(out["inbox"]), 1)
        rec = out["inbox"][0]
        self.assertEqual(rec["name"], "Football")
        self.assertEqual(rec["dev_folder"], "Football")
        self.assertEqual(rec["status"], "active")
        self.assertEqual(rec["purpose"], "force plate reporting")
        self.assertNotIn("lane", rec)
        self.assertNotIn("rank", rec)
        self.assertNotIn("stage", rec)

    def test_entry_with_no_status_override_leaves_status_alone(self):
        port = minimal_registry()
        cur = {"Alpha": {"purpose": "p"}}
        out = merge_curation.merge(port, cur, NOW)
        self.assertEqual(out["projects"][0]["status"], "active")

    def test_join_uses_dev_folder_not_name(self):
        port = minimal_registry()
        port["projects"][0]["name"] = "Alpha Project"
        port["projects"][0]["dev_folder"] = "Alpha"
        cur = {"Alpha": {"status_override": "pause"}}
        out = merge_curation.merge(port, cur, NOW)
        self.assertEqual(out["projects"][0]["status"], "paused")
        self.assertEqual(out["inbox"], [])

    def test_merge_is_idempotent(self):
        port = minimal_registry()
        cur = {"Alpha": {"status_override": "pause"}, "Football": {"purpose": "x"}}
        once = merge_curation.merge(port, cur, NOW)
        twice = merge_curation.merge(once, cur, NOW)
        self.assertEqual(once, twice)

    def test_result_validates(self):
        port = minimal_registry()
        cur = {"Alpha": {"status_override": "pause"}, "Football": {"purpose": "x"}}
        portfolio.validate(merge_curation.merge(port, cur, NOW))

    def test_input_is_not_mutated(self):
        port = minimal_registry()
        cur = {"Alpha": {"status_override": "pause"}}
        merge_curation.merge(port, cur, NOW)
        self.assertEqual(port["projects"][0]["status"], "active")
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tests.test_merge_curation -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'merge_curation'`

- [ ] **Step 3: Write the implementation**

```python
# merge_curation.py
"""Merge .curation.json into portfolio.json.

Curation records describe ~/DEV folders. Where a folder already has a project
record they update it; where it does not, the record goes to the `inbox` tier
rather than `projects`, because validate() requires a lane, a rank and a
next_action that only the user can supply.
"""
import argparse
import copy
import datetime as _dt
import json
from pathlib import Path

import portfolio

STATUS_MAP = {"resume": "active", "pause": "paused"}
SOURCE_TAG = "curation-merge-2026-08-15"


def _key(project: dict) -> str:
    return project.get("dev_folder") or project["name"]


def merge(port: dict, cur: dict, now: str) -> dict:
    data = copy.deepcopy(port)
    by_key = {_key(p): p for p in data["projects"]}
    inbox = data.setdefault("inbox", [])
    seen_inbox = {r["name"] for r in inbox}
    day = now[:10]

    for name in sorted(cur):
        entry = cur[name] or {}
        status = STATUS_MAP.get(entry.get("status_override"))
        purpose = entry.get("purpose")

        project = by_key.get(name)
        if project is not None:
            if status and project.get("status") != status:
                project["status"] = status
                project["curated_at"] = now
            if isinstance(purpose, str) and purpose.strip():
                existing = (project.get("purpose") or "").strip()
                note = f"Curation {day}: {purpose.strip()}"
                already = any(u.get("note") == note for u in project.get("updates", []))
                if purpose.strip() != existing and not already:
                    project.setdefault("updates", []).insert(0, {"date": day, "note": note})
                    project["curated_at"] = now
            continue

        if name in seen_inbox:
            continue
        record = {"name": name, "dev_folder": name, "source": SOURCE_TAG}
        if status:
            record["status"] = status
        if isinstance(purpose, str) and purpose.strip():
            record["purpose"] = purpose.strip()
        action = entry.get("action")
        if isinstance(action, str) and action.strip():
            record["next_action"] = action.strip()
        inbox.append(record)
        seen_inbox.add(name)

    portfolio.validate(data)
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Merge .curation.json into portfolio.json")
    ap.add_argument("--repo", type=Path, default=Path(__file__).parent)
    ap.add_argument("--apply", action="store_true", help="write the result (default: dry run)")
    args = ap.parse_args(argv)

    reg_path = args.repo / "portfolio.json"
    cur_path = args.repo / ".curation.json"
    port = portfolio.load_registry(reg_path)
    cur = json.loads(cur_path.read_text(encoding="utf-8"))
    now = _dt.datetime.now().replace(microsecond=0).isoformat()

    out = merge(port, cur, now)
    changed = sum(1 for a, b in zip(port["projects"], out["projects"]) if a != b)
    print(f"projects: {len(out['projects'])} ({changed} changed)  inbox: {len(out.get('inbox', []))}")
    if not args.apply:
        print("dry run — pass --apply to write")
        return 0
    portfolio.save_registry(reg_path, out)
    cur_path.rename(cur_path.with_suffix(".json.bak"))
    print(f"wrote {reg_path}; curation archived to {cur_path.with_suffix('.json.bak')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS, 56+ tests

- [ ] **Step 5: Commit**

```bash
git add merge_curation.py tests/test_merge_curation.py
git commit -m "feat: merge curation registry into portfolio with an inbox tier"
```

---

### Task 3: Run the merge for real

**Files:**
- Modify: `portfolio.json` (data, via the script)
- Modify: `.curation.json` → renamed to `.curation.json.bak`

- [ ] **Step 1: Dry run and read the numbers**

```bash
python3 merge_curation.py
```

Expected: `projects: 21 (7 changed)  inbox: 15` then `dry run — pass --apply to write`.
If `projects` is not 21 or `inbox` is not 15, STOP and report — the working copy is not what the plan assumed.

- [ ] **Step 2: Apply**

```bash
python3 merge_curation.py --apply
```

- [ ] **Step 3: Verify the spec's post-merge assertions**

```bash
python3 - <<'PY'
import json, portfolio
d = portfolio.load_registry(__import__("pathlib").Path("portfolio.json"))
assert len(d["projects"]) == 21, len(d["projects"])
assert len(d["inbox"]) == 15, len(d["inbox"])
# Match on name OR dev_folder: the curation keys are ~/DEV folder names, and they
# do not all equal the project name — DataBase_GPS_Reporting is the dev_folder of
# the project named Coach_Report.
paused = {p["name"] for p in d["projects"] if p["status"] == "paused"} | \
         {p.get("dev_folder") for p in d["projects"] if p["status"] == "paused"}
for n in ("DataBase_GPS_Reporting", "ForcePlate_DecisionSystem", "PlayerProfiles_FB",
          "Risk_Stratification_Engine", "S2_Evaluation", "Sport_Tech_Vetting", "Travel_Map"):
    assert any(n in p for p in paused if p), f"{n} not paused: {sorted(x for x in paused if x)}"
s2 = next(p for p in d["projects"] if p["name"] == "S2_Evaluation")
assert s2["stage"] == "shipped" and len(s2["updates"]) >= 3, s2["stage"]
assert not any("stage" in r or "lane" in r or "rank" in r for r in d["inbox"])
for p in d["projects"]:
    assert p.get("stage") is not None or "stage" not in p
portfolio.validate(d)
print("all post-merge assertions pass")
PY
```

Expected: `all post-merge assertions pass`

- [ ] **Step 4: Verify the renderer still works**

Run: `python3 render.py --no-scan`
Expected: exit 0, prints `wrote dashboard.html · wrote pulse.md · 21 projects · ...`

- [ ] **Step 5: Commit**

```bash
git add portfolio.json .curation.json.bak dashboard.html pulse.md
git rm --cached .curation.json 2>/dev/null || true
git commit -m "data: merge curation into portfolio, 15 records to the inbox tier"
```

---

# Phase 2 — Board

### Task 4: Make `save_registry` atomic

A half-written registry is unrecoverable; the board writes on every drag, so this matters far more than it did for a once-a-day CLI.

**Files:**
- Modify: `portfolio.py:68-73`
- Test: `tests/test_portfolio.py` (extend)

**Interfaces:**
- Produces: `portfolio.save_registry(path, data)` — unchanged signature, now atomic

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_portfolio.py

class TestAtomicSave(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "portfolio.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_invalid_data_leaves_the_original_file_untouched(self):
        good = minimal_registry()
        portfolio.save_registry(self.path, good)
        before = self.path.read_text()

        bad = minimal_registry()
        bad["projects"][0]["status"] = "bogus"
        with self.assertRaises(portfolio.RegistryError):
            portfolio.save_registry(self.path, bad)

        self.assertEqual(self.path.read_text(), before)

    def test_no_temp_files_are_left_behind(self):
        portfolio.save_registry(self.path, minimal_registry())
        leftovers = [p.name for p in self.path.parent.iterdir()
                     if p.name.startswith(".portfolio") or p.suffix == ".tmp"]
        self.assertEqual(leftovers, [])
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m unittest tests.test_portfolio -v -k Atomic`
Expected: the temp-file test may already pass; `test_invalid_data_leaves_the_original_file_untouched` should pass too, because `validate()` runs first. If both pass, the change below is still required — run it and confirm they stay green.

- [ ] **Step 3: Write the implementation**

```python
# portfolio.py — replace save_registry
def save_registry(path: Path, data: dict) -> None:
    validate(data)
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, path)          # atomic on the same filesystem
```

Add `import os` at the top of `portfolio.py` if it is not already there.

- [ ] **Step 4: Run the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add portfolio.py tests/test_portfolio.py
git commit -m "fix: write the registry atomically"
```

---

### Task 5: `reorder()` — drag sets stage and renumbers the lane

**Files:**
- Create: `board_ops.py`
- Test: `tests/test_board_ops.py` (create)

**Interfaces:**
- Consumes: `portfolio.STAGES`, `portfolio.validate`
- Produces:
  - `board_ops.live(data, lane) -> list[dict]` — that lane's projects excluding `done`/`dropped`, sorted by rank
  - `board_ops.reorder(data, name, lane, stage, position) -> dict` — mutates and returns `data`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_board_ops.py
import unittest

import board_ops
import portfolio


def registry(*specs):
    """specs: (name, lane, rank, stage, status)"""
    return {
        "meta": {"artifact_url": ""},
        "projects": [
            {"name": n, "lane": l, "rank": r, "stage": s, "status": st,
             "purpose": "p", "next_action": "n", "dev_folder": n,
             "links": [], "updates": [], "curated_at": "2026-08-01T00:00:00"}
            for (n, l, r, s, st) in specs
        ],
        "ideas": [],
        "inbox": [],
    }


class TestReorder(unittest.TestCase):
    def test_moving_across_columns_sets_the_stage(self):
        d = registry(("A", "job", 1, "idea", "active"))
        board_ops.reorder(d, "A", "job", "building", 0)
        self.assertEqual(d["projects"][0]["stage"], "building")

    def test_ranks_are_contiguous_from_one_after_a_move(self):
        d = registry(("A", "job", 1, "idea", "active"),
                     ("B", "job", 2, "spec", "active"),
                     ("C", "job", 3, "shipped", "active"))
        board_ops.reorder(d, "C", "job", "idea", 0)
        ranks = sorted(p["rank"] for p in d["projects"])
        self.assertEqual(ranks, [1, 2, 3])

    def test_rank_order_follows_the_stage_ladder_then_position(self):
        d = registry(("A", "job", 1, "spec", "active"),
                     ("B", "job", 2, "idea", "active"))
        board_ops.reorder(d, "B", "job", "idea", 0)
        by_name = {p["name"]: p["rank"] for p in d["projects"]}
        self.assertLess(by_name["B"], by_name["A"])   # idea sorts before spec

    def test_position_places_the_card_within_its_column(self):
        d = registry(("A", "job", 1, "idea", "active"),
                     ("B", "job", 2, "idea", "active"),
                     ("C", "job", 3, "spec", "active"))
        board_ops.reorder(d, "C", "job", "idea", 1)     # between A and B
        by_name = {p["name"]: p["rank"] for p in d["projects"]}
        self.assertEqual([by_name["A"], by_name["C"], by_name["B"]], [1, 2, 3])

    def test_position_beyond_the_column_length_lands_at_the_end(self):
        d = registry(("A", "job", 1, "idea", "active"),
                     ("B", "job", 2, "spec", "active"))
        board_ops.reorder(d, "B", "job", "idea", 99)
        by_name = {p["name"]: p["rank"] for p in d["projects"]}
        self.assertEqual(by_name["A"], 1)
        self.assertEqual(by_name["B"], 2)

    def test_archived_projects_are_excluded_from_renumbering(self):
        d = registry(("A", "job", 1, "idea", "active"),
                     ("Z", "job", 2, "idea", "done"))
        board_ops.reorder(d, "A", "job", "spec", 0)
        z = next(p for p in d["projects"] if p["name"] == "Z")
        self.assertEqual(z["rank"], 2)          # untouched
        self.assertEqual(next(p for p in d["projects"] if p["name"] == "A")["rank"], 1)

    def test_the_other_lane_is_not_renumbered(self):
        d = registry(("A", "job", 1, "idea", "active"),
                     ("S", "side", 5, "idea", "active"))
        board_ops.reorder(d, "A", "job", "spec", 0)
        self.assertEqual(next(p for p in d["projects"] if p["name"] == "S")["rank"], 5)

    def test_moving_between_lanes_renumbers_both(self):
        d = registry(("A", "job", 1, "idea", "active"),
                     ("B", "job", 2, "idea", "active"),
                     ("S", "side", 1, "idea", "active"))
        board_ops.reorder(d, "A", "side", "idea", 0)
        job = [p["rank"] for p in d["projects"] if p["lane"] == "job"]
        side = sorted(p["rank"] for p in d["projects"] if p["lane"] == "side")
        self.assertEqual(job, [1])
        self.assertEqual(side, [1, 2])

    def test_result_validates(self):
        d = registry(("A", "job", 1, "idea", "active"),
                     ("B", "job", 2, "idea", "active"))
        board_ops.reorder(d, "B", "job", "spec", 0)
        portfolio.validate(d)

    def test_unknown_name_raises(self):
        d = registry(("A", "job", 1, "idea", "active"))
        with self.assertRaises(portfolio.RegistryError):
            board_ops.reorder(d, "Nope", "job", "idea", 0)

    def test_invalid_stage_raises(self):
        d = registry(("A", "job", 1, "idea", "active"))
        with self.assertRaises(portfolio.RegistryError):
            board_ops.reorder(d, "A", "job", "bogus", 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tests.test_board_ops -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'board_ops'`

- [ ] **Step 3: Write the implementation**

```python
# board_ops.py
"""Pure registry mutations behind the board. No HTTP, no file I/O."""
import portfolio
from portfolio import RegistryError, STAGES, LANES, PROJECT_STATUSES

ARCHIVED = {"done", "dropped"}


def find(data: dict, name: str) -> dict:
    for p in data["projects"]:
        if p["name"] == name:
            return p
    raise RegistryError(f"unknown project: {name}")


def live(data: dict, lane: str) -> list[dict]:
    return sorted(
        (p for p in data["projects"]
         if p.get("lane") == lane and p.get("status") not in ARCHIVED),
        key=lambda p: p.get("rank") or 10**6,
    )


def _renumber(data: dict, lane: str) -> None:
    members = live(data, lane)
    ordered: list[dict] = []
    for stage in STAGES:
        ordered.extend(p for p in members if p.get("stage") == stage)
    ordered.extend(p for p in members if p.get("stage") not in STAGES)
    for i, p in enumerate(ordered, 1):
        p["rank"] = i


def reorder(data: dict, name: str, lane: str, stage: str, position: int) -> dict:
    if lane not in LANES:
        raise RegistryError(f"lane must be one of {sorted(LANES)}")
    if stage not in STAGES:
        raise RegistryError(f"stage must be one of {STAGES}")
    project = find(data, name)
    old_lane = project.get("lane")

    project["lane"] = lane
    project["stage"] = stage

    # Rebuild the destination column with the card inserted at `position`,
    # then give every card in the column a rank that sorts it correctly.
    column = [p for p in live(data, lane) if p.get("stage") == stage and p is not project]
    column.insert(max(0, min(position, len(column))), project)
    for offset, p in enumerate(column):
        p["rank"] = -(len(column) - offset)   # temporary keys, fixed by _renumber

    _renumber(data, lane)
    if old_lane and old_lane != lane:
        _renumber(data, old_lane)
    return data
```

Note on the temporary negative ranks: `_renumber` reads `live()`, which sorts by rank. Assigning descending negatives to the destination column preserves the intended within-column order through that sort, and `_renumber` immediately overwrites them with 1..N.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add board_ops.py tests/test_board_ops.py
git commit -m "feat: reorder projects by lane, stage and drop position"
```

---

### Task 6: `promote()`, `patch_project()`, `delete_project()`

**Files:**
- Modify: `board_ops.py`
- Test: `tests/test_board_ops.py` (extend)

**Interfaces:**
- Produces:
  - `board_ops.promote(data, name, lane, stage, position, purpose, next_action) -> dict`
  - `board_ops.patch_project(data, name, *, status=None, purpose=None, next_action=None, note=None, today=None) -> dict`
  - `board_ops.delete_project(data, name) -> dict`

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_board_ops.py

class TestPromote(unittest.TestCase):
    def base(self):
        d = registry(("A", "job", 1, "idea", "active"))
        d["inbox"] = [{"name": "Football", "dev_folder": "Football", "status": "active"}]
        return d

    def test_promotion_requires_a_purpose(self):
        d = self.base()
        with self.assertRaises(portfolio.RegistryError):
            board_ops.promote(d, "Football", "job", "idea", 0, "", "ship it")
        self.assertEqual(len(d["inbox"]), 1)       # still in the inbox

    def test_promotion_requires_a_next_action(self):
        d = self.base()
        with self.assertRaises(portfolio.RegistryError):
            board_ops.promote(d, "Football", "job", "idea", 0, "reporting", "   ")
        self.assertEqual(len(d["inbox"]), 1)

    def test_successful_promotion_moves_the_record(self):
        d = self.base()
        board_ops.promote(d, "Football", "job", "spec", 0, "reporting", "ship it")
        self.assertEqual(d["inbox"], [])
        rec = board_ops.find(d, "Football")
        self.assertEqual(rec["lane"], "job")
        self.assertEqual(rec["stage"], "spec")
        self.assertEqual(rec["purpose"], "reporting")
        self.assertEqual(rec["next_action"], "ship it")
        self.assertEqual(rec["dev_folder"], "Football")
        portfolio.validate(d)

    def test_promotion_keeps_the_inbox_status(self):
        d = self.base()
        d["inbox"][0]["status"] = "paused"
        board_ops.promote(d, "Football", "job", "idea", 0, "p", "n")
        self.assertEqual(board_ops.find(d, "Football")["status"], "paused")

    def test_promoting_an_unknown_name_raises(self):
        d = self.base()
        with self.assertRaises(portfolio.RegistryError):
            board_ops.promote(d, "Ghost", "job", "idea", 0, "p", "n")


class TestPatch(unittest.TestCase):
    def test_status_change_is_applied_and_renumbers(self):
        d = registry(("A", "job", 1, "idea", "active"), ("B", "job", 2, "idea", "active"))
        board_ops.patch_project(d, "A", status="done")
        self.assertEqual(board_ops.find(d, "A")["status"], "done")
        self.assertEqual(board_ops.find(d, "B")["rank"], 1)

    def test_invalid_status_raises(self):
        d = registry(("A", "job", 1, "idea", "active"))
        with self.assertRaises(portfolio.RegistryError):
            board_ops.patch_project(d, "A", status="bogus")

    def test_note_is_prepended_with_a_date(self):
        d = registry(("A", "job", 1, "idea", "active"))
        board_ops.patch_project(d, "A", note="did a thing", today="2026-08-15")
        self.assertEqual(board_ops.find(d, "A")["updates"][0],
                         {"date": "2026-08-15", "note": "did a thing"})

    def test_note_does_not_overwrite_history(self):
        d = registry(("A", "job", 1, "idea", "active"))
        board_ops.find(d, "A")["updates"] = [{"date": "2026-08-01", "note": "older"}]
        board_ops.patch_project(d, "A", note="newer", today="2026-08-15")
        self.assertEqual(len(board_ops.find(d, "A")["updates"]), 2)
        self.assertEqual(board_ops.find(d, "A")["updates"][1]["note"], "older")

    def test_blank_note_is_ignored(self):
        d = registry(("A", "job", 1, "idea", "active"))
        board_ops.patch_project(d, "A", note="   ", today="2026-08-15")
        self.assertEqual(board_ops.find(d, "A")["updates"], [])

    def test_purpose_and_next_action_are_editable(self):
        d = registry(("A", "job", 1, "idea", "active"))
        board_ops.patch_project(d, "A", purpose="new purpose", next_action="new action")
        self.assertEqual(board_ops.find(d, "A")["purpose"], "new purpose")
        self.assertEqual(board_ops.find(d, "A")["next_action"], "new action")


class TestDelete(unittest.TestCase):
    def test_delete_removes_and_renumbers(self):
        d = registry(("A", "job", 1, "idea", "active"), ("B", "job", 2, "idea", "active"))
        board_ops.delete_project(d, "A")
        self.assertEqual([p["name"] for p in d["projects"]], ["B"])
        self.assertEqual(board_ops.find(d, "B")["rank"], 1)

    def test_deleting_an_unknown_name_raises(self):
        d = registry(("A", "job", 1, "idea", "active"))
        with self.assertRaises(portfolio.RegistryError):
            board_ops.delete_project(d, "Ghost")
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tests.test_board_ops -v`
Expected: FAIL with `AttributeError: module 'board_ops' has no attribute 'promote'`

- [ ] **Step 3: Write the implementation**

```python
# append to board_ops.py

def promote(data, name, lane, stage, position, purpose, next_action):
    inbox = data.setdefault("inbox", [])
    record = next((r for r in inbox if r["name"] == name), None)
    if record is None:
        raise RegistryError(f"unknown inbox record: {name}")
    if not (purpose or "").strip():
        raise RegistryError("promotion needs a purpose")
    if not (next_action or "").strip():
        raise RegistryError("promotion needs a next action")

    project = {
        "name": record["name"],
        "dev_folder": record.get("dev_folder", record["name"]),
        "lane": lane,
        "rank": 10**6,                       # placeholder; reorder assigns the real one
        "status": record.get("status", "active"),
        "stage": stage,
        "purpose": purpose.strip(),
        "next_action": next_action.strip(),
        "links": [],
        "updates": record.get("updates", []),
    }
    data["projects"].append(project)
    try:
        reorder(data, name, lane, stage, position)
    except RegistryError:
        data["projects"].remove(project)     # leave the inbox untouched on failure
        raise
    data["inbox"] = [r for r in inbox if r["name"] != name]
    return data


def patch_project(data, name, *, status=None, purpose=None,
                  next_action=None, note=None, today=None):
    project = find(data, name)
    if status is not None:
        if status not in PROJECT_STATUSES:
            raise RegistryError(f"status must be one of {sorted(PROJECT_STATUSES)}")
        project["status"] = status
    if purpose is not None:
        project["purpose"] = purpose
    if next_action is not None:
        project["next_action"] = next_action
    if note is not None and note.strip():
        project.setdefault("updates", []).insert(0, {"date": today, "note": note.strip()})
    if project.get("lane"):
        _renumber(data, project["lane"])
    return data


def delete_project(data, name):
    project = find(data, name)
    lane = project.get("lane")
    data["projects"] = [p for p in data["projects"] if p is not project]
    if lane:
        _renumber(data, lane)
    return data
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add board_ops.py tests/test_board_ops.py
git commit -m "feat: promote inbox records, patch and delete projects"
```

---

### Task 7: Server skeleton — token, Origin check, read routes

**Files:**
- Create: `board.py`
- Test: `tests/test_board_server.py` (create)

**Interfaces:**
- Consumes: `board_ops`, `portfolio`
- Produces:
  - `board.make_server(repo: Path, token: str, port: int = 0) -> http.server.HTTPServer`
  - `board.Handler` with attributes `repo`, `token` set by `make_server`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_board_server.py
import json
import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import board
import portfolio

REPO = Path(__file__).resolve().parent.parent


def seed(dirpath: Path):
    data = {
        "meta": {"artifact_url": ""},
        "projects": [
            {"name": "A", "lane": "job", "rank": 1, "status": "active", "stage": "idea",
             "purpose": "p", "next_action": "n", "dev_folder": "A",
             "links": [], "updates": [], "curated_at": "2026-08-01T00:00:00"},
        ],
        "ideas": [],
        "inbox": [{"name": "Football", "dev_folder": "Football", "status": "active"}],
    }
    portfolio.save_registry(dirpath / "portfolio.json", data)
    shutil.copy(REPO / "board.html", dirpath / "board.html")


class ServerCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        seed(self.dir)
        self.token = "test-token"
        self.srv = board.make_server(self.dir, self.token, port=0)
        self.port = self.srv.server_address[1]
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.tmp.cleanup()

    def url(self, path, with_token=True):
        sep = "&" if "?" in path else "?"
        return f"http://127.0.0.1:{self.port}{path}" + (f"{sep}token={self.token}" if with_token else "")

    def get(self, path, with_token=True):
        return urllib.request.urlopen(self.url(path, with_token))

    def post(self, path, payload, origin=None, with_token=True):
        req = urllib.request.Request(
            self.url(path, with_token),
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Origin": origin if origin is not None else f"http://127.0.0.1:{self.port}"},
            method="POST",
        )
        return urllib.request.urlopen(req)


class TestReadRoutes(ServerCase):
    def test_root_serves_the_page(self):
        body = self.get("/").read().decode()
        self.assertIn("<html", body.lower())

    def test_registry_endpoint_returns_the_data(self):
        data = json.loads(self.get("/api/registry").read())
        self.assertEqual(len(data["projects"]), 1)
        self.assertEqual(len(data["inbox"]), 1)

    def test_api_without_a_token_is_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.get("/api/registry", with_token=False)
        self.assertEqual(cm.exception.code, 403)

    def test_api_with_a_wrong_token_is_rejected(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/registry?token=nope")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 403)

    def test_post_from_a_foreign_origin_is_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.post("/api/project/A", {"status": "paused"}, origin="http://evil.example")
        self.assertEqual(cm.exception.code, 403)

    def test_server_binds_loopback_only(self):
        self.assertEqual(self.srv.server_address[0], "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m unittest tests.test_board_server -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'board'`

- [ ] **Step 3: Write the implementation**

```python
# board.py
"""Local drag-and-drop board over portfolio.json.

Binds 127.0.0.1 only. A per-run token guards /api/*, and writes additionally
require a same-origin request, because any page in the browser can POST to a
localhost port.
"""
import argparse
import datetime as _dt
import http.server
import json
import secrets
import threading
import webbrowser
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import board_ops
import portfolio
from portfolio import RegistryError

LOCK = threading.Lock()


class Handler(http.server.BaseHTTPRequestHandler):
    repo: Path = None
    token: str = ""
    undo: dict = None

    def log_message(self, *args):        # keep the terminal quiet
        pass

    # ---------- helpers ----------
    def _send(self, code, payload=None, body=None, ctype="application/json"):
        data = body if body is not None else json.dumps(payload or {}).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _authorised(self, parsed) -> bool:
        got = parse_qs(parsed.query).get("token", [""])[0]
        return secrets.compare_digest(got, self.token)

    def _same_origin(self) -> bool:
        origin = self.headers.get("Origin")
        if origin is None:
            return True                  # non-browser client, e.g. curl
        host = self.headers.get("Host", "")
        return origin in (f"http://{host}", f"https://{host}")

    def _load(self):
        return portfolio.load_registry(self.repo / "portfolio.json")

    def _save(self, data):
        portfolio.save_registry(self.repo / "portfolio.json", data)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(length) or b"{}")

    # ---------- routes ----------
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            page = (self.repo / "board.html").read_bytes()
            return self._send(200, body=page, ctype="text/html; charset=utf-8")
        if not parsed.path.startswith("/api/"):
            return self._send(404, {"error": "not found"})
        if not self._authorised(parsed):
            return self._send(403, {"error": "bad or missing token"})
        if parsed.path == "/api/registry":
            data = self._load()
            data["today"] = _dt.date.today().isoformat()
            return self._send(200, data)
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if not self._authorised(parsed):
            return self._send(403, {"error": "bad or missing token"})
        if not self._same_origin():
            return self._send(403, {"error": "cross-origin write refused"})
        return self._send(404, {"error": "not found"})


def make_server(repo: Path, token: str, port: int = 0) -> http.server.HTTPServer:
    handler = type("BoundHandler", (Handler,), {"repo": Path(repo), "token": token})
    return http.server.HTTPServer(("127.0.0.1", port), handler)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Local portfolio board")
    ap.add_argument("--repo", type=Path, default=Path(__file__).parent)
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args(argv)

    portfolio.load_registry(args.repo / "portfolio.json")   # refuse to start on a bad file

    token = secrets.token_urlsafe(16)
    srv = make_server(args.repo, token, args.port)
    url = f"http://127.0.0.1:{srv.server_address[1]}/?token={token}"
    print(f"board at {url}")
    print("ctrl-c to stop")
    if not args.no_open:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The page fetches `/api/*` with the token from its own query string, so the token never needs to be embedded in the HTML file on disk.

- [ ] **Step 4: Create a placeholder page so the server has something to serve**

```bash
printf '<!doctype html><html><body><h1>board</h1></body></html>\n' > board.html
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add board.py board.html tests/test_board_server.py
git commit -m "feat: localhost board server with token and origin checks"
```

---

### Task 8: Write routes

**Files:**
- Modify: `board.py` (`do_POST`, add `do_DELETE`)
- Test: `tests/test_board_server.py` (extend)

**Interfaces:**
- Produces these routes, all requiring `?token=` and same-origin:
  - `POST /api/move` — `{name, lane, stage, position}` → `{ok: true, lane: [{name, rank, stage}, ...]}`
  - `POST /api/project/<name>` — `{status?, purpose?, next_action?, note?}` → `{ok: true}`
  - `POST /api/inbox/<name>/promote` — `{lane, stage, position, purpose, next_action}` → `{ok: true}`
  - `POST /api/undo` — `{}` → `{ok: true}`
  - `DELETE /api/project/<name>` and `DELETE /api/inbox/<name>` → `{ok: true}`
  - Any `RegistryError` → HTTP 400 with `{"error": "<validator message>"}`

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_board_server.py

class TestWriteRoutes(ServerCase):
    def registry(self):
        return json.loads(self.get("/api/registry").read())

    def test_move_sets_stage_and_persists(self):
        self.post("/api/move", {"name": "A", "lane": "job", "stage": "building", "position": 0})
        self.assertEqual(self.registry()["projects"][0]["stage"], "building")

    def test_move_returns_the_new_lane_order(self):
        body = json.loads(
            self.post("/api/move", {"name": "A", "lane": "job", "stage": "spec", "position": 0}).read()
        )
        self.assertEqual(body["lane"], [{"name": "A", "rank": 1, "stage": "spec"}])

    def test_move_with_a_bogus_stage_returns_400(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.post("/api/move", {"name": "A", "lane": "job", "stage": "nope", "position": 0})
        self.assertEqual(cm.exception.code, 400)
        self.assertIn("stage", json.loads(cm.exception.read())["error"])

    def test_patch_status(self):
        self.post("/api/project/A", {"status": "paused"})
        self.assertEqual(self.registry()["projects"][0]["status"], "paused")

    def test_patch_note_gets_todays_date(self):
        self.post("/api/project/A", {"note": "did a thing"})
        update = self.registry()["projects"][0]["updates"][0]
        self.assertEqual(update["note"], "did a thing")
        self.assertRegex(update["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_promote_without_a_purpose_returns_400_and_keeps_the_record(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.post("/api/inbox/Football/promote",
                      {"lane": "job", "stage": "idea", "position": 0,
                       "purpose": "", "next_action": "go"})
        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(len(self.registry()["inbox"]), 1)

    def test_promote_succeeds_with_both_fields(self):
        self.post("/api/inbox/Football/promote",
                  {"lane": "job", "stage": "idea", "position": 0,
                   "purpose": "reporting", "next_action": "go"})
        data = self.registry()
        self.assertEqual(data["inbox"], [])
        self.assertIn("Football", [p["name"] for p in data["projects"]])

    def test_delete_project(self):
        req = urllib.request.Request(self.url("/api/project/A"), method="DELETE",
                                     headers={"Origin": f"http://127.0.0.1:{self.port}"})
        urllib.request.urlopen(req)
        self.assertEqual(self.registry()["projects"], [])

    def test_undo_restores_the_previous_state(self):
        self.post("/api/project/A", {"status": "paused"})
        self.post("/api/undo", {})
        self.assertEqual(self.registry()["projects"][0]["status"], "active")

    def test_undo_with_nothing_to_undo_returns_400(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.post("/api/undo", {})
        self.assertEqual(cm.exception.code, 400)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tests.test_board_server -v -k Write`
Expected: FAIL — routes return 404

- [ ] **Step 3: Write the implementation**

```python
# board.py — replace do_POST and add do_DELETE

    def _mutate(self, fn):
        """Run fn(data), snapshot for undo, save. Returns the saved registry."""
        with LOCK:
            data = self._load()
            snapshot = json.loads(json.dumps(data))
            fn(data)
            self._save(data)
            type(self).undo = snapshot
            return data

    def do_POST(self):
        parsed = urlparse(self.path)
        if not self._authorised(parsed):
            return self._send(403, {"error": "bad or missing token"})
        if not self._same_origin():
            return self._send(403, {"error": "cross-origin write refused"})

        parts = [p for p in parsed.path.split("/") if p]     # ["api", ...]
        try:
            body = self._body()
        except json.JSONDecodeError:
            return self._send(400, {"error": "body is not valid JSON"})

        try:
            if parts == ["api", "move"]:
                data = self._mutate(lambda d: board_ops.reorder(
                    d, body["name"], body["lane"], body["stage"], int(body.get("position", 0))))
                lane = [{"name": p["name"], "rank": p["rank"], "stage": p.get("stage")}
                        for p in board_ops.live(data, body["lane"])]
                return self._send(200, {"ok": True, "lane": lane})

            if parts == ["api", "undo"]:
                with LOCK:
                    snapshot = type(self).undo
                    if snapshot is None:
                        return self._send(400, {"error": "nothing to undo"})
                    self._save(snapshot)
                    type(self).undo = None
                return self._send(200, {"ok": True})

            if len(parts) == 3 and parts[:2] == ["api", "project"]:
                self._mutate(lambda d: board_ops.patch_project(
                    d, parts[2],
                    status=body.get("status"),
                    purpose=body.get("purpose"),
                    next_action=body.get("next_action"),
                    note=body.get("note"),
                    today=_dt.date.today().isoformat()))
                return self._send(200, {"ok": True})

            if len(parts) == 4 and parts[:2] == ["api", "inbox"] and parts[3] == "promote":
                self._mutate(lambda d: board_ops.promote(
                    d, parts[2], body["lane"], body["stage"], int(body.get("position", 0)),
                    body.get("purpose", ""), body.get("next_action", "")))
                return self._send(200, {"ok": True})

        except RegistryError as e:
            return self._send(400, {"error": str(e)})
        except KeyError as e:
            return self._send(400, {"error": f"missing field: {e.args[0]}"})

        return self._send(404, {"error": "not found"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if not self._authorised(parsed):
            return self._send(403, {"error": "bad or missing token"})
        if not self._same_origin():
            return self._send(403, {"error": "cross-origin write refused"})
        parts = [p for p in parsed.path.split("/") if p]
        try:
            if len(parts) == 3 and parts[:2] == ["api", "project"]:
                self._mutate(lambda d: board_ops.delete_project(d, parts[2]))
                return self._send(200, {"ok": True})
            if len(parts) == 3 and parts[:2] == ["api", "inbox"]:
                def drop(d):
                    before = len(d.get("inbox", []))
                    d["inbox"] = [r for r in d.get("inbox", []) if r["name"] != parts[2]]
                    if len(d["inbox"]) == before:
                        raise RegistryError(f"unknown inbox record: {parts[2]}")
                self._mutate(drop)
                return self._send(200, {"ok": True})
        except RegistryError as e:
            return self._send(400, {"error": str(e)})
        return self._send(404, {"error": "not found"})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add board.py tests/test_board_server.py
git commit -m "feat: board write routes for move, patch, promote, delete and undo"
```

---

### Task 9: The page — layout A, drag, status dropdown

Rewrite from scratch. `prototype/board.html` shows the shape but was written with no error handling and no persistence; do not copy it wholesale.

**Files:**
- Modify: `board.html` (replace the placeholder)

**Interfaces:**
- Consumes: `GET /api/registry`, `POST /api/move`, `POST /api/project/<name>`

- [ ] **Step 1: Write the page**

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Portfolio board</title>
<style>
  :root{--bg:#12141a;--panel:#1a1d26;--panel2:#20242f;--line:#2c3140;--ink:#e6e9f0;
        --dim:#98a0b3;--faint:#6b7385;--accent:#7c8cff;--bad:#ff8b8b}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
       font:14px/1.45 ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif}
  header{padding:12px 16px;border-bottom:1px solid var(--line);display:flex;gap:12px;align-items:center}
  h1{font-size:15px;margin:0;font-weight:650}
  .tabs{display:flex;gap:6px;margin-left:auto}
  .tab{background:var(--panel);border:1px solid var(--line);color:var(--dim);
       padding:5px 14px;border-radius:7px;cursor:pointer}
  .tab.on{background:var(--accent);border-color:var(--accent);color:#0d0f14;font-weight:600}
  button.plain{background:var(--panel);border:1px solid var(--line);color:var(--dim);
               padding:5px 12px;border-radius:7px;cursor:pointer}
  .cols{display:flex;gap:10px;padding:14px;overflow-x:auto;align-items:flex-start}
  .col{background:var(--panel);border:1px solid var(--line);border-radius:11px;
       min-width:224px;width:224px;flex:0 0 auto}
  .col>h2{margin:0;padding:10px 11px;font-size:11px;letter-spacing:.9px;text-transform:uppercase;
          color:var(--dim);border-bottom:1px solid var(--line);display:flex;justify-content:space-between}
  .drop{padding:9px;display:flex;flex-direction:column;gap:8px;min-height:70px}
  .col.over{outline:2px solid var(--accent);outline-offset:-2px}
  .inbox{background:#1b1726;border-color:#3a3050}
  .card{background:var(--panel2);border:1px solid var(--line);border-radius:9px;
        padding:9px 10px;cursor:grab;position:relative}
  .card.open{cursor:default}
  .card h3{margin:0 0 5px;font-size:13px;font-weight:600;padding-right:74px;word-break:break-word}
  .st{position:absolute;top:6px;right:6px;font-size:10px;padding:3px 6px;border-radius:99px;
      background:#0d0f14;color:var(--dim);border:1px solid var(--line);font-family:inherit}
  .card p{margin:0;color:var(--dim);font-size:12px;
          display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
  .bar{height:3px;background:#000;border-radius:99px;margin-top:8px;overflow:hidden}
  .bar i{display:block;height:100%;background:var(--accent)}
  .rk{color:var(--faint);font-size:10px;margin-top:4px}
  .panel{margin-top:9px;padding-top:9px;border-top:1px solid var(--line);
         display:flex;flex-direction:column;gap:6px}
  .panel label{font-size:10px;letter-spacing:.7px;text-transform:uppercase;color:var(--faint)}
  .panel textarea,.panel input{width:100%;background:#0d0f14;color:var(--ink);
        border:1px solid var(--line);border-radius:6px;padding:6px 7px;font:12px/1.4 inherit}
  .panel .missing{border-color:#7a3030}
  .up{font-size:11px;color:var(--dim);background:#0d0f14;border-radius:5px;padding:5px 7px}
  .up b{color:var(--faint);font-weight:500}
  .warn{font-size:11px;color:var(--bad);background:#2a1616;border:1px solid #5a2626;
        border-radius:6px;padding:5px 7px}
  .flash{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);z-index:99;
         background:#2a1616;color:var(--bad);border:1px solid #5a2626;padding:8px 14px;
         border-radius:8px;font-size:12.5px;display:none;max-width:70vw}
</style>
</head>
<body>
<header>
  <h1>Portfolio board</h1>
  <span id="meta" style="color:var(--faint);font-size:12px"></span>
  <div class="tabs" id="tabs"></div>
  <button class="plain" id="undo">Undo</button>
</header>
<div id="app"></div>
<div class="flash" id="flash"></div>

<script>
const TOKEN = new URLSearchParams(location.search).get("token") || "";
const STAGES = ["idea","grilled","spec","planned","building","shipped"];
const STATUSES = ["active","paused","done","dropped"];
const ARCHIVED = new Set(["done","dropped"]);
let REG = null, lane = "job", openCard = null;

function flash(msg){
  const f = document.getElementById("flash");
  f.textContent = msg; f.style.display = "block";
  clearTimeout(flash.t); flash.t = setTimeout(()=>f.style.display="none", 5000);
}
async function api(path, opts = {}){
  const sep = path.includes("?") ? "&" : "?";
  const res = await fetch(path + sep + "token=" + encodeURIComponent(TOKEN), {
    headers: {"Content-Type":"application/json"}, ...opts
  });
  if(!res.ok){
    let msg = res.statusText;
    try { msg = (await res.json()).error || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}
async function load(){ REG = await api("/api/registry"); render(); }

// any failed write reloads from disk, so the board never shows a state that was not saved
async function write(path, payload, method = "POST"){
  try {
    await api(path, {method, body: JSON.stringify(payload || {})});
  } catch(e){
    flash(e.message);
  }
  await load();
}

const idx = s => Math.max(0, STAGES.indexOf(s));
const live = l => REG.projects
  .filter(p => p.lane === l && !ARCHIVED.has(p.status))
  .sort((a,b) => (a.rank||1e6) - (b.rank||1e6));

let dragged = null;
function card(rec, from){
  const open = openCard === rec.name;
  const d = document.createElement("div");
  d.className = "card" + (open ? " open" : "");
  d.dataset.name = rec.name;
  d.draggable = !open;

  const h = document.createElement("h3"); h.textContent = rec.name;
  d.append(h);

  const sel = document.createElement("select");
  sel.className = "st";
  STATUSES.forEach(v => {
    const o = document.createElement("option");
    o.value = v; o.textContent = v; o.selected = v === (rec.status || "active");
    sel.append(o);
  });
  sel.onmousedown = e => e.stopPropagation();
  sel.onclick = e => e.stopPropagation();
  sel.onchange = e => {
    e.stopPropagation();
    if(from === "inbox"){ rec.status = sel.value; return; }
    write(`/api/project/${encodeURIComponent(rec.name)}`, {status: sel.value});
  };
  d.append(sel);

  if(!open){
    const p = document.createElement("p");
    p.textContent = rec.purpose || "— no purpose yet —";
    d.append(p);
  }
  if(from !== "inbox"){
    const b = document.createElement("div"); b.className = "bar";
    const i = document.createElement("i");
    i.style.width = ((idx(rec.stage)+1)/STAGES.length*100).toFixed(0) + "%";
    b.append(i);
    const r = document.createElement("div"); r.className = "rk";
    r.textContent = `#${rec.rank ?? "—"} · ${rec.stage || "unstaged"}`;
    d.append(b, r);
  }
  if(open) d.append(panel(rec, from));

  d.onclick = () => { openCard = open ? null : rec.name; render(); };
  d.addEventListener("dragstart", e => {
    dragged = {rec, from};
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", rec.name);
  });
  d.addEventListener("dragend", () => dragged = null);
  return d;
}

function panel(rec, from){
  const p = document.createElement("div"); p.className = "panel";
  p.onclick = e => e.stopPropagation();
  p.onmousedown = e => e.stopPropagation();

  const needsFields = from === "inbox";
  if(needsFields && (!rec.purpose || !rec.next_action)){
    const w = document.createElement("div"); w.className = "warn";
    w.textContent = "Drag onto a stage column to promote. Purpose and next action are both required first.";
    p.append(w);
  }
  const field = (key, label, tag) => {
    const l = document.createElement("label"); l.textContent = label;
    const el = document.createElement(tag);
    if(tag === "textarea") el.rows = 3;
    el.value = rec[key] || "";
    if(!el.value) el.classList.add("missing");
    el.oninput = () => { rec[key] = el.value; el.classList.toggle("missing", !el.value); };
    el.onchange = () => {
      if(from === "inbox") return;             // inbox edits are held until promotion
      write(`/api/project/${encodeURIComponent(rec.name)}`, {[key]: el.value});
    };
    p.append(l, el);
  };
  field("purpose", "purpose", "textarea");
  field("next_action", "next action", "input");

  if(from !== "inbox"){
    const l = document.createElement("label"); l.textContent = "add update";
    const add = document.createElement("input");
    add.placeholder = "one line, then Enter";
    add.onkeydown = e => {
      if(e.key !== "Enter" || !add.value.trim()) return;
      write(`/api/project/${encodeURIComponent(rec.name)}`, {note: add.value.trim()});
    };
    p.append(l, add);
    (rec.updates || []).slice(0, 6).forEach(u => {
      const d = document.createElement("div"); d.className = "up";
      const b = document.createElement("b"); b.textContent = u.date + " ";
      d.append(b, document.createTextNode(u.note));
      p.append(d);
    });
    const del = document.createElement("button");
    del.className = "plain"; del.textContent = "Delete project";
    del.onclick = () => {
      if(confirm(`Delete "${rec.name}"? This rewrites portfolio.json.`))
        write(`/api/project/${encodeURIComponent(rec.name)}`, null, "DELETE");
    };
    p.append(del);
  }
  return p;
}

function column(title, count, cls){
  const c = document.createElement("div"); c.className = "col " + (cls || "");
  const h = document.createElement("h2");
  const a = document.createElement("span"); a.textContent = title;
  const b = document.createElement("span"); b.textContent = count;
  h.append(a, b);
  const z = document.createElement("div"); z.className = "drop";
  c.append(h, z);
  return {col: c, zone: z};
}

function dropTarget(colEl, zoneEl, stage){
  colEl.addEventListener("dragover", e => { e.preventDefault(); colEl.classList.add("over"); });
  colEl.addEventListener("dragleave", () => colEl.classList.remove("over"));
  colEl.addEventListener("drop", e => {
    e.preventDefault(); colEl.classList.remove("over");
    if(!dragged) return;
    const cards = [...zoneEl.querySelectorAll(".card")];
    let position = cards.length;
    for(let i = 0; i < cards.length; i++){
      const r = cards[i].getBoundingClientRect();
      if(e.clientY < r.top + r.height/2){ position = i; break; }
    }
    const {rec, from} = dragged;
    if(from === "inbox"){
      write(`/api/inbox/${encodeURIComponent(rec.name)}/promote`,
            {lane, stage, position, purpose: rec.purpose || "", next_action: rec.next_action || ""});
    } else {
      write("/api/move", {name: rec.name, lane, stage, position});
    }
  });
}

function render(){
  const app = document.getElementById("app");
  app.textContent = "";
  const wrap = document.createElement("div"); wrap.className = "cols";

  const inbox = REG.inbox || [];
  const ib = column("Inbox", inbox.length, "inbox");
  inbox.forEach(r => ib.zone.append(card(r, "inbox")));
  wrap.append(ib.col);

  STAGES.forEach(s => {
    const list = live(lane).filter(p => p.stage === s);
    const c = column(s, list.length);
    list.forEach(p => c.zone.append(card(p, "board")));
    dropTarget(c.col, c.zone, s);
    wrap.append(c.col);
  });

  const arch = REG.projects.filter(p => ARCHIVED.has(p.status));
  const ac = column("Archive", arch.length);
  arch.forEach(p => ac.zone.append(card(p, "board")));
  wrap.append(ac.col);
  app.append(wrap);

  document.getElementById("meta").textContent =
    `${REG.projects.length} projects · ${inbox.length} inbox · ${arch.length} archived`;

  const tabs = document.getElementById("tabs");
  tabs.textContent = "";
  ["job","side"].forEach(l => {
    const b = document.createElement("button");
    b.className = "tab" + (l === lane ? " on" : "");
    b.textContent = l;
    b.onclick = () => { lane = l; openCard = null; render(); };
    tabs.append(b);
  });
}

document.getElementById("undo").onclick = () => write("/api/undo", {});
load();
</script>
</body>
</html>
```

- [ ] **Step 2: Verify the JS parses**

Run:
```bash
node -e "const fs=require('fs');const h=fs.readFileSync('board.html','utf8');new Function(h.match(/<script>([\s\S]*)<\/script>/)[1]);console.log('JS syntax OK')"
```
Expected: `JS syntax OK`

- [ ] **Step 3: Run the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS — the server tests copy `board.html` into their temp dir, so a broken file breaks `test_root_serves_the_page`.

- [ ] **Step 4: Drive it against the real registry**

```bash
python3 board.py
```

Check by hand, then stop it with ctrl-c:
1. Both lanes load; `job` shows 14 live projects, `side` shows 7.
2. Drag a card between two stage columns — the `#rank` labels renumber.
3. Change a status dropdown, then reload the page — the change survived.
4. Open a card, edit the purpose, click away, reload — the edit survived.
5. Type an update, press Enter — it appears with today's date.
6. Drag `ValdReport` out of Inbox — a red message appears and it stays in the Inbox.
7. Fill in its purpose and next action, drag again — it lands on the board.
8. Press Undo — the promotion is reversed.

- [ ] **Step 5: Verify the registry is still valid after manual testing**

```bash
python3 -c "import portfolio,pathlib;portfolio.validate(portfolio.load_registry(pathlib.Path('portfolio.json')));print('registry valid')"
python3 render.py --no-scan
```
Expected: `registry valid`, then a successful render.

- [ ] **Step 6: Commit**

```bash
git add board.html portfolio.json
git commit -m "feat: board page with drag, status dropdown and inline editing"
```

---

### Task 10: Document it and retire the prototype

**Files:**
- Modify: `README.md`
- Delete: `prototype/`

- [ ] **Step 1: Add a README section**

```markdown
## Board

```
python3 board.py
```

Opens a drag-and-drop board on `127.0.0.1` and prints the URL. The URL carries a
one-time token; `/api/*` refuses requests without it, and writes must be
same-origin. Ctrl-C stops it.

- Columns are stages; the tab switches lane. Dragging sets the stage, and the
  drop position sets priority — `rank` is recomputed for the whole lane, never
  typed.
- Status is a dropdown: `active`, `paused`, `done`, `dropped`. Done and dropped
  move to the Archive column.
- Clicking a card opens it for editing purpose, next action, and updates.
- The Inbox holds projects that are not yet ranked. Dragging one onto the board
  promotes it, which requires a purpose and a next action first.
- Undo reverses the last write.

Every write validates against `portfolio.validate` before it touches disk, backs
the file up to `portfolio.json.bak`, and replaces it atomically.
```

- [ ] **Step 2: Remove the prototype**

```bash
git rm -r prototype/
```

It stays reachable on the `worktree-portfolio-merge-editor` branch history, which is where a throwaway belongs.

- [ ] **Step 3: Run the full suite one last time**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: describe the board; retire the prototype"
```

---

## Self-Review

**Spec coverage:**

| Spec requirement | Task |
|---|---|
| 13 overlapping records updated, curation status wins | 2 |
| Portfolio purpose kept, curation phrasing becomes an update | 2 |
| 15 records to an inbox tier with no lane/rank/stage | 1, 2 |
| Merge reads the working copy, not HEAD | 3 |
| `.curation.json` archived to `.bak` | 2 (`main`), 3 |
| Post-merge assertions | 3 |
| Layout A: one lane, stage columns, job/side tab | 9 |
| Drag sets stage; drop position sets rank | 5, 9 |
| Rank recomputed per lane, never typed | 5 |
| Status is a select, not a cycle | 9 |
| Card expands for purpose / next action / add update / history | 9 |
| Empty required fields outlined in red | 9 |
| Card not draggable while open | 9 |
| Promotion blocked without purpose and next action | 6, 8, 9 — **functionally covered, flow deviates** (see below) |
| Archive drawer for done/dropped | 9 |
| Create and delete | 8 (delete), 9 (delete UI) |
| `validate()` before every write | 4, 8 |
| Atomic write and backup | 4 |
| Refuse to start on an unparseable registry | 7 (`main`) |
| Per-run token and Origin check | 7, 8 |
| Single-level undo | 8, 9 |
| Failed write shows the server's message and does not lie about state | 9 (`write()` reloads) |
| `curated_at` stamped on write | **not in the original plan; added in the final fix wave** — `board_ops.patch_project` and `promote` stamp it with `datetime.now().isoformat(timespec="seconds")`, matching `portfolio.py`'s writers. `reorder` deliberately abstains: a drag is a re-prioritisation, not a curation event, and stamping every drag would keep `render.py`'s `_last_touch` perpetually fresh and mute the staleness signal the dashboard exists to surface. |
| Stdlib only, no CDN | Global Constraints |

**Deviation found and accepted — promotion flow:** the *functional* guarantee holds and is tested (a promotion without a purpose or a next action is refused, and the inbox record is left untouched). The spec's *specified flow* was not built: the spec asked that the drop be accepted visually and the card open inline with those two fields focused and the rest of the board dimmed, with Cancel returning the card to the Inbox. What shipped instead is: open the card, type the two fields, close it (a card is undraggable while open), then drag — and a red toast if a field is missing. The guard is real; the guided modal is not.

**Gap found and accepted:** the spec's "`+` at the head of each column" for creating a project from scratch has no task. Every one of the 36 known projects arrives through the merge or the inbox, so creation is unreachable on day one. `POST /api/project` is specified in Task 8's interface block but not implemented or tested — **it is deliberately deferred**, and the README does not claim it. Add it as a follow-up once the board has been used.

**Placeholder scan:** no TBD/TODO; every code step carries real code; test bodies are complete.

**Type consistency:** `board_ops.reorder(data, name, lane, stage, position)`, `promote(data, name, lane, stage, position, purpose, next_action)`, `patch_project(data, name, *, status, purpose, next_action, note, today)`, `delete_project(data, name)`, `live(data, lane)`, `find(data, name)` — signatures used in Tasks 5, 6, 8 match their definitions. `merge_curation.merge(port, cur, now)` matches Tasks 2 and 3. Route shapes in Task 8's tests match the handler.

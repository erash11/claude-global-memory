# Portfolio Dashboard (Phase 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A two-lane (job/side) project registry + idea inbox rendered into a rich self-contained dashboard.html and 3-line pulse.md, updatable via a `/project` skill, surfaced via Artifact URL, session-start snapshot, daily scheduled render, and morning briefing.

**Architecture:** One source of truth (`portfolio.json`) mutated only through `portfolio.py` (backup + validation), rendered by `render.py` which reuses activity heuristics imported from the existing triage.py skill. Surfacing is wiring: keystone.ps1 appends pulse.md to the session snapshot; morning-cadence.ps1 runs the render daily.

**Tech Stack:** Python 3.14 at `C:\Python314\python.exe`, stdlib only (json, argparse, unittest, html, datetime, pathlib). No pip installs. PowerShell for wiring. Git repo at `C:\Users\eric_rash\Desktop\DEV\project-triage` (work happens in the current worktree checkout of it).

## Global Constraints

- Working dir for all repo tasks: the current git worktree of `project-triage` (canonical repo root: `C:\Users\eric_rash\Desktop\DEV\project-triage`).
- Python interpreter: `C:\Python314\python.exe` (run tests as `C:\Python314\python.exe -m unittest discover -s tests -v` from the repo/worktree root).
- Stdlib only — no third-party dependencies, no pip.
- Do NOT modify `C:\Users\eric_rash\.claude\skills\project-triage\triage.py` — import from it read-only.
- Generated files (`dashboard.html`, `pulse.md`, `*.bak`) are gitignored; `portfolio.json` IS tracked.
- The generator must never write `dashboard.html` if the registry fails validation (spec: never publish a blank dashboard).
- Dashboard HTML must be a single self-contained file: inline CSS/JS only, no external requests (Artifact CSP), `<meta name="viewport">` present, readable on mobile, light/dark via `prefers-color-scheme` plus `:root[data-theme="dark"]` / `:root[data-theme="light"]` overrides.
- Spec (authoritative for schema/behavior): `docs/specs/2026-07-31-portfolio-dashboard-design.md`
- Commit after every task with a conventional message; end commit messages with the Claude co-author trailer.

## File Structure

```
project-triage/
├── portfolio.json          # registry (Task 1 seeds it) — tracked
├── portfolio.py            # registry load/save/mutate + CLI (Task 1, 4)
├── render.py               # assemble + render dashboard.html & pulse.md + CLI (Tasks 2-4)
├── .gitignore              # Task 1
├── README.md               # Task 6 (setup: new-tab, scheduled wiring, URLs)
├── tests/
│   ├── test_portfolio.py   # Task 1
│   ├── test_assemble.py    # Task 2
│   └── test_render.py      # Task 3
├── docs/specs/…            # exists
└── docs/plans/…            # this file
(dashboard.html, pulse.md, portfolio.json.bak — generated, gitignored)

~/.claude/skills/project/SKILL.md          # Task 5 (new skill)
KeystoneOS/scripts/keystone.ps1            # Task 6 (append pulse to snapshot)
KeystoneOS/scripts/morning-cadence.ps1     # Task 6 (daily render step)
```

---

### Task 1: Registry module `portfolio.py` + seeded `portfolio.json`

**Files:**
- Create: `portfolio.py`, `portfolio.json`, `.gitignore`, `tests/test_portfolio.py`, `tests/__init__.py` (empty)

**Interfaces (Produces):**
- `load_registry(path: Path) -> dict` — raises `RegistryError(str)` on missing file, bad JSON, or schema violation.
- `save_registry(path: Path, data: dict) -> None` — copies existing file to `<path>.bak` first, validates `data`, writes UTF-8 pretty JSON (indent=2).
- `add_idea(data: dict, pitch: str, source: str = "") -> dict` — appends `{"captured_at": <now ISO>, "pitch": pitch, "source": source, "status": "inbox"}` to `data["ideas"]`, returns the new idea dict.
- `add_update(data: dict, name: str, note: str, next_action: str | None = None) -> dict` — appends `{"date": <today YYYY-MM-DD>, "note": note}` to the named project's `updates` (name match case-insensitive), sets `next_action` if given, stamps `curated_at`; raises `RegistryError` if project name not found.
- `validate(data: dict) -> None` — raises `RegistryError` listing all problems: top-level keys `meta`/`projects`/`ideas` present; every project has `name`(str), `lane` in {"job","side"}, `rank`(int ≥ 1), `status` in {"active","paused","done","dropped"}, `purpose`(str), `next_action`(str); ranks unique within a lane among `active` projects; every idea has `pitch`(str) and `status` in {"inbox","promoted","parked","dropped"}.
- `RegistryError(Exception)`

**Registry schema** (exactly as spec; `meta` holds `{"artifact_url": ""}`):

```json
{
  "meta": {"artifact_url": ""},
  "projects": [
    {"name": "…", "lane": "job", "rank": 1, "status": "active",
     "purpose": "…", "next_action": "…", "dev_folder": "…",
     "links": [], "updates": [{"date": "2026-07-31", "note": "…"}],
     "curated_at": "2026-07-31T12:00:00"}
  ],
  "ideas": [
    {"captured_at": "2026-07-31T12:00:00", "pitch": "…", "source": "…", "status": "inbox"}
  ]
}
```

- [ ] **Step 1: Write `.gitignore`**

```gitignore
dashboard.html
pulse.md
*.bak
__pycache__/
```

- [ ] **Step 2: Write failing tests** in `tests/test_portfolio.py` (create empty `tests/__init__.py` too):

```python
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
             "purpose": "p", "next_action": "n", "dev_folder": "",
             "links": [], "updates": [], "curated_at": "2026-07-31T00:00:00"},
        ],
        "ideas": [],
    }


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "portfolio.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_round_trip(self):
        data = minimal_registry()
        portfolio.save_registry(self.path, data)
        self.assertEqual(portfolio.load_registry(self.path), data)

    def test_save_creates_bak_of_previous_version(self):
        portfolio.save_registry(self.path, minimal_registry())
        data2 = minimal_registry()
        data2["projects"][0]["purpose"] = "changed"
        portfolio.save_registry(self.path, data2)
        bak = json.loads((self.path.parent / "portfolio.json.bak").read_text(encoding="utf-8"))
        self.assertEqual(bak["projects"][0]["purpose"], "p")

    def test_load_rejects_bad_json(self):
        self.path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(portfolio.RegistryError):
            portfolio.load_registry(self.path)

    def test_validate_rejects_bad_lane_and_duplicate_rank(self):
        data = minimal_registry()
        data["projects"].append(dict(data["projects"][0], name="Beta", lane="hobby"))
        with self.assertRaises(portfolio.RegistryError):
            portfolio.validate(data)
        data["projects"][1]["lane"] = "job"  # now duplicate rank 1 in job lane
        with self.assertRaises(portfolio.RegistryError):
            portfolio.validate(data)

    def test_add_idea_defaults_to_inbox(self):
        data = minimal_registry()
        idea = portfolio.add_idea(data, "Build X", source="reading Y")
        self.assertEqual(idea["status"], "inbox")
        self.assertEqual(data["ideas"][0]["pitch"], "Build X")
        self.assertTrue(idea["captured_at"])  # ISO timestamp present

    def test_add_update_appends_and_sets_next_action(self):
        data = minimal_registry()
        portfolio.add_update(data, "Alpha", "did a thing", next_action="do next thing")
        self.assertEqual(data["projects"][0]["updates"][-1]["note"], "did a thing")
        self.assertEqual(data["projects"][0]["next_action"], "do next thing")

    def test_add_update_unknown_project_raises(self):
        with self.assertRaises(portfolio.RegistryError):
            portfolio.add_update(minimal_registry(), "Nope", "x")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run to verify failure** — `C:\Python314\python.exe -m unittest discover -s tests -v` from repo root. Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'portfolio'`.

- [ ] **Step 4: Implement `portfolio.py`** — module docstring, then:

```python
from __future__ import annotations

import datetime as _dt
import json
import shutil
from pathlib import Path

LANES = {"job", "side"}
PROJECT_STATUSES = {"active", "paused", "done", "dropped"}
IDEA_STATUSES = {"inbox", "promoted", "parked", "dropped"}


class RegistryError(Exception):
    pass


def validate(data: dict) -> None:
    problems: list[str] = []
    for key in ("meta", "projects", "ideas"):
        if key not in data:
            problems.append(f"missing top-level key: {key}")
    ranks_seen: dict[str, set[int]] = {}
    for p in data.get("projects", []):
        name = p.get("name") or "<unnamed>"
        if not isinstance(p.get("name"), str) or not p.get("name"):
            problems.append("project with missing/empty name")
        if p.get("lane") not in LANES:
            problems.append(f"{name}: lane must be one of {sorted(LANES)}")
        if not isinstance(p.get("rank"), int) or p.get("rank", 0) < 1:
            problems.append(f"{name}: rank must be an int >= 1")
        if p.get("status") not in PROJECT_STATUSES:
            problems.append(f"{name}: status must be one of {sorted(PROJECT_STATUSES)}")
        for field in ("purpose", "next_action"):
            if not isinstance(p.get(field), str):
                problems.append(f"{name}: {field} must be a string")
        if p.get("status") == "active" and p.get("lane") in LANES and isinstance(p.get("rank"), int):
            lane_ranks = ranks_seen.setdefault(p["lane"], set())
            if p["rank"] in lane_ranks:
                problems.append(f"{name}: duplicate rank {p['rank']} in lane {p['lane']}")
            lane_ranks.add(p["rank"])
    for i in data.get("ideas", []):
        if not isinstance(i.get("pitch"), str) or not i.get("pitch"):
            problems.append("idea with missing/empty pitch")
        if i.get("status") not in IDEA_STATUSES:
            problems.append(f"idea '{i.get('pitch', '?')[:30]}': bad status")
    if problems:
        raise RegistryError("; ".join(problems))


def load_registry(path: Path) -> dict:
    if not path.exists():
        raise RegistryError(f"registry not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise RegistryError(f"registry unreadable: {e}") from e
    validate(data)
    return data


def save_registry(path: Path, data: dict) -> None:
    validate(data)
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_idea(data: dict, pitch: str, source: str = "") -> dict:
    idea = {
        "captured_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "pitch": pitch,
        "source": source,
        "status": "inbox",
    }
    data.setdefault("ideas", []).append(idea)
    return idea


def add_update(data: dict, name: str, note: str, next_action: str | None = None) -> dict:
    for p in data.get("projects", []):
        if p["name"].lower() == name.lower():
            p.setdefault("updates", []).append(
                {"date": _dt.date.today().isoformat(), "note": note}
            )
            if next_action:
                p["next_action"] = next_action
            p["curated_at"] = _dt.datetime.now().isoformat(timespec="seconds")
            return p
    raise RegistryError(f"no project named '{name}'")
```

- [ ] **Step 5: Run tests, verify all pass.**

- [ ] **Step 6: Write the seed `portfolio.json`** (validate by running `C:\Python314\python.exe -c "from pathlib import Path; import portfolio; portfolio.load_registry(Path('portfolio.json')); print('valid')"`):

```json
{
  "meta": {"artifact_url": ""},
  "projects": [
    {"name": "SPA_Presentation", "lane": "job", "rank": 1, "status": "active",
     "purpose": "S.P.A. presentation from the 2026-07-30 Chris Ruf meeting",
     "next_action": "Draft the outline from the meeting notes",
     "dev_folder": "", "links": [], "updates": [], "curated_at": "2026-07-31T12:00:00"},
    {"name": "NCAA_BestPractices_Doc", "lane": "job", "rank": 2, "status": "active",
     "purpose": "NCAA best practices document (Chris Ruf meeting deliverable)",
     "next_action": "Collect source material and set the doc skeleton",
     "dev_folder": "", "links": [], "updates": [], "curated_at": "2026-07-31T12:00:00"},
    {"name": "Sport_Tech_Vetting", "lane": "job", "rank": 3, "status": "active",
     "purpose": "Tech vetting process and framework discussed with Chris Ruf",
     "next_action": "Write the one-page vetting framework draft",
     "dev_folder": "Sport_Tech_Vetting", "links": [], "updates": [], "curated_at": "2026-07-31T12:00:00"},
    {"name": "OKRs_2026-27", "lane": "job", "rank": 4, "status": "active",
     "purpose": "Applied Performance unit goals and OKRs for this season",
     "next_action": "Review current draft against season calendar",
     "dev_folder": "", "links": [], "updates": [], "curated_at": "2026-07-31T12:00:00"},
    {"name": "Ask_The_Library", "lane": "job", "rank": 5, "status": "active",
     "purpose": "Health & Performance Evidence Library / Ask the Library",
     "next_action": "Continue current workstream",
     "dev_folder": "LibraryProject", "links": [], "updates": [], "curated_at": "2026-07-31T12:00:00"},
    {"name": "Morning_Briefing", "lane": "side", "rank": 1, "status": "active",
     "purpose": "Automated morning briefing: scrape/scour sources, report what's new in the space",
     "next_action": "Define source list and briefing format",
     "dev_folder": "morning-briefing", "links": [], "updates": [], "curated_at": "2026-07-31T12:00:00"},
    {"name": "TSSHB_Skills", "lane": "side", "rank": 2, "status": "active",
     "purpose": "Turn the Sport Science Handbook (Virgile & Lewis) principles into Claude Skills — Adam's blessing confirmed",
     "next_action": "Pick the first chapter/principle to convert into a skill",
     "dev_folder": "TSSHB_Skills", "links": [], "updates": [], "curated_at": "2026-07-31T12:00:00"},
    {"name": "SportScience_Curriculum", "lane": "side", "rank": 3, "status": "active",
     "purpose": "15-16 week sport science curriculum for students, built from existing resource docs and study materials",
     "next_action": "Sketch the week-by-week topic map",
     "dev_folder": "CPSS_BaylorSportScience_Curriculum", "links": [], "updates": [], "curated_at": "2026-07-31T12:00:00"}
  ],
  "ideas": []
}
```

- [ ] **Step 7: Commit** — `git add -A && git commit -m "feat: registry module with validation, backup, and seeded portfolio"` (+ trailer).

---

### Task 2: `render.py` data assembly (registry × triage heuristics)

**Files:**
- Create: `render.py`, `tests/test_assemble.py`

**Interfaces:**
- Consumes: `portfolio.load_registry` (Task 1).
- Produces:
  - `scan_heuristics(dev_root: Path) -> dict[str, dict]` — maps DEV folder name → `{"mtime_date": str, "days_since": float, "changed_30d": int}` by importing the installed triage skill: `sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "project-triage"))` then `import triage`; calls `triage.newest_mtime` and `triage.files_changed_in_window` per top-level folder (skip `triage.SKIP_FOLDERS` and dot-dirs). Any per-folder `OSError` → folder omitted (spec: degrade, never fail).
  - `assemble(registry: dict, heur: dict[str, dict], today: datetime.date) -> dict` — pure function, no I/O. Returns viewmodel:
    ```python
    {
      "generated": "YYYY-MM-DD",
      "front_burner": {"job": [top-2 active job projects by rank], "side": [top-2 active side]},
      "lanes": {"job": [all job projects, active first by rank, then paused/done/dropped],
                "side": [...]},
      "ideas_inbox": [ideas with status=="inbox", each + "age_days": int],
      "ideas_parked": [status=="parked"],
      "momentum": [{"name", "note", "date"} for updates or heuristic changes within last 7d],
      "artifact_url": registry["meta"].get("artifact_url", ""),
    }
    ```
    Each project in the viewmodel gains: `"last_touch": str|None` (max of latest update date and heuristic mtime_date for its dev_folder), `"stale": bool` (True when project is active and last_touch is None or ≥ 14 days before `today`), `"activity": heur.get(dev_folder)` (may be None).

- [ ] **Step 1: Write failing tests** in `tests/test_assemble.py`:

```python
import datetime
import unittest

import render


def fixture_registry():
    def proj(name, lane, rank, updates=None, dev_folder=""):
        return {"name": name, "lane": lane, "rank": rank, "status": "active",
                "purpose": "p", "next_action": f"next for {name}",
                "dev_folder": dev_folder, "links": [], "updates": updates or [],
                "curated_at": "2026-07-01T00:00:00"}
    return {
        "meta": {"artifact_url": "https://example.test/a"},
        "projects": [
            proj("JobTop", "job", 1, updates=[{"date": "2026-07-30", "note": "moved"}]),
            proj("JobTwo", "job", 2),
            proj("JobThree", "job", 3),
            proj("SideTop", "side", 1, dev_folder="side_top"),
        ],
        "ideas": [
            {"captured_at": "2026-07-01T09:00:00", "pitch": "old idea", "source": "", "status": "inbox"},
            {"captured_at": "2026-07-30T09:00:00", "pitch": "parked idea", "source": "", "status": "parked"},
        ],
    }


TODAY = datetime.date(2026, 7, 31)


class TestAssemble(unittest.TestCase):
    def setUp(self):
        self.heur = {"side_top": {"mtime_date": "2026-07-29", "days_since": 2.0, "changed_30d": 4}}
        self.vm = render.assemble(fixture_registry(), self.heur, TODAY)

    def test_front_burner_top2_by_rank(self):
        self.assertEqual([p["name"] for p in self.vm["front_burner"]["job"]], ["JobTop", "JobTwo"])
        self.assertEqual([p["name"] for p in self.vm["front_burner"]["side"]], ["SideTop"])

    def test_staleness(self):
        by_name = {p["name"]: p for p in self.vm["lanes"]["job"] + self.vm["lanes"]["side"]}
        self.assertFalse(by_name["JobTop"]["stale"])    # updated yesterday
        self.assertTrue(by_name["JobTwo"]["stale"])     # no updates, no activity
        self.assertFalse(by_name["SideTop"]["stale"])   # dev activity 2d ago

    def test_idea_inbox_with_age(self):
        self.assertEqual(len(self.vm["ideas_inbox"]), 1)
        self.assertEqual(self.vm["ideas_inbox"][0]["age_days"], 30)
        self.assertEqual(len(self.vm["ideas_parked"]), 1)

    def test_momentum_lists_recent_updates(self):
        names = [m["name"] for m in self.vm["momentum"]]
        self.assertIn("JobTop", names)
        self.assertNotIn("JobThree", names)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run, verify fail** (`ModuleNotFoundError: No module named 'render'`).
- [ ] **Step 3: Implement `render.py`** with `scan_heuristics` and `assemble` per the Produces block. Staleness rule: `last_touch = max(latest update date, activity mtime_date if dev_folder matched)`; stale iff status=="active" and (last_touch is None or (today - last_touch).days >= 14). Momentum: any project with an update dated within 7 days of `today` (note = latest such update's note), or activity `days_since <= 7` (note "recent file activity", date = mtime_date).
- [ ] **Step 4: Run tests, verify pass.**
- [ ] **Step 5: Commit** — `feat: viewmodel assembly merging registry with triage heuristics`.

---

### Task 3: Dashboard + pulse rendering

**Files:**
- Modify: `render.py` (add rendering)
- Create: `tests/test_render.py`

**Interfaces:**
- Consumes: `assemble` viewmodel (Task 2).
- Produces:
  - `render_dashboard(vm: dict) -> str` — full HTML document string.
  - `render_pulse(vm: dict) -> str` — ≤ 3 lines of plain markdown.

**Dashboard layout** (single file, inline CSS/JS, no external requests):
1. Header: "Portfolio — front burner first" + generated date.
2. **Front burner hero**: two large cards (top job, top side), each showing lane label, project name, `next_action` in large type, last-touch line. Second-ranked items as smaller cards beneath.
3. **Lanes**: two columns (stack on mobile via `@media (max-width: 700px)`), ranked cards: rank number, name, status pill, purpose, next_action, staleness flag `⚠ Nd untouched` when `stale`, latest update line.
4. **Idea inbox**: list with pitch, source, `age_days`; parked ideas inside a `<details>` collapsed block.
5. **Momentum strip**: "Moved in the last 7 days" chips.
6. Footer: how to update ("/project idea … · /project update … — Claude re-renders automatically").
Visual style: reuse the triage.py dark palette as the dark theme; define light-theme variables under `@media (prefers-color-scheme: light)` and honor `:root[data-theme="…"]` overrides (Artifact viewer toggle). All dynamic text through `html.escape`.

**Pulse format** (exactly):
```
**Front burner** · job: <name> — <next_action> · side: <name> — <next_action>
⚠ Stale: <comma-separated stale active project names>   ← line only present when non-empty
💡 Inbox: <N> idea(s) waiting                            ← line only present when N > 0
```

- [ ] **Step 1: Write failing tests** in `tests/test_render.py` (reuse the fixture via `from tests.test_assemble import fixture_registry, TODAY`):

```python
import unittest

import render
from tests.test_assemble import fixture_registry, TODAY


class TestRender(unittest.TestCase):
    def setUp(self):
        heur = {"side_top": {"mtime_date": "2026-07-29", "days_since": 2.0, "changed_30d": 4}}
        self.vm = render.assemble(fixture_registry(), heur, TODAY)
        self.html = render.render_dashboard(self.vm)

    def test_html_is_self_contained_document(self):
        self.assertIn("<!doctype html>", self.html.lower())
        self.assertIn("viewport", self.html)
        for marker in ("https://cdn", 'src="http', "@import url("):
            self.assertNotIn(marker, self.html.replace(self.vm["artifact_url"], ""))

    def test_hero_shows_top_next_actions(self):
        self.assertIn("next for JobTop", self.html)
        self.assertIn("next for SideTop", self.html)

    def test_stale_flag_and_inbox_present(self):
        self.assertIn("untouched", self.html)   # JobTwo stale flag
        self.assertIn("old idea", self.html)    # inbox pitch

    def test_pulse_three_lines_max(self):
        pulse = render.render_pulse(self.vm)
        lines = [l for l in pulse.splitlines() if l.strip()]
        self.assertLessEqual(len(lines), 3)
        self.assertIn("JobTop", lines[0])
        self.assertTrue(any("JobTwo" in l for l in lines))  # stale line
        self.assertTrue(any("1 idea" in l for l in lines))  # inbox line


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run, verify fail** (AttributeError: no `render_dashboard`).
- [ ] **Step 3: Implement** `render_dashboard` + `render_pulse` per layout spec.
- [ ] **Step 4: Run full suite, verify pass.**
- [ ] **Step 5: Commit** — `feat: dashboard and pulse rendering`.

---

### Task 4: CLI wiring + end-to-end run

**Files:**
- Modify: `render.py` (add `main()`), `portfolio.py` (add `main()`)

**Interfaces:**
- Produces (used verbatim by the Task 5 skill — do not rename flags):
  - `C:\Python314\python.exe render.py` → loads `portfolio.json` (sibling of the script), runs `scan_heuristics` over `~/Desktop/DEV`, writes `dashboard.html` + `pulse.md` next to the script, prints `wrote dashboard.html · wrote pulse.md · <N> projects · <M> inbox ideas · stale: <names or none>`. On RegistryError: print `[error] <message>` to stderr, exit 2, write nothing.
  - `--no-scan` → skip heuristics (empty dict), for fast skill-driven re-renders.
  - `C:\Python314\python.exe portfolio.py add-idea "<pitch>" --source "<source>"` → load, mutate, save, print `idea captured (<N> in inbox)`.
  - `C:\Python314\python.exe portfolio.py add-update "<name>" "<note>" --next-action "<optional>"` → load, mutate, save, print `updated <name>`.
  - Both portfolio.py verbs exit 2 with `[error] …` on RegistryError (e.g. unknown project).

- [ ] **Step 1: Implement both `main()` functions** with argparse (`portfolio.py` uses subparsers `add-idea` / `add-update`; paths resolved via `Path(__file__).resolve().parent`).
- [ ] **Step 2: End-to-end smoke test** (manual, from repo root):
  - `C:\Python314\python.exe portfolio.py add-idea "test idea" --source "smoke"` → `idea captured (1 in inbox)`
  - `C:\Python314\python.exe render.py --no-scan` → success line; `dashboard.html` and `pulse.md` exist; open dashboard.html, confirm hero + lanes + "test idea" in inbox.
  - `C:\Python314\python.exe render.py` (full scan) → success; confirm Sport_Tech_Vetting / morning-briefing cards show activity data.
  - Remove the smoke idea: edit `portfolio.json` to delete it, re-run `render.py --no-scan`.
  - `C:\Python314\python.exe -m unittest discover -s tests -v` → all pass.
- [ ] **Step 3: Commit** — `feat: CLI entry points for render and registry mutation`.

---

### Task 5: `/project` skill

**Files:**
- Create: `C:\Users\eric_rash\.claude\skills\project\SKILL.md`
- Create (memory): `C:\Users\eric_rash\.claude\projects\C--Users-eric-rash\memory\feedback_project_idea_capture.md` + pointer line in that directory's `MEMORY.md`

**Interfaces:**
- Consumes: the exact CLI commands from Task 4.

**SKILL.md content requirements** (frontmatter: `name: project`, description listing triggers: "/project", "new idea:", "log progress on", "project update", "add to my project inbox", "show my projects", "re-rank my projects"):
1. **Paths block**: repo `C:\Users\eric_rash\Desktop\DEV\project-triage`, interpreter `C:\Python314\python.exe`, registry `portfolio.json`.
2. **Verbs** (each ends with re-render + republish, see 3):
   - `idea <pitch>` → run `portfolio.py add-idea "<pitch>" --source "<conversation context, ≤8 words>"`.
   - `update <name> <note>` → `portfolio.py add-update …` (fuzzy-match name against registry names first; if ambiguous, ask).
   - `rank` → read registry, show both lanes' active projects with ranks, take the user's new order, rewrite `rank` fields directly with Edit, validate by running `render.py --no-scan`.
   - `promote <idea>` → ask lane + next_action, set idea status to `promoted`, append a new project (next free rank in lane) with Edit, then render.
   - bare `/project` → render + republish + show pulse.md contents in chat.
3. **Render + republish ritual** (after every mutation): run `render.py --no-scan`; then publish `dashboard.html` via the Artifact tool — if `meta.artifact_url` is non-empty pass it as `url`, favicon `🔥`, title "Portfolio — Front Burner"; if it was empty, write the returned URL into `meta.artifact_url` and re-run `render.py --no-scan` + republish once so the page shows its own URL.
4. **Rules**: never reorder ranks yourself; never delete projects/ideas without confirmation; on `[error]` output stop and show it; registry is the single source of truth — never edit dashboard.html.

**feedback memory file** (conversation-capture behavior, capture-insight pattern):

```markdown
---
name: project-idea-capture
description: Offer (never silently write) to file new project ideas/milestones to the portfolio inbox
metadata:
  type: feedback
---

When a conversation clearly spawns a new project idea, or completes a milestone
on a tracked portfolio project, offer once: "Want me to file that to your
project inbox / log it on <project>?" On yes, use the /project skill verbs.

**Why:** Eric's side-project ideas historically died on paper scraps; capture
must be frictionless but never silent.
**How to apply:** Offer only when the signal is clear (an "I should build…" /
"new idea…" statement or a completed deliverable on a tracked project). One
offer, no nagging. Registry: portfolio.json at
C:\Users\eric_rash\Desktop\DEV\project-triage\portfolio.json.
```

- [ ] **Step 1: Write SKILL.md** per requirements above.
- [ ] **Step 2: Write the feedback memory file** and add the pointer line to that memory dir's `MEMORY.md`.
- [ ] **Step 3: Verify** — SKILL.md frontmatter parses (name + description present), all referenced paths exist, CLI flags match Task 4 exactly.
- [ ] **Step 4: Commit** any repo-side docs touched (skill + memory live outside the repo).

---

### Task 6: Surfacing wiring (snapshot pulse, daily render, morning briefing, README)

**Files:**
- Modify: `C:\Users\eric_rash\Desktop\DEV\KeystoneOS\scripts\keystone.ps1` (snapshot section)
- Modify: `C:\Users\eric_rash\Desktop\DEV\KeystoneOS\scripts\morning-cadence.ps1`
- Create: `README.md` (repo root)

**Interfaces:**
- Consumes: `pulse.md` and `render.py` CLI (Task 4). Pulse path used in wiring is the CANONICAL checkout: `C:\Users\eric_rash\Desktop\DEV\project-triage\pulse.md` (wiring goes live only after the branch merges and Task 7 runs a real render there).

- [ ] **Step 1: Pulse into session snapshot.** Read `keystone.ps1`, find the function/section that assembles the "KeystoneOS Unified Snapshot" text (it emits `## User Profile`, `## Active Projects and Pending Decisions`, etc.). Insert a new section immediately after the snapshot header:

```powershell
$pulsePath = "C:\Users\eric_rash\Desktop\DEV\project-triage\pulse.md"
if (Test-Path $pulsePath) {
    $out += "`n## Front Burner (portfolio)`n"
    $out += (Get-Content $pulsePath -Raw)
}
```

Adapt variable names to the script's actual accumulation pattern (it may build with `Add-Content`, a StringBuilder, or an array — match it). Verify by running the snapshot generation the same way the SessionStart hook does and confirming the section appears (or is cleanly absent while pulse.md doesn't exist yet).

- [ ] **Step 2: Daily render.** In `morning-cadence.ps1`, after its existing steps, append:

```powershell
# Portfolio dashboard daily re-render (project-triage/render.py)
try {
    & "C:\Python314\python.exe" "C:\Users\eric_rash\Desktop\DEV\project-triage\render.py" 2>&1 |
        ForEach-Object { Write-Output "[portfolio] $_" }
} catch {
    Write-Output "[portfolio] render failed: $_"
}
```

(Non-fatal on failure — must never break the rest of the morning cadence.) Verify by running `morning-cadence.ps1` manually and confirming the `[portfolio]` lines appear and the rest of the cadence still completes.

- [ ] **Step 3: Morning briefing lead.** In `DEV\morning-briefing`, locate the briefing prompt/template (check `config.toml` and the `morning_briefing/` package for the report template). Add a lead section instruction: "Open with the contents of `C:\Users\eric_rash\Desktop\DEV\project-triage\pulse.md` under the heading 'Front burner today', followed by the dashboard link from portfolio.json meta.artifact_url." If the briefing is not yet operational (it's a side-lane project itself), instead add this as a TODO note in its README and record it as an update on the Morning_Briefing project via `portfolio.py add-update`.

- [ ] **Step 4: README.md** at repo root covering: what this system is (3 sentences), the one-diagram architecture from the spec, how to use `/project`, CLI reference, where surfacing is wired (keystone.ps1 section name, morning-cadence.ps1), and the **Chrome new-tab setup** (manual, Eric): install "New Tab Redirect" extension or set homepage → `file:///C:/Users/eric_rash/Desktop/DEV/project-triage/dashboard.html` (or the Artifact URL for cross-device).

- [ ] **Step 5: Commit** repo files — `feat: surfacing wiring and README`. KeystoneOS edits: commit in the KeystoneOS repo with message `feat: portfolio pulse in snapshot + daily dashboard render`.

---

### Task 7: First real render + Artifact publish + backup remote (main session)

This task runs in the main session (needs the Artifact tool), not a subagent. It happens AFTER the branch is merged/pushed so the canonical checkout has the code.

- [ ] **Step 1:** From the canonical checkout, run `C:\Python314\python.exe render.py` (full scan). Review dashboard.html visually.
- [ ] **Step 2:** Publish `dashboard.html` as an Artifact (favicon `🔥`, title "Portfolio — Front Burner", description "Eric's two-lane project front burner, idea inbox, and momentum").
- [ ] **Step 3:** Write the returned URL into `portfolio.json` → `meta.artifact_url` (via Edit), re-run `render.py --no-scan`, republish to the same URL.
- [ ] **Step 4:** Run the snapshot generation once to confirm the pulse section renders end-to-end.
- [ ] **Step 5:** Create a private GitHub repo `erash11/project-triage` (`gh repo create --private`), push. (Matches the 2026-07-28 "everything in DEV gets a private remote" practice.)
- [ ] **Step 6:** Commit any final tweaks; report the Artifact URL + local paths to Eric with the one manual step left (Chrome new-tab).

## Self-Review (done at write time)

- **Spec coverage:** registry (T1), generator+heuristics reuse (T2), dashboard+pulse (T3), CLI/error handling incl. no-render-on-invalid + .bak (T1/T4), skill+conversation capture (T5), all four surfacing channels (T6/T7 + manual new-tab documented), seed data (T1), testing strategy (T1-T4), Phase 2 exclusions honored (no session-end hook, no reMarkable sweep).
- **Placeholder scan:** none — every code step has concrete code or a fully specified interface/layout to implement against.
- **Type consistency:** `RegistryError`, `add_idea`, `add_update`, `assemble` viewmodel keys, and CLI flags are named identically across tasks.

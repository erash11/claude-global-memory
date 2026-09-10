# Standalone Post-Practice Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing session-debrief dashboard view into a standalone single-practice HTML report a coach can be handed, sharing one set of derivations with the dashboard rather than growing a second copy.

**Architecture:** Four new modules under `src/kinexon/`. `chart_assets.py` holds CSS and chart JS extracted verbatim from `build_dashboard.py` so both shells share one copy. `data_quality.py` reads a gitignored staff-curated config and computes heuristic suspicions. `debrief.py` holds every new derivation as pure functions. `build_report.py` is the standalone shell. `report.py` gains a `debrief` block in its payload; `build_dashboard.py` imports the shared assets.

**Tech Stack:** Python 3.14 (stdlib only — `sqlite3`, `statistics`, `json`, `dataclasses`), pytest for tests, vanilla JS + inline SVG in the generated page. `duckdb` is needed only for the force plate join and is already an optional dependency.

## Global Constraints

- **No athlete data in any tracked file, ever.** No real names, jersey numbers, or per-athlete figures in source, tests, fixtures, docs, or commit messages. Tests use synthetic names only (`Athlete One`, `Athlete Two`, …).
- **Generated reports are gitignored.** `dashboards/post-practice-*.html` carries names in the page and is data, not code.
- **Force plate data is read-only and never cached.** Go through the existing `forceplate.load()`. Do not add a local copy, and do not write to `forceplate.db`.
- **Python interpreter:** `C:\Users\eric_rash\AppData\Local\Python\bin\python.exe`. Use the PowerShell tool, not Bash.
- **`$env:PYTHONPATH = "src"`** must be set for every command in this plan.
- **Polarity is fixed and must not be inverted.** For exposure measures (jumps, load, density) *above* an athlete's own normal is the risk direction and takes `--above-normal`. For outcome measures (Peak Power / BM) a *decline* is the risk direction. Semantic tokens `--above-normal` / `--below-normal` already exist in the CSS; use them, never `--pole-hi` / `--pole-lo` directly.
- **Thresholds must match `verify.py` exactly** where they overlap: implausible-total is `< 0.25 × position median`, zero-session is `value == 0`.
- **No causal or prescriptive language in generated prose.** The words `hard`, `easy`, `too much`, `should`, `recommend` must never appear in verdict output. This is asserted by a test.
- **Every command runs from the worktree root**, `C:\Users\eric_rash\Desktop\DEV\Kinexon_Volleyball\.claude\worktrees\post-practice-report`.

## File Structure

| File | Responsibility |
|---|---|
| `src/kinexon/chart_assets.py` | NEW. `CSS`, `PRINT_CSS`, `HELPERS_JS`, `CHARTS_JS` as string constants. No logic. |
| `src/kinexon/data_quality.py` | NEW. Load and validate `config/data-quality.json`; compute heuristic suspects. |
| `src/kinexon/debrief.py` | NEW. Verdict, exceptions, readiness intersection, and the assembled per-practice structure. Pure functions — takes a payload dict, returns a dict. No file or database I/O. |
| `src/kinexon/build_report.py` | NEW. The standalone shell and its CLI. |
| `src/kinexon/report.py` | MOD. Adds `payload["debrief"]`. |
| `src/kinexon/build_dashboard.py` | MOD. Imports `chart_assets`; debrief tab renders the precomputed structure. |
| `config/data-quality.example.json` | NEW, tracked. Format documentation. |
| `tests/conftest.py` | NEW. Synthetic payload fixture. |
| `tests/test_data_quality.py` | NEW. |
| `tests/test_debrief.py` | NEW. |
| `tests/test_build_report.py` | NEW. Smoke test. |

---

### Task 1: Extract shared CSS and chart JS into `chart_assets.py`

Pure refactor. The dashboard's generated output must be byte-identical afterwards except for its timestamp — that is the acceptance test, and it is exact rather than eyeballed.

**Files:**
- Create: `src/kinexon/chart_assets.py`
- Modify: `src/kinexon/build_dashboard.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `chart_assets.CSS: str`, `chart_assets.PRINT_CSS: str`, `chart_assets.HELPERS_JS: str`, `chart_assets.CHARTS_JS: str`.

**Contract for consumers of `CHARTS_JS`:** it requires two globals to already exist in the page — `DATA` (the embedded payload) and `state` (an object with at least a `.metric` string key). `lineChart` reads `decimals(state.metric)` as its y-axis default. Both shells define `state` before including these assets. Do not "fix" this during extraction; changing it would alter dashboard output and break the byte-identical check.

- [ ] **Step 1: Capture the pre-refactor baseline**

The database must exist first. If `data/kinexon.db` is absent, run the ingest per the README, then:

```powershell
$env:PYTHONPATH = "src"
python -m kinexon.build_dashboard --out "$env:TEMP/dash-before.html"
```

Expected: prints a byte count. This file is the reference and is outside the repo on purpose — it carries athlete names.

- [ ] **Step 2: Create `chart_assets.py` by moving text verbatim**

Cut from `build_dashboard.py`'s `TEMPLATE` and paste into the new module. Move **text only** — do not reformat, rename, or "improve" anything.

```python
"""Design tokens and chart primitives shared by every generated page.

Extracted from build_dashboard.py so the coach dashboard and the standalone
post-practice report render from one copy rather than two that drift.

Two globals must already exist in the page before CHARTS_JS runs:

    DATA    the embedded payload
    state   an object with at least a `metric` key — lineChart reads
            decimals(state.metric) as its y-axis default

Colour follows the job the number is doing, not taste:

  * magnitude (totals, position splits)  -> one hue, length carries the value
  * polarity  (above/below own normal)   -> the validated diverging pair + neutral zero
  * ordinal   (jump-height bands)        -> steps of one sequential ramp, low to high
  * state     (flags)                    -> reserved status colours, never a series
"""

from __future__ import annotations

# Everything between <style> and </style> in the old TEMPLATE, verbatim.
CSS = r"""
  :root {
    color-scheme: light;
    ...
"""

# Old TEMPLATE lines 182-253: $, esc, num, sum, mean, median, scale, SEQ,
# BAND_STEPS, the ATH/SESS/METRIC lookups, decimals, unitOf, fmtMetric, hhmm,
# prettyType, dateLabel, valueOf, baseOf, deviation, and the tooltip handler.
# NOT `roster()` — it reads state.pos and stays in build_dashboard.py.
HELPERS_JS = r"""
const $ = s => document.querySelector(s);
...
"""

# Old TEMPLATE lines 264-497: CHART_W, svgOpen, hbars, divergingBars,
# stackedBars, heatmap, lineChart, scatter, tableFrom.
CHARTS_JS = r"""
const CHART_W = 1150;
...
"""

# Report-only. The dashboard never includes this.
PRINT_CSS = r"""
  @media print {
    .appbar, .ctrl, .btn, #tip { display:none !important; }
    body { background:#fff; }
    .card, .tile { break-inside:avoid; border-color:#ccc; }
    .qhead { break-after:avoid; }
    main { max-width:none; padding:0; }
    a[href]:after { content:""; }
  }
"""
```

Boundaries, exactly: `CSS` is the old lines 41–157. `HELPERS_JS` is 182–253. `CHARTS_JS` is 264–497. `roster` (line 227) and `state` (217–225) stay behind in `build_dashboard.py`.

- [ ] **Step 3: Rewrite `build_dashboard.py`'s TEMPLATE to interpolate**

`TEMPLATE` is a raw string, so build it by concatenation rather than f-string — the JS contains braces that would break `.format()`.

```python
from kinexon.chart_assets import CSS, HELPERS_JS, CHARTS_JS

TEMPLATE = (r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Baylor Volleyball — Kinexon practice report</title>
<style>""" + CSS + r"""</style>
</head>
<body>
""" + APPBAR + r"""
<script>
const DATA = __PAYLOAD__;
""" + HELPERS_JS + STATE_JS + CHARTS_JS + VIEWS_JS + r"""
</script>
</body>
</html>
""")
```

where `STATE_JS` holds old lines 217–230 (`state`, `roster`) and `VIEWS_JS` holds everything from `viewSession` to the closing `render()` call.

Order matters: `HELPERS_JS` defines `decimals`, `STATE_JS` defines `state`, and `CHARTS_JS` uses both — so it must come third.

- [ ] **Step 4: Verify the output is byte-identical**

```powershell
$env:PYTHONPATH = "src"
python -m kinexon.build_dashboard --out "$env:TEMP/dash-after.html"
$a = Get-Content "$env:TEMP/dash-before.html" -Raw
$b = Get-Content "$env:TEMP/dash-after.html" -Raw
# generated_at is the only legitimate difference
$rx = '"generated_at":"[^"]*"'
if (($a -replace $rx,'X') -eq ($b -replace $rx,'X')) { "IDENTICAL" } else { "DIFFERS - extraction is wrong" }
```

Expected: `IDENTICAL`. Anything else means text was altered during the move — diff the two files and fix before continuing. Do not proceed on `DIFFERS`.

- [ ] **Step 5: Delete the temp files and commit**

```powershell
Remove-Item "$env:TEMP/dash-before.html","$env:TEMP/dash-after.html"
git add src/kinexon/chart_assets.py src/kinexon/build_dashboard.py
git commit -m "refactor: extract shared CSS and chart primitives into chart_assets"
```

---

### Task 2: `data_quality.py` — the staff-curated config

**Files:**
- Create: `src/kinexon/data_quality.py`, `config/data-quality.example.json`, `tests/conftest.py`, `tests/test_data_quality.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `DataQuality` dataclass with fields `reviewed: bool`, `exclusions: list[dict]`, `path: str`
  - `load(path: str | Path | None = None) -> DataQuality`
  - `excluded_ids(dq: DataQuality, athletes: list[dict], practice_no: int) -> dict[str, dict]` — maps `athlete_id` (str) to the exclusion record
  - `suspects(payload: dict, metric: str = "jumps") -> list[dict]` — records shaped `{"athlete_id": str, "practice_no": int | None, "reason": str, "note": str}`

- [ ] **Step 1: Write the synthetic payload fixture**

Create `tests/conftest.py`. Every test in this plan builds on it. No real athlete data, ever.

```python
"""Synthetic fixtures. No real roster, no real names, no real database.

The shapes here mirror what report.build_payload emits. When that changes, this
changes with it.
"""
from __future__ import annotations

import statistics
from datetime import date, timedelta

import pytest

POSITIONS = {"OH": "Outside hitter", "MB": "Middle blocker", "S": "Setter"}


def _baseline(values_by_metric):
    """Mirror report.build_payload's baseline block."""
    out = {}
    for metric, per_session in values_by_metric.items():
        per_athlete = {}
        for session_values in per_session.values():
            for aid, v in session_values.items():
                per_athlete.setdefault(aid, []).append(v)
        out[metric] = {
            aid: {
                "mean": statistics.fmean(s),
                "sd": statistics.stdev(s) if len(s) > 1 else 0.0,
                "n": len(s),
                "min": min(s), "max": max(s),
            }
            for aid, s in per_athlete.items()
        }
    return out


def make_payload(jumps_by_practice, durations=None, athletes=None, readiness=None):
    """jumps_by_practice: {practice_no: {athlete_id: jumps}}, ids as ints."""
    athletes = athletes or [
        {"id": 1, "name": "Athlete One",   "num": 1, "pos": "OH"},
        {"id": 2, "name": "Athlete Two",   "num": 2, "pos": "OH"},
        {"id": 3, "name": "Athlete Three", "num": 3, "pos": "MB"},
        {"id": 4, "name": "Athlete Four",  "num": 4, "pos": "S"},
    ]
    durations = durations or {p: 7200 for p in jumps_by_practice}
    # Two-a-days, like the real block: practices 1-2 on day one, 3-4 on day two.
    base = date(2026, 7, 30)
    sessions = [
        {"no": p, "label": f"P{p}",
         "date": (base + timedelta(days=(p - 1) // 2)).isoformat(),
         "start": "09:00", "type": "Camp,Full", "duration_s": durations[p]}
        for p in sorted(jumps_by_practice)
    ]
    values = {"jumps": {str(p): {str(a): v for a, v in per.items()}
                        for p, per in jumps_by_practice.items()}}
    return {
        "generated_at": "2026-08-02T12:00:00",
        "block": {"first_date": sessions[0]["date"], "last_date": sessions[-1]["date"],
                  "practices": len(sessions), "athletes": len(athletes)},
        "metrics": [{"key": "jumps", "label": "Jumps", "unit": None, "family": "load"}],
        "jump_bands": [],
        "positions": POSITIONS,
        "athletes": athletes,
        "attendance": {},
        "sessions": sessions,
        "values": values,
        "squad": {},
        "baseline": _baseline(values),
        "drills": {},
        "extended_metrics": [],
        "readiness": readiness or {"available": False, "reason": "no store in tests",
                                   "tests": {}, "unmatched": [], "metrics": [],
                                   "primary": "Peak Power / BM",
                                   "block_start": "2026-07-30", "block_end": "2026-08-02",
                                   "response": None},
    }


@pytest.fixture
def payload():
    """Six practices, four athletes. P6 is short and dense; athlete 1 spikes in P6."""
    return make_payload(
        jumps_by_practice={
            1: {1: 200, 2: 210, 3: 190, 4: 150},
            2: {1: 205, 2: 205, 3: 195, 4: 155},
            3: {1: 195, 2: 215, 3: 185, 4: 145},
            4: {1: 210, 2: 200, 3: 200, 4: 150},
            5: {1: 190, 2: 208, 3: 188, 4: 152},
            6: {1: 320, 2: 202, 3: 192, 4: 148},
        },
        durations={1: 11400, 2: 5460, 3: 9600, 4: 11400, 5: 13560, 6: 3600},
    )
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_data_quality.py`:

```python
import json
import pytest
from kinexon import data_quality as dq


def test_missing_config_is_unreviewed_and_excludes_nothing(tmp_path):
    result = dq.load(tmp_path / "absent.json")
    assert result.reviewed is False
    assert result.exclusions == []


def test_present_config_is_reviewed(tmp_path):
    p = tmp_path / "dq.json"
    p.write_text(json.dumps({"exclusions": [
        {"athlete": "Athlete Two", "scope": "block", "reason": "sensor",
         "note": "flat all block", "confirmed_by": "staff",
         "confirmed_on": "2026-08-02"}]}), encoding="utf-8")
    result = dq.load(p)
    assert result.reviewed is True
    assert len(result.exclusions) == 1


def test_block_scope_excludes_every_practice(tmp_path, payload):
    p = tmp_path / "dq.json"
    p.write_text(json.dumps({"exclusions": [
        {"athlete": "Athlete Two", "scope": "block", "reason": "sensor",
         "note": "n", "confirmed_by": "s", "confirmed_on": "2026-08-02"}]}),
        encoding="utf-8")
    result = dq.load(p)
    for practice in (1, 6):
        assert "2" in dq.excluded_ids(result, payload["athletes"], practice)


def test_session_scope_excludes_only_named_practices(tmp_path, payload):
    p = tmp_path / "dq.json"
    p.write_text(json.dumps({"exclusions": [
        {"athlete": "Athlete Two", "scope": "session", "practices": [3],
         "reason": "sensor", "note": "n", "confirmed_by": "s",
         "confirmed_on": "2026-08-02"}]}), encoding="utf-8")
    result = dq.load(p)
    assert "2" in dq.excluded_ids(result, payload["athletes"], 3)
    assert "2" not in dq.excluded_ids(result, payload["athletes"], 4)


def test_unknown_athlete_fails_loudly(tmp_path, payload):
    p = tmp_path / "dq.json"
    p.write_text(json.dumps({"exclusions": [
        {"athlete": "Nobody At All", "scope": "block", "reason": "sensor",
         "note": "n", "confirmed_by": "s", "confirmed_on": "2026-08-02"}]}),
        encoding="utf-8")
    result = dq.load(p)
    with pytest.raises(ValueError, match="Nobody At All"):
        dq.excluded_ids(result, payload["athletes"], 1)


def test_invalid_reason_rejected(tmp_path):
    p = tmp_path / "dq.json"
    p.write_text(json.dumps({"exclusions": [
        {"athlete": "A", "scope": "block", "reason": "vibes", "note": "n",
         "confirmed_by": "s", "confirmed_on": "2026-08-02"}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="vibes"):
        dq.load(p)


def test_session_scope_without_practices_rejected(tmp_path):
    p = tmp_path / "dq.json"
    p.write_text(json.dumps({"exclusions": [
        {"athlete": "A", "scope": "session", "practices": [], "reason": "sensor",
         "note": "n", "confirmed_by": "s", "confirmed_on": "2026-08-02"}]}),
        encoding="utf-8")
    with pytest.raises(ValueError, match="practices"):
        dq.load(p)


def test_suspects_flags_low_block_total(payload):
    payload["values"]["jumps"]["1"]["2"] = 5
    for p in ("2", "3", "4", "5", "6"):
        payload["values"]["jumps"][p]["2"] = 5
    found = dq.suspects(payload)
    assert any(s["athlete_id"] == "2" and s["reason"] == "low_total" for s in found)


def test_suspects_flags_zero_session(payload):
    payload["values"]["jumps"]["4"]["3"] = 0
    found = dq.suspects(payload)
    assert any(s["athlete_id"] == "3" and s["reason"] == "zero_session"
               and s["practice_no"] == 4 for s in found)


def test_suspects_clean_payload_is_empty(payload):
    assert dq.suspects(payload) == []
```

- [ ] **Step 3: Run the tests to verify they fail**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_data_quality.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'kinexon.data_quality'`.

- [ ] **Step 4: Implement `data_quality.py`**

```python
"""The staff's answer to "is this number real?", and the heuristics that ask.

Two states, and the difference between them is the whole point:

  confirmed   a human wrote it in config/data-quality.json. Held out of the
              exceptions block and out of squad averages, kept visible in the
              ranked list with its reason printed.
  suspected   a heuristic noticed it. Never excluded on its own — marked as
              unreviewed and left in place.

A missing config excludes nothing and says so. So the report can neither invent
an exclusion nor quietly present unreviewed data as clean.

The heuristics here deliberately mirror verify.py's thresholds. If one moves,
move the other, or the report and the verifier will disagree about the same
athlete.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_FILE = "config/data-quality.json"
VALID_REASONS = {"sensor", "tagging", "role", "attendance"}
VALID_SCOPES = {"block", "session"}

# Mirrors verify.py's "implausible readings" check.
LOW_TOTAL_FRACTION = 0.25


@dataclass
class DataQuality:
    reviewed: bool
    exclusions: list[dict] = field(default_factory=list)
    path: str = ""


def _resolve(path: str | Path | None) -> Path:
    candidate = Path(path or os.environ.get("KINEXON_DATA_QUALITY") or CONFIG_FILE)
    if candidate.is_absolute() or candidate.exists():
        return candidate
    for parent in Path(__file__).resolve().parents:
        if (parent / candidate).exists():
            return parent / candidate
    return candidate


def load(path: str | Path | None = None) -> DataQuality:
    """Read the config. Absent is a normal outcome, not an error."""
    resolved = _resolve(path)
    try:
        raw = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return DataQuality(reviewed=False, path=str(resolved))

    exclusions = []
    for entry in raw.get("exclusions", []):
        scope = entry.get("scope", "block")
        reason = entry.get("reason", "")
        if scope not in VALID_SCOPES:
            raise ValueError(f"data-quality: scope {scope!r} is not one of {sorted(VALID_SCOPES)}")
        if reason not in VALID_REASONS:
            raise ValueError(f"data-quality: reason {reason!r} is not one of {sorted(VALID_REASONS)}")
        if scope == "session" and not entry.get("practices"):
            raise ValueError("data-quality: scope 'session' requires a non-empty practices list")
        exclusions.append({
            "athlete": entry["athlete"],
            "scope": scope,
            "practices": list(entry.get("practices") or []),
            "reason": reason,
            "note": entry.get("note", ""),
            "confirmed_by": entry.get("confirmed_by", ""),
            "confirmed_on": entry.get("confirmed_on", ""),
        })
    return DataQuality(reviewed=True, exclusions=exclusions, path=str(resolved))


def excluded_ids(dq: DataQuality, athletes: list[dict], practice_no: int) -> dict[str, dict]:
    """{athlete_id: exclusion record} for this practice.

    An entry naming an athlete who is not on the roster is a loud failure. A typo
    that silently excluded nobody would be indistinguishable from a clean review.
    """
    by_name = {a["name"]: str(a["id"]) for a in athletes}
    out: dict[str, dict] = {}
    for entry in dq.exclusions:
        if entry["athlete"] not in by_name:
            raise ValueError(
                f"data-quality names {entry['athlete']!r}, who is not on the roster")
        if entry["scope"] == "block" or practice_no in entry["practices"]:
            out[by_name[entry["athlete"]]] = entry
    return out


def suspects(payload: dict, metric: str = "jumps") -> list[dict]:
    """Heuristic suspicions. Advisory only — these never exclude anything."""
    per_practice = payload["values"].get(metric, {})
    positions = {str(a["id"]): a["pos"] for a in payload["athletes"]}

    totals: dict[str, float] = {}
    for session_values in per_practice.values():
        for aid, value in session_values.items():
            totals[aid] = totals.get(aid, 0.0) + value

    by_position: dict[str, list[float]] = {}
    for aid, total in totals.items():
        by_position.setdefault(positions.get(aid, "?"), []).append(total)

    found: list[dict] = []
    for aid, total in sorted(totals.items()):
        group = sorted(by_position[positions.get(aid, "?")])
        median = group[len(group) // 2]
        if median > 0 and total < median * LOW_TOTAL_FRACTION:
            found.append({
                "athlete_id": aid, "practice_no": None, "reason": "low_total",
                "note": f"{total:.0f} across the block against a {median:.0f} "
                        f"median for the group",
            })

    for practice, session_values in sorted(per_practice.items(), key=lambda kv: int(kv[0])):
        for aid, value in sorted(session_values.items()):
            if value == 0:
                found.append({
                    "athlete_id": aid, "practice_no": int(practice),
                    "reason": "zero_session",
                    "note": f"no {metric} recorded in a session that ran",
                })
    return found
```

- [ ] **Step 5: Run the tests to verify they pass**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_data_quality.py -v
```

Expected: 10 passed.

- [ ] **Step 6: Write the tracked example config and gitignore the real one**

Create `config/data-quality.example.json`:

```json
{
  "_comment": [
    "Copy to config/data-quality.json and fill in the staff's answers. That file is",
    "gitignored, because naming an athlete's data problem is athlete data.",
    "",
    "Only CONFIRMED problems belong here. verify.py's heuristics are suspicions, not",
    "answers — the report shows those separately as unreviewed. Writing an entry here",
    "is the act of a human deciding a number is not real.",
    "",
    "scope    'block' (every practice) or 'session' (only the listed practices).",
    "practices  required and non-empty when scope is 'session'.",
    "reason   one of: sensor, tagging, role, attendance.",
    "note     what a coach reading the report should understand. It is printed.",
    "",
    "An entry naming someone not on the roster is a hard error, not a no-op."
  ],
  "exclusions": [
    {
      "athlete": "Jane Doe",
      "scope": "block",
      "practices": [],
      "reason": "sensor",
      "note": "23 jumps across the block against a 379 median for her group",
      "confirmed_by": "staff",
      "confirmed_on": "2026-08-02"
    },
    {
      "athlete": "Sam Smith-Jones",
      "scope": "session",
      "practices": [5],
      "reason": "attendance",
      "note": "left the session early; partial data",
      "confirmed_by": "staff",
      "confirmed_on": "2026-08-02"
    }
  ]
}
```

Append to `.gitignore`, directly beneath the existing `config/name-aliases.json` entry:

```gitignore
# The data-quality review names athletes and describes their data problems.
# The .example file shows the format.
config/data-quality.json
```

- [ ] **Step 7: Commit**

```powershell
git add src/kinexon/data_quality.py config/data-quality.example.json .gitignore tests/
git commit -m "feat: staff-curated data-quality config, separate from heuristic suspicion"
```

---

### Task 3: `debrief.py` — the verdict line

**Files:**
- Create: `src/kinexon/debrief.py`, `tests/test_debrief.py`

**Interfaces:**
- Consumes: `tests/conftest.py::payload`.
- Produces:
  - `squad_totals(payload, metric) -> dict[int, float]`
  - `session_facts(payload, practice_no, metric) -> list[dict]` — each `{"kind", "value", "z", "rank_top", "rank_bottom", "phrase"}`
  - `verdict(payload, practice_no, metric) -> dict` — `{"text": str, "facts": list[dict]}`
  - Constants `VERDICT_Z = 1.0`, `BANNED_WORDS`

**Wording note:** the spec's illustrative sentence was a hand-written sketch. The template below says the same kinds of things in a form that stays grammatical for every combination of facts, which free-form assembly does not: two ordinal facts, then the numbers with their block reference.

The sketch also asserted more than the data supports — it called Practice 6 the block's lowest total, which it is not (Practice 2 is). That is exactly the failure mode the template exists to prevent: the generated verdict scores each fact before stating it, and Practice 6's total sits 0.28 SD from the block mean, so it never qualifies as notable and is never mentioned.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_debrief.py`:

```python
import pytest
from kinexon import debrief
from conftest import make_payload


def test_squad_total_sums_every_athlete(payload):
    totals = debrief.squad_totals(payload, "jumps")
    assert totals[1] == 200 + 210 + 190 + 150
    assert totals[6] == 320 + 202 + 192 + 148


def test_verdict_names_the_two_most_divergent_facts(payload):
    """P6 z-scores against the block: total +2.00, density +1.85, duration -1.45.

    The verdict takes the top two by magnitude, so duration is correctly dropped
    even though the session is genuinely the shortest. Asserting on the mechanism
    rather than on a hoped-for sentence.
    """
    text = debrief.verdict(payload, 6, "jumps")["text"].lower()
    assert "highest total" in text
    assert "highest density" in text
    assert "862 jumps at" in text
    assert "block average" in text


def test_duration_fact_phrases_the_shortest_session(payload):
    facts = {f["kind"]: f for f in debrief.session_facts(payload, 6, "jumps")}
    assert facts["duration"]["phrase"] == "shortest session"
    assert facts["duration"]["rank_bottom"] == 0


def test_verdict_is_never_causal_or_prescriptive(payload):
    for practice in range(1, 7):
        text = debrief.verdict(payload, practice, "jumps")["text"].lower()
        for word in debrief.BANNED_WORDS:
            assert word not in text, f"P{practice} verdict used {word!r}: {text}"


def test_verdict_falls_back_when_nothing_diverges():
    flat = make_payload(
        jumps_by_practice={p: {1: 200, 2: 200, 3: 200, 4: 200} for p in range(1, 7)},
        durations={p: 7200 for p in range(1, 7)},
    )
    text = debrief.verdict(flat, 3, "jumps")["text"]
    assert text.startswith("A typical session for this block")


def test_verdict_suppresses_ordinals_below_three_sessions():
    two = make_payload(
        jumps_by_practice={1: {1: 100, 2: 100}, 2: {1: 300, 2: 300}},
        durations={1: 7200, 2: 3600},
    )
    text = debrief.verdict(two, 2, "jumps")["text"]
    assert "shortest" not in text.lower()
    assert "highest" not in text.lower()
    assert "600 jumps" in text


def test_verdict_single_session_has_no_block_comparison():
    one = make_payload(jumps_by_practice={1: {1: 100, 2: 120}}, durations={1: 7200})
    text = debrief.verdict(one, 1, "jumps")["text"]
    assert "block average" not in text.lower()
    assert "220 jumps" in text
```

- [ ] **Step 2: Run the tests to verify they fail**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_debrief.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'kinexon.debrief'`.

- [ ] **Step 3: Implement the verdict half of `debrief.py`**

```python
"""Everything the post-practice report derives, as pure functions.

Kept in Python rather than in the page's JavaScript for the reason report.py
already gives: the numbers a coach sees should be checkable without a browser.
These are also the first pieces of this pipeline with enough judgement in them
to be worth a test, which is the other half of the reason.

Nothing here touches a file or a database. Everything takes the payload
report.build_payload already produced.
"""

from __future__ import annotations

import statistics

# A fact has to clear this to be worth a sentence. Below it, the session is
# ordinary and the report says so rather than manufacturing a story from noise.
VERDICT_Z = 1.0

# Never generated. The verdict reports where a session sat; it does not
# interpret, and it does not tell a coach what to do. Asserted by a test.
BANNED_WORDS = ("hard", "easy", "too much", "should", "recommend")

_PHRASES = {
    #  kind      high end             low end
    "duration": ("{o}longest session", "{o}shortest session"),
    "total":    ("{o}highest total",   "{o}lowest total"),
    "density":  ("{o}highest density", "{o}lowest density"),
}
_ORDINALS = {0: "", 1: "second-"}


def squad_totals(payload: dict, metric: str) -> dict[int, float]:
    """Squad total per practice — the sum over every athlete carrying a value.

    Matches what the dashboard's debrief view already computes, so the standalone
    report and the dashboard can never disagree about the same session.
    """
    per_practice = payload["values"].get(metric, {})
    return {s["no"]: sum(per_practice.get(str(s["no"]), {}).values())
            for s in payload["sessions"]}


def _z(value: float, series: list[float]) -> float:
    if len(series) < 2:
        return 0.0
    sd = statistics.stdev(series)
    return 0.0 if sd == 0 else (value - statistics.fmean(series)) / sd


def _ranks(value: float, series: list[float]) -> tuple[int, int]:
    """(rank from the top, rank from the bottom), both 0-indexed, ties shared."""
    return (sum(1 for v in series if v > value),
            sum(1 for v in series if v < value))


def session_facts(payload: dict, practice_no: int, metric: str) -> list[dict]:
    """Duration, total and density for this session, scored against the block.

    The z includes the session being described. Excluding it would make the same
    practice score differently depending on which report it appeared in, which is
    worse than the mild shrinkage that including it causes.
    """
    sessions = payload["sessions"]
    totals = squad_totals(payload, metric)

    series = {
        "duration": [s["duration_s"] for s in sessions],
        "total": [totals[s["no"]] for s in sessions],
        "density": [totals[s["no"]] / (s["duration_s"] / 60)
                    for s in sessions if s["duration_s"]],
    }
    this = next(s for s in sessions if s["no"] == practice_no)
    mine = {
        "duration": this["duration_s"],
        "total": totals[practice_no],
        "density": (totals[practice_no] / (this["duration_s"] / 60)
                    if this["duration_s"] else None),
    }

    facts = []
    for kind in ("duration", "total", "density"):
        value = mine[kind]
        if value is None:
            continue
        z = _z(value, series[kind])
        top, bottom = _ranks(value, series[kind])
        phrase = ""
        if len(sessions) >= 3 and abs(z) >= VERDICT_Z:
            high, low = _PHRASES[kind]
            if top in _ORDINALS and z > 0:
                phrase = high.format(o=_ORDINALS[top])
            elif bottom in _ORDINALS and z < 0:
                phrase = low.format(o=_ORDINALS[bottom])
        facts.append({"kind": kind, "value": value, "z": z,
                      "rank_top": top, "rank_bottom": bottom, "phrase": phrase})
    return facts


def verdict(payload: dict, practice_no: int, metric: str) -> dict:
    """Two sentences: where the session sat, then the numbers behind it."""
    facts = session_facts(payload, practice_no, metric)
    label = next((m["label"] for m in payload["metrics"] if m["key"] == metric), metric)
    label = label.lower()

    ranked = sorted((f for f in facts if f["phrase"]),
                    key=lambda f: abs(f["z"]), reverse=True)[:2]
    if len(ranked) == 2:
        head = f"{_cap(ranked[0]['phrase'])} and {ranked[1]['phrase']} of the block."
    elif len(ranked) == 1:
        head = f"{_cap(ranked[0]['phrase'])} of the block."
    else:
        head = "A typical session for this block on volume and density."

    by_kind = {f["kind"]: f for f in facts}
    total = by_kind["total"]["value"]
    density = by_kind.get("density", {}).get("value")

    tail = f"{total:,.0f} {label}"
    if density is not None:
        tail += f" at {density:,.2f}/min"

    sessions = payload["sessions"]
    if len(sessions) >= 2:
        totals = squad_totals(payload, metric)
        mean_total = statistics.fmean(totals.values())
        densities = [totals[s["no"]] / (s["duration_s"] / 60)
                     for s in sessions if s["duration_s"]]
        tail += f", against a block average of {mean_total:,.0f}"
        if densities and density is not None:
            tail += f" and {statistics.fmean(densities):,.2f}/min"
    tail += "."

    return {"text": f"{head} {tail}", "facts": facts}


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:]
```

- [ ] **Step 4: Run the tests to verify they pass**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_debrief.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```powershell
git add src/kinexon/debrief.py tests/test_debrief.py
git commit -m "feat: descriptive verdict line for the post-practice report"
```

---

### Task 4: `debrief.py` — exceptions, exclusions and the data-quality line

**Files:**
- Modify: `src/kinexon/debrief.py`, `tests/test_debrief.py`

**Interfaces:**
- Consumes: `debrief.squad_totals`, `data_quality.excluded_ids`, `data_quality.suspects`.
- Produces:
  - `deviation(payload, metric, practice_no, athlete_id) -> dict | None` — `{"value","mean","sd","n","pct","z"}`, mirroring the JS `deviation()`
  - `exceptions(payload, practice_no, metric, excluded: dict) -> dict` — `{"high": [...], "low": [...], "n_considered": int}`
  - Constants `EXCEPTION_Z = 1.5`, `MIN_BASELINE_N = 3`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_debrief.py`:

```python
def test_deviation_mirrors_the_dashboard(payload):
    d = debrief.deviation(payload, "jumps", 6, "1")
    assert d["value"] == 320
    assert d["n"] == 6
    assert d["z"] > 0
    assert d["pct"] == pytest.approx((320 - d["mean"]) / d["mean"] * 100)


def test_exception_flags_the_spike(payload):
    result = debrief.exceptions(payload, 6, "jumps", excluded={})
    assert [r["athlete_id"] for r in result["high"]] == ["1"]
    assert result["n_considered"] == 4


def test_exception_boundary_is_inclusive_at_one_point_five():
    # athlete 1: five values of 100 then one of X, chosen so z lands on 1.5 exactly.
    base = [100.0] * 5
    import statistics as st
    # solve X such that (X - mean) / sd == 1.5 over the six values
    lo, hi = 100.0, 1000.0
    for _ in range(200):
        mid = (lo + hi) / 2
        series = base + [mid]
        z = (mid - st.fmean(series)) / st.stdev(series)
        if z < 1.5:
            lo = mid
        else:
            hi = mid
    spike = round((lo + hi) / 2, 6)
    p = make_payload(
        jumps_by_practice={i + 1: {1: v, 2: 100} for i, v in enumerate(base + [spike])},
        durations={i: 7200 for i in range(1, 7)},
    )
    d = debrief.deviation(p, "jumps", 6, "1")
    assert d["z"] == pytest.approx(1.5, abs=1e-3)
    result = debrief.exceptions(p, 6, "jumps", excluded={})
    assert "1" in [r["athlete_id"] for r in result["high"]]


def test_short_baseline_is_ineligible():
    # athlete 2 appears in two practices only
    p = make_payload(jumps_by_practice={
        1: {1: 200, 2: 100}, 2: {1: 200}, 3: {1: 200},
        4: {1: 200}, 5: {1: 200}, 6: {1: 400, 2: 900},
    })
    result = debrief.exceptions(p, 6, "jumps", excluded={})
    assert "2" not in [r["athlete_id"] for r in result["high"]]
    assert result["n_considered"] == 1


def test_excluded_athlete_is_held_out_of_exceptions(payload):
    excluded = {"1": {"reason": "sensor", "note": "n"}}
    result = debrief.exceptions(payload, 6, "jumps", excluded=excluded)
    assert result["high"] == []
    assert result["n_considered"] == 3


def test_every_exception_carries_its_n(payload):
    result = debrief.exceptions(payload, 6, "jumps", excluded={})
    for row in result["high"] + result["low"]:
        assert row["n"] >= debrief.MIN_BASELINE_N
```

- [ ] **Step 2: Run the tests to verify they fail**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_debrief.py -v -k "deviation or exception or baseline"
```

Expected: FAIL — `AttributeError: module 'kinexon.debrief' has no attribute 'deviation'`.

- [ ] **Step 3: Implement**

Add to `src/kinexon/debrief.py`:

```python
# An athlete-session this far from her own mean is worth a coach's eye. It matches
# what the dashboard already flags, so the two views can never disagree about who
# is unusual.
EXCEPTION_Z = 1.5

# Below this many sessions, an athlete's "own normal" is not a baseline. She still
# appears in the ranked list; she is just not eligible to be called an exception.
MIN_BASELINE_N = 3


def deviation(payload: dict, metric: str, practice_no: int,
              athlete_id: str) -> dict | None:
    """One athlete's session against her own block mean. Mirrors the JS deviation()."""
    value = payload["values"].get(metric, {}).get(str(practice_no), {}).get(str(athlete_id))
    base = payload["baseline"].get(metric, {}).get(str(athlete_id))
    if value is None or not base or not base["mean"]:
        return None
    return {
        "value": value, "mean": base["mean"], "sd": base["sd"], "n": base["n"],
        "pct": (value - base["mean"]) / base["mean"] * 100,
        "z": (value - base["mean"]) / base["sd"] if base["sd"] > 0 else 0.0,
    }


def exceptions(payload: dict, practice_no: int, metric: str,
               excluded: dict[str, dict]) -> dict:
    """Athletes more than EXCEPTION_Z from their own normal in this session.

    Confirmed exclusions are removed before selection, so a sensor fault cannot
    occupy a slot in a list a coach is meant to act on. They stay in the ranked
    chart — this only governs who gets named at the top.
    """
    high, low, considered = [], [], 0
    for athlete in payload["athletes"]:
        aid = str(athlete["id"])
        if aid in excluded:
            continue
        d = deviation(payload, metric, practice_no, aid)
        if d is None or d["n"] < MIN_BASELINE_N:
            continue
        considered += 1
        if abs(d["z"]) < EXCEPTION_Z:
            continue
        row = {"athlete_id": aid, **d}
        (high if d["z"] > 0 else low).append(row)

    high.sort(key=lambda r: r["z"], reverse=True)
    low.sort(key=lambda r: r["z"])
    return {"high": high, "low": low, "n_considered": considered}
```

- [ ] **Step 4: Run the tests to verify they pass**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_debrief.py -v
```

Expected: 12 passed.

- [ ] **Step 5: Commit**

```powershell
git add src/kinexon/debrief.py tests/test_debrief.py
git commit -m "feat: exception selection that holds confirmed-bad data out"
```

---

### Task 5: `debrief.py` — the readiness intersection

**Files:**
- Modify: `src/kinexon/debrief.py`, `tests/test_debrief.py`

**Interfaces:**
- Consumes: `payload["readiness"]`, `forceplate.vald_name`, `forceplate.PRIMARY_METRIC`.
- Produces:
  - `entry_readiness(payload) -> dict[str, dict]` — `athlete_id` to `{"value","date","stale"}`
  - `readiness_flags(payload, practice_no, metric, high: list) -> dict | None`
  - Constants `STALE_DAYS = 60`, `LOW_READINESS_FRACTION = 0.25`, `MIN_FOR_QUARTILE = 4`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_debrief.py`:

```python
def _readiness(tests):
    return {"available": True, "reason": "", "tests": tests, "unmatched": [],
            "metrics": [{"key": "Peak Power / BM", "label": "Peak power / BM",
                         "unit": "W/kg", "noisy": False}],
            "primary": "Peak Power / BM", "block_start": "2026-07-30",
            "block_end": "2026-08-02", "response": None}


def test_no_readiness_section_when_store_unavailable(payload):
    assert debrief.readiness_flags(payload, 6, "jumps", high=[{"athlete_id": "1"}]) is None


def test_intersection_names_high_load_on_low_entry(payload):
    payload["readiness"] = _readiness({
        "Athlete One":   [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 40.0}}],
        "Athlete Two":   [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 55.0}}],
        "Athlete Three": [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 58.0}}],
        "Athlete Four":  [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 60.0}}],
    })
    result = debrief.readiness_flags(payload, 6, "jumps", high=[{"athlete_id": "1", "z": 2.1}])
    assert [f["athlete_id"] for f in result["flagged"]] == ["1"]
    assert result["flagged"][0]["stale"] is False


def test_high_load_on_normal_entry_is_not_flagged(payload):
    payload["readiness"] = _readiness({
        "Athlete One":   [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 60.0}}],
        "Athlete Two":   [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 40.0}}],
        "Athlete Three": [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 41.0}}],
        "Athlete Four":  [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 42.0}}],
    })
    result = debrief.readiness_flags(payload, 6, "jumps", high=[{"athlete_id": "1", "z": 2.1}])
    assert result["flagged"] == []


def test_stale_baseline_is_marked_not_dropped(payload):
    payload["readiness"] = _readiness({
        "Athlete One":   [{"date": "2026-04-23", "metrics": {"Peak Power / BM": 40.0}}],
        "Athlete Two":   [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 55.0}}],
        "Athlete Three": [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 58.0}}],
        "Athlete Four":  [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 60.0}}],
    })
    result = debrief.readiness_flags(payload, 6, "jumps", high=[{"athlete_id": "1", "z": 2.1}])
    assert result["flagged"][0]["stale"] is True
    assert result["flagged"][0]["tested_on"] == "2026-04-23"


def test_too_few_baselines_for_a_quartile(payload):
    payload["readiness"] = _readiness({
        "Athlete One": [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 40.0}}],
        "Athlete Two": [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 55.0}}],
    })
    result = debrief.readiness_flags(payload, 6, "jumps", high=[{"athlete_id": "1", "z": 2.1}])
    assert result["flagged"] == []
    assert "quartile" in result["reason"].lower()


def test_tests_on_or_after_block_start_are_not_entry_readiness(payload):
    payload["readiness"] = _readiness({
        "Athlete One": [
            {"date": "2026-07-28", "metrics": {"Peak Power / BM": 40.0}},
            {"date": "2026-08-05", "metrics": {"Peak Power / BM": 70.0}},
        ],
        "Athlete Two":   [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 55.0}}],
        "Athlete Three": [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 58.0}}],
        "Athlete Four":  [{"date": "2026-07-28", "metrics": {"Peak Power / BM": 60.0}}],
    })
    entry = debrief.entry_readiness(payload)
    assert entry["1"]["value"] == 40.0
    assert entry["1"]["date"] == "2026-07-28"


def test_polarity_exposure_up_is_risk_outcome_down_is_risk():
    """The inversion the handoff warns about, locked in a test.

    Exposure (jumps): above her own normal takes the risk pole.
    Outcome (Peak Power / BM): a decline takes the risk pole.
    """
    assert debrief.risk_pole("exposure", +1.0) == "above-normal"
    assert debrief.risk_pole("exposure", -1.0) == "below-normal"
    assert debrief.risk_pole("outcome", -1.0) == "above-normal"
    assert debrief.risk_pole("outcome", +1.0) == "below-normal"
```

- [ ] **Step 2: Run the tests to verify they fail**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_debrief.py -v -k "readiness or entry or polarity or quartile or stale"
```

Expected: FAIL — `AttributeError: module 'kinexon.debrief' has no attribute 'readiness_flags'`.

- [ ] **Step 3: Implement**

Add to `src/kinexon/debrief.py` (the `forceplate` import goes at the top with the others):

```python
from datetime import date

from kinexon import forceplate

# A baseline older than this is reported as stale rather than used as if it were
# current. Two athletes in the FA26 block were last tested 98 days out.
STALE_DAYS = 60

# "Low entry readiness" is the bottom quartile of this squad. Not a population
# norm — none exists for volleyball, which is the same reason volleyball never
# runs through the football classification engine.
LOW_READINESS_FRACTION = 0.25

# Below this many baselines a quartile is not a meaningful cut, so the section
# says so instead of flagging on a threshold it cannot support.
MIN_FOR_QUARTILE = 4


def risk_pole(measure: str, direction: float) -> str:
    """Which CSS token a move takes.

    Exposure measures (jumps, load, density) are the amount of work absorbed, so
    MORE is the direction that carries risk. Outcome measures (Peak Power / BM)
    are performance, so LESS is. Getting this backwards would quietly reverse the
    meaning of a chart, so it is one function with one test rather than a
    convention repeated at each call site.
    """
    if measure not in ("exposure", "outcome"):
        raise ValueError(f"measure must be 'exposure' or 'outcome', not {measure!r}")
    adverse = direction > 0 if measure == "exposure" else direction < 0
    return "above-normal" if adverse else "below-normal"


def _days_between(earlier: str, later: str) -> int:
    return (date.fromisoformat(later) - date.fromisoformat(earlier)).days


def entry_readiness(payload: dict) -> dict[str, dict]:
    """Each athlete's last primary-metric test strictly before the block started."""
    readiness = payload.get("readiness") or {}
    if not readiness.get("available"):
        return {}
    primary = readiness.get("primary", forceplate.PRIMARY_METRIC)
    block_start = readiness["block_start"]
    tests = readiness.get("tests", {})

    out: dict[str, dict] = {}
    for athlete in payload["athletes"]:
        history = tests.get(forceplate.vald_name(athlete["name"]), [])
        prior = [t for t in history
                 if t["date"] < block_start and primary in (t.get("metrics") or {})]
        if not prior:
            continue
        latest = max(prior, key=lambda t: t["date"])
        out[str(athlete["id"])] = {
            "value": latest["metrics"][primary],
            "date": latest["date"],
            "stale": _days_between(latest["date"], block_start) > STALE_DAYS,
        }
    return out


def readiness_flags(payload: dict, practice_no: int, metric: str,
                    high: list[dict]) -> dict | None:
    """Athletes above their own load normal today who also entered the block low.

    Entry readiness is a pre-block snapshot, not a response to today's session —
    there is no CMJ on or after the block ended, so the block's effect is still
    unmeasured. The caveat travels with the section wherever it renders.
    """
    readiness = payload.get("readiness") or {}
    if not readiness.get("available"):
        return None

    entry = entry_readiness(payload)
    values = sorted(e["value"] for e in entry.values())
    if len(values) < MIN_FOR_QUARTILE:
        return {"flagged": [], "threshold": None, "n_baselines": len(values),
                "primary": readiness.get("primary", forceplate.PRIMARY_METRIC),
                "reason": f"only {len(values)} entry baselines — too few for a "
                          f"squad quartile"}

    cut = statistics.quantiles(values, n=4)[0]
    flagged = []
    for row in high:
        aid = row["athlete_id"]
        e = entry.get(aid)
        if e is None or e["value"] > cut:
            continue
        flagged.append({"athlete_id": aid, "load_z": row.get("z"),
                        "value": e["value"], "tested_on": e["date"],
                        "stale": e["stale"]})
    flagged.sort(key=lambda f: f["value"])
    return {"flagged": flagged, "threshold": cut, "n_baselines": len(values),
            "primary": readiness.get("primary", forceplate.PRIMARY_METRIC),
            "reason": ""}
```

- [ ] **Step 4: Run the tests to verify they pass**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_debrief.py -v
```

Expected: 19 passed.

- [ ] **Step 5: Commit**

```powershell
git add src/kinexon/debrief.py tests/test_debrief.py
git commit -m "feat: high-load-on-low-entry-readiness intersection, with polarity locked by test"
```

---

### Task 6: Assemble `for_practice` and wire it into the payload

**Files:**
- Modify: `src/kinexon/debrief.py`, `src/kinexon/report.py`, `tests/test_debrief.py`

**Interfaces:**
- Consumes: everything from Tasks 2–5.
- Produces:
  - `debrief.DEBRIEF_FAMILIES = ("load", "density")`
  - `debrief.for_practice(payload, practice_no, metric="jumps", dq=None) -> dict`
  - `payload["debrief"]` shaped `{metric_key: {str(practice_no): structure}}`

**Why only two families:** a "squad total" is only meaningful for a metric you can sum. Summing `speed_avg` or `jump_height_max` across sixteen athletes produces a number with no referent, and the current dashboard will happily do it if you pick one of those in the metric picker. The precomputed debrief covers the `load` and `density` families only — the exposure metrics — which is also what keeps the payload growth bounded.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_debrief.py`:

```python
def test_for_practice_assembles_every_section(payload):
    result = debrief.for_practice(payload, 6, "jumps")
    assert result["practice_no"] == 6
    assert result["verdict"]["text"]
    assert result["headline"]["total"] == 862
    assert result["headline"]["on_sensors"] == 4
    assert result["exceptions"]["high"][0]["athlete_id"] == "1"
    assert result["data_quality"]["total"] == 4
    assert result["data_quality"]["usable"] == 4
    assert result["data_quality"]["reviewed"] is False


def test_data_quality_counts_are_scoped_to_the_session():
    # athlete 2 sat out P6 entirely
    p = make_payload(jumps_by_practice={
        1: {1: 200, 2: 200}, 2: {1: 200, 2: 200}, 3: {1: 200, 2: 200},
        4: {1: 200, 2: 200}, 5: {1: 200, 2: 200}, 6: {1: 200},
    })
    result = debrief.for_practice(p, 6, "jumps")
    assert result["data_quality"]["total"] == 1


def test_confirmed_exclusion_reduces_usable_but_keeps_the_athlete(payload, tmp_path):
    import json
    from kinexon import data_quality
    cfg = tmp_path / "dq.json"
    cfg.write_text(json.dumps({"exclusions": [
        {"athlete": "Athlete One", "scope": "block", "reason": "sensor",
         "note": "flat", "confirmed_by": "s", "confirmed_on": "2026-08-02"}]}),
        encoding="utf-8")
    result = debrief.for_practice(payload, 6, "jumps", dq=data_quality.load(cfg))
    assert result["data_quality"]["usable"] == 3
    assert result["data_quality"]["total"] == 4
    assert result["data_quality"]["reviewed"] is True
    assert [e["athlete_id"] for e in result["excluded"]] == ["1"]
    assert result["exceptions"]["high"] == []


def test_suspected_is_reported_but_not_excluded():
    # Athlete 2 must share a position group with athlete 1 for the median check to
    # have anything to compare against — athletes 3 and 4 are alone in theirs.
    p = make_payload(jumps_by_practice={
        i: {1: 200, 2: 5, 3: 200, 4: 200} for i in range(1, 7)})
    result = debrief.for_practice(p, 6, "jumps")
    assert result["excluded"] == []
    assert any(s["athlete_id"] == "2" for s in result["suspected"])
```

Note `862` in the first test is `320 + 202 + 192 + 148`.

- [ ] **Step 2: Run the tests to verify they fail**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_debrief.py -v -k "for_practice or scoped or confirmed or suspected"
```

Expected: FAIL — `AttributeError: module 'kinexon.debrief' has no attribute 'for_practice'`.

- [ ] **Step 3: Implement `for_practice`**

Add to `src/kinexon/debrief.py` (with `from kinexon import data_quality` at the top):

```python
# A debrief is only meaningful for a metric you can sum across a squad. Summing an
# average speed or a maximum jump height produces a number with no referent.
DEBRIEF_FAMILIES = ("load", "density")


def for_practice(payload: dict, practice_no: int, metric: str = "jumps",
                 dq: data_quality.DataQuality | None = None) -> dict:
    """Everything the post-practice report renders for one session."""
    if dq is None:
        dq = data_quality.DataQuality(reviewed=False)

    excluded = data_quality.excluded_ids(dq, payload["athletes"], practice_no)
    suspected = [s for s in data_quality.suspects(payload, metric)
                 if s["practice_no"] in (None, practice_no)]

    session = next(s for s in payload["sessions"] if s["no"] == practice_no)
    per_athlete = payload["values"].get(metric, {}).get(str(practice_no), {})
    total = sum(per_athlete.values())
    on_sensors = len(per_athlete)

    exc = exceptions(payload, practice_no, metric, excluded)

    return {
        "practice_no": practice_no,
        "metric": metric,
        "verdict": verdict(payload, practice_no, metric),
        "headline": {
            "total": total,
            "per_min": total / (session["duration_s"] / 60) if session["duration_s"] else None,
            "duration_s": session["duration_s"],
            "per_athlete": total / on_sensors if on_sensors else 0.0,
            "on_sensors": on_sensors,
        },
        "exceptions": exc,
        "excluded": [{"athlete_id": aid, **record} for aid, record in sorted(excluded.items())],
        "suspected": suspected,
        "data_quality": {
            # Scoped to the session, not the roster: an athlete who did not train
            # is absent from both counts rather than counted as a data problem.
            "total": on_sensors,
            "usable": on_sensors - sum(1 for aid in excluded if aid in per_athlete),
            "reviewed": dq.reviewed,
        },
        "readiness_flags": readiness_flags(payload, practice_no, metric, exc["high"]),
    }
```

- [ ] **Step 4: Wire it into the payload**

In `src/kinexon/report.py`, add `from kinexon import data_quality, debrief` to the imports, then replace the `return { ... }` at the end of `build_payload` with a named dict followed by the debrief block:

```python
    payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        ...
        "extended_metrics": extended,
    }

    # Precomputed per (metric, practice) so the dashboard tab and the standalone
    # report render the same numbers from the same source rather than each
    # deriving its own. Restricted to the exposure families — a squad total is
    # meaningless for an average speed or a maximum jump height.
    dq = data_quality.load()
    payload["debrief"] = {
        key: {str(s["no"]): debrief.for_practice(payload, s["no"], key, dq)
              for s in sessions}
        for key, _, _, family in HEADLINE_METRICS
        if family in debrief.DEBRIEF_FAMILIES
    }
    return payload
```

- [ ] **Step 5: Run the full suite and check the payload size**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/ -v
python -m kinexon.report --out "$env:TEMP/payload.json"
```

Expected: all tests pass, and the payload writes without error. Measure the debrief block's share of the payload and report the actual figure rather than assuming.

**Measured outcome:** 36,378 bytes on a 156,483-byte payload — **23.2% growth**, after removing two pieces of pure waste found by measuring rather than guessing: the verdict was embedding the ranked `facts` list that only the tests read, and every exception row carried `mean` and `sd` that each shell can already get from the `baseline` block it embeds. Trimming those took it from 36.1% to 23.2%.

Keep all eight exposure metrics at that figure. Dropping the `density` family would bring it to roughly 15% but would strip the new sections from `jumps_per_min` — the metric that carries the report's central argument, since Practice 6 is the second-lowest-total and second-densest session of the block. 36 KB on a local HTML file is not a cost worth that.

- [ ] **Step 6: Verify against the real database, then delete the temp payload**

```powershell
python -m kinexon.verify
Remove-Item "$env:TEMP/payload.json"
```

Expected: `verify` reports the same PASS/WARN set as before this change. It reads the database, which this task did not touch, so any difference means something is wrong.

- [ ] **Step 7: Commit**

```powershell
git add src/kinexon/debrief.py src/kinexon/report.py tests/test_debrief.py
git commit -m "feat: assemble the per-practice debrief and carry it in the payload"
```

---

### Task 7: `build_report.py` — the standalone shell

**Files:**
- Create: `src/kinexon/build_report.py`, `tests/test_build_report.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: `chart_assets.CSS/PRINT_CSS/HELPERS_JS/CHARTS_JS`, `report.build_payload`, `debrief.DEBRIEF_FAMILIES`.
- Produces: `narrow(payload, practice_no, metric) -> dict`, `render(payload, practice_no, metric) -> str`, `build(db_path, out_dir, practices, metric) -> list[Path]`.

Section order is fixed by the spec: header, verdict, data-quality line, exceptions, readiness intersection, tiles, ranked bars, position groups, jump-height mix, drills, data notes, footer.

- [ ] **Step 1: Write the failing smoke tests**

Create `tests/test_build_report.py`:

```python
import re
import pytest
from kinexon import build_report


def test_narrow_keeps_only_the_named_practice(payload):
    payload["debrief"] = {"jumps": {}}
    narrow = build_report.narrow(payload, 6, "jumps")
    assert [s["no"] for s in narrow["sessions"]] == [6]
    assert list(narrow["values"]["jumps"].keys()) == ["6"]
    # baselines must survive narrowing — every comparison depends on them
    assert narrow["baseline"]["jumps"]["1"]["n"] == 6


def test_render_produces_a_complete_document(payload):
    from kinexon import debrief
    payload["debrief"] = {"jumps": {"6": debrief.for_practice(payload, 6, "jumps")}}
    html = build_report.render(payload, 6, "jumps")
    assert html.startswith("<!doctype html>")
    assert html.rstrip().endswith("</html>")
    assert "__PAYLOAD__" not in html
    assert "@media print" in html


def test_render_has_no_unrendered_template_markers(payload):
    from kinexon import debrief
    payload["debrief"] = {"jumps": {"6": debrief.for_practice(payload, 6, "jumps")}}
    html = build_report.render(payload, 6, "jumps")
    assert not re.search(r"__[A-Z_]+__", html)


def test_unknown_practice_lists_the_available_ones(payload):
    payload["debrief"] = {"jumps": {}}
    with pytest.raises(ValueError, match=r"1, 2, 3, 4, 5, 6"):
        build_report.render(payload, 99, "jumps")


def test_non_exposure_metric_rejected(payload):
    payload["debrief"] = {"jumps": {}}
    with pytest.raises(ValueError, match="speed_avg"):
        build_report.render(payload, 6, "speed_avg")
```

- [ ] **Step 2: Run the tests to verify they fail**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_build_report.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'kinexon.build_report'`.

- [ ] **Step 3: Implement `build_report.py`**

```python
"""One practice, one file, no dashboard.

    python -m kinexon.build_report --practice 6

The dashboard is for browsing. This is for handing to someone: it opens without
a server, prints, and survives being emailed. It carries athlete names in the
page, so it is data and it is gitignored.

There is deliberately no metric picker. An artifact you hand someone should not
depend on which control they last touched, so the report is fixed to jumps with
jumps per minute beside it and mechanical load second. --metric overrides that
for anyone who wants a load-led version; nothing about the structure changes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kinexon import debrief
from kinexon.chart_assets import CHARTS_JS, CSS, HELPERS_JS, PRINT_CSS
from kinexon.report import HEADLINE_METRICS, build_payload

DEFAULT_METRIC = "jumps"
SECOND_METRIC = "mechanical_load"

_EXPOSURE = {key for key, _, _, family in HEADLINE_METRICS
             if family in debrief.DEBRIEF_FAMILIES}


def narrow(payload: dict, practice_no: int, metric: str) -> dict:
    """Everything this one practice needs, and nothing else.

    Baselines and the roster survive intact — every comparison on the page is an
    athlete against her own block mean, so narrowing those away would break the
    only comparison the data supports.
    """
    keep = str(practice_no)
    return {
        **payload,
        "sessions": [s for s in payload["sessions"] if s["no"] == practice_no],
        "values": {m: {keep: per.get(keep, {})} for m, per in payload["values"].items()},
        "squad": {m: {keep: per[keep]} for m, per in payload["squad"].items() if keep in per},
        "drills": {keep: payload["drills"].get(keep, [])},
        "debrief": {metric: {keep: payload["debrief"][metric][keep]}}
                   if keep in payload.get("debrief", {}).get(metric, {}) else {},
    }


def render(payload: dict, practice_no: int, metric: str = DEFAULT_METRIC) -> str:
    available = sorted(s["no"] for s in payload["sessions"])
    if practice_no not in available:
        raise ValueError(
            f"no practice {practice_no} — available: "
            + ", ".join(str(n) for n in available))
    if metric not in _EXPOSURE:
        raise ValueError(
            f"{metric!r} is not an exposure metric, so a squad total for it has no "
            f"meaning — choose one of: " + ", ".join(sorted(_EXPOSURE)))

    narrowed = narrow(payload, practice_no, metric)
    return TEMPLATE \
        .replace("__PAYLOAD__", json.dumps(narrowed, separators=(",", ":"))) \
        .replace("__METRIC__", json.dumps(metric)) \
        .replace("__SECOND__", json.dumps(SECOND_METRIC)) \
        .replace("__PRACTICE__", str(practice_no))


def build(db_path: Path, out_dir: Path, practices: list[int],
          metric: str = DEFAULT_METRIC) -> list[Path]:
    payload = build_payload(db_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for practice in practices:
        path = out_dir / f"post-practice-P{practice}.html"
        path.write_text(render(payload, practice, metric), encoding="utf-8")
        written.append(path)
    return written


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=Path("data/kinexon.db"))
    parser.add_argument("--out-dir", type=Path, default=Path("dashboards"))
    parser.add_argument("--practice", type=int, help="default: the most recent")
    parser.add_argument("--all", action="store_true", help="one file per practice")
    parser.add_argument("--metric", default=DEFAULT_METRIC)
    args = parser.parse_args(argv)

    if not args.db.exists():
        print(f"no database at {args.db} — run kinexon.ingest first", file=sys.stderr)
        return 2

    payload = build_payload(args.db)
    numbers = sorted(s["no"] for s in payload["sessions"])
    if not numbers:
        print("no practices in the database", file=sys.stderr)
        return 2

    if args.all:
        chosen = numbers
    elif args.practice is not None:
        chosen = [args.practice]
    else:
        chosen = [numbers[-1]]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for practice in chosen:
        try:
            html = render(payload, practice, args.metric)
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 2
        path = args.out_dir / f"post-practice-P{practice}.html"
        path.write_text(html, encoding="utf-8")
        print(f"{len(html):,} bytes -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Write the page template**

Append `TEMPLATE` to `build_report.py`, above `main`. It reuses the shared assets and defines the minimal `state` that `CHARTS_JS` requires.

```python
TEMPLATE = (r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Practice __PRACTICE__ — Baylor Volleyball post-practice report</title>
<style>""" + CSS + PRINT_CSS + r"""
  .verdict { font-size:17px; line-height:1.45; max-width:70ch; margin:0 0 18px; }
  .dqline  { font-size:13px; color:var(--ink-2); margin:0 0 22px; }
  .exc     { display:grid; gap:8px; margin:0 0 6px; }
  .exc-row { display:flex; gap:12px; align-items:baseline; }
  .exc-z   { font-variant-numeric:tabular-nums; font-weight:600; min-width:5.5em; }
  .exc-hi .exc-z { color:var(--above-normal); }
  .exc-lo .exc-z { color:var(--below-normal); }
  .excluded { opacity:.5; }
</style>
</head>
<body>
<main id="app"></main>
<div id="tip"></div>
<footer id="foot"></footer>
<script>
const DATA = __PAYLOAD__;
const METRIC_KEY = __METRIC__;
const SECOND_KEY = __SECOND__;
const PRACTICE = __PRACTICE__;
""" + HELPERS_JS + r"""
/* CHARTS_JS reads decimals(state.metric); the report has no picker, so this is
   the whole of its state. */
const state = {metric: METRIC_KEY, table: false};
const D = DATA.debrief[METRIC_KEY][String(PRACTICE)];
""" + CHARTS_JS + r"""
function renderReport() { /* sections 1-12, in the order the spec fixes */ }
renderReport();
</script>
</body>
</html>
""")
```

Fill `renderReport()` by porting `viewSession()` from `build_dashboard.py` — the tiles, ranked bars, position groups, jump-height mix and drill sections transfer unchanged apart from reading `PRACTICE` instead of `state.practice` and `METRIC_KEY` instead of `state.metric`. The new sections read from `D`:

- **Verdict** — `<p class="verdict">${esc(D.verdict.text)}</p>`
- **Data-quality line** — `D.data_quality.reviewed` false renders *"N of N athletes with data. No data-quality review on file"* plus, when `D.suspected.length`, *"— K unreviewed flag(s), see notes"*. True renders *"U of T athletes with usable data. X excluded — see notes"*.
- **Exceptions** — `D.exceptions.high` then `.low`, each row `ATH[r.athlete_id].name`, `${r.z>=0?'+':''}${num(r.z,1)} SD`, class `exc-hi` / `exc-lo`. Empty on both sides renders *"Nobody was more than 1.5 SD from her own normal today."* Always followed by *"(n=… practices behind each average — a prompt to look, not a finding.)"*
- **Readiness** — skip entirely when `D.readiness_flags` is null. Render `reason` when it is set and `flagged` is empty. Otherwise one row per flag with name, `load_z`, `value`, `tested_on`, and `(stale — tested <date>)` when `stale`. Always close with *"Entry readiness is a pre-block snapshot, not a response to today. No CMJ on or after the block ended exists, so the block's effect is still unmeasured."*
- **Data notes** — `D.excluded` with reason and note, `D.suspected` labelled unreviewed, any athlete with `baseline.n < 6` named as a short baseline.
- **Mechanical load line** — beneath the tiles, from `valueOf(SECOND_KEY, PRACTICE, id)` summed across athletes, with its own percentage against the block average.

Excluded athletes keep their bar in the ranked chart with `class="excluded"` and their reason in the tooltip. They are held out of the exceptions block only.

- [ ] **Step 5: Run the tests to verify they pass**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/test_build_report.py -v
```

Expected: 5 passed.

- [ ] **Step 6: Build against the real database and check it in a browser**

```powershell
$env:PYTHONPATH = "src"
python -m kinexon.build_report --all
```

Expected: six files under `dashboards/`. Open `post-practice-P6.html` and confirm: the verdict names the short dense session, the exceptions block is above the tiles, and no section is empty-but-present. Practice 1 must show the drill breakdown; the other five must show the note explaining its absence.

To screenshot, serve over HTTP — the Playwright MCP blocks `file:` URLs:

```powershell
python -m http.server 8765 --directory dashboards
```

Delete any screenshots afterwards; they carry athlete names.

- [ ] **Step 7: Gitignore the output and commit**

`dashboards/*.html` already covers `post-practice-*.html` via the existing rule, and the `!dashboards/PROTOTYPE_*.html` negation does not match it. Confirm rather than assume:

```powershell
git check-ignore -v dashboards/post-practice-P6.html
```

Expected: prints the matching `.gitignore` rule. If it prints nothing the file is tracked and the rule needs fixing before committing.

```powershell
git add src/kinexon/build_report.py tests/test_build_report.py
git commit -m "feat: standalone single-practice post-practice report"
```

---

### Task 8: Render the precomputed structure in the dashboard tab

**Files:**
- Modify: `src/kinexon/build_dashboard.py`

**Interfaces:**
- Consumes: `payload["debrief"][metric][practice]`.
- Produces: nothing new.

The point of this task is that the two shells stop being able to disagree. `viewSession` keeps its charts and drops its derivations.

- [ ] **Step 1: Replace the derived sections in `viewSession`**

In `viewSession()`, read the precomputed structure at the top and use it for the sections that now have one:

```javascript
function viewSession() {
  const p = state.practice, s = SESS[p], key = state.metric, M = METRIC[key];
  const D = (DATA.debrief[key] || {})[String(p)] || null;
  ...
```

- Add the verdict line and the data-quality line beneath the `.hook` block.
- Replace the locally computed `flagged` list with `D.exceptions`, and move it **above** the ranked chart, per §4 of the decisions doc.
- Add the readiness intersection block from `D.readiness_flags`.
- Grey excluded athletes in the ranked chart using `D.excluded`.

Keep the existing tiles, position groups, band mix and drill sections as they are — they read `valueOf` directly and need no change.

`D` is null when the metric picker is on a non-exposure metric, since only the `load` and `density` families are precomputed. Guard every new section with `if (D)` so those metrics render exactly as they do today.

- [ ] **Step 2: Rebuild and compare the two shells by eye**

```powershell
$env:PYTHONPATH = "src"
python -m kinexon.build_dashboard
python -m kinexon.build_report --practice 6
```

Open both. The dashboard's session tab on Practice 6 with the metric on jumps, and `post-practice-P6.html`, must state the same verdict, name the same exceptions, and show the same data-quality counts. A difference here means one shell is still deriving something itself.

- [ ] **Step 3: Run the full suite**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/ -v
python -m kinexon.verify
```

Expected: all tests pass; `verify` unchanged.

- [ ] **Step 4: Commit**

```powershell
git add src/kinexon/build_dashboard.py
git commit -m "feat: dashboard debrief renders the precomputed structure"
```

---

### Task 9: Documentation

**Files:**
- Modify: `README.md`, `docs/post-practice-report-decisions.md`, `docs/data-inventory.md`

- [ ] **Step 1: Update `README.md`**

In "How it works", extend section 4 to cover both shells and add the new command to Quick start:

```markdown
python -m kinexon.build_report --all     # -> dashboards/post-practice-P<N>.html
```

Add a short paragraph: the dashboard is for browsing, the report is for handing to someone; both render the same precomputed debrief, so they cannot disagree. Mention `config/data-quality.json` beside the existing `config/name-aliases.json` note, and add `tests/` to the Layout block.

- [ ] **Step 2: Mark the resolved decisions**

In `docs/post-practice-report-decisions.md`, mark §1, §2, §4, §6 and §7 **ANSWERED** in the same style §3 already uses, each with a one-line statement of the answer and a pointer to `docs/superpowers/specs/2026-08-02-post-practice-report-design.md`. Leave §5 open — it is a question for the volleyball staff, not a design decision — and leave §8 as it is.

- [ ] **Step 3: Note the config in `docs/data-inventory.md`**

In "Data-quality items to resolve with the staff", add a line explaining that once an item is decided, it is recorded in `config/data-quality.json` and the report then holds that athlete out of the exceptions block while keeping her visible in the ranked list. The four items themselves stay as they are — they still need a human answer.

- [ ] **Step 4: Commit**

```powershell
git add README.md docs/
git commit -m "docs: record the post-practice report and the decisions it settles"
```

---

## Verification Before Completion

Run all of this before calling the work done, and report actual output rather than expectation:

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/ -v          # every test passes
python -m kinexon.verify            # same PASS/WARN set as before the change
python -m kinexon.build_dashboard   # builds
python -m kinexon.build_report --all  # six files
git status --short                  # no generated HTML, no db, no screenshots staged
git log --oneline origin/main..HEAD # the commits this plan produced
```

Then grep the staged diff for athlete surnames before the final push. The handoff records this going wrong twice — once in docs, once hard-coded into `forceplate.py` — so it is a step, not a habit.

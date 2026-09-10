# Spring Evals × PFF Correlation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a unified per-athlete dataset joining Baylor's Spring 2026 eval views (keyword + semantic) with PFF on-field reality (recency-weighted grade + snaps), then produce a master Excel workbook and a written report with three layered views: validation correlation, mis-valued players, and a future-contributor watchlist.

**Architecture:** A small Python package (`src/`) of focused, single-responsibility modules run with real Python (so outputs persist to disk). Deterministic modules (extract, crosswalk, PFF blend, master assembly, analysis) are built TDD with pytest. Semantic scoring is a Claude-judgment task that emits a schema-validated JSON artifact. The name-match crosswalk is a first-class reviewable artifact with a human review gate before any correlation runs. The PFF DuckDB is accessed read-only.

**Tech Stack:** Python 3.14, duckdb (read-only against `pff.db`), openpyxl (xlsx read + workbook write), pandas/numpy, scipy.stats (Spearman/Pearson), pytest.

**Conventions:**
- Project root: `C:\Users\eric_rash\Desktop\DEV\Football\SpringPlayerEvals_SymAnalysis`
- Run commands from project root. Use `python -m pytest ...` and `python -m src.<module>`.
- Intermediate artifacts → `data/`. Final deliverables → `outputs/`.
- All PFF DB access is `SELECT` only. Never open `pff.db` writable.
- Commit after each task (this is a fresh local git repo; no remote, no push).

---

## File Structure

```
src/
  __init__.py
  config.py          # paths, constants (blend weights, tiers, position→unit, thresholds)
  extract_eval.py    # xlsx → data/eval_wide.csv, data/keyword_scores.csv, data/notes_for_scoring.json
  semantic_schema.py # validate data/semantic_scores.json + data/themes.json
  crosswalk.py       # name normalization + match 99 athletes → PFF Baylor players
  pff_metrics.py     # read-only pff.db → per-player blended grade/snaps + per-season + trend
  master.py          # join keyword+semantic+pff → data/master.csv + derived flags
  analysis.py        # correlations + mis-valued lists + watchlist → data/analysis.json
  workbook.py        # data/master.csv (+views) → outputs/SpringEvals_PFF_Master.xlsx
  report.py          # master + analysis → outputs/SpringEvals_PFF_Report.md
tests/
  __init__.py
  conftest.py
  test_extract_eval.py
  test_semantic_schema.py
  test_crosswalk.py
  test_pff_metrics.py
  test_master.py
  test_analysis.py
data/                # intermediate artifacts + the Claude-authored semantic_scores.json
outputs/             # final deliverables
```

**Data contracts (locked — later tasks depend on these exact names):**

`data/eval_wide.csv`: `athlete_id,last,first,position,pc_note,n_note,str_note,ac_note`
`data/keyword_scores.csv`: `athlete_id,keyword_pc,keyword_n,keyword_str,keyword_ac,keyword_overall,keyword_rank`
`data/notes_for_scoring.json`: list of `{athlete_id,last,first,position,PC,N,STR,AC}`
`data/semantic_scores.json`: list of `{athlete_id:int, trajectory:int(1-5), rationale:str, tier:str, sentiment:{PC,N,STR,AC each in positive|neutral|concerning}, red_flag:bool}`
`data/themes.json`: `{PC:{positive:[str],negative:[str]}, N:{...}, STR:{...}, AC:{...}}`
`data/crosswalk.csv`: `athlete_id,last,first,position,pff_player_id,pff_name,pff_position,match_confidence,reason` (confidence ∈ confident|fuzzy|unmatched)
`data/pff_metrics.csv`: `pff_player_id,grade_2023,grade_2024,grade_2025,snaps_2023,snaps_2024,snaps_2025,grade_blended,snaps_blended,career_trend` (trend ∈ improving|flat|declining|insufficient)
`data/master.csv`: all athlete fields + keyword_* + trajectory,rationale,tier,red_flag,sent_pc,sent_n,sent_str,sent_ac + pff_player_id,match_confidence,grade_blended,snaps_blended,grade_2025/2024/2023,snaps_2025/2024/2023,career_trend + flag_undervalued,flag_overvalued,flag_watchlist,flag_projection
`data/analysis.json`: `{correlations:[...], misvalued:{undervalued:[...],overvalued:[...]}, watchlist:[...], summary:{...}}`

---

## Task 0: Project scaffolding

**Files:**
- Create: `src/__init__.py`, `tests/__init__.py`, `.gitignore`, `pytest.ini`

- [ ] **Step 1: Create package markers and config files**

`src/__init__.py`: (empty file)
`tests/__init__.py`: (empty file)

`.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
.ctx-mode-*/
~$*.xlsx
```

`pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -q
```

- [ ] **Step 2: Create data/ and outputs/ directories with .gitkeep**

Create empty files `data/.gitkeep` and `outputs/.gitkeep`.

- [ ] **Step 3: Verify pytest runs (no tests yet)**

Run: `python -m pytest`
Expected: `no tests ran` (exit code 5) — confirms pytest is wired.

- [ ] **Step 4: Commit**

```bash
git add src tests .gitignore pytest.ini data/.gitkeep outputs/.gitkeep
git commit -m "chore: scaffold package, tests, data/outputs dirs"
```

---

## Task 1: Config module

**Files:**
- Create: `src/config.py`
- Test: `tests/test_extract_eval.py` (shared conftest added here)
- Create: `tests/conftest.py`

- [ ] **Step 1: Write `src/config.py`**

```python
"""Central paths and constants. No logic — import this everywhere."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"

EVAL_XLSX = ROOT / "2026 Spring Football 1on1 Exiting Meetings.xlsx"
WIDE_SHEET = "Wide Format"
RANKINGS_SHEET = "Player Rankings"

# PFF DuckDB — READ ONLY. Never open writable.
PFF_DB = Path(r"C:\Users\eric_rash\Desktop\DEV\Football\PFF_Data_Project\data\pff.db")
BAYLOR_TEAM_ID = "118"
PFF_SEASONS = (2023, 2024, 2025)
BLEND_WEIGHTS = {2025: 3, 2024: 2, 2023: 1}

TIERS = ["Strong trajectory", "Trending positive", "Mixed signals", "Needs attention"]
SENTIMENTS = ["positive", "neutral", "concerning"]
DEPARTMENTS = ["PC", "N", "STR", "AC"]

# Eval position → PFF primary unit grade_type
OFFENSE_POS = {"QB", "OL", "WR", "TE", "RB"}
DEFENSE_POS = {"LB", "DE", "DL", "S", "STAR", "CB"}
SPECIALIST_POS = {"SPECIALISTS"}

def unit_for_position(pos: str) -> str | None:
    """Return 'offense'/'defense' grade_type for an eval position, or None for specialists."""
    p = (pos or "").strip().upper()
    if p in OFFENSE_POS:
        return "offense"
    if p in DEFENSE_POS:
        return "defense"
    return None  # specialists / unknown

# Derived-flag thresholds
TRAJECTORY_WATCHLIST_MIN = 4      # semantic trajectory >=4 to be "rising"
MISVALUE_Z_THRESHOLD = 1.0        # |z(trajectory) - z(grade)| >= 1.0 => mis-valued
TREND_DELTA = 3.0                 # season grade delta for improving/declining
```

- [ ] **Step 2: Write `tests/conftest.py`**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

- [ ] **Step 3: Write failing test for `unit_for_position`**

`tests/test_extract_eval.py`:
```python
from src import config

def test_unit_for_position():
    assert config.unit_for_position("QB") == "offense"
    assert config.unit_for_position("ol") == "offense"
    assert config.unit_for_position("CB") == "defense"
    assert config.unit_for_position("STAR") == "defense"
    assert config.unit_for_position("SPECIALISTS") is None
    assert config.unit_for_position("") is None
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/test_extract_eval.py::test_unit_for_position -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/conftest.py tests/test_extract_eval.py
git commit -m "feat: config constants + position→unit mapping"
```

---

## Task 2: Extract eval data from xlsx

**Files:**
- Create: `src/extract_eval.py`
- Test: `tests/test_extract_eval.py` (extend)

- [ ] **Step 1: Write failing tests (extend `tests/test_extract_eval.py`)**

Add:
```python
import subprocess, sys, csv, json
from pathlib import Path
from src import config

def _run_extract():
    r = subprocess.run([sys.executable, "-m", "src.extract_eval"],
                       cwd=config.ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r

def test_extract_produces_all_artifacts():
    _run_extract()
    assert (config.DATA / "eval_wide.csv").exists()
    assert (config.DATA / "keyword_scores.csv").exists()
    assert (config.DATA / "notes_for_scoring.json").exists()

def test_eval_wide_has_99_athletes_first_is_bennett():
    _run_extract()
    rows = list(csv.DictReader(open(config.DATA / "eval_wide.csv", encoding="utf-8")))
    assert len(rows) == 99
    a1 = [r for r in rows if r["athlete_id"] == "1"][0]
    assert a1["last"] == "Bennett" and a1["first"] == "Nate" and a1["position"] == "QB"
    assert a1["pc_note"].strip() != "" and a1["ac_note"].strip() != ""

def test_notes_json_shape():
    _run_extract()
    notes = json.load(open(config.DATA / "notes_for_scoring.json", encoding="utf-8"))
    assert len(notes) == 99
    assert set(notes[0].keys()) == {"athlete_id","last","first","position","PC","N","STR","AC"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_extract_eval.py -v`
Expected: FAIL (`No module named 'src.extract_eval'`).

- [ ] **Step 3: Implement `src/extract_eval.py`**

```python
"""Extract eval data from the workbook into clean intermediate artifacts.

Reads 'Wide Format' (one row per athlete, 4 dept notes) and 'Player Rankings'
(existing keyword scores). Header-driven so column reorders don't break it.
"""
import csv, json
import openpyxl
from src import config

def _header_map(ws, header_row):
    return {str(ws.cell(header_row, c).value).strip(): c
            for c in range(1, ws.max_column + 1)
            if ws.cell(header_row, c).value not in (None, "")}

def extract_wide():
    wb = openpyxl.load_workbook(config.EVAL_XLSX, data_only=True, read_only=True)
    ws = wb[config.WIDE_SHEET]
    hm = _header_map(ws, 1)
    def col(name): return hm[name]
    rows = []
    for r in range(2, ws.max_row + 1):
        aid = ws.cell(r, col("Athlete ID")).value
        if aid in (None, ""):
            continue
        rows.append({
            "athlete_id": int(aid),
            "last": (ws.cell(r, col("Last Name")).value or "").strip(),
            "first": (ws.cell(r, col("First Name")).value or "").strip(),
            "position": (ws.cell(r, col("Position")).value or "").strip(),
            "pc_note": (ws.cell(r, col("PC Note")).value or "").strip(),
            "n_note": (ws.cell(r, col("N Note")).value or "").strip(),
            "str_note": (ws.cell(r, col("STR Note")).value or "").strip(),
            "ac_note": (ws.cell(r, col("AC Note")).value or "").strip(),
        })
    wb.close()
    rows.sort(key=lambda x: x["athlete_id"])
    return rows

def extract_keyword_scores():
    """Player Rankings: title row 1, headers row 2, data row 3+. Header-driven."""
    wb = openpyxl.load_workbook(config.EVAL_XLSX, data_only=True, read_only=True)
    ws = wb[config.RANKINGS_SHEET]
    hm = _header_map(ws, 2)
    # tolerant header lookup
    def find(*cands):
        for name, c in hm.items():
            low = name.lower()
            if any(cand in low for cand in cands):
                return c
        return None
    c_id = find("athlete id")
    c_pc = find("pc score"); c_n = find("n score"); c_str = find("str score")
    c_ac = find("ac score"); c_overall = find("overall", "total", "development score")
    c_rank = find("rank")
    rows = []
    for r in range(3, ws.max_row + 1):
        aid = ws.cell(r, c_id).value if c_id else None
        if aid in (None, ""):
            continue
        def num(c):
            v = ws.cell(r, c).value if c else None
            return v if isinstance(v, (int, float)) else None
        rows.append({
            "athlete_id": int(aid),
            "keyword_pc": num(c_pc), "keyword_n": num(c_n),
            "keyword_str": num(c_str), "keyword_ac": num(c_ac),
            "keyword_overall": num(c_overall), "keyword_rank": num(c_rank),
        })
    wb.close()
    return rows

def main():
    config.DATA.mkdir(exist_ok=True)
    wide = extract_wide()
    with open(config.DATA / "eval_wide.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["athlete_id","last","first","position",
                                          "pc_note","n_note","str_note","ac_note"])
        w.writeheader(); w.writerows(wide)
    kw = extract_keyword_scores()
    with open(config.DATA / "keyword_scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["athlete_id","keyword_pc","keyword_n",
                                          "keyword_str","keyword_ac","keyword_overall","keyword_rank"])
        w.writeheader(); w.writerows(kw)
    notes = [{"athlete_id": r["athlete_id"], "last": r["last"], "first": r["first"],
              "position": r["position"], "PC": r["pc_note"], "N": r["n_note"],
              "STR": r["str_note"], "AC": r["ac_note"]} for r in wide]
    json.dump(notes, open(config.DATA / "notes_for_scoring.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(f"extracted {len(wide)} athletes, {len(kw)} keyword rows")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_extract_eval.py -v`
Expected: PASS (all 4 tests). If `keyword_scores.csv` headers differ, the tolerant `find()` should still locate them; if a column is genuinely absent it stores `None` (acceptable).

- [ ] **Step 5: Commit**

```bash
git add src/extract_eval.py tests/test_extract_eval.py
git commit -m "feat: extract eval wide-format, keyword scores, notes-for-scoring"
```

---

## Task 3: Semantic-score schema validator

**Files:**
- Create: `src/semantic_schema.py`
- Test: `tests/test_semantic_schema.py`

- [ ] **Step 1: Write failing tests**

`tests/test_semantic_schema.py`:
```python
import json, pytest
from src import semantic_schema as ss
from src import config

GOOD = [{"athlete_id": i, "trajectory": 3, "rationale": "ok",
         "tier": "Mixed signals",
         "sentiment": {"PC":"positive","N":"neutral","STR":"positive","AC":"concerning"},
         "red_flag": False} for i in range(1, 100)]

def test_good_passes():
    errs = ss.validate_scores(GOOD, expected_ids=set(range(1,100)))
    assert errs == []

def test_bad_trajectory_flagged():
    bad = [dict(GOOD[0], trajectory=7)] + GOOD[1:]
    errs = ss.validate_scores(bad, expected_ids=set(range(1,100)))
    assert any("trajectory" in e for e in errs)

def test_missing_athlete_flagged():
    errs = ss.validate_scores(GOOD[:-1], expected_ids=set(range(1,100)))
    assert any("missing" in e.lower() for e in errs)

def test_bad_tier_flagged():
    bad = [dict(GOOD[0], tier="Amazing")] + GOOD[1:]
    errs = ss.validate_scores(bad, expected_ids=set(range(1,100)))
    assert any("tier" in e for e in errs)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_semantic_schema.py -v`
Expected: FAIL (`No module named 'src.semantic_schema'`).

- [ ] **Step 3: Implement `src/semantic_schema.py`**

```python
"""Validate the Claude-authored semantic_scores.json against the locked schema."""
import json
from src import config

def validate_scores(scores, expected_ids):
    errs = []
    seen = set()
    for i, s in enumerate(scores):
        aid = s.get("athlete_id")
        tag = f"[athlete_id={aid}]"
        if not isinstance(aid, int):
            errs.append(f"row {i}: athlete_id not int"); continue
        seen.add(aid)
        t = s.get("trajectory")
        if not (isinstance(t, int) and 1 <= t <= 5):
            errs.append(f"{tag} trajectory must be int 1-5, got {t!r}")
        if not str(s.get("rationale", "")).strip():
            errs.append(f"{tag} rationale empty")
        if s.get("tier") not in config.TIERS:
            errs.append(f"{tag} tier invalid: {s.get('tier')!r}")
        sent = s.get("sentiment", {})
        for dept in config.DEPARTMENTS:
            if sent.get(dept) not in config.SENTIMENTS:
                errs.append(f"{tag} sentiment[{dept}] invalid: {sent.get(dept)!r}")
        if not isinstance(s.get("red_flag"), bool):
            errs.append(f"{tag} red_flag must be bool")
    missing = expected_ids - seen
    if missing:
        errs.append(f"missing athlete_ids: {sorted(missing)}")
    extra = seen - expected_ids
    if extra:
        errs.append(f"unexpected athlete_ids: {sorted(extra)}")
    return errs

def validate_themes(themes):
    errs = []
    for dept in config.DEPARTMENTS:
        d = themes.get(dept)
        if not isinstance(d, dict) or "positive" not in d or "negative" not in d:
            errs.append(f"themes[{dept}] must have positive+negative lists")
    return errs

def main():
    scores = json.load(open(config.DATA / "semantic_scores.json", encoding="utf-8"))
    import csv
    ids = {int(r["athlete_id"]) for r in csv.DictReader(
        open(config.DATA / "eval_wide.csv", encoding="utf-8"))}
    errs = validate_scores(scores, ids)
    themes_path = config.DATA / "themes.json"
    if themes_path.exists():
        errs += validate_themes(json.load(open(themes_path, encoding="utf-8")))
    if errs:
        print("INVALID:"); [print("  -", e) for e in errs]; raise SystemExit(1)
    print(f"semantic_scores.json valid: {len(scores)} athletes")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_semantic_schema.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add src/semantic_schema.py tests/test_semantic_schema.py
git commit -m "feat: semantic-score schema validator"
```

---

## Task 4: Semantic scoring (Claude judgment task)

**Files:**
- Create: `data/semantic_scores.json`, `data/themes.json` (authored by Claude)

> This task is performed by Claude reading the notes — not by mechanical code. It is the semantic value-add over keyword matching.

- [ ] **Step 1: Generate the notes file**

Run: `python -m src.extract_eval`
Expected: `extracted 99 athletes, N keyword rows`. Confirms `data/notes_for_scoring.json` exists.

- [ ] **Step 2: Read the notes and score every athlete**

Read `data/notes_for_scoring.json` (all 99 athletes, 4 notes each). For EACH athlete, read all four department notes holistically and assign:
- `trajectory` (int 1–5): 5 = strong upward developmental trajectory across departments; 1 = concerning across the board.
- `rationale` (1–2 sentences citing the actual signal in the notes).
- `tier`: one of exactly `Strong trajectory` · `Trending positive` · `Mixed signals` · `Needs attention`.
- `sentiment`: per department `PC/N/STR/AC`, each exactly `positive` | `neutral` | `concerning`.
- `red_flag` (bool): true iff ≥2 departments are `concerning`.

Scoring guidance (apply consistently):
- Tier↔trajectory alignment: 5→Strong trajectory, 4→Trending positive, 3→Mixed signals, 1–2→Needs attention. Use judgment at boundaries but keep them consistent.
- `red_flag` must be derivable from `sentiment` (≥2 concerning). Self-check this before writing.

Write `data/semantic_scores.json` as a JSON list matching the locked schema (athlete_id, trajectory, rationale, tier, sentiment{PC,N,STR,AC}, red_flag). Use the native Write tool (not a sandbox).

- [ ] **Step 3: Extract themes**

Across all 99 athletes' notes, identify the most common positive and negative themes per department. Write `data/themes.json`:
```json
{"PC":{"positive":["..."],"negative":["..."]},
 "N":{"positive":["..."],"negative":["..."]},
 "STR":{"positive":["..."],"negative":["..."]},
 "AC":{"positive":["..."],"negative":["..."]}}
```

- [ ] **Step 4: Validate the artifacts**

Run: `python -m src.semantic_schema`
Expected: `semantic_scores.json valid: 99 athletes`. If it prints `INVALID`, fix the flagged rows and re-run until valid.

- [ ] **Step 5: Commit**

```bash
git add data/semantic_scores.json data/themes.json
git commit -m "feat: semantic trajectory scores + themes for 99 athletes"
```

---

## Task 5: Crosswalk (name match to PFF) + review gate

**Files:**
- Create: `src/crosswalk.py`
- Test: `tests/test_crosswalk.py`

- [ ] **Step 1: Write failing tests**

`tests/test_crosswalk.py`:
```python
from src import crosswalk as cw

def test_normalize_name():
    assert cw.norm_name("O'Brien", "Sean") == "sean obrien"
    assert cw.norm_name("Smith", "John Jr.") == "john smith"      # suffix dropped
    assert cw.norm_name(" Davis ", " Ryan ") == "ryan davis"

def test_match_confident_unique():
    pff = [{"pff_player_id":"10","name":"Nate Bennett","position":"QB"},
           {"pff_player_id":"11","name":"Edward Griffin","position":"QB"}]
    m = cw.match_one({"athlete_id":1,"last":"Bennett","first":"Nate","position":"QB"}, pff)
    assert m["match_confidence"] == "confident" and m["pff_player_id"] == "10"

def test_match_unmatched():
    pff = [{"pff_player_id":"10","name":"Nate Bennett","position":"QB"}]
    m = cw.match_one({"athlete_id":2,"last":"Newcomer","first":"Freshman","position":"WR"}, pff)
    assert m["match_confidence"] == "unmatched" and m["pff_player_id"] == ""

def test_match_fuzzy_position_mismatch():
    pff = [{"pff_player_id":"10","name":"Nate Bennett","position":"S"}]
    m = cw.match_one({"athlete_id":1,"last":"Bennett","first":"Nate","position":"QB"}, pff)
    assert m["match_confidence"] == "fuzzy"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_crosswalk.py -v`
Expected: FAIL (`No module named 'src.crosswalk'`).

- [ ] **Step 3: Implement `src/crosswalk.py`**

```python
"""Match the 99 spring athletes to PFF Baylor players by normalized name.

Confidence:
  confident  - unique normalized full-name match (position compatible or specialist)
  fuzzy      - matched name but position group disagrees, OR >1 candidate
  unmatched  - no PFF Baylor name match (expected for freshmen/transfers/walk-ons)
PFF DB is opened READ ONLY.
"""
import csv, re, unicodedata
import duckdb
from src import config

_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}

def norm_name(last, first):
    full = f"{first} {last}"
    full = unicodedata.normalize("NFKD", full).encode("ascii", "ignore").decode()
    full = full.lower().replace(".", " ")
    full = re.sub(r"[^a-z\s]", "", full)            # drop apostrophes/hyphens
    toks = [t for t in full.split() if t and t not in _SUFFIXES]
    return " ".join(toks)

def _pos_compatible(eval_pos, pff_pos):
    u = config.unit_for_position(eval_pos)
    if u is None:
        return True  # specialist — don't penalize on position
    off = {"QB","RB","HB","FB","WR","TE","T","G","C","OL","OT","OG"}
    deff = {"DE","DT","DL","NT","EDGE","LB","ILB","OLB","MLB","S","FS","SS","CB","DB","STAR","NB"}
    p = (pff_pos or "").upper()
    return (p in off) if u == "offense" else (p in deff)

def match_one(athlete, pff_players):
    key = norm_name(athlete["last"], athlete["first"])
    cands = [p for p in pff_players if norm_name(*_split(p["name"])) == key]
    if not cands:
        return _row(athlete, None, "unmatched", "no PFF Baylor name match")
    if len(cands) > 1:
        return _row(athlete, cands[0], "fuzzy", f"{len(cands)} PFF candidates with same name")
    c = cands[0]
    if _pos_compatible(athlete["position"], c["position"]):
        return _row(athlete, c, "confident", "unique name + compatible position")
    return _row(athlete, c, "fuzzy", f"position mismatch eval={athlete['position']} pff={c['position']}")

def _split(name):
    parts = name.split()
    if len(parts) >= 2:
        return parts[-1], " ".join(parts[:-1])   # last, first
    return name, ""

def _row(athlete, pff, conf, reason):
    return {"athlete_id": athlete["athlete_id"], "last": athlete["last"],
            "first": athlete["first"], "position": athlete["position"],
            "pff_player_id": (pff["pff_player_id"] if pff else ""),
            "pff_name": (pff["name"] if pff else ""),
            "pff_position": (pff["position"] if pff else ""),
            "match_confidence": conf, "reason": reason}

def load_pff_baylor_players():
    con = duckdb.connect(str(config.PFF_DB), read_only=True)
    rows = con.execute(f"""
        SELECT DISTINCT p.pff_player_id, p.name,
               FIRST_VALUE(g.position) OVER (PARTITION BY p.pff_player_id
                   ORDER BY g.season DESC) AS position
        FROM pff_grades g JOIN players p USING(pff_player_id)
        WHERE CAST(g.team_id AS VARCHAR) = '{config.BAYLOR_TEAM_ID}'
    """).fetchall()
    con.close()
    # dedupe (window can repeat); keep first position per id
    out, seen = [], set()
    for pid, name, pos in rows:
        if pid in seen: continue
        seen.add(pid)
        out.append({"pff_player_id": str(pid), "name": name, "position": pos})
    return out

def main():
    athletes = list(csv.DictReader(open(config.DATA / "eval_wide.csv", encoding="utf-8")))
    for a in athletes:
        a["athlete_id"] = int(a["athlete_id"])
    pff = load_pff_baylor_players()
    rows = [match_one(a, pff) for a in athletes]
    with open(config.DATA / "crosswalk.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["athlete_id","last","first","position",
            "pff_player_id","pff_name","pff_position","match_confidence","reason"])
        w.writeheader(); w.writerows(rows)
    from collections import Counter
    c = Counter(r["match_confidence"] for r in rows)
    print(f"crosswalk: {dict(c)} (total {len(rows)})")
    print("REVIEW NEEDED (fuzzy/unmatched):")
    for r in rows:
        if r["match_confidence"] != "confident":
            print(f"  id={r['athlete_id']:>3} {r['first']} {r['last']} ({r['position']}) "
                  f"-> {r['match_confidence']}: {r['reason']}"
                  f"{' | pff='+r['pff_name'] if r['pff_name'] else ''}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_crosswalk.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Run the crosswalk against real data**

Run: `python -m src.crosswalk`
Expected: prints confidence counts + a REVIEW list of fuzzy/unmatched athletes. Writes `data/crosswalk.csv`.

- [ ] **Step 6: HUMAN REVIEW GATE**

Present the fuzzy/unmatched list to the user. For each, confirm the correct `pff_player_id` (or confirm "no PFF history → leave unmatched / projection cohort"). Apply any corrections by editing `data/crosswalk.csv` (set `pff_player_id`, `pff_name`, and `match_confidence` to `confident`). **Do not proceed to Task 7 until the user signs off on the crosswalk.**

- [ ] **Step 7: Commit**

```bash
git add src/crosswalk.py tests/test_crosswalk.py data/crosswalk.csv
git commit -m "feat: PFF name-match crosswalk + reviewed corrections"
```

---

## Task 6: PFF metrics (blended grade/snaps + per-season + trend)

**Files:**
- Create: `src/pff_metrics.py`
- Test: `tests/test_pff_metrics.py`

- [ ] **Step 1: Write failing tests (pure blend math, no DB)**

`tests/test_pff_metrics.py`:
```python
from src import pff_metrics as pm

def test_blend_grade_weighted():
    # 2025=80(w3), 2024=70(w2), 2023=60(w1) -> (240+140+60)/6 = 73.333
    g = pm.blend({2025:80.0, 2024:70.0, 2023:60.0})
    assert round(g, 2) == 73.33

def test_blend_partial_seasons():
    # only 2025 present -> equals 2025
    assert pm.blend({2025: 65.0}) == 65.0
    # 2024 + 2023 -> (70*2 + 60*1)/3
    assert round(pm.blend({2024:70.0, 2023:60.0}), 2) == 66.67

def test_blend_empty_is_none():
    assert pm.blend({}) is None

def test_career_trend():
    assert pm.career_trend({2023:60.0, 2025:70.0}) == "improving"   # +10 >= 3
    assert pm.career_trend({2023:70.0, 2025:60.0}) == "declining"   # -10 <= -3
    assert pm.career_trend({2023:70.0, 2025:71.0}) == "flat"        # +1
    assert pm.career_trend({2025:70.0}) == "insufficient"           # one season
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_pff_metrics.py -v`
Expected: FAIL (`No module named 'src.pff_metrics'`).

- [ ] **Step 3: Implement `src/pff_metrics.py`**

```python
"""Per-player PFF metrics from pff.db (READ ONLY).

Season overall grade = snap-weighted avg of the player's primary-unit
(offense/defense) grade rows that season. Season snaps = sum of that unit's
snap_count. Blended = recency-weighted (3:2:1) across seasons present.
Specialists (no offense/defense unit) get null grade but real snap totals
from all their grade rows.
"""
import csv
import duckdb
from src import config

def blend(by_season: dict):
    """Recency-weighted (BLEND_WEIGHTS) mean over seasons present. None if empty."""
    num = den = 0.0
    for season, val in by_season.items():
        if val is None:
            continue
        w = config.BLEND_WEIGHTS.get(season, 0)
        num += w * val; den += w
    return (num / den) if den else None

def career_trend(grade_by_season: dict):
    seasons = sorted(s for s, v in grade_by_season.items() if v is not None)
    if len(seasons) < 2:
        return "insufficient"
    delta = grade_by_season[seasons[-1]] - grade_by_season[seasons[0]]
    if delta >= config.TREND_DELTA:
        return "improving"
    if delta <= -config.TREND_DELTA:
        return "declining"
    return "flat"

def _query(con, pff_ids):
    """Return {pff_player_id: {'grade':{season:val}, 'snaps':{season:val}}}."""
    if not pff_ids:
        return {}
    idlist = ",".join(f"'{i}'" for i in pff_ids)
    # primary-unit grade per (player, season): snap-weighted over offense/defense rows
    grade_rows = con.execute(f"""
        SELECT CAST(pff_player_id AS VARCHAR) pid, season,
               SUM(grade_value*snap_count)/NULLIF(SUM(snap_count),0) AS g,
               SUM(snap_count) AS unit_snaps
        FROM pff_grades
        WHERE CAST(pff_player_id AS VARCHAR) IN ({idlist})
          AND grade_type IN ('offense','defense') AND snap_count > 0
        GROUP BY 1,2
    """).fetchall()
    out = {pid: {"grade": {}, "snaps": {}} for pid in pff_ids}
    for pid, season, g, snaps in grade_rows:
        out.setdefault(pid, {"grade": {}, "snaps": {}})
        out[pid]["grade"][int(season)] = (float(g) if g is not None else None)
        out[pid]["snaps"][int(season)] = int(snaps or 0)
    # specialists: snaps from all grade rows when no offense/defense snaps recorded
    spec_rows = con.execute(f"""
        SELECT CAST(pff_player_id AS VARCHAR) pid, season, SUM(snap_count) s
        FROM pff_grades
        WHERE CAST(pff_player_id AS VARCHAR) IN ({idlist}) AND snap_count > 0
        GROUP BY 1,2
    """).fetchall()
    for pid, season, s in spec_rows:
        d = out.setdefault(pid, {"grade": {}, "snaps": {}})
        d["snaps"].setdefault(int(season), int(s or 0))  # only if no unit snaps set
    return out

def build(pff_ids):
    con = duckdb.connect(str(config.PFF_DB), read_only=True)
    data = _query(con, pff_ids)
    con.close()
    rows = []
    for pid in pff_ids:
        g = data.get(pid, {}).get("grade", {})
        s = data.get(pid, {}).get("snaps", {})
        rows.append({
            "pff_player_id": pid,
            "grade_2023": g.get(2023), "grade_2024": g.get(2024), "grade_2025": g.get(2025),
            "snaps_2023": s.get(2023), "snaps_2024": s.get(2024), "snaps_2025": s.get(2025),
            "grade_blended": blend(g),
            "snaps_blended": blend({k: float(v) for k, v in s.items()}),
            "career_trend": career_trend(g),
        })
    return rows

def main():
    xwalk = list(csv.DictReader(open(config.DATA / "crosswalk.csv", encoding="utf-8")))
    pff_ids = sorted({r["pff_player_id"] for r in xwalk if r["pff_player_id"]})
    rows = build(pff_ids)
    cols = ["pff_player_id","grade_2023","grade_2024","grade_2025",
            "snaps_2023","snaps_2024","snaps_2025","grade_blended","snaps_blended","career_trend"]
    with open(config.DATA / "pff_metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"pff_metrics: {len(rows)} matched players")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_pff_metrics.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Run against real data**

Run: `python -m src.pff_metrics`
Expected: `pff_metrics: N matched players` (N = distinct matched pff_player_ids). Writes `data/pff_metrics.csv`.

- [ ] **Step 6: Commit**

```bash
git add src/pff_metrics.py tests/test_pff_metrics.py data/pff_metrics.csv
git commit -m "feat: PFF blended grade/snaps + per-season + career trend"
```

---

## Task 7: Master table assembly + derived flags

**Files:**
- Create: `src/master.py`
- Test: `tests/test_master.py`

- [ ] **Step 1: Write failing tests for flag logic**

`tests/test_master.py`:
```python
from src import master as m

def test_zscores():
    z = m.zscores([1.0, 2.0, 3.0])
    assert round(z[0], 3) == -1.225 and round(z[2], 3) == 1.225

def test_flags_overvalued_undervalued():
    # high trajectory, low grade -> overvalued; low trajectory, high grade -> undervalued
    recs = [
        {"athlete_id":1,"trajectory":5,"grade_blended":40.0,"snaps_blended":500.0,"match_confidence":"confident"},
        {"athlete_id":2,"trajectory":1,"grade_blended":90.0,"snaps_blended":500.0,"match_confidence":"confident"},
        {"athlete_id":3,"trajectory":3,"grade_blended":65.0,"snaps_blended":500.0,"match_confidence":"confident"},
    ]
    flags = m.derive_flags(recs)
    assert flags[1]["flag_overvalued"] and not flags[1]["flag_undervalued"]
    assert flags[2]["flag_undervalued"] and not flags[2]["flag_overvalued"]

def test_projection_and_watchlist():
    recs = [
        {"athlete_id":9,"trajectory":5,"grade_blended":None,"snaps_blended":None,"match_confidence":"unmatched"},
        {"athlete_id":8,"trajectory":4,"grade_blended":70.0,"snaps_blended":20.0,"match_confidence":"confident"},
    ]
    flags = m.derive_flags(recs)
    assert flags[9]["flag_projection"] and flags[9]["flag_watchlist"]   # high traj, no snaps
    assert flags[8]["flag_watchlist"]                                   # high traj, low snaps
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_master.py -v`
Expected: FAIL (`No module named 'src.master'`).

- [ ] **Step 3: Implement `src/master.py`**

```python
"""Join keyword + semantic + crosswalk + PFF into one row per athlete; derive flags."""
import csv, json, statistics
from src import config

def zscores(vals):
    xs = [v for v in vals if v is not None]
    if len(xs) < 2:
        return [0.0 for _ in vals]
    mu = statistics.mean(xs); sd = statistics.pstdev(xs)
    if sd == 0:
        return [0.0 for _ in vals]
    return [((v - mu) / sd if v is not None else None) for v in vals]

def derive_flags(recs):
    """recs need: athlete_id, trajectory, grade_blended, snaps_blended, match_confidence.
    Returns {athlete_id: {flag_undervalued,flag_overvalued,flag_watchlist,flag_projection}}."""
    matched = [r for r in recs if r.get("grade_blended") is not None]
    ztraj = dict(zip([r["athlete_id"] for r in matched],
                     zscores([r["trajectory"] for r in matched])))
    zgrade = dict(zip([r["athlete_id"] for r in matched],
                      zscores([r["grade_blended"] for r in matched])))
    snaps_present = [r["snaps_blended"] for r in recs if r.get("snaps_blended") not in (None, 0)]
    snap_median = statistics.median(snaps_present) if snaps_present else 0.0
    out = {}
    for r in recs:
        aid = r["athlete_id"]; t = r.get("trajectory")
        over = under = False
        if aid in ztraj:
            delta = ztraj[aid] - zgrade[aid]
            over = delta >= config.MISVALUE_Z_THRESHOLD
            under = delta <= -config.MISVALUE_Z_THRESHOLD
        projection = (r.get("match_confidence") == "unmatched") or (not r.get("snaps_blended"))
        low_snaps = (not r.get("snaps_blended")) or (r["snaps_blended"] < snap_median)
        watch = (t is not None and t >= config.TRAJECTORY_WATCHLIST_MIN) and low_snaps
        out[aid] = {"flag_undervalued": under, "flag_overvalued": over,
                    "flag_watchlist": watch, "flag_projection": projection}
    return out

def _read_csv(path, key="athlete_id", cast_int=True):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    if cast_int:
        for r in rows:
            r[key] = int(r[key])
    return {r[key]: r for r in rows}

def _num(v):
    try:
        return float(v) if v not in (None, "", "None") else None
    except (TypeError, ValueError):
        return None

def main():
    wide = _read_csv(config.DATA / "eval_wide.csv")
    kw = _read_csv(config.DATA / "keyword_scores.csv")
    xwalk = _read_csv(config.DATA / "crosswalk.csv")
    sem = {s["athlete_id"]: s for s in json.load(
        open(config.DATA / "semantic_scores.json", encoding="utf-8"))}
    pffm = {r["pff_player_id"]: r for r in csv.DictReader(
        open(config.DATA / "pff_metrics.csv", encoding="utf-8"))}

    recs = []
    for aid, w in sorted(wide.items()):
        s = sem.get(aid, {})
        x = xwalk.get(aid, {})
        pid = x.get("pff_player_id", "")
        pf = pffm.get(pid, {})
        rec = {
            "athlete_id": aid, "last": w["last"], "first": w["first"], "position": w["position"],
            "keyword_pc": _num(kw.get(aid, {}).get("keyword_pc")),
            "keyword_n": _num(kw.get(aid, {}).get("keyword_n")),
            "keyword_str": _num(kw.get(aid, {}).get("keyword_str")),
            "keyword_ac": _num(kw.get(aid, {}).get("keyword_ac")),
            "keyword_overall": _num(kw.get(aid, {}).get("keyword_overall")),
            "keyword_rank": _num(kw.get(aid, {}).get("keyword_rank")),
            "trajectory": s.get("trajectory"), "rationale": s.get("rationale"),
            "tier": s.get("tier"), "red_flag": s.get("red_flag"),
            "sent_pc": s.get("sentiment", {}).get("PC"),
            "sent_n": s.get("sentiment", {}).get("N"),
            "sent_str": s.get("sentiment", {}).get("STR"),
            "sent_ac": s.get("sentiment", {}).get("AC"),
            "pff_player_id": pid, "match_confidence": x.get("match_confidence", "unmatched"),
            "grade_blended": _num(pf.get("grade_blended")),
            "snaps_blended": _num(pf.get("snaps_blended")),
            "grade_2025": _num(pf.get("grade_2025")), "grade_2024": _num(pf.get("grade_2024")),
            "grade_2023": _num(pf.get("grade_2023")),
            "snaps_2025": _num(pf.get("snaps_2025")), "snaps_2024": _num(pf.get("snaps_2024")),
            "snaps_2023": _num(pf.get("snaps_2023")),
            "career_trend": pf.get("career_trend", "insufficient"),
        }
        recs.append(rec)

    flags = derive_flags(recs)
    for r in recs:
        r.update(flags[r["athlete_id"]])

    cols = ["athlete_id","last","first","position",
            "keyword_pc","keyword_n","keyword_str","keyword_ac","keyword_overall","keyword_rank",
            "trajectory","rationale","tier","red_flag","sent_pc","sent_n","sent_str","sent_ac",
            "pff_player_id","match_confidence","grade_blended","snaps_blended",
            "grade_2025","grade_2024","grade_2023","snaps_2025","snaps_2024","snaps_2023",
            "career_trend","flag_undervalued","flag_overvalued","flag_watchlist","flag_projection"]
    with open(config.DATA / "master.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in recs:
            w.writerow({k: r.get(k) for k in cols})
    n_matched = sum(1 for r in recs if r["grade_blended"] is not None)
    print(f"master: {len(recs)} athletes, {n_matched} with PFF grade")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_master.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Run against real data**

Run: `python -m src.master`
Expected: `master: 99 athletes, N with PFF grade`. Writes `data/master.csv`.

- [ ] **Step 6: Commit**

```bash
git add src/master.py tests/test_master.py data/master.csv
git commit -m "feat: master table assembly + mis-valued/watchlist/projection flags"
```

---

## Task 8: Analysis (correlations + mis-valued lists + watchlist)

**Files:**
- Create: `src/analysis.py`
- Test: `tests/test_analysis.py`

- [ ] **Step 1: Write failing tests**

`tests/test_analysis.py`:
```python
from src import analysis as an

def test_corr_perfect_positive():
    r = an.corr([1,2,3,4,5], [10,20,30,40,50])
    assert round(r["spearman"], 3) == 1.0 and round(r["pearson"], 3) == 1.0 and r["n"] == 5

def test_corr_drops_none_pairs():
    r = an.corr([1,2,None,4], [2,4,9,8])
    assert r["n"] == 3

def test_corr_insufficient():
    r = an.corr([1], [2])
    assert r["spearman"] is None and r["n"] == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_analysis.py -v`
Expected: FAIL (`No module named 'src.analysis'`).

- [ ] **Step 3: Implement `src/analysis.py`**

```python
"""Correlations, mis-valued lists, and watchlist from data/master.csv."""
import csv, json
from scipy import stats
from src import config

def corr(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 2:
        return {"n": n, "spearman": None, "pearson": None}
    xa = [p[0] for p in pairs]; ya = [p[1] for p in pairs]
    sp = stats.spearmanr(xa, ya); pe = stats.pearsonr(xa, ya)
    return {"n": n, "spearman": float(sp.statistic), "spearman_p": float(sp.pvalue),
            "pearson": float(pe.statistic), "pearson_p": float(pe.pvalue)}

def _num(v):
    try:
        return float(v) if v not in (None, "", "None") else None
    except (TypeError, ValueError):
        return None

def _b(v):
    return str(v).strip().lower() == "true"

def main():
    recs = list(csv.DictReader(open(config.DATA / "master.csv", encoding="utf-8")))
    for r in recs:
        for k in ("keyword_overall","trajectory","grade_blended","snaps_blended"):
            r[k] = _num(r[k])

    correlations = []
    pairs = [("keyword_overall","grade_blended"), ("trajectory","grade_blended"),
             ("keyword_overall","snaps_blended"), ("trajectory","snaps_blended")]
    for a, b in pairs:
        c = corr([r[a] for r in recs], [r[b] for r in recs])
        c["x"], c["y"], c["scope"] = a, b, "roster"
        correlations.append(c)
    # within-position (n>=5) for the headline trajectory vs grade
    from collections import defaultdict
    bypos = defaultdict(list)
    for r in recs:
        bypos[r["position"]].append(r)
    for pos, rs in sorted(bypos.items()):
        c = corr([r["trajectory"] for r in rs], [r["grade_blended"] for r in rs])
        if c["n"] >= 5:
            c["x"], c["y"], c["scope"] = "trajectory", "grade_blended", f"pos:{pos}"
            correlations.append(c)

    matched = [r for r in recs if r["grade_blended"] is not None]
    over = sorted((r for r in matched if _b(r["flag_overvalued"])),
                  key=lambda r: r["trajectory"] or 0, reverse=True)
    under = sorted((r for r in matched if _b(r["flag_undervalued"])),
                   key=lambda r: r["grade_blended"], reverse=True)
    watch = sorted((r for r in recs if _b(r["flag_watchlist"])),
                   key=lambda r: (r["trajectory"] or 0, -(r["snaps_blended"] or 0)), reverse=True)

    def slim(r):
        return {"athlete_id": int(r["athlete_id"]), "name": f"{r['first']} {r['last']}",
                "position": r["position"], "trajectory": r["trajectory"], "tier": r["tier"],
                "keyword_overall": r["keyword_overall"], "grade_blended": r["grade_blended"],
                "snaps_blended": r["snaps_blended"], "career_trend": r["career_trend"],
                "match_confidence": r["match_confidence"], "rationale": r["rationale"]}

    out = {
        "correlations": correlations,
        "misvalued": {"overvalued": [slim(r) for r in over],
                      "undervalued": [slim(r) for r in under]},
        "watchlist": [slim(r) for r in watch],
        "summary": {"n_athletes": len(recs), "n_matched": len(matched),
                    "n_unmatched": sum(1 for r in recs if r["match_confidence"]=="unmatched")},
    }
    json.dump(out, open(config.DATA / "analysis.json", "w", encoding="utf-8"), indent=1)
    print(f"analysis: {len(matched)}/{len(recs)} matched; "
          f"{len(over)} overvalued, {len(under)} undervalued, {len(watch)} watchlist")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_analysis.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Run against real data**

Run: `python -m src.analysis`
Expected: `analysis: N/99 matched; X overvalued, Y undervalued, Z watchlist`. Writes `data/analysis.json`.

- [ ] **Step 6: Commit**

```bash
git add src/analysis.py tests/test_analysis.py data/analysis.json
git commit -m "feat: correlations, mis-valued lists, watchlist"
```

---

## Task 9: Master Excel workbook

**Files:**
- Create: `src/workbook.py`

- [ ] **Step 1: Implement `src/workbook.py`**

```python
"""Write outputs/SpringEvals_PFF_Master.xlsx from the computed artifacts."""
import csv, json
import openpyxl
from openpyxl.styles import Font, PatternFill
from src import config

TIER_FILL = {
    "Strong trajectory": "C6EFCE", "Trending positive": "DDEBF7",
    "Mixed signals": "FFF2CC", "Needs attention": "F8CBAD",
}

def _rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))

def _sheet_from_dicts(wb, title, rows, headers):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append([r.get(h) for h in headers])
    ws.freeze_panes = "A2"
    return ws

def main():
    config.OUTPUTS.mkdir(exist_ok=True)
    master = _rows(config.DATA / "master.csv")
    analysis = json.load(open(config.DATA / "analysis.json", encoding="utf-8"))
    themes = json.load(open(config.DATA / "themes.json", encoding="utf-8")) \
        if (config.DATA / "themes.json").exists() else {}

    wb = openpyxl.Workbook(); wb.remove(wb.active)

    master_cols = list(master[0].keys())
    ws = _sheet_from_dicts(wb, "Master", master, master_cols)
    tier_idx = master_cols.index("tier") + 1
    for row in range(2, len(master) + 2):
        tv = ws.cell(row, tier_idx).value
        if tv in TIER_FILL:
            ws.cell(row, tier_idx).fill = PatternFill("solid", fgColor=TIER_FILL[tv])

    cor = wb.create_sheet("Correlations")
    cor.append(["x", "y", "scope", "n", "spearman", "spearman_p", "pearson", "pearson_p"])
    for c in cor[1]:
        c.font = Font(bold=True)
    for c in analysis["correlations"]:
        cor.append([c.get("x"), c.get("y"), c.get("scope"), c.get("n"),
                    c.get("spearman"), c.get("spearman_p"), c.get("pearson"), c.get("pearson_p")])

    view_cols = ["athlete_id","name","position","trajectory","tier","keyword_overall",
                 "grade_blended","snaps_blended","career_trend","match_confidence","rationale"]
    _sheet_from_dicts(wb, "Overvalued", analysis["misvalued"]["overvalued"], view_cols)
    _sheet_from_dicts(wb, "Undervalued", analysis["misvalued"]["undervalued"], view_cols)
    _sheet_from_dicts(wb, "Watchlist", analysis["watchlist"], view_cols)

    redflags = [r for r in master if str(r.get("red_flag")).lower() == "true"]
    _sheet_from_dicts(wb, "Red Flags", redflags, master_cols)

    xwalk = _rows(config.DATA / "crosswalk.csv")
    _sheet_from_dicts(wb, "Crosswalk", xwalk, list(xwalk[0].keys()))

    if themes:
        tw = wb.create_sheet("Themes")
        tw.append(["Department", "Polarity", "Theme"])
        for c in tw[1]:
            c.font = Font(bold=True)
        for dept in config.DEPARTMENTS:
            for pol in ("positive", "negative"):
                for t in themes.get(dept, {}).get(pol, []):
                    tw.append([dept, pol, t])

    out = config.OUTPUTS / "SpringEvals_PFF_Master.xlsx"
    wb.save(out)
    print(f"wrote {out} ({len(wb.sheetnames)} sheets: {wb.sheetnames})")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it**

Run: `python -m src.workbook`
Expected: `wrote ...SpringEvals_PFF_Master.xlsx (9 sheets: [...])`.

- [ ] **Step 3: Smoke-verify the workbook opens with expected sheets**

Run:
```bash
python -c "import openpyxl,src.config as c; wb=openpyxl.load_workbook(c.OUTPUTS/'SpringEvals_PFF_Master.xlsx'); print(wb.sheetnames); print('Master rows', wb['Master'].max_row)"
```
Expected: sheet list includes `Master, Correlations, Overvalued, Undervalued, Watchlist, Red Flags, Crosswalk, Themes`; `Master rows 100` (header + 99).

- [ ] **Step 4: Commit**

```bash
git add src/workbook.py outputs/SpringEvals_PFF_Master.xlsx
git commit -m "feat: master Excel workbook with views + tier shading"
```

---

## Task 10: Written report

**Files:**
- Create: `src/report.py`

- [ ] **Step 1: Implement `src/report.py`**

```python
"""Render outputs/SpringEvals_PFF_Report.md from analysis + master + themes."""
import csv, json
from src import config

def _fmt(v, nd=1):
    return "—" if v in (None, "", "None") else (f"{float(v):.{nd}f}" if _isnum(v) else str(v))

def _isnum(v):
    try:
        float(v); return True
    except (TypeError, ValueError):
        return False

def _corr_line(c):
    sp = "—" if c["spearman"] is None else f"{c['spearman']:+.2f}"
    pe = "—" if c.get("pearson") is None else f"{c['pearson']:+.2f}"
    return f"| {c['x']} → {c['y']} | {c['scope']} | {c['n']} | {sp} | {pe} |"

def _view_table(rows):
    out = ["| Player | Pos | Traj | Tier | KW | PFF grade | Snaps | Trend | Why |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['name']} | {r['position']} | {r['trajectory']} | {r['tier']} | "
                   f"{_fmt(r['keyword_overall'])} | {_fmt(r['grade_blended'])} | "
                   f"{_fmt(r['snaps_blended'],0)} | {r['career_trend']} | {r['rationale']} |")
    return "\n".join(out)

def main():
    config.OUTPUTS.mkdir(exist_ok=True)
    a = json.load(open(config.DATA / "analysis.json", encoding="utf-8"))
    themes = json.load(open(config.DATA / "themes.json", encoding="utf-8")) \
        if (config.DATA / "themes.json").exists() else {}
    master = list(csv.DictReader(open(config.DATA / "master.csv", encoding="utf-8")))
    s = a["summary"]
    L = []
    L.append("# Baylor Football — Spring 2026 Evals × PFF Correlation\n")
    L.append(f"_Generated from {s['n_athletes']} athlete evaluations; "
             f"{s['n_matched']} matched to PFF on-field data, "
             f"{s['n_unmatched']} unmatched (projection cohort)._\n")

    L.append("## 1. Validation — does internal perception track on-field reality?\n")
    L.append("| Internal → On-field | Scope | n | Spearman | Pearson |")
    L.append("|---|---|---|---|---|")
    for c in a["correlations"]:
        L.append(_corr_line(c))
    L.append("\n_Spearman is the headline (rank correlation, robust to non-linearity). "
             "Within-position cells with n<5 are omitted; treat small cells as directional._\n")

    L.append("## 2. Mis-valued players\n")
    L.append("### Overvalued (high internal view, lower on-field grade)\n")
    L.append(_view_table(a["misvalued"]["overvalued"]) if a["misvalued"]["overvalued"]
             else "_None flagged._")
    L.append("\n### Undervalued (lower internal view, higher on-field grade)\n")
    L.append(_view_table(a["misvalued"]["undervalued"]) if a["misvalued"]["undervalued"]
             else "_None flagged._")

    L.append("\n## 3. Future-contributor watchlist\n")
    L.append("_Strong eval trajectory with low/zero blended snaps — the rising/projection cohort._\n")
    L.append(_view_table(a["watchlist"]) if a["watchlist"] else "_None flagged._")

    L.append("\n## 4. Themes by department\n")
    for dept in config.DEPARTMENTS:
        d = themes.get(dept, {})
        L.append(f"**{dept}** — +: {', '.join(d.get('positive', [])) or '—'} | "
                 f"−: {', '.join(d.get('negative', [])) or '—'}")

    L.append("\n## 5. Red flags (concerning in ≥2 departments)\n")
    rf = [r for r in master if str(r.get("red_flag")).lower() == "true"]
    if rf:
        L.append("| Player | Pos | PC | N | STR | AC | Tier |")
        L.append("|---|---|---|---|---|---|---|")
        for r in rf:
            L.append(f"| {r['first']} {r['last']} | {r['position']} | {r['sent_pc']} | "
                     f"{r['sent_n']} | {r['sent_str']} | {r['sent_ac']} | {r['tier']} |")
    else:
        L.append("_None flagged._")

    L.append("\n---\n_PFF grade = recency-weighted (2025:2024:2023 = 3:2:1) snap-weighted "
             "primary-unit grade. Snaps = same recency-weighted blend. "
             "PFF database accessed read-only._")

    out = config.OUTPUTS / "SpringEvals_PFF_Report.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it**

Run: `python -m src.report`
Expected: `wrote ...SpringEvals_PFF_Report.md`.

- [ ] **Step 3: Eyeball the report**

Read `outputs/SpringEvals_PFF_Report.md`. Confirm: correlation table populated, mis-valued/watchlist tables render, themes + red flags present, no `—`-only sections that should have data.

- [ ] **Step 4: Commit**

```bash
git add src/report.py outputs/SpringEvals_PFF_Report.md
git commit -m "feat: written correlation report (validation, mis-valued, watchlist, themes, red flags)"
```

---

## Task 11: End-to-end orchestrator + full run

**Files:**
- Create: `run.py`

- [ ] **Step 1: Implement `run.py`**

```python
"""Run the full pipeline in order. Semantic scoring (Task 4) and the crosswalk
review gate (Task 5) are manual and must already be complete."""
import subprocess, sys
from src import config

STEPS = ["src.extract_eval", "src.semantic_schema", "src.crosswalk",
         "src.pff_metrics", "src.master", "src.analysis", "src.workbook", "src.report"]

def main():
    for mod in STEPS:
        print(f"\n=== {mod} ===")
        r = subprocess.run([sys.executable, "-m", mod], cwd=config.ROOT)
        if r.returncode != 0:
            print(f"FAILED at {mod}"); raise SystemExit(r.returncode)
    print("\nPipeline complete. Deliverables in outputs/.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the full test suite**

Run: `python -m pytest`
Expected: all tests PASS.

- [ ] **Step 3: Run the full pipeline end to end**

Run: `python run.py`
Expected: each stage prints its summary; ends `Pipeline complete.` Both files exist in `outputs/`.

- [ ] **Step 4: Commit**

```bash
git add run.py
git commit -m "feat: end-to-end pipeline orchestrator"
```

---

## Task 12: Memory + project registration

- [ ] **Step 1: Update KeystoneOS / global memory**

At this natural break, register the project per the user's two-tier memory system:
- Tier B (`~/.claude/global-memory/MEMORY.md`): add an active-thread line for this project (location, state: MVP complete, deliverables in `outputs/`). Respect the 2,500-char cap (consolidate if needed).
- Tier A (`~/.claude/projects/<slug>/memory/`): if a durable project fact is warranted (e.g. the PFF crosswalk-by-name convention, the 3:2:1 blend decision), add a `project_*.md` file + MEMORY.md pointer.

- [ ] **Step 2: Final commit**

```bash
git add -A
git commit -m "chore: project state + memory registration"
```

---

## Self-Review (completed during planning)

- **Spec coverage:** semantic scoring (T3–4), crosswalk + gate (T5), recency-weighted PFF blend (T6), master schema (T7), three views — validation/mis-valued/watchlist (T8), 5 handoff deliverables: trajectory+rationale (T4), tier list (T4/workbook), cross-dept alignment via sentiment (T4/master), themes (T4/report), red flags (T4/master/report). Master workbook (T9) + report (T10) = MVP deliverables. Dashboard/PDF correctly deferred. ✓
- **Placeholder scan:** no TBD/TODO; all code blocks are complete and runnable. ✓
- **Type consistency:** `blend()`, `career_trend()`, `derive_flags()`, `corr()` signatures match across tasks; data-contract column names are reused verbatim from the locked contracts block. ✓
- **Read-only PFF:** every duckdb.connect uses `read_only=True`. ✓

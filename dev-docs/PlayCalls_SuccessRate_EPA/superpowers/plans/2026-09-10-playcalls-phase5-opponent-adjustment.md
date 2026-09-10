# Phase 5: Opponent Adjustment — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure whether Baylor's 2024→2025 offensive decline survives subtracting each opponent's defensive quality, and report the answer.

**Architecture:** One new pure module `src/playcalls/opponent.py` holding the CFBD-side classifiers, the per-opponent defensive baseline, and the adjustment arithmetic. One new renderer `src/playcalls/opponent_report.py`. Two new root builders following the existing `build_alignment_tables.py` / `build_alignment_report.py` pair. One fix to existing code (`cfbd._attach_pre_snap_score`) that Phase 5 exposes.

**Tech Stack:** Python 3.12, pandas, duckdb, pytest. Venv at `.venv/`, created by `/Users/kristinarash/.local/bin/uv`.

**Spec:** `docs/superpowers/specs/2026-09-10-playcalls-phase5-opponent-adjustment-design.md`

## Global Constraints

- **Write "EPA (CFBD PPA)" on first use in any report, never bare "EPA".** A test enforces it for `REPORT.md`; Task 7 adds the equivalent for `OPPONENT.md`.
- **`MIN_SAMPLE = 15`**, imported from `src.playcalls.analysis`. Applied to `epa_plays` for EPA tables and to `graded` for success tables. Never lowered.
- **Every table prints `plays`, `graded` and `epa_plays` as separate columns.** They differ, and printing one as another is how a coverage problem becomes a wrong rate.
- **This repo never calls the CFBD API and never writes to `pff.db`.** Read-only, both.
- **Baselines exclude Baylor** (`offense != "Baylor"`) and **exclude non-FBS offences**.
- **The headline excludes FCS opponents**, one per season. Raw figures are printed both ways.
- **Adjusted tables classify run/pass and gain from CFBD on both sides.** The reconciliation table uses chart fields. Never mix.
- **Seasons come from `seasons.resolve_seasons()`**, never a hardcoded tuple.
- Run tests with `.venv/bin/python -m pytest -q`. GNU `timeout` is not installed; do not use it.
- Commit after every task. Never merge to `main`; never delete a branch.

---

### Task 1: Fix `_attach_pre_snap_score` to group by (game, offence)

Existing defect, exposed by this phase. `cfbd._attach_pre_snap_score` groups by `gameId` alone. That is correct only because `load_baylor_plays` filters `offense = 'Baylor'` in SQL first, so one game holds one offence. Task 3 loads all teams, where offence alternates within a game — the previous row's `offenseScore` would then belong to the other team.

**Files:**
- Modify: `src/playcalls/cfbd.py:142-146` (the `grouped = ...` block and its docstring)
- Test: `tests/test_cfbd.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `cfbd._attach_pre_snap_score(frame)` correct for a frame containing more than one offence per game. Signature unchanged.

- [ ] **Step 1: Write the failing test — a two-possession all-teams fixture**

Add to `tests/test_cfbd.py`:

```python
def test_pre_snap_score_does_not_leak_across_offences_in_one_game():
    """The all-teams defect. Grouping by gameId alone makes the previous
    row's offenseScore belong to the OTHER team.

    One game, two possessions. Alpha scores a touchdown to go 7-0, then Beta
    takes over. Beta's first snap must read pre_offense_score 0 (Beta has not
    scored) and pre_defense_score 7 (Alpha has). Grouping by gameId alone
    reads the previous row -- Alpha's 7 -- as Beta's own score.
    """
    frame = pd.DataFrame({
        "gameId": [1, 1, 1, 1],
        "driveNumber": [1, 1, 2, 2],
        "playNumber": [1, 2, 1, 2],
        "offense": ["Alpha", "Alpha", "Beta", "Beta"],
        "defense": ["Beta", "Beta", "Alpha", "Alpha"],
        # post-play scores, from the offence's perspective on each row
        "offenseScore": [0, 7, 0, 0],
        "defenseScore": [0, 0, 7, 7],
    })

    out = cfbd._attach_pre_snap_score(frame)
    beta = out[out["offense"] == "Beta"].reset_index(drop=True)

    assert list(beta["pre_offense_score"]) == [0, 0], (
        "Beta's own score leaked from Alpha's row"
    )
    assert list(beta["pre_defense_score"]) == [7, 7], (
        "Beta's opponent score is wrong"
    )
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `.venv/bin/python -m pytest tests/test_cfbd.py::test_pre_snap_score_does_not_leak_across_offences_in_one_game -q`

Expected: FAIL. Beta's first snap reads `pre_offense_score` 7, because the shift crosses the possession change.

- [ ] **Step 3: Write the second test — Baylor's existing output must not move**

```python
def test_pre_snap_score_unchanged_for_a_single_offence_frame():
    """The fix must be a no-op for every frame Phase 2 built.

    In a Baylor-only frame `offense` is constant within a game, so grouping by
    (gameId, offense) yields identical groups to grouping by gameId. Asserted
    rather than assumed, because Phase 2's whole score-state analysis rests on
    these columns.
    """
    frame = pd.DataFrame({
        "gameId": [1, 1, 1, 2, 2],
        "driveNumber": [1, 1, 2, 1, 1],
        "playNumber": [1, 2, 1, 1, 2],
        "offense": ["Baylor"] * 5,
        "defense": ["Utah"] * 3 + ["LSU"] * 2,
        "offenseScore": [0, 7, 7, 0, 3],
        "defenseScore": [0, 0, 10, 0, 0],
    })

    out = cfbd._attach_pre_snap_score(frame)

    assert list(out["pre_offense_score"]) == [0, 0, 7, 0, 0]
    assert list(out["pre_defense_score"]) == [0, 0, 0, 0, 0]
```

- [ ] **Step 4: Apply the fix**

In `src/playcalls/cfbd.py`, replace:

```python
    grouped = ordered.groupby("gameId", sort=False)
```

with:

```python
    # Grouped by (game, offence), not by game alone. In a Baylor-only frame
    # these are the same grouping, because `offense` is constant within a
    # game -- so every Phase 2 number is unchanged, and a test asserts that.
    # In an all-teams frame the offence alternates within a game, and grouping
    # by gameId alone would read the OTHER team's score as this team's
    # previous score. Nothing would raise; every garbage-time flag built on it
    # would simply be wrong.
    grouped = ordered.groupby(["gameId", "offense"], sort=False)
```

- [ ] **Step 5: Extend the docstring**

Add this paragraph to `_attach_pre_snap_score`'s docstring, after the "Two known limits" block:

```
    The grouping is (gameId, offense). Grouping by gameId alone is correct
    only for a frame already filtered to one offence, which load_baylor_plays
    produces and load_season_plays does not.
```

- [ ] **Step 6: Run the full suite**

Run: `.venv/bin/python -m pytest -q`

Expected: 251 passed. The two new tests pass and the existing 249 are unchanged.

- [ ] **Step 7: Prove the real Phase 2 output is byte-identical**

Run:

```bash
.venv/bin/python -c "
from src.playcalls import cfbd
import hashlib
for s in (2024, 2025):
    d = cfbd.load_baylor_plays(s)
    cols = d[['gameId','playNumber','pre_offense_score','pre_defense_score']]
    h = hashlib.sha256(cols.to_csv(index=False).encode()).hexdigest()
    print(s, len(d), h)
"
```

Record both hashes in the commit message. They are the evidence that the fix moved no existing number.

- [ ] **Step 8: Commit**

```bash
git add src/playcalls/cfbd.py tests/test_cfbd.py
git commit -F- <<'MSG'
Group the pre-snap score by (game, offence), not by game

_attach_pre_snap_score shifts the previous row's score within a gameId
group. That is correct only because load_baylor_plays filters
offense = 'Baylor' in SQL before calling it, so every surviving row in a
game shares one offence.

Phase 5 loads all teams. There the offence alternates within a game, so
the previous row's offenseScore belongs to the OTHER team and the
clip(upper=...) clamp compares two perspectives. Nothing raises; every
garbage-time flag built on it is simply wrong.

Grouping by (gameId, offense) is identical for a Baylor-only frame --
offense is constant within a game -- and correct for an all-teams one.
Asserted both ways rather than assumed: a two-possession fixture where
the answer is known by hand, and a single-offence fixture that must not
move. The real 2024 and 2025 pre-snap columns hash identically before
and after.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TJszvQjQaXduVaswN86tYR
MSG
```

---

### Task 2: The CFBD-side classifiers

Three pure functions with no I/O. They decide what a play was, whether it succeeded, and what level a team plays at. Everything downstream rests on them, so they are built and tested first.

**Files:**
- Create: `src/playcalls/opponent.py`
- Test: `tests/test_opponent.py`

**Interfaces:**
- Consumes: `epa.is_non_play` (existing).
- Produces:
  - `FBS_CONFERENCES: frozenset[str]`
  - `FCS_CONFERENCES: frozenset[str]`
  - `CFBD_PLAY_TYPE_TO_RUN_PASS: dict[str, str]`
  - `classify_run_pass(play_type) -> str` — `"run"`, `"pass"` or `"unknown"`
  - `derive_success(down, distance, gain) -> bool | None`
  - `is_fbs(conference) -> bool`
  - `opponent_level(conference) -> str` — `"fbs"` or `"fcs"`, raises otherwise
  - `BAYLOR = "Baylor"`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_opponent.py`:

```python
"""Phase 5: opponent adjustment."""

import pandas as pd
import pytest

from src.playcalls import opponent


class TestClassifyRunPass:
    def test_rushes_are_runs(self):
        assert opponent.classify_run_pass("Rush") == "run"
        assert opponent.classify_run_pass("Rushing Touchdown") == "run"

    def test_dropbacks_are_passes(self):
        for play_type in (
            "Pass Reception", "Pass Incompletion", "Sack",
            "Passing Touchdown", "Pass Completion",
            "Pass Interception Return", "Interception",
            "Interception Return Touchdown",
        ):
            assert opponent.classify_run_pass(play_type) == "pass", play_type

    def test_a_fumble_recovery_is_unknown_not_a_run(self):
        """CFBD gives a fumble recovery its own play type and does not say
        whether the snap behind it was a run or a pass. Guessing 'run'
        because most plays are runs would bias every run cut."""
        assert opponent.classify_run_pass("Fumble Recovery (Own)") == "unknown"
        assert opponent.classify_run_pass("Fumble Recovery (Opponent)") == "unknown"
        assert opponent.classify_run_pass("Fumble") == "unknown"

    def test_a_penalty_is_unknown(self):
        """Penalty rows stay in the play pool but must never be graded."""
        assert opponent.classify_run_pass("Penalty") == "unknown"

    def test_an_unmapped_play_type_is_unknown(self):
        """A CFBD rename or a new type must not silently become a run."""
        assert opponent.classify_run_pass("Quantum Option") == "unknown"

    def test_a_null_play_type_is_unknown(self):
        assert opponent.classify_run_pass(None) == "unknown"
        assert opponent.classify_run_pass(float("nan")) == "unknown"


class TestDeriveSuccess:
    def test_first_down_needs_half(self):
        assert opponent.derive_success(1, 10, 5) is True
        assert opponent.derive_success(1, 10, 4) is False

    def test_second_down_needs_seventy_percent(self):
        assert opponent.derive_success(2, 10, 7) is True
        assert opponent.derive_success(2, 10, 6) is False

    def test_third_and_fourth_need_the_whole_distance(self):
        assert opponent.derive_success(3, 5, 5) is True
        assert opponent.derive_success(3, 5, 4) is False
        assert opponent.derive_success(4, 1, 1) is True
        assert opponent.derive_success(4, 1, 0) is False

    def test_a_loss_is_never_a_success(self):
        assert opponent.derive_success(1, 10, -3) is False

    def test_down_five_is_none(self):
        """pff_DOWN carries 5 on 13 rows across the two seasons. There is no
        convention for a fifth down; excluding beats inventing one."""
        assert opponent.derive_success(5, 10, 10) is None

    def test_a_null_down_or_distance_is_none(self):
        assert opponent.derive_success(None, 10, 5) is None
        assert opponent.derive_success(1, None, 5) is None
        assert opponent.derive_success(1, 10, None) is None


class TestConferenceLevel:
    def test_fbs_conferences_use_cfbds_own_strings(self):
        """CFBD writes 'American Athletic', not 'AAC'. Read from the data."""
        assert opponent.is_fbs("American Athletic") is True
        assert opponent.is_fbs("Mid-American") is True
        assert opponent.is_fbs("Big 12") is True
        assert opponent.is_fbs("FBS Independents") is True

    def test_lower_divisions_are_not_fbs(self):
        for conference in ("UAC", "Southern", "Big Sky", "SWAC",
                           "Lone Star", "Northeast 10", None):
            assert opponent.is_fbs(conference) is False, conference

    def test_opponent_level_names_the_division(self):
        assert opponent.opponent_level("Big 12") == "fbs"
        assert opponent.opponent_level("UAC") == "fcs"
        assert opponent.opponent_level("Southern") == "fcs"

    def test_an_unknown_conference_raises_by_name(self):
        """A realignment or a CFBD rename must fail loudly. Returning 'fcs'
        would silently drop a real Big 12 game from the headline."""
        with pytest.raises(ValueError, match="Pac-16"):
            opponent.opponent_level("Pac-16")
```

- [ ] **Step 2: Run and confirm it fails**

Run: `.venv/bin/python -m pytest tests/test_opponent.py -q`

Expected: collection error — `No module named 'src.playcalls.opponent'`.

- [ ] **Step 3: Write the module**

Create `src/playcalls/opponent.py`:

```python
"""Phase 5: what Baylor's schedule allowed everyone else.

Phase 4 showed the 2024-to-2025 decline is not explained by alignment. The
strongest remaining structural explanation is the schedule: 2025 defences may
simply have been better. This module measures that.

Everything here classifies plays from CFBD's own columns rather than from
Baylor's charting file, and the reason is not convenience. There is no chart
for an opponent's other games, so a baseline can only be built from CFBD. A
Baylor rate built from the chart and subtracted from a baseline built from
CFBD would compare two different things -- the chart records the play CALL,
CFBD records the RESULT, and they disagree on 46 scrambles charted P and typed
Rush. So both sides of every subtraction are classified the same way, here.

Read-only against CFB_Analytics_Lab's parquet. Never calls the CFBD API.
"""

from __future__ import annotations

import pandas as pd

BAYLOR = "Baylor"

# CFBD's own conference strings, read from the parquet rather than assumed.
# CFBD writes "American Athletic", not "AAC", and "Mid-American", not "MAC".
FBS_CONFERENCES = frozenset({
    "ACC",
    "American Athletic",
    "Big 12",
    "Big Ten",
    "Conference USA",
    "FBS Independents",
    "Mid-American",
    "Mountain West",
    "Pac-12",
    "SEC",
    "Sun Belt",
})

# Only the FCS conferences an opponent could plausibly come from. This exists
# to make opponent_level raise on anything it does not recognise, so a
# realignment fails by name instead of quietly demoting a team out of the
# headline. It is not used to filter baseline offences -- is_fbs does that,
# and a Division II offence is simply not FBS.
FCS_CONFERENCES = frozenset({
    "Big Sky",
    "Coastal Athletic",
    "FCS Independents",
    "Ivy",
    "MEAC",
    "MVFC",
    "NEC",
    "OVC-Big South",
    "Patriot",
    "Pioneer",
    "SWAC",
    "Southern",
    "Southland",
    "UAC",
})

# CFBD play type -> run / pass. Explicit, and deliberately partial.
#
# Everything absent resolves to "unknown", which is excluded from run and pass
# cuts on BOTH sides of every subtraction. Fumble recoveries are the reason
# this is not a two-way split: CFBD gives them their own play type and never
# says whether the snap behind them was a run or a pass. Defaulting them to
# either would bias that cut, and they are 0.6% of plays.
#
# Penalty is here as "unknown" for a second reason. A CFBD penalty row carries
# a down, a distance and a yardsGained, so a derived success flag would score
# every penalty as a failure. Mapping it to unknown keeps it in the play pool
# -- where this repo wants it -- while keeping it out of every graded
# denominator.
CFBD_PLAY_TYPE_TO_RUN_PASS = {
    "Rush": "run",
    "Rushing Touchdown": "run",
    "Pass Reception": "pass",
    "Pass Incompletion": "pass",
    "Pass Completion": "pass",
    "Passing Touchdown": "pass",
    "Sack": "pass",
    "Interception": "pass",
    "Pass Interception Return": "pass",
    "Interception Return Touchdown": "pass",
}

UNKNOWN = "unknown"

# Down -> the share of the distance a play must gain to succeed. The standard
# convention, the same one nflfastR and Football Outsiders use. Baylor's chart
# carries its own hand-tagged Efficiency flag; the two are reconciled and the
# disagreement rate published rather than one being assumed to equal the other.
_SUCCESS_THRESHOLD = {1: 0.5, 2: 0.7, 3: 1.0, 4: 1.0}


def classify_run_pass(play_type) -> str:
    """"run", "pass", or "unknown". Never guesses."""
    if not isinstance(play_type, str):
        return UNKNOWN
    return CFBD_PLAY_TYPE_TO_RUN_PASS.get(play_type, UNKNOWN)


def derive_success(down, distance, gain) -> bool | None:
    """The 50 / 70 / 100 convention. None when the play cannot be graded.

    None rather than False for an ungradeable play, because a fifth down is
    not a failed play -- it is a play with no convention. Returning False
    would put it in the denominator as a stop.
    """
    if pd.isna(down) or pd.isna(distance) or pd.isna(gain):
        return None
    threshold = _SUCCESS_THRESHOLD.get(int(down))
    if threshold is None:
        return None
    return float(gain) >= threshold * float(distance)


def is_fbs(conference) -> bool:
    """Total, and never raises. A Division II offence is simply not FBS."""
    return conference in FBS_CONFERENCES


def opponent_level(conference) -> str:
    """"fbs" or "fcs" for one of Baylor's opponents. Raises on anything else.

    Deliberately not total. This is called only on teams Baylor actually
    played, where an unrecognised conference means a realignment or a CFBD
    rename -- and quietly returning "fcs" would drop a real conference game
    out of the headline without a word.
    """
    if conference in FBS_CONFERENCES:
        return "fbs"
    if conference in FCS_CONFERENCES:
        return "fcs"
    raise ValueError(
        f"Unknown conference {conference!r}. Add it to FBS_CONFERENCES or "
        "FCS_CONFERENCES in src/playcalls/opponent.py. It is not guessed, "
        "because guessing 'fcs' would drop the game from the headline."
    )
```

- [ ] **Step 4: Run and confirm they pass**

Run: `.venv/bin/python -m pytest tests/test_opponent.py -q`

Expected: 18 passed.

- [ ] **Step 5: Prove the mapping's coverage against real data**

Add to `tests/test_opponent.py`:

```python
def test_run_pass_mapping_covers_almost_every_epa_bearing_play():
    """A mapping that covered 60% would pass every unit test above and
    still make the run and pass cuts meaningless."""
    plays = opponent.load_season_plays(2025)
    scored = plays[plays["ppa"].notna()]
    classified = scored["playType"].map(opponent.classify_run_pass)
    covered = (classified != opponent.UNKNOWN).mean()
    assert covered >= 0.98, f"run/pass mapping covers only {covered:.3%}"
```

This depends on Task 3, so it will fail until then. That is expected and it is written now so the requirement is not forgotten.

- [ ] **Step 6: Commit**

```bash
git add src/playcalls/opponent.py tests/test_opponent.py
git commit -m "Add the CFBD-side classifiers for opponent adjustment

Three pure functions everything downstream rests on.

classify_run_pass is deliberately partial. Fumble recoveries get their own
CFBD play type and it never says whether the snap behind them was a run or
a pass, so they resolve to unknown and are excluded from run and pass cuts
on both sides. So does Penalty -- a CFBD penalty row carries a down, a
distance and a gain, so a derived success flag would score every penalty as
a failure. Unknown keeps it in the play pool and out of every graded
denominator. An unmapped type resolves to unknown rather than defaulting to
run, and a test asserts it.

derive_success returns None, not False, for an ungradeable play. A fifth
down is not a stop; it is a play with no convention.

opponent_level raises on an unrecognised conference rather than returning
fcs, because quietly demoting a team would drop a real conference game out
of the headline without a word. The conference strings were read from the
parquet: CFBD writes 'American Athletic', not 'AAC'.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TJszvQjQaXduVaswN86tYR"
```

---

### Task 3: `load_season_plays` — all teams, one season

**Files:**
- Modify: `src/playcalls/opponent.py` (add the loader)
- Test: `tests/test_opponent.py`

**Interfaces:**
- Consumes: `cfbd.CFBD_PLAYS_ROOT`, `cfbd._attach_pre_snap_score` (fixed in Task 1).
- Produces: `load_season_plays(season: int, root: str = cfbd.CFBD_PLAYS_ROOT) -> pd.DataFrame` with columns `season, gameId, week, seasonType, offense, offenseConference, defense, defenseConference, period, down, distance, yardsToGoal, yardsGained, clock_rem, playType, ppa, offenseScore, defenseScore, driveNumber, playNumber, pre_offense_score, pre_defense_score`.

- [ ] **Step 1: Write the failing tests**

```python
class TestLoadSeasonPlays:
    def test_it_loads_every_team_not_just_baylor(self):
        plays = opponent.load_season_plays(2025)
        assert len(plays) > 250_000
        assert plays["offense"].nunique() > 200
        assert "Baylor" in set(plays["offense"])

    def test_it_carries_the_conference_columns(self):
        plays = opponent.load_season_plays(2025)
        assert "offenseConference" in plays.columns
        assert "defenseConference" in plays.columns
        assert "Big 12" in set(plays["defenseConference"].dropna())

    def test_it_attaches_a_pre_snap_score(self):
        plays = opponent.load_season_plays(2025)
        assert "pre_offense_score" in plays.columns
        assert "pre_defense_score" in plays.columns

    def test_a_missing_season_raises_with_the_command_to_run(self):
        """This repo never calls the CFBD API. The free tier is 1,000 calls a
        month and the budget guard lives in CFB_Analytics_Lab."""
        with pytest.raises(FileNotFoundError, match="cfblab.pull"):
            opponent.load_season_plays(1999)
```

- [ ] **Step 2: Run and confirm they fail**

Run: `.venv/bin/python -m pytest tests/test_opponent.py::TestLoadSeasonPlays -q`

Expected: FAIL, `module 'src.playcalls.opponent' has no attribute 'load_season_plays'`.

- [ ] **Step 3: Implement**

Add to `src/playcalls/opponent.py` (imports first: `import pathlib`, `import duckdb`, `from src.playcalls import cfbd, epa`):

```python
_SEASON_QUERY = """
select
    season,
    gameId,
    week,
    seasonType,
    offense,
    offenseConference,
    defense,
    defenseConference,
    period,
    down,
    distance,
    yardsToGoal,
    yardsGained,
    "clock.minutes" * 60 + "clock.seconds" as clock_rem,
    playType,
    ppa,
    offenseScore,
    defenseScore,
    driveNumber,
    playNumber
from read_parquet(?, union_by_name = true)
"""


def load_season_plays(
    season: int, root: str = cfbd.CFBD_PLAYS_ROOT
) -> pd.DataFrame:
    """Every play in one CFBD season, all teams.

    cfbd.load_baylor_plays filters to one offence in SQL. This does not,
    because a defensive baseline needs the opponent's OTHER games. That is
    why cfbd._attach_pre_snap_score had to be grouped by (game, offence):
    in this frame the offence alternates within a game.

    The season is baked into the glob rather than filtered afterwards, for
    the same reason as load_baylor_plays -- Baylor plays Auburn in 2025 and
    again in 2026.
    """
    directory = pathlib.Path(root) / f"season={season}"
    if not directory.is_dir() or not list(directory.glob("*.parquet")):
        raise FileNotFoundError(
            f"No CFBD plays for {season} at {directory}.\n"
            "This repo never calls the CFBD API. Pull it in the repo that "
            "owns CFBD ingest, which enforces the free-tier budget guard:\n"
            f"  cd ~/DEV/CFB_Analytics_Lab && "
            f".venv/bin/python -m cfblab.pull plays --season {season}"
        )

    connection = duckdb.connect()
    try:
        frame = connection.execute(
            _SEASON_QUERY, [str(directory / "*.parquet")]
        ).df()
    finally:
        connection.close()

    frame["season"] = frame["season"].astype(int)
    return cfbd._attach_pre_snap_score(frame)
```

- [ ] **Step 4: Run the whole opponent suite**

Run: `.venv/bin/python -m pytest tests/test_opponent.py -q`

Expected: all pass, including `test_run_pass_mapping_covers_almost_every_epa_bearing_play` from Task 2 Step 5.

- [ ] **Step 5: Commit**

```bash
git add src/playcalls/opponent.py tests/test_opponent.py
git commit -m "Load a whole CFBD season, all teams

A defensive baseline needs the opponent's games against everyone else, so
this loader cannot filter to one offence the way load_baylor_plays does.
That is exactly why the pre-snap score had to be regrouped in the previous
commit: in this frame the offence alternates within a game.

Carries the conference columns, which load_baylor_plays does not need. They
do two jobs: filter baseline offences to FBS, and decide whether a Baylor
opponent is FBS or FCS.

Same missing-season error as load_baylor_plays, naming the command to run in
CFB_Analytics_Lab. This repo never calls the CFBD API.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TJszvQjQaXduVaswN86tYR"
```

---

### Task 4: `defence_baseline` — what one opponent allowed everyone else

**Files:**
- Modify: `src/playcalls/opponent.py`
- Test: `tests/test_opponent.py`

**Interfaces:**
- Consumes: `classify_run_pass`, `derive_success`, `is_fbs`, `epa.is_non_play`, `epa.is_garbage_time`.
- Produces:
  - `CUTS: tuple[str, ...]` = `("overall", "run", "pass", "early_down_run")`
  - `attach_cut_columns(frame, *, play_type_col, down_col, gain_col) -> pd.DataFrame` — adds `_run_pass`, `_derived_success`, `_graded`
  - `apply_cut(frame, cut) -> pd.DataFrame`
  - `flag_garbage(frame, *, period_col="period") -> pd.Series[bool]`
  - `summarise(frame) -> dict` — keys `plays, graded, successes, success_rate, epa_plays, epa_total, epa_per_play`
  - `defence_baseline(season_plays, opponent_cfbd_name, cut, *, exclude_garbage=False) -> dict`

- [ ] **Step 1: Write the failing tests**

```python
def _fake_season():
    """Two defences, one of which played Baylor. Hand-built so every
    expected number can be checked by eye."""
    return pd.DataFrame({
        "gameId":            [1, 1, 2, 2, 3, 3],
        "driveNumber":       [1, 1, 1, 1, 1, 1],
        "playNumber":        [1, 2, 1, 2, 1, 2],
        "offense":           ["Baylor", "Baylor", "Utah", "Utah", "Rice", "Rice"],
        "offenseConference": ["Big 12", "Big 12", "Big 12", "Big 12",
                              "American Athletic", "American Athletic"],
        "defense":           ["TCU"] * 6,
        "defenseConference": ["Big 12"] * 6,
        "period":            [1, 1, 1, 1, 1, 1],
        "down":              [1, 1, 1, 2, 1, 1],
        "distance":          [10, 10, 10, 10, 10, 10],
        "yardsGained":       [9, 1, 8, 2, 6, 0],
        "playType":          ["Rush", "Rush", "Rush", "Rush",
                              "Pass Reception", "Timeout"],
        "ppa":               [0.5, -0.3, 0.4, -0.2, 0.6, None],
        "offenseScore":      [0, 0, 0, 0, 0, 0],
        "defenseScore":      [0, 0, 0, 0, 0, 0],
        "pre_offense_score": [0, 0, 0, 0, 0, 0],
        "pre_defense_score": [0, 0, 0, 0, 0, 0],
    })


class TestDefenceBaseline:
    def test_it_excludes_baylors_own_game(self):
        """Without this the adjustment is circular: Baylor's bad day makes
        the opponent look good, which then excuses Baylor's bad day."""
        result = opponent.defence_baseline(_fake_season(), "TCU", "overall")
        # Baylor's two plays (ppa 0.5, -0.3) must not be in the total.
        # Utah 0.4 + Utah -0.2 + Rice 0.6 = 0.8 over 3 EPA plays.
        assert result["epa_plays"] == 3
        assert result["epa_total"] == pytest.approx(0.8)

    def test_it_excludes_non_fbs_offences(self):
        """Every FBS defence plays an FCS body-bag game. Leaving it in
        flatters the baseline and so understates Baylor."""
        season = _fake_season()
        season.loc[season["offense"] == "Rice", "offenseConference"] = "Southern"
        result = opponent.defence_baseline(season, "TCU", "overall")
        assert result["epa_plays"] == 2  # Utah only

    def test_it_drops_non_plays(self):
        """A Timeout carries the state of the play behind it and a gain of 0.
        Left in, it is a free failure in every denominator it touches."""
        result = opponent.defence_baseline(_fake_season(), "TCU", "overall")
        assert result["plays"] == 3  # Utah x2 + Rice reception; Timeout gone

    def test_epa_plays_never_exceeds_plays(self):
        result = opponent.defence_baseline(_fake_season(), "TCU", "overall")
        assert result["epa_plays"] <= result["plays"]

    def test_the_run_cut_uses_cfbd_play_type(self):
        result = opponent.defence_baseline(_fake_season(), "TCU", "run")
        assert result["epa_plays"] == 2  # Utah's two rushes
        assert result["epa_total"] == pytest.approx(0.2)

    def test_the_early_down_run_cut_filters_on_down(self):
        season = _fake_season()
        season.loc[3, "down"] = 3  # Utah's second rush becomes 3rd down
        result = opponent.defence_baseline(season, "TCU", "early_down_run")
        assert result["epa_plays"] == 1

    def test_derived_success_excludes_unknown_play_types(self):
        """A Penalty row has a down, a distance and a gain. Graded, it is a
        free failure on both sides of the subtraction."""
        season = _fake_season()
        season.loc[2, "playType"] = "Penalty"
        result = opponent.defence_baseline(season, "TCU", "overall")
        assert result["graded"] == 2  # Utah's 2nd-down rush + Rice reception
```

- [ ] **Step 2: Run and confirm they fail**

Run: `.venv/bin/python -m pytest tests/test_opponent.py::TestDefenceBaseline -q`

Expected: FAIL, no attribute `defence_baseline`.

- [ ] **Step 3: Implement**

Add to `src/playcalls/opponent.py`:

```python
CUTS = ("overall", "run", "pass", "early_down_run")


def attach_cut_columns(
    frame: pd.DataFrame,
    *,
    play_type_col: str,
    down_col: str,
    distance_col: str,
    gain_col: str,
) -> pd.DataFrame:
    """Add _run_pass, _derived_success and _graded.

    The column names are arguments because this runs over two differently
    shaped frames: a raw CFBD season, and the joined Baylor table. What it
    must NOT do is take them from different sources on the two sides -- both
    callers pass CFBD columns, which is the whole point of the module.
    """
    out = frame.copy()
    out["_run_pass"] = out[play_type_col].map(classify_run_pass)
    out["_derived_success"] = [
        derive_success(down, distance, gain)
        for down, distance, gain in zip(
            out[down_col], out[distance_col], out[gain_col]
        )
    ]
    # Graded means gradeable: a real run or pass, on a down with a
    # convention. Penalties and fumble recoveries are plays but not grades.
    out["_graded"] = (
        out["_run_pass"].isin(("run", "pass"))
        & out["_derived_success"].notna()
    )
    return out


def apply_cut(frame: pd.DataFrame, cut: str) -> pd.DataFrame:
    """One of CUTS. Assumes attach_cut_columns has run."""
    if cut == "overall":
        return frame
    if cut == "run":
        return frame[frame["_run_pass"] == "run"]
    if cut == "pass":
        return frame[frame["_run_pass"] == "pass"]
    if cut == "early_down_run":
        return frame[
            (frame["_run_pass"] == "run") & frame["_down_for_cut"].isin((1, 2))
        ]
    raise ValueError(f"Unknown cut {cut!r}. Known cuts: {', '.join(CUTS)}")


def flag_garbage(frame: pd.DataFrame, *, period_col: str = "period") -> pd.Series:
    """Garbage time from the PRE-snap score, never the post-play score."""
    margin = pd.to_numeric(
        frame["pre_offense_score"], errors="coerce"
    ) - pd.to_numeric(frame["pre_defense_score"], errors="coerce")
    return pd.Series(
        [
            epa.is_garbage_time(period, value)
            if pd.notna(period) and pd.notna(value)
            else False
            for period, value in zip(frame[period_col], margin)
        ],
        index=frame.index,
    )


def summarise(frame: pd.DataFrame) -> dict:
    """plays, graded, successes and the EPA (CFBD PPA) totals.

    plays, graded and epa_plays are three different counts and all three are
    returned. A play can be graded with no EPA (CFBD scores no penalty-wiped
    play) and can carry EPA without being graded (a fumble recovery). Using
    one as the other is how a coverage problem turns into a wrong rate.
    """
    values = pd.to_numeric(frame.get("_epa"), errors="coerce")
    graded = frame["_graded"]
    successes = int((graded & frame["_derived_success"].fillna(False)).sum())
    epa_plays = int(values.notna().sum())
    epa_total = float(values.sum()) if epa_plays else 0.0
    graded_n = int(graded.sum())

    return {
        "plays": int(len(frame)),
        "graded": graded_n,
        "successes": successes,
        "success_rate": round(successes / graded_n, 4) if graded_n else None,
        "epa_plays": epa_plays,
        "epa_total": round(epa_total, 4),
        "epa_per_play": round(epa_total / epa_plays, 4) if epa_plays else None,
    }


def defence_baseline(
    season_plays: pd.DataFrame,
    opponent_cfbd_name: str,
    cut: str,
    *,
    exclude_garbage: bool = False,
) -> dict:
    """What one defence allowed non-Baylor FBS offences, on one cut.

    Baylor is excluded by offence name, not by game, so a hypothetical second
    meeting in the same season is excluded too. Without that the adjustment is
    circular -- Baylor's own bad day would make the opponent look better,
    which would then partly excuse Baylor's bad day.
    """
    frame = season_plays[
        (season_plays["defense"] == opponent_cfbd_name)
        & (season_plays["offense"] != BAYLOR)
        & season_plays["offenseConference"].map(is_fbs)
    ].copy()

    frame = frame[~frame["playType"].map(epa.is_non_play)]

    frame = attach_cut_columns(
        frame,
        play_type_col="playType",
        down_col="down",
        distance_col="distance",
        gain_col="yardsGained",
    )
    frame["_down_for_cut"] = pd.to_numeric(frame["down"], errors="coerce")
    frame["_epa"] = pd.to_numeric(frame["ppa"], errors="coerce")

    if exclude_garbage:
        frame = frame[~flag_garbage(frame)]

    return summarise(apply_cut(frame, cut))
```

- [ ] **Step 4: Run and confirm they pass**

Run: `.venv/bin/python -m pytest tests/test_opponent.py -q`

Expected: all pass.

- [ ] **Step 5: Sanity-check against real data**

Run:

```bash
.venv/bin/python -c "
from src.playcalls import opponent
p = opponent.load_season_plays(2025)
for team in ('Texas Tech', 'Samford', 'Auburn'):
    b = opponent.defence_baseline(p, team, 'overall')
    print(f'{team:12s} plays={b[\"plays\"]:4d} epa_plays={b[\"epa_plays\"]:4d} '
          f'epa/play={b[\"epa_per_play\"]:+.4f} sr={b[\"success_rate\"]:.3f}')
"
```

Expected: Texas Tech's EPA allowed should be clearly negative (a good defence); Samford's should be near zero or positive but computed over FBS offences only — **if Samford's `plays` is 0, that is correct and expected**, because Samford plays no FBS offences other than Baylor. Record the numbers.

- [ ] **Step 6: Handle the empty-baseline case explicitly**

If Step 5 shows Samford with zero FBS plays, add this test and confirm it already passes:

```python
def test_an_opponent_with_no_fbs_baseline_returns_nulls_not_zero():
    """Samford plays no FBS offence other than Baylor. Its baseline is
    genuinely absent, and absent must not read as 0.000 EPA allowed --
    that would look like a perfectly average defence."""
    season = _fake_season()
    season.loc[season["offense"] != "Baylor", "offenseConference"] = "Southern"
    result = opponent.defence_baseline(season, "TCU", "overall")
    assert result["epa_plays"] == 0
    assert result["epa_per_play"] is None
    assert result["success_rate"] is None
```

- [ ] **Step 7: Commit**

```bash
git add src/playcalls/opponent.py tests/test_opponent.py
git commit -m "Compute what one defence allowed everyone else

Baylor is excluded from its own opponent's baseline by offence name, not by
game, so a second meeting in one season would be excluded too. Without it
the adjustment is circular: Baylor's bad day makes the opponent look better,
which then partly excuses Baylor's bad day.

Baseline offences are filtered to FBS. Every FBS defence plays an FCS
body-bag game, and leaving it in flatters the baseline and so understates
Baylor. The parquet carries 311 defences across 40 conferences including
Division II, so this is a real filter and not a formality.

Three counts are returned, never one standing in for another. A play can be
graded with no EPA (CFBD scores no penalty-wiped play) and can carry EPA
without being graded (a fumble recovery has no run/pass).

An absent baseline returns None, not 0.0. Zero EPA allowed reads as a
perfectly average defence; absent must not look like average.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TJszvQjQaXduVaswN86tYR"
```

---

### Task 5: `schedule_strength` and `adjusted_table`

The two deliverables. `schedule_strength` answers the descriptive question on its own; `adjusted_table` does the subtraction.

**Files:**
- Modify: `src/playcalls/opponent.py`
- Test: `tests/test_opponent.py`

**Interfaces:**
- Consumes: everything from Tasks 2-4, plus `cfbd.OPPONENT_TO_CFBD`.
- Produces:
  - `baylor_cut_frame(joined, season, cut, *, exclude_garbage=False) -> pd.DataFrame` — Baylor's plays for one cut, classified from CFBD columns
  - `schedule_strength(joined, season_plays, season, cut, *, exclude_garbage=False) -> pd.DataFrame` — one row per game
  - `adjusted_table(joined, plays_by_season, cut, *, exclude_garbage=False) -> pd.DataFrame` — one row per season

`schedule_strength` columns: `season, game_code, opponent, opponent_cfbd, level, baylor_plays, baylor_graded, baylor_successes, baylor_epa_plays, baylor_epa_total, baseline_plays, baseline_epa_plays, baseline_epa_per_play, baseline_success_rate`.

`adjusted_table` columns: `season, cut, games, games_fbs, plays, graded, epa_plays, raw_all_games_epa, raw_fbs_only_epa, schedule_baseline_epa, adjusted_epa, raw_all_games_sr, raw_fbs_only_sr, schedule_baseline_sr, adjusted_sr`.

- [ ] **Step 1: Write the failing tests**

```python
class TestAdjustment:
    def test_baylor_side_is_classified_from_cfbd_not_the_chart(self):
        """The scramble trap. 46 Baylor plays are charted P and typed Rush.
        A chart-based pass rate would include scrambles the opponent
        baseline structurally excludes."""
        joined = pd.DataFrame({
            "season": [2025, 2025],
            "game_code": ["2501", "2501"],
            "def_team": ["ALAU", "ALAU"],
            "run_pass": ["P", "P"],          # chart says pass
            "cfbd_play_type": ["Rush", "Pass Reception"],
            "down": [1, 1], "distance": [10, 10],
            "gain": [7, 12], "cfbd_yards_gained": [7.0, 12.0],
            "epa": [0.3, 0.5], "quarter": [1.0, 1.0],
            "garbage_time": [False, False],
            "efficiency": ["Y", "Y"],
        })
        runs = opponent.baylor_cut_frame(joined, 2025, "run")
        assert len(runs) == 1, "the scramble must count as a run, as CFBD sees it"

    def test_adjusted_is_raw_fbs_minus_the_baseline(self):
        """Hand-checkable arithmetic. Two games, one FCS."""
        joined = pd.DataFrame({
            "season": [2025] * 4,
            "game_code": ["2501", "2501", "2502", "2502"],
            "def_team": ["ALAU", "ALAU", "ALSM", "ALSM"],
            "run_pass": ["R"] * 4,
            "cfbd_play_type": ["Rush"] * 4,
            "down": [1] * 4, "distance": [10] * 4,
            "gain": [5, 5, 20, 20], "cfbd_yards_gained": [5.0, 5.0, 20.0, 20.0],
            "epa": [0.2, 0.4, 2.0, 2.0], "quarter": [1.0] * 4,
            "garbage_time": [False] * 4,
            "efficiency": ["Y"] * 4,
        })
        # Auburn (FBS) allowed +0.1/play; Samford is FCS and excluded.
        baselines = {("Auburn", "overall"): 0.1}
        table = opponent.adjusted_table(
            joined, {2025: _season_for(baselines)}, "overall"
        )
        row = table.iloc[0]
        # raw over all four plays = (0.2+0.4+2.0+2.0)/4 = 1.15
        assert row["raw_all_games_epa"] == pytest.approx(1.15)
        # raw over Auburn only = (0.2+0.4)/2 = 0.30
        assert row["raw_fbs_only_epa"] == pytest.approx(0.30)
        assert row["schedule_baseline_epa"] == pytest.approx(0.10)
        assert row["adjusted_epa"] == pytest.approx(0.20)

    def test_weighting_is_by_plays_not_by_game(self):
        """A 90-play game must not weigh the same as a 30-play game. A mean
        of per-game means would make it."""
        # 3 plays vs Alpha (baseline 0.0), 1 play vs Beta (baseline 1.0).
        # Play-weighted baseline = (0.0*3 + 1.0*1) / 4 = 0.25
        # A mean of game means would give (0.0 + 1.0) / 2 = 0.50
        ...  # built in the same shape as the test above
        assert row["schedule_baseline_epa"] == pytest.approx(0.25)

    def test_the_headline_excludes_exactly_one_fcs_game_per_season(self):
        table = opponent.adjusted_table(joined_real, plays_by_season, "overall")
        for _, row in table.iterrows():
            assert row["games"] - row["games_fbs"] == 1

    def test_every_opponent_code_maps(self):
        """cfbd.OPPONENT_TO_CFBD raises by name on an unmapped code, which is
        the guard against the bowl-is-week-1 trap."""
        joined = pd.read_parquet("outputs/joined_plays_enriched.parquet")
        for code in joined["def_team"].dropna().unique():
            assert code in cfbd.OPPONENT_TO_CFBD, code
```

`_season_for(baselines)` is a helper that builds a minimal season frame producing the given baseline values — write it alongside `_fake_season()`.

- [ ] **Step 2: Run and confirm they fail**

Run: `.venv/bin/python -m pytest tests/test_opponent.py::TestAdjustment -q`

Expected: FAIL, no attribute `baylor_cut_frame`.

- [ ] **Step 3: Implement `baylor_cut_frame`**

```python
def baylor_cut_frame(
    joined: pd.DataFrame,
    season: int,
    cut: str,
    *,
    exclude_garbage: bool = False,
) -> pd.DataFrame:
    """Baylor's plays for one cut, classified the way the baseline is.

    Every classifying column here comes from CFBD, not the chart, and that is
    the point. The chart records the play CALL and CFBD records the RESULT;
    46 plays are charted P and typed Rush. A chart-classified Baylor rate
    subtracted from a CFBD-classified baseline would compare two different
    things and say nothing.

    down and distance are the chart's, and that is not an exception: they are
    the join key, so on a matched row they equal CFBD's by construction.
    """
    frame = joined[joined["season"] == season].copy()
    frame = attach_cut_columns(
        frame,
        play_type_col="cfbd_play_type",
        down_col="down",
        distance_col="distance",
        gain_col="cfbd_yards_gained",
    )
    frame["_down_for_cut"] = pd.to_numeric(frame["down"], errors="coerce")
    frame["_epa"] = pd.to_numeric(frame["epa"], errors="coerce")

    if exclude_garbage:
        frame = frame[~frame["garbage_time"].fillna(False).astype(bool)]

    return apply_cut(frame, cut)
```

- [ ] **Step 4: Implement `schedule_strength`**

```python
def schedule_strength(
    joined: pd.DataFrame,
    season_plays: pd.DataFrame,
    season: int,
    cut: str,
    *,
    exclude_garbage: bool = False,
) -> pd.DataFrame:
    """One row per Baylor game: what Baylor did, and what that defence
    normally allowed.

    This is the descriptive answer on its own. If Baylor's 2025 opponents did
    not allow materially less than its 2024 opponents, opponent adjustment is
    refuted as the explanation before any subtraction is done.
    """
    baylor = baylor_cut_frame(
        joined, season, cut, exclude_garbage=exclude_garbage
    )

    rows = []
    for game_code, game in baylor.groupby("game_code", sort=True):
        code = game["def_team"].dropna().iloc[0]
        name = cfbd.OPPONENT_TO_CFBD[code]  # raises by name on an unmapped code

        conference = season_plays.loc[
            season_plays["defense"] == name, "defenseConference"
        ]
        level = opponent_level(
            conference.iloc[0] if len(conference) else None
        )

        baseline = defence_baseline(
            season_plays, name, cut, exclude_garbage=exclude_garbage
        )
        summary = summarise(game)

        rows.append({
            "season": season,
            "cut": cut,
            "game_code": game_code,
            "opponent": code,
            "opponent_cfbd": name,
            "level": level,
            "baylor_plays": summary["plays"],
            "baylor_graded": summary["graded"],
            "baylor_successes": summary["successes"],
            "baylor_epa_plays": summary["epa_plays"],
            "baylor_epa_total": summary["epa_total"],
            "baseline_plays": baseline["plays"],
            "baseline_graded": baseline["graded"],
            "baseline_epa_plays": baseline["epa_plays"],
            "baseline_epa_per_play": baseline["epa_per_play"],
            "baseline_success_rate": baseline["success_rate"],
        })

    return pd.DataFrame(rows)
```

- [ ] **Step 5: Implement `adjusted_table`**

```python
def _weighted(values, weights):
    """Play-weighted mean, skipping rows with no baseline.

    Weighted, not a mean of means: a 90-play game must not weigh the same as
    a 30-play game.
    """
    pairs = [
        (value, weight)
        for value, weight in zip(values, weights)
        if value is not None and pd.notna(value) and weight
    ]
    if not pairs:
        return None, 0
    total_weight = sum(weight for _, weight in pairs)
    return sum(value * weight for value, weight in pairs) / total_weight, total_weight


def adjusted_table(
    joined: pd.DataFrame,
    plays_by_season: dict[int, pd.DataFrame],
    cut: str,
    *,
    exclude_garbage: bool = False,
) -> pd.DataFrame:
    """One row per season: raw, raw-FBS-only, baseline, adjusted.

    Three raw columns rather than one, because excluding the FCS game moves
    Baylor's RAW number too. A reader who saw only `adjusted` beside
    REPORT.md's 57.4% would reasonably conclude one document was wrong. The
    step from raw_all_games to raw_fbs_only is schedule composition; the step
    from there to adjusted is opponent quality.
    """
    rows = []
    for season in sorted(plays_by_season):
        games = schedule_strength(
            joined, plays_by_season[season], season, cut,
            exclude_garbage=exclude_garbage,
        )
        if games.empty:
            continue
        fbs = games[games["level"] == "fbs"]

        def ratio(frame, numerator, denominator):
            total = frame[denominator].sum()
            return round(frame[numerator].sum() / total, 4) if total else None

        baseline_epa, _ = _weighted(
            fbs["baseline_epa_per_play"], fbs["baylor_epa_plays"]
        )
        baseline_sr, _ = _weighted(
            fbs["baseline_success_rate"], fbs["baylor_graded"]
        )
        raw_fbs_epa = ratio(fbs, "baylor_epa_total", "baylor_epa_plays")
        raw_fbs_sr = ratio(fbs, "baylor_successes", "baylor_graded")

        rows.append({
            "season": season,
            "cut": cut,
            "games": int(len(games)),
            "games_fbs": int(len(fbs)),
            "plays": int(games["baylor_plays"].sum()),
            "graded": int(games["baylor_graded"].sum()),
            "epa_plays": int(games["baylor_epa_plays"].sum()),
            "raw_all_games_epa": ratio(games, "baylor_epa_total", "baylor_epa_plays"),
            "raw_fbs_only_epa": raw_fbs_epa,
            "schedule_baseline_epa": round(baseline_epa, 4) if baseline_epa is not None else None,
            "adjusted_epa": round(raw_fbs_epa - baseline_epa, 4)
                if raw_fbs_epa is not None and baseline_epa is not None else None,
            "raw_all_games_sr": ratio(games, "baylor_successes", "baylor_graded"),
            "raw_fbs_only_sr": raw_fbs_sr,
            "schedule_baseline_sr": round(baseline_sr, 4) if baseline_sr is not None else None,
            "adjusted_sr": round(raw_fbs_sr - baseline_sr, 4)
                if raw_fbs_sr is not None and baseline_sr is not None else None,
        })

    return pd.DataFrame(rows)
```

- [ ] **Step 6: Apply MIN_SAMPLE**

Add `from src.playcalls.analysis import MIN_SAMPLE` and suppress any `schedule_strength` row whose `baseline_epa_plays` is below it by setting `baseline_epa_per_play` and `baseline_success_rate` to `None` — do **not** drop the row, because the game still counts in `games` and in the raw figures. Add a test asserting a 5-play baseline is suppressed to `None` while the game's own row survives.

- [ ] **Step 7: Run the suite**

Run: `.venv/bin/python -m pytest -q`

Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add src/playcalls/opponent.py tests/test_opponent.py
git commit -m "Add schedule strength and the opponent-adjusted table

schedule_strength answers the descriptive question on its own: if Baylor's
2025 opponents did not allow materially less than its 2024 opponents, the
schedule explanation is refuted before any subtraction happens.

Baylor's side is classified from CFBD columns, not the chart. The chart
records the play CALL and CFBD records the RESULT -- 46 plays are charted P
and typed Rush. A chart-classified Baylor rate subtracted from a
CFBD-classified baseline would compare two different things. down and
distance stay the chart's, which is not an exception: they are the join key,
so on a matched row they equal CFBD's by construction.

Weighting is by plays, not a mean of per-game means. A 90-play game must not
weigh what a 30-play game weighs.

Three raw columns, not one. Excluding the FCS game moves Baylor's raw number
too, so a lone adjusted figure beside REPORT.md's 57.4% would read as a
contradiction. raw_all_games to raw_fbs_only is schedule composition;
raw_fbs_only to adjusted is opponent quality.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TJszvQjQaXduVaswN86tYR"
```

---

### Task 6: `reconcile_success` — does the charted flag match the convention?

A deliverable in its own right. It tells the staff how far its hand-tagged `Efficiency` flag sits from the industry convention, which nobody in this project has measured.

**Files:**
- Modify: `src/playcalls/opponent.py`
- Test: `tests/test_opponent.py`

**Interfaces:**
- Consumes: `derive_success`, `charting.SUCCESS_RATE_EXCLUDED`.
- Produces: `reconcile_success(joined) -> tuple[pd.DataFrame, dict]` — a per-season crosstab and a summary dict with `agreement_rate`, `charted_only`, `derived_only`, `compared`.

- [ ] **Step 1: Write the failing test**

```python
class TestReconciliation:
    def test_it_uses_chart_fields_not_cfbd_fields(self):
        """This table asks whether Baylor's hand-charted flag agrees with the
        convention ON BAYLOR'S OWN CHARTED FIELDS. Blending CFBD gains in
        would mix two questions and answer neither."""
        joined = pd.DataFrame({
            "season": [2025, 2025],
            "down": [1, 1], "distance": [10, 10],
            "gain": [6, 6],                    # chart: both successes
            "cfbd_yards_gained": [6.0, 1.0],   # CFBD disagrees on the second
            "efficiency": ["Y", "Y"],
        })
        _, summary = opponent.reconcile_success(joined)
        assert summary["agreement_rate"] == 1.0

    def test_x_and_blank_efficiency_leave_the_denominator(self):
        """X is a kneel or a penalty -- deliberately not graded."""
        joined = pd.DataFrame({
            "season": [2025] * 3,
            "down": [1, 1, 1], "distance": [10, 10, 10],
            "gain": [6, 6, 6],
            "efficiency": ["Y", "X", ""],
        })
        _, summary = opponent.reconcile_success(joined)
        assert summary["compared"] == 1

    def test_it_reports_disagreement_in_both_directions(self):
        joined = pd.DataFrame({
            "season": [2025] * 2,
            "down": [1, 1], "distance": [10, 10],
            "gain": [6, 2],
            "efficiency": ["N", "Y"],   # both disagree with the convention
        })
        _, summary = opponent.reconcile_success(joined)
        assert summary["agreement_rate"] == 0.0
        assert summary["derived_only"] == 1   # derived Y, charted N
        assert summary["charted_only"] == 1   # charted Y, derived N
```

- [ ] **Step 2: Run and confirm it fails**

Run: `.venv/bin/python -m pytest tests/test_opponent.py::TestReconciliation -q`

- [ ] **Step 3: Implement**

```python
def reconcile_success(joined: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Baylor's charted Efficiency against the 50/70/100 convention.

    CLAUDE.md requires that a re-derived success flag be reconciled against
    the charted one and the disagreement rate published. This does that, and
    it is a finding in its own right: it says how far the staff's hand-tagged
    flag sits from the convention every public number uses.

    Chart fields on both sides, deliberately. The question is whether the
    charted flag agrees with the convention applied to the charted gain, not
    whether the chart agrees with CFBD -- that is a separate figure, in
    provenance.
    """
    frame = joined.copy()
    graded = ~frame["efficiency"].isin(SUCCESS_RATE_EXCLUDED)
    frame = frame[graded].copy()

    frame["_charted"] = frame["efficiency"].eq("Y")
    frame["_derived"] = [
        derive_success(down, distance, gain)
        for down, distance, gain in zip(
            frame["down"], frame["distance"], frame["gain"]
        )
    ]
    frame = frame[frame["_derived"].notna()].copy()
    frame["_derived"] = frame["_derived"].astype(bool)

    crosstab = (
        frame.groupby(["season", "_charted", "_derived"])
        .size()
        .reset_index(name="plays")
    )

    agree = int((frame["_charted"] == frame["_derived"]).sum())
    compared = int(len(frame))
    summary = {
        "compared": compared,
        "agreement_rate": round(agree / compared, 4) if compared else None,
        "charted_only": int((frame["_charted"] & ~frame["_derived"]).sum()),
        "derived_only": int((~frame["_charted"] & frame["_derived"]).sum()),
    }
    return crosstab, summary
```

Import `SUCCESS_RATE_EXCLUDED` from `src.playcalls.charting`.

- [ ] **Step 4: Run and confirm they pass**

Run: `.venv/bin/python -m pytest tests/test_opponent.py -q`

- [ ] **Step 5: Look at the real answer**

Run:

```bash
.venv/bin/python -c "
import pandas as pd
from src.playcalls import opponent
j = pd.read_parquet('outputs/joined_plays_enriched.parquet')
crosstab, summary = opponent.reconcile_success(j)
print(summary)
print(crosstab.to_string(index=False))
"
```

Record the agreement rate. If it is below about 0.90, that is a finding and it belongs in the report's opening, not a footnote.

- [ ] **Step 6: Commit**

```bash
git add src/playcalls/opponent.py tests/test_opponent.py
git commit -m "Reconcile the charted efficiency flag against the convention

CLAUDE.md requires that a re-derived success flag be reconciled against the
charted one and the disagreement rate published. Phase 5 re-derives success
because CFBD has no Efficiency column and no other team is hand-charted, so
this is that reconciliation.

It is also a finding on its own. Nobody in this project has measured how far
Baylor's hand-tagged flag sits from the 50/70/100 convention every public
number uses, and a staff quoting one against the other should know.

Chart fields on both sides here, unlike the adjusted tables. The question is
whether the charted flag agrees with the convention applied to the charted
gain. Whether the chart agrees with CFBD is a different figure and lives in
provenance.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01TJszvQjQaXduVaswN86tYR"
```

---

### Task 7: The builders, the report, and the naming guard

**Files:**
- Create: `src/playcalls/opponent_report.py`, `build_opponent_tables.py`, `build_opponent_report.py`
- Modify: `tests/test_opponent.py`
- Output: `outputs/tables/opponent_*.csv`, `outputs/OPPONENT.md`, `outputs/opponent_provenance.json`

**Interfaces:**
- Consumes: everything above, `seasons.resolve_seasons`.
- Produces: `render_opponent_report(tables: dict, provenance: dict) -> str`.

- [ ] **Step 1: Write the naming-guard test first**

The existing guard does not cover this file. `tests/test_report.py:138` calls `render_report()` directly, so it guards `REPORT.md`'s renderer only.

```python
def test_opponent_report_names_epas_source_before_any_bare_mention():
    """The gap test_report.py leaves open. Its guard calls render_report()
    directly, so a second report file inherits nothing from it."""
    text = opponent_report.render_opponent_report(_stub_tables(), _stub_provenance())
    assert "EPA (CFBD PPA)" in text
    first_qualified = text.index("EPA (CFBD PPA)")
    first_any = text.index("EPA")
    assert first_any == first_qualified, (
        f"EPA mentioned before it is source-qualified: "
        f"{text[first_any:first_any + 120]!r}"
    )
```

- [ ] **Step 2: Write `build_opponent_tables.py`**

Follows `build_alignment_tables.py`'s shape. Reads seasons from `seasons.resolve_seasons()`, loads each season's CFBD plays once into `plays_by_season`, then writes:

```
outputs/tables/opponent_schedule_strength.csv         (all seasons, all cuts)
outputs/tables/opponent_adjusted.csv                  (one row per season x cut)
outputs/tables/opponent_adjusted_clean.csv            (garbage time excluded)
outputs/tables/opponent_success_reconciliation.csv
outputs/tables/opponent_runpass_classification_audit.csv
outputs/opponent_provenance.json
```

The audit CSV lists every distinct `playType` seen, its count, its classification, and whether it carries PPA — so an unmapped type is visible rather than inferred.

Provenance carries: seasons run, `MIN_SAMPLE`, the FBS conference set, per-season run/pass coverage, the chart-vs-CFBD gain agreement rate (97.3% at time of writing), the reconciliation summary, and the FCS games excluded by name.

- [ ] **Step 3: Write the renderer and `build_opponent_report.py`**

`OPPONENT.md` sections, in this order:

1. **What this answers, and what it cannot.** Names the question and states plainly that a schedule effect and a decline can both be true.
2. **Schedule strength** — the descriptive answer, 2024 vs 2025, and whether it refutes or supports the explanation. This comes first because it can settle the question on its own.
3. **The adjusted table** — the four cuts, three raw columns each.
4. **Per-game detail** — `schedule_strength` for the overall cut.
5. **The reconciliation** — charted vs derived success, with the agreement rate.
6. **Method and limits** — the FCS exclusion, the CFBD classification rule, garbage time, and the caveat that this is a differential and not a full opponent-strength model.

First mention of EPA must read "EPA (CFBD PPA)".

- [ ] **Step 4: Run both builders**

```bash
.venv/bin/python build_opponent_tables.py
.venv/bin/python build_opponent_report.py
```

- [ ] **Step 5: Run the full suite and the existing pipeline**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python run.py
```

Expected: all tests pass; `run.py` still passes all three gates. The Task 1 fix must not have moved any gate number.

- [ ] **Step 6: Read `outputs/OPPONENT.md` end to end**

Check the numbers against Step 5 of Tasks 4 and 6. A number in the report that does not appear in a table is a bug.

- [ ] **Step 7: Commit**

---

## Self-Review

**Spec coverage.** §2.1 → Task 5. §2.2 → Task 4 test 1. §2.3 → Tasks 2, 5. §2.3b → Tasks 2, 4. §2.4 → Task 4. §2.4b → Task 1. §2.5 → Tasks 2, 5. §2.6 → Tasks 2, 4, 6. §2.7 → Task 4 (`CUTS`), Task 5 Step 6 (`MIN_SAMPLE`). §2.8 → Task 5. §3 → all tasks. §4 → the guards are the tests named in each task. §5 → every test listed appears. §6 (the Phase 3 design question) → **not covered by any task above**; added below. §7 is out of scope by definition.

**Gap found and closed:** §6 decides the open Phase 3 question and says it is "recorded in `PHASE3-READINESS.md` as decided." No task did that. Task 8 below.

**Type consistency.** `summarise` returns the same seven keys everywhere. `defence_baseline` returns `summarise`'s dict. `schedule_strength` prefixes Baylor's with `baylor_` and the opponent's with `baseline_`. `adjusted_table` reads only those prefixed names. `_epa`, `_run_pass`, `_derived_success`, `_graded` and `_down_for_cut` are the internal columns, added by `attach_cut_columns` except `_epa` and `_down_for_cut`, which each caller sets because their source column differs.

---

### Task 8: Record the Phase 3 decision and update the docs

**Files:**
- Modify: `docs/PHASE3-READINESS.md`, `CLAUDE.md`, `AGENTS.md`

- [ ] **Step 1: Answer the open question in `PHASE3-READINESS.md`**

Replace the "Open question for a weekly cadence" section with the decision from spec §6: same pipeline and same tables, full rebuild not append, a `games` column on every cross-season row, and an in-progress season labelled "2026 (through week N)" everywhere it appears.

- [ ] **Step 2: Correct the `pff.db` path in `PHASE3-READINESS.md`**

The document writes `PFF_Data_Project/data/pff.db`. The repository actually lives at `~/DEV/Football/PFF_Data_Project/`. Verified on 2026-09-10 while re-checking the blockers; `src/playcalls/pff.py` already has the correct absolute path.

- [ ] **Step 3: Add Phase 5 to `CLAUDE.md` and `AGENTS.md`**

**Kept in sync by hand — never symlink them.** Add a "Phase 5: opponent adjustment" section covering the method, the FCS exclusion, and the CFBD-classification rule. Add these to "Things that will bite you":

- The chart records the play CALL; CFBD records the RESULT. 46 plays are charted `P` and typed `Rush`. Any subtraction across the two must classify both sides from CFBD.
- `cfbd._attach_pre_snap_score` groups by `(gameId, offense)`. Grouping by `gameId` alone is correct only for a frame already filtered to one offence.
- The CFBD parquet is not FBS-only — 311 defences across 40 conferences in 2025, including Division II. Any baseline must filter `offenseConference`.
- A CFBD `Penalty` row carries a down, a distance and a gain, so a derived success flag scores it as a failure unless it is excluded.

- [ ] **Step 4: Run the full suite**

Run: `.venv/bin/python -m pytest -q`

- [ ] **Step 5: Commit**

---

## Execution

Inline, via `superpowers:executing-plans`. The handoff is explicit that the parallel-agent authorisation from the Phase 3/4 session does **not** carry forward, and no instruction in this session re-grants it.

Before declaring the phase done: run `codex-review` for the adversarial pass. Phase 2 shipped nine real defects past 136 green tests, and the score-state error among them was an analytical mistake no test was looking for.

# The standalone post-practice report — design

**Status:** approved 2026-08-02. Supersedes the open recommendations in
`docs/post-practice-report-decisions.md` §1, §2, §4, §6, §7.

The session debrief already exists as one of four views in the coach dashboard. This
document specifies turning it into something a coach can be *handed* — a single-practice
file that opens without a dashboard, prints, and can be emailed — without growing a
second copy of the logic that would drift from the first.

---

## What was decided

| Question | Decision |
|---|---|
| What is the artifact? | Both: one renderer, two shells. The dashboard keeps its browsable debrief tab; a new command emits a standalone single-practice file. |
| What does it lead with? | A descriptive verdict line, then the named exceptions, then squad tiles. |
| What is the headline number? | Jumps and jumps per minute together, mechanical load second. The standalone report is fixed-metric; the dashboard keeps its picker. |
| Suspect data? | Confirmed-bad athletes are held out of the exceptions block but stay visible in the ranked list, marked. Nothing is ever silently dropped. |
| Force plate readiness? | The intersection only — athletes who took high load today *and* entered the block low. Not the full readiness picture. |
| Where does the logic live? | Python, in a new `debrief.py`, so the judgment-heavy parts are testable without a browser. |

§3 was already settled on 2026-08-02 (above an athlete's own normal reads as risk) and is
not reopened here. §5 — whether drill-level export becomes routine — is a question for the
volleyball staff and cannot be answered in code.

## The headline metric

The dashboard offers a metric picker. The standalone report does not: an artifact you hand
someone should not depend on which control they last touched. It is built on **jumps**,
with **jumps per minute** beside it — the pairing §2 recommends, and the pairing that keeps
Practice 6 from reading as an easy day.

**Mechanical load** appears second, as a single line beneath the tiles rather than a tile of
its own, because it is the better injury-adjacent number but the less legible one. Jump load
in joules is not an option: it exists only for Practice 1.

`--metric <key>` overrides the default for anyone who wants a load-led or density-led
version, but the committed default is jumps and nothing about the report's structure changes
when it is overridden.

---

## Architecture

Four new modules, one extraction, no change to ingest or the database schema.

```
kinexon/
  chart_assets.py    NEW  CSS custom properties + the chart JS primitives, moved
                          verbatim out of build_dashboard.py so both shells share
                          one copy
  data_quality.py    NEW  reads the gitignored config/data-quality.json
  debrief.py         NEW  the derivations — verdict, exceptions, exclusions,
                          readiness intersection. Pure functions, no I/O.
  build_report.py    NEW  the standalone shell
  report.py          MOD  payload gains ["debrief"][practice_no]
  build_dashboard.py MOD  imports chart_assets; the debrief tab renders the
                          precomputed structure rather than deriving in JS
```

The placement follows a principle already written into `report.py`'s docstring:

> Everything derived lives here rather than in the page's JavaScript, so the numbers a
> coach sees can be checked from Python without a browser.

Everything this design adds is derivation — which session was unusual, which athletes
qualify as exceptions, which are excluded and why, who is carrying load on a low entry
baseline. All of it belongs in Python, and all of it is the first logic in this repository
with enough judgment in it to be worth a test.

### The one risky edit

Extracting `chart_assets.py` moves string constants out of a 55 KB file. It is mechanical
but wide. Verification is exact rather than eyeballed: generate the dashboard before the
extraction, extract, generate again, diff the two files. They must be identical except for
the `generated_at` timestamp. If they are not, the extraction is wrong.

## Data flow

```
kinexon.db
   -> report.build_payload()                     existing
   -> debrief.for_practice(payload, n, dq)       new
   -> {dashboard tab | standalone shell}         two shells, one structure
```

`debrief.for_practice` returns, per practice:

```python
{
  "practice_no":   int,
  "verdict":       {"text": str, "facts": [...]},
  "headline":      {"total": float, "per_min": float, "duration_s": int,
                    "per_athlete": float, "on_sensors": int},
  "exceptions":    {"high": [...], "low": [...], "n_considered": int},
  "excluded":      [{"athlete_id", "reason", "note", "confirmed_on"}],
  "suspected":     [{"athlete_id", "reason", "note"}],
  "data_quality":  {"usable": int, "total": int, "reviewed": bool},
  "readiness_flags": [...] | None,
}
```

Force plate data continues to be read through the existing read-only `forceplate.load()`.
No new copy of it is created anywhere — the central-store principle holds.

## The verdict line

Never free text. It scores three facts about the session — duration, squad total, squad
density — as a z-score against every session in the block, takes the two most divergent,
and states each alongside its rank.

The z includes the session being described, matching how an athlete's own baseline is
already computed in `report.py` (her mean across the block includes the practice being
compared to it). Excluding it would make the same session score differently depending on
which report it appeared in, which is worse than the mild shrinkage that including it
causes.

> Second-shortest session of the block, and the second-highest jump density. 900 jumps
> at 9.39/min, against a block average of 1,015 and 6.78/min.

Four rules keep it descriptive:

1. Ranks are stated only when the block holds three or more sessions. Below that, the
   sentence reports raw values with no ordinal language.
2. No causal and no prescriptive vocabulary, ever — not "hard", "easy", "too much",
   "should", "recommend". The line reports where the session sat; it does not interpret.
3. If no fact reaches |z| ≥ 1.0, the line reads *"A typical session for this block on
   volume and density"*. It does not manufacture a story out of noise.
4. Two sentences maximum.

Practice 6 is the case that motivates the whole feature: the second-lowest jump total in
the block, and a report leading on totals would call it a light day. It was the
second-densest session of the six.

*(Corrected 2026-08-03: this originally read "the lowest jump total", inherited from
`post-practice-report-decisions.md` §2. Practice 2 is lowest at 529 against Practice 6's
900. The point stands and the code was never affected.)*

## Exceptions

An athlete-session qualifies at |z| ≥ 1.5 against that athlete's own mean across the
block. The threshold matches what the dashboard already flags, so the two views can never
disagree about who is unusual.

- Confirmed exclusions are removed before selection, so a sensor fault cannot occupy a
  slot in the list.
- An athlete needs n ≥ 3 sessions in her baseline to be eligible at all. The middle
  blocker who arrived at Practice 4 sits at exactly 3; she is eligible, and every figure
  derived from her baseline is marked with its n.
- Both directions are reported and labelled by pole. Above her own normal is the risk
  direction and takes the warm token; below it is cool. These are exposure measures.
- The n behind each average is printed. At n=6 this is a prompt to look, not a finding,
  and the report says so in the footer.

## Data quality — confirmed versus suspected

The report distinguishes two states, and the distinction is the point of this section.

**Confirmed** — a human entry in `config/data-quality.json`. Excluded from the exceptions
block and from squad averages, kept in the ranked list greyed out, with the reason printed
in Data Notes.

**Suspected** — a heuristic flag from `verify`. Never auto-excluded. Marked in the ranked
list and named in Data Notes as unreviewed.

A missing config file excludes nothing, prints *"no data-quality review on file"*, and
still surfaces the unreviewed count. So the report cannot invent an exclusion on its own,
and it cannot quietly present unreviewed data as clean. Both failure modes are visible.

The counts in the data-quality line are scoped to the session, not the roster: `total` is
the number of athletes with data for *this* practice, and `usable` is that number minus the
confirmed exclusions applying to it. An athlete who did not train that day is absent from
both, and her absence is reported by the attendance note rather than counted as a data
problem.

`config/data-quality.json` is gitignored. `config/data-quality.example.json` is tracked
and shows the format, mirroring how `name-aliases.json` already works.

```json
{
  "exclusions": [
    {
      "athlete": "Preferred Name",
      "scope": "block",
      "practices": [],
      "reason": "sensor",
      "note": "23 jumps across the block against a 379 median for her group",
      "confirmed_by": "staff",
      "confirmed_on": "2026-08-02"
    }
  ]
}
```

`scope` is `block` or `session`; `practices` is required and non-empty when scope is
`session`. `reason` is one of `sensor`, `tagging`, `role`, `attendance`. An entry naming
an athlete who does not exist in the roster is a loud failure, not a silent no-op — the
same posture `verify` takes when the alias map stops joining.

## Readiness intersection

The block's effect on readiness is not measurable: there is no CMJ on or after 2 August.
What is available is *entry* readiness — each athlete's last Peak Power / BM before the
block — and its value in a daily report is entirely in the intersection with that day's
load, which does change from session to session.

An athlete is named when both hold:

- z ≥ +1.5 on today's load against her own block mean, and
- entry Peak Power / BM in the bottom quartile of this squad.

The quartile is of this squad, not a population norm, because no volleyball norm exists —
the same reasoning that keeps volleyball out of the football classification engine.
Bottom quartile of 16 is four athletes; below-median would be eight and the flag would go
stale within a week. The threshold is configurable.

Entry baselines older than 60 days are marked stale rather than used silently. Two
athletes were last tested 23 April, 98 days before the block. If the force plate store is
unreachable the whole section disappears and one line explains why, matching how
`forceplate.py` already degrades.

The caveat rides along every time the section renders: entry readiness is a pre-block
snapshot, not a response to today's session.

## Section order

1. Header — practice number, date, type, duration, athletes on sensors
2. Verdict line
3. Data-quality line
4. Worth a look — the exceptions
5. High load on low entry readiness — when any, and when the store is reachable
6. Tiles — squad jumps, jumps per minute, session length, per athlete — then mechanical
   load as a single line beneath them
7. Ranked bars — every athlete against her own normal, exclusions greyed
8. By position group
9. Jump-height band mix
10. Drill breakdown, or the note explaining why there isn't one
11. Data notes — exclusions with reasons, unreviewed flags, stale and short baselines
12. Footer — generated timestamp, block definition, the n caveat

## The standalone shell

```powershell
python -m kinexon.build_report                  # most recent practice
python -m kinexon.build_report --practice 6
python -m kinexon.build_report --all            # one file per practice
python -m kinexon.build_report --metric mechanical_load
```

Output is `dashboards/post-practice-P<N>.html`, self-contained, gitignored because it
carries athlete names in the page. It embeds a payload narrowed to one practice — that
session's values, the roster, each athlete's baseline, the practice's debrief structure,
and only the readiness rows the intersection needs. It carries a print stylesheet so
`html-to-pdf` produces a clean page rather than a screenshot of a web app.

Delivery stays manual — a file on the share drive. Whether it should be emailed on
session-end or read the next morning is §1, and that needs an answer from the coaching
staff before it is worth automating.

## Error handling

| Condition | Behaviour |
|---|---|
| `--practice` names a session that does not exist | Error listing the available practice numbers |
| Force plate store unreachable | Readiness section omitted, one line explains |
| `config/data-quality.json` absent | Nothing excluded, "no data-quality review on file", unreviewed count still shown |
| Exclusion names an unknown athlete | Loud failure |
| Athlete baseline n < 3 | Ineligible for exceptions, marked in the ranked list |
| No drill export for the practice | The existing note about drill-level export |
| No athlete has usable data | Report still generates and states it |

## Testing

`tests/test_debrief.py`, pytest, on synthetic fixtures. No real roster, no real names, no
real database — the privacy rule holds inside the test suite as firmly as everywhere else.
This is the repository's first test module.

Coverage:

- **Verdict** — a divergent session, a typical session hitting the |z| < 1.0 fallback, a
  two-session block suppressing ordinal language, and an assertion that no causal or
  prescriptive word appears in generated output.
- **Exceptions** — the boundary at exactly 1.5, both directions, an n=2 baseline held out,
  n printed alongside every average.
- **Data quality** — confirmed entries removed from exceptions and from squad averages;
  suspected entries retained but marked; missing config excluding nothing; an unknown
  athlete name failing loudly.
- **Readiness** — empty and non-empty intersections, stale baseline marking at the 60-day
  boundary, and the store being unavailable.
- **Polarity** — that above-normal on an exposure measure takes the risk pole, and that a
  *decline* in Peak Power / BM takes it too.

That last one exists because the inversion is easy to get backwards and getting it
backwards would quietly reverse the meaning of a chart. It gets a test rather than a
comment.

A smoke test builds a report for every practice in a synthetic database and asserts the
output parses as HTML and contains no unrendered template markers.

## Out of scope, deliberately

- **Acute:chronic workload ratio** — needs roughly 28 days of chronic load; this block is
  three. It becomes computable with no code change once four weeks are ingested.
- **The block's effect on readiness** — blocked on a post-block CMJ existing. That is a
  staffing ask, not an engineering task, and `docs/volleyball-jump-testing-ask.md` is the
  memo making it.
- **Drill detail for practices 2–6** — blocked on the export changing in KINEXON OS.
- **Email or scheduled delivery** — blocked on §1, which needs a coach's answer.

None of these are blocked on this design, and none of them block it.

# Portfolio Dashboard — Design Spec

**Date:** 2026-07-31
**Status:** Approved design, pre-implementation
**Owner:** Eric Rash
**Location:** `C:\Users\eric_rash\Desktop\DEV\project-triage\`

## Problem

Side-project ideas get captured on paper scraps and die there. Work front-burner
items (SPA presentation, NCAA best-practices doc, tech vetting framework, OKRs,
Ask the Library) live in meeting notes and lists that are hard to chip away at.
The existing project-triage dashboard solved the *data* problem (activity
heuristics over `~/Desktop/DEV`) but was generated exactly once (2026-05-22)
and never opened again — the failure is **surfacing**, not data. Out of sight,
out of mind.

## Decisions made (with Eric, 2026-07-31)

1. **Evolve project-triage**, don't build a new system — but the dashboard must
   become rich/immersive and pushed at Eric, not pulled by him.
2. **All four update paths** wanted: daily scheduled scan, session-end hook,
   quick slash command, proactive conversation capture. Hook deferred to
   Phase 2 (hooks are the historically fragile layer in this environment).
3. **Idea capture:** tell Claude anywhere ("new idea: …"); papers transcribed
   the same way.
4. **Surfacing — all four channels:** published Artifact URL (phone-openable),
   session-start pulse, Chrome new-tab page, morning-briefing lead.
5. **Priority model:** two lanes — `job` and `side` — each hand-ranked by Eric.
   Claude flags staleness but never reorders.
6. Note: no "Wayfinder" skill exists in this environment; `loop-designer` and
   `project-triage` are the closest installed analogs.

## Architecture

One source of truth, one render step, many funnels in, many surfaces out.

```
  /project skill ─┐
  conversation    ├─→ portfolio.json ─→ generator (render.py) ─→ dashboard.html (local)
  capture         │        ↑                    │                ├─→ Artifact URL (published)
  daily scan ─────┘   triage heuristics         └─→ pulse.md ────┴─→ session-start snapshot
  (Phase 2: hook,     (from triage.py)
   reMarkable sweep)
```

No two surfaces can disagree because every surface is a render of the same file.

### Component 1 — Registry: `portfolio.json`

Lives at `DEV\project-triage\portfolio.json`, git-tracked. Two collections:

```json
{
  "projects": [
    {
      "name": "SPA_Presentation",
      "lane": "job",                  // "job" | "side"
      "rank": 1,                      // hand-set order within lane
      "status": "active",             // active | paused | done | dropped
      "purpose": "one-liner",
      "next_action": "the single next concrete step",
      "dev_folder": "optional — folder name under DEV for activity heuristics",
      "links": ["optional paths/URLs"],
      "updates": [{"date": "2026-07-31", "note": "what moved"}],
      "curated_at": "ISO-8601"
    }
  ],
  "ideas": [
    {
      "captured_at": "ISO-8601",
      "pitch": "one-line pitch",
      "source": "conversation w/ Chris Ruf | reading X | paper scrap",
      "status": "inbox"               // inbox | promoted | parked | dropped
    }
  ]
}
```

**Day-one seed** (from 2026-07-31 conversation):
- Job lane: SPA presentation, NCAA best-practices document, tech vetting
  process/framework (all from 2026-07-30 Chris Ruf meeting), Applied
  Performance OKRs 2026-27, Ask the Library.
- Side lane: morning briefing, TSSHB → Claude Skills (Virgile/Lewis book,
  Adam's blessing confirmed), 15–16 week sport science curriculum
  (CPSS_BaylorSportScience_Curriculum folder exists).

### Component 2 — Generator: `render.py`

Python script (run with `C:\Python314\python.exe`, same as triage.py). Steps:

1. Load `portfolio.json`.
2. Import/reuse activity-heuristic logic from the existing
   `~\.claude\skills\project-triage\triage.py` for any project with a
   `dev_folder` — last-touch dates and momentum, no duplicate implementation.
3. Render `dashboard.html` — a single self-contained file (inline CSS/JS,
   works as an Artifact under strict CSP and as a local new-tab page):
   - **Front burner hero:** top 1–2 of each lane, big, with `next_action`
     front and center.
   - **Two lanes:** ranked cards with status, staleness flags
     (⚠ no touch ≥ 14 days), latest update line.
   - **Idea inbox:** inbox-status ideas with age; parked ideas collapsed.
   - **Momentum strip:** which projects moved in the last 7 days (from
     updates[] + heuristics).
   - Light/dark aware, phone-readable (it will be opened from the Artifact
     URL on mobile).
4. Write `pulse.md` (≤ 3 lines): today's #1 job item + #1 side item + any
   staleness warning. Consumed by the session-start snapshot.

Design of the HTML follows the `dataviz` / `artifact-design` skill guidance at
implementation time.

### Component 3 — `/project` skill (new skill: `project`)

Verbs, all of which end by re-running the generator and republishing:

- `/project idea <pitch>` — 10-second capture to `ideas[]`.
- `/project update <name> <note>` — append to `updates[]`, refresh
  `next_action` if given.
- `/project rank` — interactive re-rank of a lane.
- `/project promote <idea>` — idea → project (asks lane + next_action).
- `/project` (bare) — render + republish + show the pulse.

**Conversation capture:** the skill doc instructs Claude (via a memory/feedback
entry, not a hook) that when a conversation clearly spawns a project idea or
completes a milestone, offer once: "Want me to file that to your project
inbox?" — offers, never silently writes (capture-insight pattern).

### Component 4 — Surfacing

- **Published Artifact:** stable URL, republished on every render. The URL is
  recorded in `portfolio.json` (`meta.artifact_url`) so every session
  republishes to the same page.
- **Daily scan:** a scheduled routine (Claude scheduled agent, or riding the
  existing KeystoneOS Morning task) that re-runs the generator — picks up DEV
  activity drift daily and re-flags staleness — and republishes.
- **Session-start pulse:** `pulse.md` gets appended into the existing
  KeystoneOS unified snapshot hook output (one `Get-Content` added to the
  snapshot script) so every Claude session opens with the front burner.
- **Morning briefing:** the morning-briefing project's prompt gains one line:
  lead with `pulse.md` + dashboard URL.
- **Chrome new-tab:** Eric one-time setup — point new-tab/homepage at the
  local `dashboard.html` or the Artifact URL (documented in README, manual).

### Phase 2 (after ~1 week of real use, explicitly deferred)

- **Session-end hook:** Stop-hook that detects the project a session touched
  and proposes a registry update. Deferred: hook layer has a documented
  failure history here (`.errors.log`, memsearch flush patch stripping).
- **reMarkable sweep:** daily scan checks recent reMarkable notebooks for
  idea-scrap pages (remarkable MCP is connected) and proposes inbox entries.
- Anything the first week of use proves unnecessary gets cut, not built.

## Error handling

- Generator validates `portfolio.json` on load; on parse failure it refuses to
  render (never publishes a blank dashboard) and reports the error.
- Registry writes are read-modify-write with a `.bak` of the prior version.
- If Artifact publish fails, the local HTML still updates; publish retries on
  the next render.
- Missing `dev_folder` or heuristic errors degrade to "no activity data" on
  the card, never a render failure.

## Testing

- Unit: registry round-trip (load → mutate → save → reload), staleness math,
  seed-file validity.
- Golden render: generator run against a fixture registry produces HTML
  containing expected hero/lane/inbox markers.
- Manual acceptance: `/project idea` from a fresh session lands in the inbox
  and appears on the republished page; pulse shows in a new session's snapshot.

## Out of scope

- No task-level tracking (this is projects + next actions, not a todo app).
- No auto-reprioritization by Claude — ranks are Eric's.
- No live server / database — file + render only.
- Existing daily triage skill keeps working unchanged; `render.py` reuses its
  heuristics rather than replacing `triage.py`.

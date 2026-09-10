# Portfolio merge + Kanban board — design

**Date:** 2026-08-15
**Status:** approved — ready for implementation planning (revision 4)
**Repo:** `~/DEV/project-triage` (`erash11/project-triage`, branch `master`)

Revision 4 folds in what the prototype settled. Revision 3 replaced the dropdown
editor with a drag-and-drop board. Revision 2 replaced a merge design that could
not have been implemented. See [Corrections](#corrections).

## Validated by prototype

A throwaway prototype was built and driven by the user before this plan was
committed to — `prototype/board.html` on branch `worktree-portfolio-merge-editor`
(commits `1393a80`, `27b590f`). Three structurally different layouts were built
with the real registry inlined and no persistence.

**Layout A won: one lane at a time, stage columns across, a `job`/`side` tab.**
The alternatives were rejected — both lanes as stacked swimlanes (too wide to
scan) and a dense row list with a six-square stage dial (fast, but the drag
target was too small to feel right).

Two changes came out of driving it, and both are now part of the design:

1. **Status is a `<select>`, not a click-cycle chip.** Cycling forces a full
   loop back around when you overshoot, which is a mistake you make constantly
   on a four-value field.
2. **Text editing lives on the card.** Clicking a card expands it in place with
   purpose, next action, an add-update line, and the update history. The user
   asked whether this belonged on the board at all; driving it confirmed it did.

The prototype is a primary source and stays on that branch. It is not promoted
into `master` — it was written under prototype constraints, with no tests, no
error handling, and no persistence.

## Problem

Two registries describe the same portfolio and neither is complete.

| | `.curation.json` | `portfolio.json` |
|---|---|---|
| Created | 2026-08-15 (this session) | earlier, maintained via `/project` |
| Entries | 28 | 21 |
| Fields | `purpose`, `status_override`, `action`, `curated_at` | `name`, `lane`, `rank`, `status`, `stage`, `purpose`, `next_action`, `dev_folder`, `links`, `updates`, `curated_at` |
| Written by | `project-triage` skill | `portfolio.py` CLI |
| Rendered to | `YYYY-MM-DD.html` (daily triage) | `dashboard.html`, `pulse.md` |

Overlap is small: 13 projects in both, 8 only in `portfolio.json`, 15 only in
`.curation.json` — 36 distinct projects.

The 8 portfolio-only entries have no `~/DEV` folder (`OKRs_2026-27`,
`NCAA_BestPractices_Doc`, `SPA_Presentation`, `TSSHB_Skills`,
`CPSS_BaylorSportScience_Curriculum`, `Transformative_Athlete_Experience`,
`morning-briefing`, `project-triage`). A folder scan can never discover them,
so any merge that works by rescanning the filesystem silently drops them.

Separately, the user wants to manage the portfolio by dragging cards around a
board on their own machine, not by dictating changes to an agent.

## What `validate()` actually requires

Measured, not assumed. Every record in `projects` must carry:

| Field | Rule |
|---|---|
| `name` | non-empty string |
| `lane` | `job` or `side` — **required** |
| `rank` | int ≥ 1, **unique within a lane among `active` projects** |
| `status` | one of `active`, `paused`, `done`, `dropped` — there is no `inactive` |
| `purpose` | string — **required** |
| `next_action` | string — **required** |
| `stage` | optional, but if the key is present it must be one of `idea`, `grilled`, `spec`, `planned`, `building`, `shipped`. A present-but-`null` stage fails. |

This is why the 15 new projects cannot simply be appended: only 13 have a
status, only 9 have a purpose, and none has a lane, rank, or next_action.

## Decisions taken

1. **`portfolio.json` is the source of truth.**
2. **On status conflicts, today's answers win.** All 21 portfolio projects were
   marked `active`; that field had never been maintained.
3. **Local only.** A server on `127.0.0.1`, never exposed to the network.
4. **Unranked projects go to an inbox tier** rather than into `projects`.
5. **The board owns `rank`.** Priority is expressed by where a card sits, not
   by typing a number.

## Part 1 — Merge

### A. The 13 overlapping projects — updated in place

Join on `dev_folder` where present, else `name`, against `.curation.json` keys
(which are `~/DEV` folder names). Exact matching only; a wrong join silently
corrupts two records.

| Field | Rule |
|---|---|
| `status` | Curation wins where it expresses one: `resume` → `active`, `pause` → `paused`. Those are the only two override values present. Where curation has none, portfolio's stands. |
| `purpose` | Portfolio's is retained — longer, more context. Where curation's differs, it is appended to `updates` as a dated note, so neither phrasing is lost. |
| `stage`, `next_action`, `lane`, `rank`, `links`, `updates` | Portfolio only. Carried over untouched. |
| `curated_at` | Stamped on any record the merge modifies. |

Seven records change from `active` to `paused`: `DataBase_GPS_Reporting`,
`ForcePlate_DecisionSystem`, `PlayerProfiles_FB_03-28-2026`,
`Risk_Stratification_Engine`, `S2_Evaluation`, `Sport_Tech_Vetting`,
`Travel_Map`.

### B. The 15 new projects — a new `inbox` tier

A new top-level `inbox` list holding records identified but not yet placed:

```json
{
  "name": "Football",
  "dev_folder": "Football",
  "status": "active",
  "purpose": "Force plate reporting, player progress reporting, and then associated analytics projects.",
  "source": "curation-merge-2026-08-15"
}
```

Only fields the user actually supplied are written. `validate()` does not
police `inbox`, so partial records are legal there and illegal in `projects`.
That asymmetry is the point: the inbox is where a project waits until it has
enough information to be placed on a board.

### Verified

Run against a copy of the live registry:

- `validate()` accepts the added `inbox` key — **pass**
- `render.py --no-scan` exits 0 and reports `21 projects` — **pass**
- No inbox project renders as a card in `dashboard.html` — **pass**

### Constraints

- **The merge must read the working-copy `portfolio.json`, not `HEAD`.** There
  are 43 uncommitted lines including S2_Evaluation's move to `shipped` with its
  update history.
- `.curation.json` is preserved as `.curation.json.bak` and no longer written.
- A timestamped backup is written before the first write.

### Post-merge assertions

21 records in `projects` and 15 in `inbox`; all 8 portfolio-only names present;
S2_Evaluation still `shipped` with `updates` intact; the 7 conflicted projects
read `paused`; no `stage` key set to `null`; `validate()` raises nothing;
`render.py --no-scan` exits 0.

## Part 2 — The board

### Shape

`board.py`, stdlib only, no third-party JavaScript.

```
python3 board.py            # binds 127.0.0.1 on a free port, opens the browser
```

One HTML page, vanilla JS using native HTML5 drag events. No build step, no
CDN, no network access. Desktop only — native drag events do not work on touch,
and adding a touch shim is not worth it for a tool used at a desk.

### Layout

**One board per lane.** A `Job` / `Side` tab switches between them. This is not
cosmetic: `rank` is unique *per lane*, so a board scoped to one lane is what
makes drag-to-prioritise well defined.

Columns, left to right:

| Column | Holds |
|---|---|
| **Inbox** | `inbox` records — shared across both boards, since they have no lane yet |
| **Idea → Grilled → Spec → Planned → Building** | `projects` in that lane at that stage |
| **Shipped** | stage `shipped` |
| **Archive** (collapsed drawer) | status `done` or `dropped`, any stage |

Two different notions of "finished" exist in the data and both are kept:
`stage: shipped` means the work is delivered; `status: done`/`dropped` means the
project is off the books. Shipped stays a visible column; done and dropped move
into the Archive drawer, out of the way but recoverable.

### The card

Collapsed:

- Project name
- Status — a colour-coded `<select>` carrying `active` / `paused` / `done` /
  `dropped`. Not a cycle: overshooting a four-value cycle costs three more
  clicks to correct.
- A fill bar showing stage position: `idea` is 1/6, `shipped` is 6/6
- Purpose, truncated to two lines
- Rank and stage

Expanded — clicking the card opens it in place:

- **purpose** — multi-line, editable
- **next action** — single line, editable
- **add update** — one line; on Enter it prepends `{date, note}` to `updates`
- **update history** and links, read-only
- Required fields that are empty are outlined in red, so gaps are visible
  without opening every card
- **The card stops being draggable while open**, so text can be selected
  without the card flying across the board

### Drag semantics

| Gesture | Effect |
|---|---|
| Drag a card to another column | Sets `stage` |
| Drag a card up or down | Sets priority within the lane |
| Drag from Inbox onto a board | Promotion — the board supplies `lane`, the column supplies `stage`, the drop position supplies `rank` |
| Drag to Archive | Sets `status` to `done` |

**Rank is recomputed, never typed.** After any drop, every card in that lane is
renumbered 1..N by reading columns in ladder order, then top-to-bottom within
each column. This guarantees uniqueness and leaves no gaps, which is exactly
what `validate()` demands. The cost is that one drag rewrites several records;
the file is small and every write is atomic, so this is acceptable.

### Promotion

Dropping an inbox card onto a lane board supplies `lane`, `stage`, and `rank`
from geometry. `validate()` also requires `purpose` and `next_action` as
strings. Six of the fifteen inbox records have no purpose and none has a next
action.

So: if either is missing, the drop is accepted visually and the card opens
inline with those two fields focused and the rest of the board dimmed. Nothing
is written until both are filled. Cancelling returns the card to the Inbox. The
server never invents either value.

### Creating and deleting

- **New card** — a `+` at the head of each column. Name is required; the column
  and board supply stage and lane; purpose and next action are collected in the
  same inline form before the first write.
- **Delete** — on the card's expand panel, behind a confirm that names the
  project. Deleting writes a backup first, as every mutation does.

### API

| Route | Purpose |
|---|---|
| `GET /` | The board |
| `GET /api/registry` | Current registry as JSON |
| `POST /api/move` | `{name, lane, stage, position}` — the single endpoint every drag uses; recomputes ranks and returns the new lane ordering |
| `POST /api/project/<name>` | Patch `status`, `purpose`, `next_action`, or append a `note` |
| `POST /api/project` | Create |
| `DELETE /api/project/<name>` | Delete |
| `POST /api/inbox/<name>/promote` | Inbox → `projects`, requires the four fields |
| `DELETE /api/inbox/<name>` | Drop an inbox record |

A `note` is appended to `updates` as `{date, note}`; it never overwrites an
existing update. `curated_at` is stamped on write.

### Write safety

- Every write runs `validate()` first and is rejected with the validator's own
  message on failure.
- Writes are atomic: temp file in the same directory, then `os.replace`.
- A timestamped backup precedes the first mutation of each session.
- The server refuses to start if `portfolio.json` does not parse.
- **Single-level undo.** The pre-drop registry is held in memory and an Undo
  control restores it. Drag makes destructive mistakes easy and fast, which the
  dropdown design did not; this is the mitigation.

### Access control

Binding to `127.0.0.1` stops other machines, but any web page open in the
browser can POST to a localhost port. So a random token is generated per run and
embedded in the URL the browser opens; `/api/*` rejects requests without it, and
`Origin` is checked on writes.

That is not defence against a local attacker holding the token. It stops a stray
page in another tab from silently rewriting the registry.

### Failure behaviour

A rejected write snaps the card back to where it came from and surfaces the
server's message on the card. The board never shows a position that is not on
disk.

### Out of scope for v1

Touch and mobile, editing `links`, multi-select drag, keyboard reordering,
undo deeper than one step, and any write path back to `.curation.json`.

## Relationship to the `project-triage` skill

The skill keeps scanning `~/DEV` and producing the daily `YYYY-MM-DD.html`. Its
activity heuristics are unchanged. What changes is that it reads curated prose
from `portfolio.json`, and a scanned folder with no registry record is reported
as an inbox candidate rather than as "uncurated".

Heuristic status and curated status remain separate values that may disagree.
Recency and intent are different questions, and the disagreement is the signal
the daily report exists to surface.

## Risks

| Risk | Mitigation |
|---|---|
| Merge runs against `HEAD`, losing 43 uncommitted lines | Explicit working-copy read; assertion that S2_Evaluation's updates survive |
| Wrong join corrupts two records | Exact matching only; unmatched names go to the inbox |
| A stray drag silently reprioritises a lane | Single-level undo; every mutation backed up |
| Rank recompute rewrites many records per drag | Atomic write, `validate()` before write, small file |
| Promotion invents `purpose` / `next_action` | Write blocked until the user supplies both |
| Another tab rewrites the registry | Per-run token plus `Origin` check |
| Inbox becomes a junk drawer | It is the leftmost column on every board, and records can be deleted outright |

## Corrections

**Revision 3 → 4.** The prototype replaced two guesses with answers: layout A
over the swimlane and dense-list alternatives, and a status dropdown over the
click-cycle chip. Card-level text editing was promoted from a sub-clause of the
expand control to a named part of the design, because it is where the user will
spend most of their time — 14 of the 15 inbox records are missing a purpose, a
next action, or both.

**Revision 2 → 3.** The dropdown editor was replaced by a board. The dropdown
design also left `rank` unsolved — it was read-only, so the 15 inbox records had
no way to acquire one. Drag-to-position solves it: rank stops being a number the
user types and becomes a consequence of where the card sits.

**Revision 1 → 2.** Revision 1 was checked against `portfolio.py` and failed:

1. It used `status: "inactive"`, which is not a valid status.
2. It set `stage: null` on new records; a present-but-null stage fails.
3. It omitted `lane` and never mentioned `rank` or `next_action`, all three of
   which `validate()` requires. This is what forced the inbox tier.

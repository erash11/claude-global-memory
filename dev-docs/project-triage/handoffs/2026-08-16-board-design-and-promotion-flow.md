# Handoff — board design system + promotion flow

**Date:** 2026-08-16
**Repo:** `~/DEV/project-triage` — `master`, pushed, working tree clean
**Tests:** 184 passing (`python3 -m unittest discover -s tests -t .`)
**Commits:** `e143747`, `025a03d`, `c586b60`, `9d47e7c`, `b14674e`, `809b5ed`, `9778c34`

## What this session was

Started as "where is my Kanban board?" and became five rounds of design and
behaviour work on `board.html` — the local drag-and-drop board over
`portfolio.json`, served by `board.py`. Every round was driven by Eric noticing
something while using it.

## Decisions, and the reasoning that would otherwise be lost

**1. The board joined the Front Burner design system; it was never on it.**
`DESIGN.md` describes a stadium-scorebug world (Baylor green, gold, Oswald) that
`dashboard.html` renders. `board.html` was generic dark-SaaS with a periwinkle
accent — the design detector scored 21 of 22 findings as "outside DESIGN.md",
plus a flat-type-hierarchy warning. Two surfaces over one registry looked like
two products. Now 11 findings, all advisory (shadow alphas and alarm-red tints
the dashboard uses identically), hierarchy warning cleared.

Green is **one continuous field under all columns**, not eight saturated blocks —
that holds DESIGN.md's 30–60% green commitment while the black cards stay the
things you read. The gold left bar goes **only on the #1 card in a lane**; on
every card it is wallpaper and gold stops meaning "this is the one".

**2. Card titles broke mid-syllable because names are one unbroken word.**
`AT_Utilization_B / enchmarks`. Two fixes: `<wbr>` at each underscore (built as
DOM nodes, never `innerHTML` — names stay untrusted text), and the status pill
moved off the name row down to the stage row, which had width to spare. Measured
in Chrome: title width **106px → 181px**; most names now set on one line.

**3. The oversized purpose box was invalid CSS, not a sizing choice.**
`font:12px/1.4 inherit` — a CSS-wide keyword cannot sit inside a shorthand, so
the whole declaration was dropped and the box fell back to the UA default:
13.3px monospace with `resize:both`, whose handle dragged it outside its column.
Verified empirically in Chrome that the old declaration parses to an empty
string. Split into longhands; `resize:vertical`.

**4. Archive became a drop target; inbox ideas can be retired outright.**
Archive was previously reachable only via the status dropdown, and an inbox idea
that went nowhere had no exit at all (`promote` required fields, and the inbox
has no delete button). New `archive_inbox` op. Board card → Archive marks
`dropped`; `done` stays a deliberate dropdown choice. It deliberately avoids
`promote` (requires fields) and `reorder` (raises on archived), setting `rank`
directly — `live()` filters archived out, so lane ranking is untouched.

**5. A lane switch, because the board could not move a project across lanes.**
The board renders one lane and drops into the lane it is showing, so a
mislabeled project was unreachable — and no CLI path existed either
(`add-idea` / `add-update` / `set-stage` only). `reorder` already supported the
move; only the UI could not reach it. `set_lane` delegates to `reorder` for the
ordinary case (renumbers both lanes) and moves archived/unstaged projects by
hand, without inventing a stage. It **stamps `curated_at`** unlike a bare
`reorder`: this module's rule is drag = re-prioritisation (no stamp), edit =
curation (stamp), and fixing a lane is a correction. The tab follows the card.

**6. Un-archiving an inbox retiree returns it to the Inbox.**
Records archived from the inbox carry `archived_from_inbox`. Guarded: if an
inbox record under that name was recreated meanwhile, it stays a project rather
than creating two records with one name. This closed a hole knowingly accepted
in `e143747`.

**7. The promotion gate was removed, not softened.**
It required purpose + next action, blocking the drag the board exists for — and
it never held: both fields could be cleared immediately after and `validate`
still passed. It *was* guarding something real (the dashboard renders the next
action as its 27px hero line; blank meant a blank headline). So the gate went
and the gap is surfaced instead: `_needs_action` is **one predicate read by both
surfaces** so board and dashboard cannot disagree — active status, whitespace
counts as blank, paused and archived never flagged. The dashboard empty state
renders **in** the next-action slot rather than collapsing it (keeps the hero
geometry) and drops the gold arrow, since gold means progress.

`render_pulse` says it in plain words with **no ⚠** — that glyph already means
"stale" in pulse vocabulary and the snapshot/briefing wiring parses that line.

**8. Every promotion lands `active`.** It used to inherit the inbox record's
status; 8 of 14 inbox records are `paused`, so drags landed paused *and*
unflagged (the flag is active-only) — the exact case the flag exists to catch.

## Files created or modified

All under `~/DEV/project-triage/`:

- `board.html` — full restyle onto DESIGN.md tokens; `<wbr>` names; pill on the
  stage row; lane switch; needs-a-next-action flag; archive drop target
- `board.py` — `/oswald.woff2` route (module-relative `FONT_PATH`, unauth —
  a CSS `url()` cannot carry the token); `/api/project/<n>/lane`;
  `/api/inbox/<n>/archive`
- `board_ops.py` — `set_lane`, `archive_inbox`, `_restore_to_inbox`; `promote`
  de-gated and always active; `patch_project` restore branch
- `render.py` — `NEEDS_ACTION`, `_needs_action`, `_next_action_html`; empty
  state in hero / mini-card / lane row; `render_pulse` wording; `.missing` CSS
- `README.md` — Board section rewritten for all of the above
- `tests/test_board_ops.py`, `tests/test_board_server.py`, `tests/test_render.py`
- `docs/handoffs/2026-08-16-board-design-and-promotion-flow.md` — this file

## Registry writes from outside this session

`portfolio.json` was modified twice today by something other than this session
(proven: the board's writes went to a sandbox copy under
`~/.claude/jobs/*/tmp/boardcheck/`, which has its own `.bak`). Both recorded as
separate data commits so registry history stays readable:

- **09:03** — ranks only, both lanes (`9d47e7c`)
- **09:56** — `CFB_Victory_Model` promoted to the side lane (`809b5ed`)

Keep this split. Do not fold registry changes into code commits.

## Next actions

1. **Nothing is blocking.** The board is shippable and in daily use.
2. Consider whether the `/project` skill (`~/.claude/skills/project/SKILL.md`,
   outside this repo) should stop asking for a next action on promote, now that
   the board does not. Left alone deliberately — different surface, its call.
3. `CFB_Victory_Model` currently has `next_action: "idea"`, which reads oddly on
   the dashboard as `→ idea`. Probably wants a real verb phrase.
4. A restored inbox idea lands at the **bottom** of the Inbox, not its original
   position. The Inbox has no sort order, so there is nowhere else to put it.
   Only worth fixing if it starts to annoy.
5. `dashboard.html` and `pulse.md` are gitignored build outputs and were last
   rendered 2026-08-15 13:47 — they will pick up the new empty state on the next
   `render.py` run.

## Mid-flight

Nothing. Working tree clean, all tests green, `master` in sync with `origin`.

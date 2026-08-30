# 2026-08-29 — Fireflies intake, rename-path repair, meetings knowledge graph

## What this session did

Three things, in order:

1. Ingested 8 new Fireflies meetings (2026-08-15 → 2026-08-27) into the SecondBrain vault
   and renamed the 7 that had date-only titles.
2. Diagnosed and worked around a broken Fireflies rename path, then made the fix permanent
   in the `name-meetings` skill.
3. Rebuilt the meetings knowledge graph from scratch (all 263 notes) and upgraded graphify.

## The core finding — read this before renaming any Fireflies meeting

**Both obvious rename paths are broken, and one of them lies about it.**

- `fireflies-pp-cli transcripts update` sends `updateMeetingTitle(id:…, title:…)`.
  The schema wants `updateMeetingTitle(input: {id:…, title:…})`. Every call is an HTTP 400.
  The field name really is `id` — do not "fix" this by renaming it to `meetingId`. The
  *shape* is wrong.
- The Fireflies MCP tool `fireflies_update_meeting_title` returns `{"success": true}` and
  then does not reliably write. In this session 2 of 7 renames landed promptly, 5 had not
  landed after 8 minutes of polling, and one diagnostic write surfaced ~20–30 minutes later.
  **Writes are erratically delayed, not dropped** — a rename you believe failed can land an
  hour later and clobber a good title.

This burned ~45 minutes because `name-meetings/REFERENCE.md` documents a "hard daily rate
limit", and the symptom (writes accepted, nothing persisting) looked exactly like one. It
was not. A real rate limit surfaces as an explicit `429`.

**What broke it:** the CLI bug was patched locally on 2026-07-22 (upstream PR
mvanhorn/printing-press-library#1571, never merged). The binary was rebuilt 2026-08-05,
which wiped the patch. Expect this to recur on every reinstall until that PR merges. There
is no Fireflies manuscript on this machine (`~/printing-press/manuscripts` holds only
catapult and zotero), so the CLI cannot currently be regenerated.

**The fix that works:** `~/.claude/skills/name-meetings/scripts/rename.py` — calls GraphQL
directly with the keychain API key and verifies every write by reading the title back, so it
cannot report a silent failure as success. It does not depend on the CLI build, so a
reinstall cannot regress it.

## Second trap — the list endpoint lags

Fireflies' **list** endpoint (what `sync` and `transcripts find` read) trails the
**single-transcript** endpoint by minutes. Right after a rename it is normal for `find` to
still show the old title while the rename is genuinely applied.

Do **not** re-issue the rename — that is how a good title gets clobbered. Wait ~4 minutes,
re-run `sync --full`, verify, and only then export. `meeting-sync` builds vault filenames
from the synced title, so exporting too early bakes the stale title into the filename, and a
later re-export creates a *second* file rather than fixing the first.

## Files created or modified

**New vault notes** (all in `/Users/kristinarash/SecondBrain/Inbox/meetings/`):
- `2026-08-15_Football__Hydration__Weight_Flag_Automation.md`
- `2026-08-17_Volleyball_PracticePlanning.md`
- `2026-08-19_Applied_Performance__Fall_Ops__Tech_Inventory.md`
- `2026-08-22_Football__Practice_Intensity__Game_Week_Prep.md`
- `2026-08-24_Athletics_All_Staff__Personnel__Software_Inventory.md`
- `2026-08-24_WHOOP_Webinar__HRV_CV__Acute_Stress_Response.md`
- `2026-08-26_Athletics_All_Staff__One_of_One_Vision__Culture.md`
- `2026-08-27_Applied_Performance__Job_Profiles_FMS__Logistics.md`

**Skill changes** (⚠️ `~/.claude/skills/` is gitignored — these are NOT under version control):
- `~/.claude/skills/name-meetings/scripts/rename.py` — NEW, the working rename path
- `~/.claude/skills/name-meetings/SKILL.md` — points at rename.py, bans CLI + MCP, adds the
  list-endpoint lag warning
- `~/.claude/skills/name-meetings/REFERENCE.md` — new "Why renames bypass the CLI and MCP"
  section; rate-limit section de-emphasised; resume mode uses `rename.py --pending`;
  transient/permanent table corrected
- `~/.claude/skills/graphify/` — upgraded 0.3.27 → 0.9.51, plus a new `.venv/`
- `~/.agents/skills/graphify/` — upgraded 0.3.27 → 0.9.51

**Graph outputs** (`/Users/kristinarash/SecondBrain/Inbox/meetings/graphify-out/`):
`graph.html`, `graph.json`, `GRAPH_REPORT.md`, `manifest.json`, `cost.json`, `memory/`

**Old graph backup:** `/Users/kristinarash/SecondBrain/Inbox/graphify-out.bak-meetings-20260829/`
(1.1 MB, untracked, safe to delete)

**Memory files:**
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_fireflies-cli-broken-on-mac.md` — new rename section appended
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_graphify-runtime-setup.md` — NEW

## graphify notes

- The package is **not** installed globally. SKILL.md's `pip install graphifyy` fails under
  PEP 668. It lives in `~/.claude/skills/graphify/.venv/bin/python` — run every
  `scripts/*.py` step with that interpreter.
- `graphify install` updates **one platform at a time**. Running it plain left
  `~/.agents/skills/graphify` stale at 0.3.27, and the version warning kept firing from
  there. Update both: `--platform claude` and `--platform agents`.
- `--update` was not incremental: the June manifest held a Windows path
  (`graphify-out\GRAPH_REPORT.md`), so all 264 files read as new. After a path migration,
  plan a full rebuild.
- Move the old `graphify-out` **outside** the corpus before re-detecting. Left as a sibling
  backup inside the folder, it inflated the corpus from 265 to 327 files.
- A session rate limit killed 3 of 12 extraction agents and truncated one chunk's JSON mid
  write. Do not re-run blindly — `raw_decode` each complete object out of the `nodes`/`edges`
  arrays and drop the partial tail. That recovered all 22 files of the dead chunk intact.

Final graph: 3,725 nodes · 5,225 edges · 300 communities · 263/263 files.
87% EXTRACTED · 12% INFERRED (avg 0.76) · 1% AMBIGUOUS.

## Next actions, most important first

1. **memsearch is timing out and it is probably this session's fault.**
   `~/.claude/global-memory/transcripts/.errors.log` shows `memsearch-sync: index ETIMEDOUT`
   11× consecutively from ~15:00 local. `~/SecondBrain/Inbox/meetings` is a memsearch-indexed
   path (`~/DEV/KeystoneOS/data/memory-index-paths.json`), and `graphify-out/` inside it grew
   from ~0.8 MB to **9.9 MB** (3.4 MB `graph.json` + 3 MB `graph.html`). Either exclude
   `graphify-out/` from indexing or move the graph outside the indexed path. **Not done — this
   changes memory-system config and was left for a decision.**
2. Decide whether `~/.claude/skills/` should be version-controlled. The `.gitignore` there is
   `/*` with selective un-ignores, so today's `name-meetings` work exists only on disk. A disk
   loss or a skill reinstall would silently revert the rename fix.
3. Push SecondBrain — it is 2 commits ahead of origin (1 pre-existing + today's). Not pushed;
   only KeystoneOS is push-authorized.
4. Optional: delete `~/SecondBrain/Inbox/graphify-out.bak-meetings-20260829/`.
5. Optional: `share` and `delete` in `fireflies-pp-cli` were never tested. They may carry the
   same GraphQL shape bug. They send real outward-facing actions, so they were not probed.

## Open questions

- Should the Fireflies manuscript be rebuilt in Printing Press so the CLI can be regenerated?
  Deferred — only 1 of ~40 commands is confirmed broken and `rename.py` covers it.
- Does upstream PR #1571 have a path to merging? If not, every CLI reinstall re-breaks
  `transcripts update`.

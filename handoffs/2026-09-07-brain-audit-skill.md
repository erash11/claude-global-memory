# Handoff — `brain-audit` skill shipped

**Date:** 2026-09-07 (late) · **Status: COMPLETE, run once. Baseline 67/100.**

Written during `/closeout`, because this skill was built late in the evening and appeared in
no handoff, no memory file and no commit. Committed to `~/.claude/skills` so it cannot be
lost. (It was still `measure.sh`-only when the closeout sweep started; `SKILL.md` landed
minutes later, so an earlier draft of this file described it as unfinished. It is not.)

## What it does

Scores the second brain **as a system**, stores the score, proposes exactly two next
builds, then stops.

Its stated reason for existing is a real finding, and still true at the time of writing:
**`~/SecondBrain/audits/` has held exactly one report — `os-audit-2026-07-24-secondbrain.md` —
for 45 days.** The skill exists to make the score a *trend* rather than a one-off.

**Step 1** runs `measure.sh` (~7 s, facts only). Its contract: *never estimate a number this
script reports; a `MISSING` or `none` value is a finding, not an error to work around.*

**Step 2** scores four C's at 25 points each, every score anchored to a measured number so
runs a month apart are comparable:

| C | Measures |
|---|---|
| **Context** | Evergreen facts on disk — `USER.md`/`MEMORY.md` under cap, 35+ Tier A memories, `Knowledge/` freshness |
| **Connections** | Live data arriving — meeting sync, portfolio JSON, ledger |
| **Capabilities** | Skills that actually get *used*, not merely installed |
| **Cadence** | What keeps it alive — launchd jobs green **and** `Notes/` fresh |

Cadence is deliberately scored hardest on `Notes/`, not on the jobs: *"Every job being
green while synthesis is frozen is the exact failure this system keeps repeating."*

**Step 3** runs three narrative tests (teammate / context-switch / head-emptying) that
shape the write-up but do **not** move the number.

**Step 4** writes `~/SecondBrain/audits/brain-audit-YYYY-MM-DD.md` and appends to a trend
table.

## Boundaries, already settled in the frontmatter

- **NOT** automation plumbing — launchd, venvs, backup freshness → `claude-stack-doctor`.
- **NOT** note-level rot — stale seeds, duplicates, conflicting claims → `improve-system`.

That second line resolves the overlap question worth asking about any new vault auditor.

## First run — baseline 67/100

Ran the same evening. `~/SecondBrain/audits/brain-audit-2026-09-07.md`, with the row
appended to `~/SecondBrain/audits/_trend.md`.

| C | Score | The finding |
|---|---:|---|
| Context | 17 / 25 | Tier A strong (40 memories), `Knowledge/` 2d fresh. But **`MEMORY.md` at 100% of cap** and **0 grill sessions** — the biggest evergreen decisions are still only in Eric's head. |
| Connections | 22 / 25 | All three live sources in window; ledger at 27d is nearly out of its 30d window. |
| Capabilities | 15 / 25 | 161 skills installed. The July audit's one finding did ship, but **no audit→build loop existed until today**, so most findings were never converted into anything. |
| Cadence | 13 / 25 | All 9 launchd jobs `exit=0`, and `Notes/` **35 days stale**. Green jobs, frozen synthesis — the exact failure the rubric is weighted to catch. |

**The headline is the gap between capture and synthesis.** `Inbox/` 288 files, 0 days
stale. `Notes/` 23 files, 35 days stale. Material arrives and is not processed.

The report also records a deliberate rubric interpretation worth honouring on the next
run: Context scored **17 rather than the flat 13** the "one file over cap" anchor implies,
because `MEMORY.md` was over by two characters rather than meaningfully bloated, and the
17 reflects the grill gap instead. Hold that reading so the column keeps meaning one thing.

## Next actions

1. **Act on the two builds the report proposes**, so the next run has movement to measure.
   Capabilities explicitly scores "audit-driven builds shipped since last run" — the skill
   grades whether its own advice was taken, and a second flat score means the loop failed.
2. **Close the synthesis gap.** `Notes/` at 35 days and 0 grill sessions are the two
   findings that most move the score, and both are habit rather than tooling.
3. **The report is `status: raw`** — process it like any other inbox item.
4. Probable origin, unconfirmed: `SecondBrain/Inbox/2026-09-07-aios-video-gap-analysis.md`
   (same evening, `status: raw`) is a gap analysis of the vault against the AIOS approach.
   This skill is very likely the tooling response to it. Inferred from timing and subject,
   not stated anywhere — worth confirming before building further on the assumption.

## Files

| Path | State |
|---|---|
| `~/.claude/skills/brain-audit/SKILL.md` | Complete |
| `~/.claude/skills/brain-audit/measure.sh` | Complete, runs clean (exit 0) |
| `~/SecondBrain/audits/brain-audit-2026-09-07.md` | First real report, 67/100, `status: raw` |
| `~/SecondBrain/audits/_trend.md` | Trend table, one row. Append, never rewrite. |
| `~/SecondBrain/Inbox/2026-09-07-aios-video-gap-analysis.md` | Committed, `status: raw` |

---

## Addendum — written by the session that built it (closeout, same evening)

The handoff above was auto-generated mid-build. Everything in it is correct. This
section closes its open question and records what it could not see.

**Origin — confirmed, not inferred.** `Inbox/2026-09-07-aios-video-gap-analysis.md`
is exactly the source. Eric asked to mine a video (Nate Herk, "I Turned GPT-6 Astra
Into the Ultimate AI Second Brain", https://www.youtube.com/watch?v=yysILVsfLFM) for
second-brain improvements, then said "create it" about the top recommendation. The
gap analysis named four missing things; this skill is the first. The other three are
still unbuilt: a level-up step (now folded into the skill as Step 5), a topic-driven
grill, and the three-test rubric (also folded in, as Step 3).

**The two proposed builds, named.** The handoff says to act on them but not what they
are:
1. `/grill-me <topic>` writing to `~/SecondBrain/Inbox/grills/`. Chosen because
   `interview-me` is day-driven and `mattpocock-skills:grilling` writes nothing to
   disk (28 lines, no output step) — and because `user_working-conditions-bottleneck.md`
   says the limiting factor is the absence of a thinking partner and the right move is
   helping him capture what surfaces. First topics: the ATH Tech ITS
   blocker, the overdue OKR Q1 gate.
2. Put `/brain-audit` on `com.keystone.rituals`, monthly.

**Naming — do not "fix" this.** The skill is `brain-audit`, kebab-case. The vendored
LifeOS `CreateSkill` skill mandates TitleCase, but every skill Eric wrote himself
(`closeout`, `improve-system`, `claude-stack-doctor`, `interview-me`) is kebab-case,
and `/brain-audit` is what he types. Renaming it to `BrainAudit` would break his
trigger.

**Two bugs found and fixed while testing `measure.sh`:**
1. BSD `date -j -f '%Y-%m-%d'` fills unspecified time fields from the clock at call
   time, so the same date reported 34 days on one line and 35 on the next. Both
   timestamps are now pinned to `12:00:00`. The gotcha is recorded in `SKILL.md`.
2. `find -exec stat {} \;` spawned one process per file and pushed a run past the
   120s timeout. Changed to `{} +`. A full run is now ~7 seconds.

**One metric was designed and then dropped:** a count of configured MCP servers.
`~/.claude.json` holds only 1; claude.ai connectors and plugin MCPs live elsewhere, so
the number read as misleadingly low. Connections are scored on data *freshness*
instead — a configured-but-silent connector should score zero anyway. The reasoning is
left as a comment in `measure.sh` so it is not re-attempted.

**Also created or modified, not in the table above:**
- `~/.claude/skills/_shared/config.json` — added `vault_audits`, `vault_audit_trend`
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_brain-audit-loop.md` (new)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/MEMORY.md` — index line
- `~/.claude/LIFEOS/MEMORY/SKILLS/execution.jsonl` — CreateSkill log entry

**Blocker worth surfacing:** global `~/.claude/global-memory/MEMORY.md` is at
2496/2500 characters. Nothing new can be written to working memory until it is
trimmed. This is why this session's thread was written to Tier A instead. Run
`/claude-stack-doctor`.

Correction 2026-09-25: there was no Kitman vs Myelin decision, then or ever. The
vendor is Myelin, a startup AMS Baylor is not pursuing; Kitman stays.

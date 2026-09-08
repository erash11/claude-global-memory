# Handoff — `brain-audit` skill shipped

**Date:** 2026-09-07 (late) · **Status: COMPLETE and verified running — never actually run for real**

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

## Verified this session

`bash ~/.claude/skills/brain-audit/measure.sh` → **exit 0**, real numbers, no `MISSING`.
Sample of what it currently reports about the vault:

```
Notes:      23 | 2026-08-03 | 35 days stale
Knowledge: 421 | 2026-09-05 |  2 days stale
Inbox:     288 | 2026-09-07 |  0 days stale
last_interview: 2026-08-03 | 35     grill_sessions: 0
```

**Those numbers are a preview of the first real score, and they are not flattering.**
`Notes/` at 35 days stale is squarely in Cadence's middle band, and by the skill's own
argument that is the failure mode that matters most. Capture (`Inbox` 288, 0 days) is
racing ahead of synthesis (`Notes` 23, 35 days).

## Next actions

1. **Run `/brain-audit` for real.** It has never produced a report. The measurement half is
   proven; the scoring half has never been exercised end to end.
2. Expect a mediocre Cadence score and let it stand — the point is the baseline, not a
   good first number.
3. Act on the two builds it proposes, so the *next* run has something to measure movement
   against. Capabilities scores "audit-driven builds shipped since last run", so the skill
   grades whether its own advice was taken.
4. Probable origin, unconfirmed: `SecondBrain/Inbox/2026-09-07-aios-video-gap-analysis.md`
   (same evening, `status: raw`) is a gap analysis of the vault against the AIOS approach.
   This skill is very likely the tooling response to it. Inferred from timing and subject,
   not stated anywhere — worth confirming before building further on the assumption.

## Files

| Path | State |
|---|---|
| `~/.claude/skills/brain-audit/SKILL.md` | Complete |
| `~/.claude/skills/brain-audit/measure.sh` | Complete, runs clean (exit 0) |
| `~/SecondBrain/audits/` | Still one report, dated 2026-07-24 |
| `~/SecondBrain/Inbox/2026-09-07-aios-video-gap-analysis.md` | Committed, `status: raw` |

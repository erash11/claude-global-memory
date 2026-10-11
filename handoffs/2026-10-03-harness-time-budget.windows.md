# 2026-10-03 (Mac) — Harness time budget + first fix pass

## What and why
Eric asked how much time goes to harness/system upkeep versus real work. A 60-day
measurement (git commits per repo + Claude session logs) estimated ~55% system / 45% real
work (commits alone: ~65/35). He adopted a budget to flip it.

## Decisions
- System work only in a weekly **Friday 1:00–2:00 PM Central "Harness slot"** (Google
  Calendar, recurring from 2026-10-09). Outside it, add a line to `~/.claude/HARNESS_FIXES.md`
  and fix only what blocks real work today. A new tool/hook/skill must replace an old one.
- Ratio recheck: Google Calendar event 2026-11-02 19:00 Central; the method and baseline are
  in the event notes. Goal: real work above 50%.
- Rules saved as Tier A memory `feedback_harness-time-budget.md` (Mac slug only; this
  handoff and `HARNESS_FIXES.md` are the cross-machine record).
- Backup items 6–8 deliberately held until tonight's 21:00 `daily-backup` run is checked, so
  that run tests only the two earlier fixes.

## Fix pass results (Saturday, counted as this week's slot)
- #5 `CommandCentre/server.out` untracked + gitignored (CommandCentre commit, pushed).
- #4 dcg `$CLAUDE_JOB_DIR` redirect: won't fix. dcg 0.11.0 allows no exemption for
  `redirect-truncate-dynamic-path`. Absolute literal paths pass.
- #1 duplicate dcg hook: cause found (`dcg doctor` → `dcg install` re-adds the Mac-only
  absolute entry; a later settings commit sweeps it in, as in e72c374). Auto mode blocks
  Claude from editing settings.json, so the restore is Eric's. It also reappeared seconds
  after a manual removal at 11:04, cause unknown.
- #3 memsearch "Indexed 0 chunks": a helper agent was still investigating at closeout. Its
  edits, if any, are uncommitted in `~/.claude` (or nested repos). Review them before
  committing.

## Files created or modified
- `~/.claude/HARNESS_FIXES.md` (new), `~/.claude/.gitignore` (allow-list line)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/feedback_harness-time-budget.md` (new),
  `.../memory/MEMORY.md` (index line), `.../memory/project_dcg-guard-blocks.md` (dcg 0.11.0 update)
- `~/DEV/CommandCentre/.gitignore`
- `~/.claude/docs/STATUS.md`
- Google Calendar: "Rerun harness vs. real-work ratio check" (2026-11-02), "Harness slot"
  (weekly Fridays)

## Next
1. Eric: close all Claude sessions, run `git -C ~/.claude restore settings.json`, open one
   session, run `git -C ~/.claude diff --stat settings.json`. Never run `dcg install`.
2. Check tonight's 21:00 `daily-backup` result, then do items 6–8 in a Friday slot.
3. Review the memsearch agent's changes (item 3) in `git -C ~/.claude status`.

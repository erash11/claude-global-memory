# Handoff: /doctor config check (Mac, 2026-10-10)

## What was worked on
Ran `/doctor` on the Mac: install health, usage, hooks, updates, permissions.

## Decisions and reasons
- Startup hook timeouts: 17 timeouts at 5 s across 230 starts. Raised `timeout` 5 → 15 s on
  `superpowers-quiet.mjs` and `keystone-unified-snapshot.js`. Both run in about 0.1 s by hand, so
  the real cause is unknown (likely load at session start, possibly cloud sync).
  Backup: `~/.claude/settings-backup-r1mu_1t3.json`.
- Background auto-updates: `autoUpdates` false → true in `~/.claude.json`.
  Backup: `~/.claude/claude-json-backup-teppjgm3.json`. Version was already current (2.1.296).
- TypeSafe plugin: kept (zero uses in 2 days; user chose to leave it).
- Auto mode: already the default. No permission change.
- No allow rules added: the 38 denials were compound shell commands and writes, none safe to allow.

## Files changed this session
- `~/.claude/settings.json` (committed in dotclaude: `520a2c3`)
- `~/.claude.json` (not in a repo)
- `~/.claude/global-memory/transcripts/2026-10-10.md` (committed in global-memory)
- `~/DEV/project-triage/portfolio.json` (committed alone: "data: board edits 2026-10-10")
- `~/.claude/docs/STATUS.md`, `~/DEV/project-triage/docs/STATUS.md` (updated)
- This handoff

## Next actions, most important first
1. Eric: decide the duplicate dcg hook. Committed `settings.json` has two dcg entries.
   `stash@{0}` holds the removal from 2026-10-05.
2. Check startup hook timeouts again around 2026-10-17.
3. Re-run `/doctor` around 2026-10-17 to judge the 24 skills with no usage record.
4. Delete the two backup files once the changes are confirmed.

## Still open (from closeout)
- dotclaude: 55 session-transcript files under `projects/` show as changed or untracked. Not
  committed. Decide whether transcripts belong in git at all, since they can hold private content.
- `~/.claude/global-memory/transcripts/.errors.log`: 7 old entries (compiler backlog, compiler
  budget, claude-files-digest send failures, memsearch index, gps-pull API 4, daily-backup
  repo-behind and repo-diverged). Clear it once each cause is handled.
- Registry drift: 14 items from `portfolio.py crosswalk`. None new this session.
- 7-day rule: NCAA_BestPractices_Doc (1 day left), HPI_Protocol and Education_Curriculum (2 days left).
- ZoteroInjestion is on a detached HEAD. Its commits are already on origin/main.

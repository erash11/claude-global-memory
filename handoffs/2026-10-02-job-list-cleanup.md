# 2026-10-02 — Background job list cleanup (Mac)

## What
Removed 61 completed background sessions from `~/.claude/jobs/` with `claude rm <id>` (Eric approved).
`~/.claude/jobs/` went from 715 MB to 9.3 MB. Repos, memory, transcripts and handoffs were not touched —
`claude rm` deletes only the job record and its `tmp/` scratch folder.

## AIOS sessions removed too
Eric dropped AIOS Task 8 (Pi trial) and approved removing `c59d1788` and `9823c1f0`.
Checked first: Gate C findings fixed on KeystoneOS `main` (`77d9ecc`, `dae7aeb`); monthly
`com.keystone.aiosaudit` ran clean 2026-10-01. Recorded in `~/DEV/KeystoneOS/decisions/log.md`
and `docs/STATUS.md`. `~/.claude/jobs/` is now 64 KB.

## Gotchas
- The auto-mode classifier blocks `claude rm` unless the user approves in chat.
- The AIOS plan's Gate A re-run command points at the removed job scratch; it no longer works.

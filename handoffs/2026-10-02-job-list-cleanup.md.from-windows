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

## Perch-pull fix (same session)
- Cause of the 10/1 `perch-pull` failure: Perch read timeouts (30 s). 20 whole-pull restarts and
  3 failed runs (9/26, 9/27, 10/1) since 9/26. Data never lost; later runs caught up.
- Fix: `_perch_request()` in `~/DEV/PlayerProfiles_FB_03-28-2026/src/perch_ingest.py` retries each
  request (60 s read timeout, 4 tries, 5/15/45 s waits; 4xx not retried). Tests in
  `tests/test_perch.py`, 45/45 pass. Live pull 9/30-10/2 OK (769 rows). Commit `f20a062`, pushed.
- Next: nothing. Check `logs/launchd-perchpull.log` after the 10/3 10:05 run if it ever fails again.

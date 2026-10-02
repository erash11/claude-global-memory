# 2026-10-02 — Background job list cleanup (Mac)

## What
Removed 61 completed background sessions from `~/.claude/jobs/` with `claude rm <id>` (Eric approved).
`~/.claude/jobs/` went from 715 MB to 9.3 MB. Repos, memory, transcripts and handoffs were not touched —
`claude rm` deletes only the job record and its `tmp/` scratch folder.

## Kept on purpose
- `c59d1788` "skill audit development" (9/13) and `9823c1f0` "compiler lock recovery" (9/13).
  Both hold the only copy of the AIOS Gate B/C review rounds (`tmp/aios-dispositions-r*`, `gateC*`).
  The AIOS plan itself is pushed: `~/DEV/KeystoneOS/docs/superpowers/plans/2026-09-12-harness-agnostic-aios.md` (`00730b6`).
  Work paused mid Gate C with 2 decisions open. AIOS is not in Active Threads.

## Next
- Eric: decide to resume AIOS Gate C, or drop it. If drop: `claude rm c59d1788 9823c1f0`.

## Gotchas
- The auto-mode classifier blocks `claude rm` unless the user approves in chat.
- Removing a job does not delete handoffs written to `$TMPDIR` / `/var/folders` — those are already outside the job folder (and not durable).

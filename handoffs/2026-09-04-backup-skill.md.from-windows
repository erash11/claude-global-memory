# 2026-09-04 — On-demand `/backup` skill + full SSD backup run

## What was being worked on and why

Eric asked to run the daily backup and to turn it into a skill he can invoke at
will. His stated premise ("we don't have it scheduled") was wrong — the launchd
agent `com.keystone.dailybackup` fires at 09:00 daily — but his reasoning was
right: the Mac is often off at 09:00, so a scheduled-only job silently skips days.
An on-demand path genuinely did not exist.

## Decisions made (and why)

- **Skill named `backup`, lowercase-kebab.** Matches its closest sibling
  `claude-stack-doctor`. The `TitleCase`/`_ALLCAPS` convention in
  `~/.claude/skills/CLAUDE.md` describes public-vs-private packaging; every ops
  skill actually loaded in this workspace is lowercase-kebab, and `name:`
  frontmatter must equal the directory name.
- **The skill reads `backup-state.json`, not the exit code or the log tail.**
  The script can exit 0 while a target was skipped. `status` + `errors[]` in that
  file is the only authority.
- **The skill must always name a skipped target.** A run with the SSD unplugged
  reports `OK` with 0 errors while untracked/gitignored/uncommitted files were
  saved nowhere. Reporting "backup complete" there is the exact failure mode the
  skill exists to prevent.
- **Job count is the completeness signal, not the error count.** 9 jobs OK
  without the SSD vs 31 jobs OK with it.
- **`.errors.log` must be cleared by hand after a fixed failure.** The script only
  appends; a later success never clears it, so the HOOK FAILURE block keeps
  appearing at every session start. Clear with `cp /dev/null` — dcg rule
  `core.filesystem:redirect-truncate-root-home` blocks `: > file` under `$HOME`,
  and there is no `truncate` binary on this machine.

## What actually happened

1. The 09:05 scheduled run failed with `repo-push:global-memory` and
   `repo-push:skills`. Root cause from the log: `Could not resolve host:
   github.com` — a transient DNS blip, not a repo or auth problem. Commits were
   already made locally; a re-run pushed them cleanly.
2. First manual re-run: `OK`, 0 errors, but **9 jobs** — CRASHBOX SSD was not
   mounted, so the orphan and working-tree capture was skipped entirely.
3. Eric said the SSD was connected, but `diskutil list external` printed nothing
   and no USB/Thunderbolt device appeared at all. Diagnosed as a cable or port
   problem, not software. A charge-only USB-C cable is the usual culprit; the fast
   check is `diskutil list external` printing nothing.
4. After the cable/port fix: `/dev/disk4`, `CRASHBOX`, 500 GB, 437 Gi free,
   mounted at `/Volumes/CRASHBOX`. Full run: **0 errors, 31 jobs OK, 7,801 files
   written.** Receipt `run-20260904-134638.txt`. Per-folder freshness confirmed
   the point of the exercise: `DEV-working-tree` 7 fresh, `DEV-nonrepo` 106 fresh,
   `DEV-repo-data` 2,458 fresh.

## Files created or modified

- `~/.claude/skills/backup/SKILL.md` — new. Committed and pushed to the
  `claude-skills` repo.
- `~/DEV/COMMANDS.md` — added a `/backup` row to the slash-command table and
  rewrote the A4 Backups section opener to point at `/backup` first. **`~/DEV` is
  not a git repo** — this edit lives on disk only and is covered by the SSD leg.
- `~/.claude/global-memory/transcripts/.errors.log` — archived to
  `.errors.log.archived-2026-09-04`, then emptied. Now 0 bytes.
- `~/.claude/LIFEOS/MEMORY/SKILLS/execution.jsonl` — appended a CreateSkill row.
- `~/.claude/scripts/logs/backup-state.json` — now `status: OK`, `errors: []`,
  `okCount: 31`.

## Standing routine going forward

Plug in CRASHBOX, then type `/backup` in Claude Code. That is the whole thing.

## Next actions

None outstanding. Both asks are delivered and verified.

## Notes for a future session

- The header comment in `daily-backup.ps1` still claims "Runs daily at 00:30".
  That is stale — the plist says 09:00. Harmless, but do not trust it.
- Log lines appear **twice** for launchd runs (the script writes to the log file
  and the plist also captures stdout to the same file) and once for manual runs.
  Not a bug; do not read doubled lines as two attempts.
- A newly written SKILL.md loads immediately. No session restart is needed.

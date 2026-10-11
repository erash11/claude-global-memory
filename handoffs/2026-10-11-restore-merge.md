# Handoff: restore merge into ~/.claude (2026-10-11)

## What was done
- Merged the restored Windows `.claude` tree into `~/.claude`. No-overwrite rule (dev-sync): Mac copy kept; Windows copy saved as `<file>.from-windows`.
- Script: `~/.claude/jobs/788f361d/tmp/merge_windows.sh` (`dry` or `apply`). Log: `~/.claude/jobs/788f361d/tmp/merge_apply.log`.
- Apply result: new=16751, same=21334, saved_as_from_windows=7739, errors=0.
- Nothing was overwritten.

## Open
- 897 restore files were NOT copied by apply, with no error logged. Mostly `plugins/cache/claude-video/watch/0.2.0/` (891; Mac has 0.3.2 and the folder is marked orphaned). Also 5 `backups/.claude.json.backup.*`, 1 `daemon/attach-journal/*.json`, and `skills/grill-with-ui` (Windows symlink). Cause not proven.
- Decision 1: keep or delete the 7,739 `.from-windows` files.
- Decision 2: `.credentials.json` (gitignored) and `CREDENTIALS.md` (NOT gitignored, and tracked in the `~/.claude` git repo). Move out and rotate the keys, or keep.
- `~/.claude` repo NOT pushed today: ~10 dirty files (session jsonl logs). Push waits on Decision 2.
- Partial zips kept in `~/Restore/_zips/` (`claude.zip`, `claude-gws.zip`, `claude-gws-2.zip`). Do not delete.
- Background `gws auth login` jobs `bypc9pchy` and `b1109q1ld` may still be running. Stop them if not needed.

## Closeout 2026-10-11
- Pushed: `global-memory` (9ed4fd2), `graphify-out` (b0c7a97).
- Registry drift: 14 items (`portfolio.py crosswalk`). Not fixed on purpose.
- 7-day rule: NCAA_BestPractices_Doc (0 days left), HPI_Protocol (1), Education_Curriculum (1), Performance_Playbook (2). All need step 1.
- Hook failures still open: compiler backlog and budget trip, claude-files-digest send failed, memsearch-index full-set errors (daily-backup, 10-11 12:09), gps-pull exit 4, compiler flush failed 10-10.

## Next
1. Answer Decision 2 (credentials). Then rotate keys if moved.
2. Answer Decision 1.
3. Find the cause of the 897 missing files.

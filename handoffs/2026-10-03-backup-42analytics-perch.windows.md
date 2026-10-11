# 2026-10-03 — Backup manifest fix, manual backup run, perch-pull rerun (Mac)

## What and why
- `daily-backup` failed on 10/02 with `manifest-unmanaged:42Analytics`. The manifest is default-deny: any DEV folder not listed fails the health check.
- `perch-pull` showed a failure from 10/01 in `.errors.log`.

## Done
- Added `DEV/42Analytics` to `~/.claude/scripts/backup-manifest.json`: class `institutional` (confirmed by Eric; it feeds Flint), destinations `ssd` + `github`, same shape as `DEV/Flint`. Commits `971c569`, `999e01b` in dotclaude, pushed.
- Last night's 9 PM backup did not run. The Mac was shut down or restarted (power log quiet after 16:43 on 10/02, fresh boot 08:57 on 10/03). launchd runs a missed job on wake from sleep, but not after a power-off or restart.
- Ran the backup by hand: `launchctl kickstart gui/$(id -u)/com.keystone.dailybackup`. Run `20261003-094131` ended 10:16, `OK (0 errors)`. No manifest error. Index step took 34 min (2,038 chunks).
- CRASHBOX SSD not connected (Eric does not have it with him). The run logs this as SKIPPED, not as an error.
- `perch-pull`: the scheduled 10:05 run had already passed. Reran by hand at 10:23: ok, 13,826 rows, newest test 2026-10-02, Drive snapshot ok. The 10/01 failure is cleared.

## Not committed on purpose
- `~/.claude/settings.json` has an uncommitted change from another source: a second PreToolUse `Bash|PowerShell` hook with the hardcoded command `/Users/kristinarash/.local/bin/dcg`, above the existing portable `if [ -x "$HOME/.local/bin/dcg" ]` hook. That path does not exist on Windows, so it would error on every shell call there. Left out of the commit. Decide: revert with `git -C ~/.claude checkout -- settings.json`, or keep it Mac-only.

## Next
1. Decide on the `settings.json` duplicate dcg hook (above). Recommended: revert; the portable hook already runs dcg.
2. Plug in CRASHBOX before a 9 PM run to get the SSD layer captured.
3. Windows: `memsearch-sync` failed 10/02 22:00 UTC with a gRPC `_InactiveRpcError`; log at `C:\Users\eric_rash\.claude\global-memory\transcripts\.memsearch-index.log`.

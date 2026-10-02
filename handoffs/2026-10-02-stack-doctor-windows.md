# 2026-10-02 — Stack doctor on the Windows laptop

## What and why
Ran `/claude-stack-doctor` on Windows. It found 3 issues: errors-log non-empty,
`MEMORY.md` at 99% of cap, and `~/.claude` 3 commits behind origin.

## Done
- Pulled `~/.claude`. The 3 incoming Mac commits only pruned Mac-slug transcripts,
  plus one regression in `settings.json` (below). Handoff check now reads in sync.
- Removed a hardcoded `/Users/kristinarash/.local/bin/dcg` PreToolUse (Bash|PowerShell)
  hook that the Mac had added above the existing guarded `dcg` entry. It errors on
  Windows and double-runs dcg on the Mac. Commit `d59b4dd` in dotclaude, pushed.
- Cleared `transcripts/.errors.log` after archiving it to
  `transcripts/.errors.log.archived-2026-10-02` (4 entries).
- memsearch-sync grpc failure at 21:16 UTC was a Milvus restart; Milvus healthy and
  search working afterwards.

## Decisions
- **Do not re-enable `daily-backup` on Windows.** `daily-backup.ps1` is the Mac port
  (its own header says restore and re-port `daily-backup.ps1.win-orig` first), and running
  it on both machines caused nightly `repo-diverged` in August. Windows is already covered:
  "Backup AI Sessions to Drive" (daily), `Desktop\DEV` as a Drive synced root, and
  `memsearch-drain-weekly` for the reindex.
- **No new pull-only task.** `dev-sync` (also run by `/startup`) already pulls `.claude`,
  skills and global-memory. Run it on sitting down at the laptop.

## Files changed
- `~/.claude/settings.json` (dcg hook removed)
- `~/.claude/global-memory/transcripts/.errors.log` (emptied)
- `~/.claude/global-memory/transcripts/.errors.log.archived-2026-10-02` (new)
- `~/.claude/global-memory/handoffs/2026-10-02-stack-doctor-windows.md` (this file)

## Next (Mac, tonight)
1. Read `~/DEV/PlayerProfiles_FB_03-28-2026/logs/last_run.json` — perch-pull failed 10/1.
2. Add `42Analytics` to `backup-manifest.json` — `manifest-unmanaged:42Analytics`.
3. Confirm the `/Users/kristinarash/.local/bin/dcg` hook line does not reappear after
   `dev-sync`; if it does, find what dcg install step writes it.
4. `MEMORY.md` was at 2,468/2,500 chars at stack-check time (since consolidated into
   Active/Parked); re-check headroom before the next write.

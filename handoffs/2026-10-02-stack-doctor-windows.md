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

## Later the same afternoon
- The Mac pulled `d59b4dd`, then **re-added** the hardcoded dcg line in its own next
  settings commit `e72c374` (S2 rsync rule). Something on the Mac writes it into
  `settings.json` (suspect dcg self-registering; unconfirmed). Left in place on purpose;
  removing it again from Windows would just ping-pong. On Windows it fails quietly.
- Mac added 42Analytics + SoftwareTech_Review to `backup-manifest.json` (closes
  `manifest-unmanaged`). Mac pushed a perch-pull fix handoff.
- Concurrent closeouts on both machines conflicted on `transcripts/2026-10-02.md`;
  resolved with `git merge-file --union` (append-only log, kept both sides).
- `git config core.longpaths true` set **locally** in `~/.claude` on Windows; two session
  files under the `G--My-Drive-...Proulx-PelvicFloor...` slug had been skipped as
  "Filename too long".
- **memsearch-sync failed twice** (21:16 and 22:00 UTC): "Milvus Proxy is not ready yet".
  `milvus-standalone` has RestartCount=5, OOMKilled=false, exit 0, while etcd/minio stay up
  8h. Indexing hits it mid-startup. No hook/script restarts it. Cause not found yet;
  `.errors.log` entry left in place deliberately.

## Next (Mac, tonight)
0. Delete the hardcoded dcg hook entry on the Mac and see what re-adds it.
1. ~~perch-pull failed 10/1~~ — DONE: fixed on the Mac 10/2, Eric confirmed complete 10/3.
2. Add `42Analytics` to `backup-manifest.json` — `manifest-unmanaged:42Analytics`.
3. Confirm the `/Users/kristinarash/.local/bin/dcg` hook line does not reappear after
   `dev-sync`; if it does, find what dcg install step writes it.
4. `MEMORY.md` was at 2,468/2,500 chars at stack-check time (since consolidated into
   Active/Parked); re-check headroom before the next write.

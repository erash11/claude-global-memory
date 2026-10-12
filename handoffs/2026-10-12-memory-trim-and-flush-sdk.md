# Handoff 2026-10-12: memory trim and flush SDK upgrade (Mac)

## What was being worked on
- Ran `/claude-stack-doctor`. It found 4 issues: error log, flush errors, backup error, and `MEMORY.md` at 98% of its cap.
- Trimmed `MEMORY.md` (user chose option A).
- Investigated the memory flush failure "Reached maximum number of turns (2)". Upgraded the SDK to test version skew.
- Ran `/closeout`.

## Decisions and why
- **Trim `MEMORY.md` now (option A).** Cap is 2,500 chars. It was at 2,438. Now 2,264. All 5 Active Threads and all 10 Parked items kept. Parked lines keep only the NEXT step and a pointer, because each project's `STATUS.md` holds the detail.
- **Do not rebuild the memsearch index.** The error "may not be compatible with Milvus Lite 3.x" is a generic open-failure message. It also fires on lock contention. Checked: no process holds the lock, and `ms-search stats` returns 43,452 chunks. The database is healthy.
- **Upgrade `claude-agent-sdk` 0.2.152 to 0.2.165.** This tests whether bundled-CLI version skew causes the flush failures. Not proven yet.
- **Merged Windows commits `e00b378` and `8901178`** (WMI spawn for compile on Windows). The Windows path is gated on `sys.platform == "win32"`. The shared lines only use the full `uv` path and add `-u`.

## Files touched (full paths)
- `~/.claude/global-memory/MEMORY.md`
- `~/.claude/global-memory/transcripts/.errors.log` (cleared)
- `~/.claude/global-memory/transcripts/.errors.log.archived-2026-10-12` (archive)
- `~/.claude/global-memory/docs/STATUS.md`
- `~/.claude/global-memory/handoffs/2026-10-12-memory-trim-and-flush-sdk.md` (this file)
- `~/.claude/claude-memory-compiler/uv.lock` (commit `4395af3`, pushed as `d677595`)
- `~/.claude/claude-memory-compiler/docs/STATUS.md`
- `~/.claude/claude-memory-compiler/scripts/_stranded-archive/` (8 files, Oct 2–7, untracked on purpose)

## Next, most important first
1. After your next session ends, run `tail -n 20 ~/.claude/claude-memory-compiler/scripts/flush.log`. Look for `FLUSH_OK`. If "Reached maximum number of turns" returns, send the exact error text and the session-end time.
2. Tonight after 21:00, check that the `backup-error` line clears in the stack doctor. If the Milvus message returns, run `lsof +D ~/.memsearch/milvus.db` before deciding anything.
3. Keep `scripts/_stranded-archive/` off GitHub.

## Open or mid-flight
- Flush failures on Oct 10 and Oct 12 ("maximum number of turns"). The cause is not proven. The SDK upgrade is the test.
- `~/.claude` has modified live session transcripts (`projects/-Users-kristinarash-DEV/*.jsonl`). Not committed by hand. The nightly backup covers them.

# 2026-09-22 — Stack doctor run on Windows laptop

## What / why
Ran `/claude-stack-doctor` on the Windows laptop. `stack-check.ps1` is launchd-only
(macOS), so only `handoff-check.ps1` ran as-is; the rest was checked by hand.

## Findings
- Handoff: HEALTHY (global-memory, .claude, skills all in sync; memory flow 0.1 d).
- `.errors.log` compiler-backlog entry (2026-09-21): already resolved — compile run
  finished 2 ok / 0 failed; only today's daily log is uncompiled (normal).
  Archived to `transcripts/.errors.log.archived-2026-09-22`, log cleared.
- venv (py 3.14.6), memsearch, Milvus (3 containers healthy), flush (06:22 today): OK.
- `Backup AI Sessions to Drive` rc 11 on `projects` at 03:26 (run lasted 2h37m vs ~1 min):
  sleep-interrupted. Foreground robocopy re-run: rc 3, 0 failed. No fix needed.
- `flush.log` "SKIP: transcript missing": sessions opened and closed with no user turn
  (dir has only SessionStart tool-results, no .jsonl). Benign, since April.
- Windows KeystoneOS-* scheduled tasks: disabled since mid-August (Mac owns them).

## Closeout changes
- `DEV/Football/SpringPlayerEvals_SymAnalysis/.gitignore`: added `.claude/worktrees/`
  (a live worktree `pff-db-env` from another session showed as untracked).
- `DEV/Football/SpringPlayerEvals_SymAnalysis/docs/STATUS.md`: Gotchas line.

## Next
1. Consider a Windows branch in `stack-check.ps1` (Task Scheduler instead of launchctl)
   so the doctor runs end-to-end on this machine.
2. Optional: 3 stranded `session-flush-*.md` from June in
   `~/.claude/claude-memory-compiler/scripts/` — recoverable with flush.py, low value.
3. Desktop Commander MCP timed out on connect this session; retry if it recurs.

## Follow-up (same day, afternoon)
- **Doctor now runs on Windows.** `claude-stack-doctor/scripts/stack-check.ps1` picks its checks by OS
  (Task Scheduler, `.venv\Scripts`, Docker/Milvus, robocopy backup state files). Also fixed on both
  machines: the cloud receipt check now keeps only `run-*.txt` (Drive token matching had returned
  `jev_run2.jsonl`). claude-skills PR #2, merged `b25f514`. Weekly task `\Eric\KeystoneOS-StackDoctor`
  enabled (Mon 10:30, pwsh 7). Use pwsh 7; PowerShell 5.1 gives false memsearch/gws failures.
- **PFF_DB PRs merged** in owner-first order: PFF_Data_Project #1, SpringPlayerEvals_SymAnalysis #1,
  PlayCalls_SuccessRate_EPA #1. Diffs fall back to the old paths when `PFF_DB` is unset (the Mac is unaffected).
  Tests: PFF 35/35 on main and on the branch; PlayCalls failures are the same on main (no venv here, so
  `tabulate` and `ijson` are missing).
- **June stranded flushes NOT recovered**: flush.py writes to today's log, so recovering them would
  misdate June facts. Moved to `claude-memory-compiler/scripts/_stranded-archive/`.
- **Desktop Commander timeouts** (13 of the last 15 starts): npx @latest startup takes 23–46s against the 30s limit.
  Set `MCP_TIMEOUT=90000` in `~/.claude/settings.json` env (takes effect next session).
- AI-sessions backup re-run via the task: status OK 16:13.

## Open
1. `Backup DEV to Drive` has never completed: no `05_SYSTEMS\DEV_Backup`, no state file, missed its 9/20 run.
   Drive for Desktop already mirrors `Desktop\DEV`. Decide: delete the task, or fix and keep it.
2. MEMORY.md is at 2490/2500 chars; consolidate before the next write.
3. Stale `.git/worktrees/{t-PlayCalls*,p-origin_main}` dirs are locked by Drive; quit Drive, then `git worktree prune`.

## Resolved (evening)
- Open 1: `Backup DEV to Drive` deleted (Eric OK'd). Drive for Desktop's root_preference db lists
  `C:\Users\eric_rash\Desktop\DEV` as its synced root. Task XML + script in `~/.claude/scripts/retired/`;
  install-backup-triggers, verify-crossmachine, RECOVERY-INVENTORY updated. Doctor checks dropped (skills PR #3).
- Open 2: MEMORY.md consolidated 2490 → 2330 chars; stale "quit Drive to unlock worktrees" note corrected.
- Open 3: stale worktree dirs were **read-only**, not Drive-locked (prune failed even with Drive quit);
  `Remove-Item -Recurse -Force` cleared all three.
- Stack doctor on Windows: ALL CLEAR, exit 0.

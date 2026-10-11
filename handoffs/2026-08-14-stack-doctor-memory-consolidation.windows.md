# 2026-08-14 — Stack doctor run: memory consolidation + codex/sessions wedge evidence

## What this session was

A `/claude-stack-doctor` health check of the automation/memory stack. It found 4 issue
codes. I fixed the two that were mine, and diagnosed (did not fix) the backup fault, which
another session — `3db720f8`, the Codex companion — was actively working the whole time.

**Read this alongside** `~/.claude/projects/-Users-kristinarash-DEV/memory/project_backup-sync-system.md`,
which is the authority on the backup fault. That session has edited it since; treat its
version as newer than anything summarized here.

## Decisions made, and why

**1. Consolidated Tier B memory by promoting, not deleting.**
`global-memory/MEMORY.md` was at 100% of its 2,500-char cap and `USER.md` at 97%. The risk
is not the size — it is that the *next* write must then drop facts under pressure, quietly.
Rather than trim, I moved durable facts down to Tier A (the CLAUDE.md tier rule: "still true
and useful in 3 months, across multiple projects"). Now 82% and 89%.

**2. `USER.md` lost its tool-paths block deliberately.**
It duplicated `~/.claude/CLAUDE.md` verbatim, and CLAUDE.md loads every session anyway. The
memory rules say not to store what another always-loaded file already records. If you go
looking for those paths in `USER.md`, that is why they are gone.

**3. Did not clear `.errors.log`, though the stack-doctor flags it.**
`project_backup-sync-system.md` carries a standing decision: clear it only after one clean
nightly lands. The wedge is bounded but not fixed, so that condition is still unmet. The
file now holds 7 lines and will gain one per nightly. This is a known cost, not a fault —
it is startup noise every session until the wedge is explained.

**4. Did not run my own backup, and did not `kill -9` the wedged processes.**
Another session owned that run. Two writers on one backup is the documented root cause of
this system's worst past failure. Reaping PPID-1 orphans was safe (separate process tree);
escalating was not.

## Files created or modified

Created:
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_cfb-forecast-capture.md`
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_automation-cadence.md`
- `~/.claude/global-memory/handoffs/2026-08-14-stack-doctor-memory-consolidation.md` (this file)

Modified:
- `~/.claude/projects/-Users-kristinarash-DEV/memory/MEMORY.md` — 2 new index pointers
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_backup-sync-system.md` — added a
  live-reproduction evidence section (sibling session has edited it further since)
- `~/.claude/global-memory/MEMORY.md` — rewritten, 2496 → 2061 chars
- `~/.claude/global-memory/USER.md` — 1331 → 1230 chars

Fixed defect: `MEMORY.md` (Tier A index) pointed at `project-cfb-forecast-capture`, a file
that had never existed. All 11 pointers now resolve.

## The wedge — what is actually known

Root cause is **still open**. It is bounded by a watchdog the sibling session added
(`Invoke-Rsync`, 900s ceiling, hard SIGKILL, commit `8863a37`). Measured, not inferred:

- 4 rsync processes used <0.03s CPU across 34–85 minutes. A hang, not a slow transfer.
- The mirror was already complete (256/256 files). Nothing left to copy, still hangs.
- The mount is healthy: recursive `find` and a `touch` write both returned instantly.
- The wedged processes ignored SIGTERM.
- Orphaned `rsync --server` receivers are a *symptom*: an earlier run hung at 10:32 before
  the oldest orphan existed (13:55), and killing the orphans unblocked nothing.

Do not go hunting for a `pkill` in `daily-backup.ps1` — there is none (verified by grep).
The anchored `pkill -f "^/usr/bin/rsync"` that strands receivers lives in an ad-hoc
interactive wrapper; it cannot match the `--server` child, whose `argv[0]` is bare `rsync`.

## Next actions, most important first

1. **Explain the wedge.** Run the single `codex/sessions` rsync in the foreground with
   output visible — no PowerShell pipeline, no `Select-Object`. `Invoke-Rsync` pipes through
   `2>&1 | Select-Object -Last 3`, so that run's own diagnostics are the one thing nobody has
   read. (Owned by session `3db720f8`.)
2. **Then clear `.errors.log`** — and only then.
3. **Expect 3 issue codes on tomorrow's stack-doctor run**, not 0: `snapshot:sessions`,
   `rsync-timeout`, `backup-error`, plus `task:com.keystone.dailybackup`. All four are the
   same single wedge seen from four places. They will not self-clear.

## Mid-flight / caveats

- `project_backup-sync-system.md` existed in three versions at last check (source 14133,
  Drive 10247, SSD 10586) because it was being edited during the backup run. Nothing is
  corrupt; the newest content is local-only until the next run captures it.
- `~/.claude/settings.json` has an uncommitted change (`defaultMode: auto → dontAsk`) that
  did not come from this session. Left alone; the nightly auto-commits that repo.

## Verified good as of 17:5x

Backups are sound. Tier A memory is byte-identical across source, Drive, and SSD for 11 of
12 files. Tier B is pushed (empty diff vs `origin/main`). The reattached CRASHBOX SSD holds
39,868 files across the three DEV layers, including 1,612 files of
`Risk_Stratification_Engine` data with multi-MB CSVs, under receipt `run-20260814-154848` —
the first SSD capture since 2026-08-06.

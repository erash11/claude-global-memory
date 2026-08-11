# 2026-08-11 — Stack doctor sweep

Follow-on to `2026-08-07-doctor-cleanup.md`. Ran `/claude-stack-doctor`, fixed every
issue that was mine to fix, and left the rest for Eric.

## Verdict movement — read this carefully, the count understates the change

Raw verdict: **8 issue(s) → 6 issue(s)**. The count is a poor measure here, because
three of the six remaining codes are *lagging indicators* that read the last run's
result rather than current state. Breakdown of what's left:

| Code | Status |
|---|---|
| `task:com.keystone.morningbriefing` | **Genuinely open** — Outlook auth, needs Eric |
| `backup-cloud-stale` | **Genuinely open** — DriveFS, needs Eric |
| `errors-log` | Correct: non-empty *because* of the open Outlook item |
| `task:com.keystone.dailybackup` | Lagging — reflects the 07:47 run's exit code; clears tonight |
| `backup-error` | Lagging — now reduced to `manifest-unmanaged` only (a scope call), down from 4 errors |
| `flush-error` | Lagging — greps historical FLUSH_ERROR text in the 8/08 + 8/11 daily logs; the cause is fixed and a flush has since succeeded |

Fully cleared at the source: `skill-tax`, `memfile-full:MEMORY.md`,
`repo-diverged:skills`, `repo-diverged:SecondBrain`.

## Root causes fixed (not just symptoms)

**1. `repo-diverged:skills` — recurring every single night.**
Six files were tracked but regenerated on every run:
`claude-stack-doctor/scripts/last-weekly-run.log` and five `__pycache__/*.pyc`.
The nightly backup committed them, so the repo diverged, and `Sync-Repo`
deliberately refuses to merge a diverged repo from automation → error every night.
Untracked all six and added them to `.gitignore` (commit `a259114`). This is the
highest-leverage fix in the sweep: it removes the churn at the source.

**2. `skill-tax` was a FALSE POSITIVE.** The check counted every `SKILL.md` on disk
(133 skills / 65,467 chars, "205% of budget") with no knowledge of `skillOverrides`.
72 of those are set to `"off"` and are never loaded. Verified the overrides actually
work before patching anything: **0 of the 72 appear in the session's skill listing**
(61 expected from `disk - off`, 60 observed). Patched `stack-check.ps1` to read the
`skillOverrides` key and exclude disabled skills. Now reports
**61 skills / 27,093 chars — OK, 85% of budget**, which matches the independent count.
The /doctor skill cleanup did land; the monitor was measuring the wrong thing.

**3. `flush-error` — repeated 8/08 and 8/11**, which the documented rule says means
bundled-CLI version skew rather than transient contention. `claude-agent-sdk`
**0.2.110 → 0.2.136** (26 versions behind) via
`uv lock --upgrade-package claude-agent-sdk && uv sync`. Verified after: a flush
succeeded (`last-flush.json` 0h). memsearch re-checked — the flush patch was NOT
stripped (that landmine applies to memsearch pip ops, not this uv upgrade).

**4. `repo-diverged:SecondBrain` — a genuine two-writer conflict, resolved without
picking a winner.** Four untracked morning briefings existed locally while origin had
*different* committed versions of three of the same dates (local 8/07 had a working
Outlook fetch; origin's was degraded). Local git history was 4 commits behind since
the migration, so the briefing script kept regenerating files the repo already had.
**All four local variants preserved** at
`~/.claude/doctor-backup-20260807-135924/secondbrain-local-briefings/*.local.md`,
then pulled to `40851e8`. Eric should decide which 8/07 and 8/10 to keep — the
content differs materially, and that was not mine to choose.

**5. `daily-backup.ps1` lied in dry-run mode.** The `git add/commit/push` calls sit
inside `if (-not $DryRun)`, but the `Log "... committed/pushed"` lines sit *outside*
it — so `-DryRun` printed "committed 1 change(s) / pushed" for work it never did.
Nearly caused a false conclusion during this sweep. Fixed: those three log lines are
now dry-run aware (`[dry-run] would commit/push/fast-forward`).

**6. `MEMORY.md` was at 2498/2500 (100%)** — the next write would have failed.
Consolidated wording only; **all 16 threads preserved**. Now 2328/2500 (93%).

**7. `.errors.log`** — 10 resolved entries moved to
`transcripts/.errors-archive-2026-08-11.log`, each annotated with how it was
resolved. Only genuinely-open items remain in the live file.

## Still open — both need Eric, neither is auto-fixable

1. **Outlook auth expired** → run `DEV/morning-briefing/scripts/reauth.sh`.
   Interactive; briefings are shipping with 0 email threads until then. This is the
   only entry left in `.errors.log`.
2. **DriveFS 154h stale** — files reach the local Google Drive cache but Drive isn't
   syncing. Check GoogleDriveFS is running and signed in. Needs Eric at the machine.

## Reported, deliberately NOT "fixed"

- `snapshot:sessions` — rsync `mmap: Resource deadlock avoided` on a live Codex
  `.jsonl`. A file-in-use race, **not rot**. Nothing to repair.
- `manifest-unmanaged: COG_S2_Position_Reports, S2_Evaluation` — adding DEV dirs to
  `backup-manifest.json` is a scope decision for Eric.
- SSD `/Volumes/CRASHBOX` not mounted — orphan capture skipped; expected when unplugged.
- **The 73 unversioned skill files** (from the 8/07 handoff) remain unversioned. The
  three-way fork is still a design decision. The nearest no-decision improvement:
  add `~/.agents/skills` to `backup-manifest.json` so it stops living in only two
  places. Proposed, not applied.
- Compiler backlog is 4 logs. Self-healing (2/night vs ~1 new/day) and forcing it
  costs real money, so it was left alone.

## Verification

`daily-backup.ps1 -DryRun` after the fixes: **zero `DIVERGED` lines**, all four repos
clean. Confirmed the dry run mutated nothing (uncommitted edits still uncommitted,
`skills` HEAD unchanged).

Post-pull symlink integrity re-checked, since a `git pull` in `~/.claude/skills` is
exactly what destroyed 73 files on 8/07: **21/21 symlinks resolve, 0 broken, 154
`SKILL.md` reachable** (`find -L`, follows symlinks; the 133 figure counts top-level
dirs only — two different counting methods, both correct).

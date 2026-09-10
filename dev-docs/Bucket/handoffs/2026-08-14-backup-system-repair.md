# Handoff — 2026-08-14 — Backup/sync system repair

Full-day repair of the nightly backup after the 2026-08-05 Windows→Mac migration. Started
from `docs/SYSTEM-HEALTH-FINDINGS.md` (a 7-item diagnosis written 08-13 from logs). Ended
with the root cause of the longest-running symptom actually fixed, not just bounded.

## Outcome

The nightly (`~/.claude/scripts/daily-backup.ps1`, launchd `com.keystone.dailybackup`,
00:30 + ~07:23) went from `ERROR (5 errors)` with the SSD layer silently skipped, to a
completing run that captures every layer.

## What was wrong, and what fixed it

**1. Two writers on shared repos.** The retired Windows box still ran `daily-backup.ps1`
and pushed, manufacturing `repo-diverged:SecondBrain` nightly. Retired 2026-08-14: all 9
KeystoneOS/MorningBriefing scheduled tasks disabled (not unregistered). It had contributed
no unique history since 08-05 — only two append-only Windows failure logs, preserved to
`~/Desktop/windows-retirement-2026-08-14/` on that machine and deliberately NOT pushed
(origin had already untracked `.memsearch-index.log` in `a0e58c9`; committing would have
reverted a Mac-side decision).

**2. `Invoke-Rsync` reported false success.** A copy that moved zero bytes logged `SNAP OK`
off a stale `$LASTEXITCODE`. Fixed with a launch guard + `$global:LASTEXITCODE = 0`.

**3. `snapshot:sessions` — the one that took all day.** Four wrong theories died before the
right one. Chain: Google Drive was mirroring `~/DEV` as a device-backup folder ("My Mac"),
including 34 `.git` dirs / 3,470 files → VS Code's `git.autofetch` rewrote every
`FETCH_HEAD` on a 180s cycle → Drive uploaded all 34 each time → `PRECONDITION_FAILED`
storms and stuck threads → DriveFS degraded → placeholder fetches stalled for minutes →
rsync blocked on one → **the run never reached the SSD capture.**

Fixed by removing `~/DEV` from Drive Preferences → "Folders from your computer" (keeping
the cloud copy). Verified: `PRECONDITION_FAILED` 14 → 0, `ProcessDownloadEvent` errors
11 → 0, Drive CPU 64.6% → 0.0%, and 5/5 cold placeholder fetches now complete in 2–3s.

**4. SSD layer dark since 08-06.** CRASHBOX reattached; first capture since migration ran
2026-08-14 16:05 — 53,533 files, ~24 GB, receipt verified. Includes
Risk_Stratification_Engine (2.0 GB) and ForcePlate_DecisionSystem (1.6 GB), which had no
backup anywhere.

**5. Manifest gaps.** 6 unclassified `~/DEV` dirs added. `Football_Data_DEV` classed
personal per Eric. Athlete-data rule held: `COG_S2_Position_Reports` → institutional.

**6. Retired the morning brief** at Eric's request — `com.keystone.morningbriefing` booted
out + disabled, plist and `~/DEV/morning-briefing` retained, dropped from stack-doctor.

**7. False `backup-cloud-stale (218h)` alarm.** stack-doctor watched `RESTORE.md`, which
the job *copies* rather than rewrites, so its mtime never advanced. Repointed at per-run
receipts.

## Decisions worth preserving

- **Never delete Drive copies to fix a read stall.** Both files that hung were verified
  byte-identical to source *before* anything was touched. Deleting would have destroyed a
  good backup to repair a read path.
- **Don't disable `git.autofetch`** as the fix — it masks the symptom, costs a useful
  feature, and leaves 3,470 `.git` files mirrored to churn on every commit/checkout.
- **Verify Drive by md5 metadata, not by reading.** Reads are the unreliable layer.
- **Keep `.errors.log` entries until a cold nightly proves the fix.** Clearing early would
  hide conditions that hadn't been verified.

## Files created / modified

Created:
- `~/.claude/scripts/verify-drive-backup.sh` — md5 verifier (`0d2edb5`)
- `~/DEV/Bucket/docs/FIX-STATUS-2026-08-14.md`
- `~/DEV/Bucket/docs/handoffs/2026-08-14-backup-system-repair.md` (this file)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_backup-sync-system.md`
  (Tier A; **not in git** — `~/.claude/.gitignore` starts `/*` and `projects/` is not
  allowlisted, so its only copies are the Drive `claude-projects` snapshot and the SSD)

Modified:
- `~/.claude/scripts/daily-backup.ps1` — rsync false-OK guard, non-macOS platform guard
  (`ac2af1d`), per-copy watchdog (`8863a37`)
- `~/.claude/scripts/backup-manifest.json` — 62 → 68 paths
- `~/.claude/skills/claude-stack-doctor/scripts/stack-check.ps1` — cloud heartbeat fix,
  morning-brief removed from checked sets
- `~/.claude/global-memory/USER.md` — corrected stale Windows-era facts to macOS
- `~/.claude/global-memory/MEMORY.md` — consolidated under the 2,500-char cap
- `~/DEV/Bucket/docs/SYSTEM-HEALTH-FINDINGS.md`, `docs/AGENT-FIX-PROMPT.md` (`ce94371`)
- `~/Desktop/SecondBrain` — reconciled; both machines' briefings preserved, Mac copies
  renamed `*.mac-local.md`

## Next actions

1. **Check the 06:15 nightly.** Acceptance: `end: OK (0 errors)`, no `repo-diverged`, an SSD
   capture line, and `codex/sessions : OK`. This is the first *cold* run — today's testing
   warmed a lot of DriveFS cache, so a warm pass would not have proven anything.
2. **Then clear `~/.claude/global-memory/transcripts/.errors.log`** (7 stale lines). Not
   before — every condition named in them is fixed but unverified against a cold run.
3. **Optional:** `My Drive/OneDrive-Import/` holds 22 `.git` dirs / 7,292 files. Static,
   not churning, so not urgent — but it is dead weight in Drive.
4. **Optional:** three non-KeystoneOS tasks left enabled on the Windows box
   (`CFB-ForecastCaptureReminder`, `DailyGmailDigest`, `Refresh_All_Data`). None touch the
   shared repos.

## Traps that cost real time today

- `$(find ...)` word-splits on the space in "My Drive" — bit me three times. Use
  `-print0` / `read -r -d ''`.
- `du` on a DriveFS path reports *local cache*, not logical size. Compare file counts and
  `stat -f%z`.
- **Reading a Drive file materializes it**, so any scan warms the cache and a later run
  passes for reasons that will not hold after eviction.
- `pkill -f "^/usr/bin/rsync"` matches only the client; the `--server` child's `argv[0]` is
  bare `rsync`, so that pattern strands receivers. Match the destination path instead.
- A wedged rsync ignores SIGTERM. Only SIGKILL clears it.
- Reading an exit code through a pipe returns the last element's status.

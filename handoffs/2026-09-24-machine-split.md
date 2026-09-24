# Handoff — 2026-09-24 — Windows by day, Mac by evening

## What and why

Eric is making Windows the primary daytime machine and the Mac the evening one, so that he
isn't bouncing between them. The session (Windows) started with a question about where the
Drive migration put everything. It then covered cross-machine sync, and finally built what
the day/evening split needs.

## Decisions

- **Windows = day, Mac = evening.** Everything that is text already crosses via GitHub. What was
  still stuck on one machine: the Mac's scheduled jobs and its data, plus Tier A memory.
- **Tier A memory is mirrored.** `dev-sync` runs `~/.claude/skills/dev-sync/mirror_memory.py`,
  which merges the Mac and Windows slug folders (the newer file wins; `MEMORY.md` is merged;
  nothing is deleted). First run: 53 copied, 66 replaced, 16 indexes merged. Pushed as
  dotclaude `e893618`. (claude-skills PR #7)
- **The Mac stays the only writer of GPS, Perch and VALD.** After each pull it writes Parquet
  to `00_Primary_Storage_Drive/athlete-snapshots/{gps,perch,vald}/` with a `manifest.json`.
  There is a stale-writer guard (`--force` overrides). Windows reads the Parquet directly.
  (GPS #3, Perch #1, VALD #4)
- **The Mac daily-backup moves to 21:00**, with a makeup window of 21:00-23:59, so the 07:00
  reconcile doesn't re-run it. The CRASHBOX SSD capture only happens if the drive is attached
  at 21:00. (KeystoneOS #21, claude-skills #8)
- **Ritual nudges move to Windows.** `ritual-check.ps1` has its `msg.exe` branch back, with
  OS-aware paths. The stack doctor now expects `KeystoneOS-Rituals` on Windows and flags
  `com.keystone.rituals` if it is still loaded on the Mac.
- **S2 data lives on Drive:** `04_RESEARCH/03_Active_Studies/S2_Evaluation/data`.
  `build_report.py` resolves `$S2_DATA_DIR`, then Drive, then local `data/`. (S2_Evaluation #1)
  The archived originals were copied in from `08_ARCHIVE/PERSONAL/ThreeStandard/DataConsulting/S2`.
- **GPS `.pbix` is out of scope.** A colleague publishes it and holds the data.

## Mid-flight (not confirmed)

- A message was sent over Remote Control to the Mac session "forecast capture setup". It asks
  that session to (1) set the backup plist to 21:00, and (2) rsync S2 `data/` to Drive. That
  sends `ol_scores.csv` and `team_scores.csv`, which exist only on the Mac. No reply is
  possible, and it may need Eric's approval on the Mac first.

## Next actions

1. **Windows:** run `ritual-check.ps1 -Notify` once, then `Enable-ScheduledTask -TaskName 'KeystoneOS-Rituals'`.
2. **Mac:**
   - `launchctl bootout gui/$(id -u)/com.keystone.rituals`
   - Confirm the backup plist says 21:00 (`launchctl print gui/$(id -u)/com.keystone.dailybackup`).
   - Run `export_snapshot.py --dry-run` and then for real in each of the three pull repos.
   - Check that `logs/last_run.json` has `snapshot_export` ok after the next pull.
3. **Mac:** confirm the S2 rsync ran (the folder should now include `ol_scores.csv`).
4. **Decide:** build a Windows 17:30 auto-push of the context repos only (not DEV projects).
5. **Follow-up:** point Perch's `config.py` / `src/data.py` Windows reads at the Parquet snapshots.
6. **Fix:** the Windows `Backup AI Sessions to Drive` task failed (rc=1) this morning.
   `backup-ai-sessions.ps1` has a 5-line uncommitted change from another session, committed in
   this closeout. Verify with `/claude-stack-doctor`.

## Gotchas

- Windows `git worktree remove` leaves `.git/worktrees/<name>` behind ("Permission denied").
  Clear the read-only attribute, then `Remove-Item -Force`, then `git worktree prune`.
- The auto-mode classifier blocks listing the S2 Drive data folder (athlete-named file), so
  confirm that folder by hand.
- Two snapshot tables can legitimately shrink (GPS `positional_norms`, VALD `athlete_baselines`).
  The export refuses them until it is run once with `--force`.

## Files touched

- `~/.claude/skills/dev-sync/{SKILL.md,mirror_memory.py}`, `~/.claude/skills/backup/SKILL.md`,
  `~/.claude/skills/claude-stack-doctor/{SKILL.md,scripts/stack-check.ps1}`
- `DEV/KeystoneOS/{data/jobs.json,scripts/ritual-check.ps1,docs/STATUS.md}`
- `DEV/S2_Evaluation/{build_report.py,AGENTS.md,docs/STATUS.md,docs/program/README_DATA.md}`
- The three pull repos: `src/snapshot.py`, `export_snapshot.py`, the pull scripts, tests, CLAUDE.md, STATUS.md
- `~/.claude/projects/*/memory/` (the mirror run)
- Drive: `04_RESEARCH/03_Active_Studies/S2_Evaluation/data/` (3 files copied from the archive)

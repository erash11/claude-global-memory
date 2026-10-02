# 2026-10-02 — Mac tasks for the Windows "google drive migration audit" session

## What and why
The Windows session (2026-09-24) asked the Mac to do two Mac-only jobs after the
machine split (Windows = day, Mac = evening):
1. Move `com.keystone.dailybackup` from 09:00 to 21:00.
2. Copy `~/DEV/S2_Evaluation/data/` to Drive, because S2_Evaluation PR #1 moved data/ to Drive.

## Outcome
- Backup: already at 21:00 when checked on 10/02 (someone set it after 9/24).
  PlistBuddy shows `Hour = 21, Minute = 0`, and launchd has loaded it.
  `com.keystone.rituals` was not touched.
- S2 data: Drive `.../00_Primary_Storage_Drive/04_RESEARCH/03_Active_Studies/S2_Evaluation/data/`
  now has 5 entries: ol_scores.csv 981, team_scores.csv 5270 (both new),
  S2_Cognition_Analysis_Template.xlsx 12979, Team_S2_AllTime.csv 17880,
  radar_Aigbedion,_Omar.png 237314 (already there). The local data/ is unchanged.
- The Windows session was sent a "done" message. Delivery is not confirmed.

## Decisions
- Added one exact Bash allow rule in `~/.claude/settings.json` (dotclaude e72c374)
  for `rsync -a --ignore-existing <S2 data> <Drive S2 data>`. It is an exact path,
  with no wildcard. Eric asked for it after the auto-mode classifier blocked the
  copy as "PII Data Handling".
- Use `--ignore-existing`, not `--update`, for one-way copies into the Drive mount.
  `--update` hung for 11 min on a file already on Drive, because Drive rewrites
  mtimes. Also recorded in Mac Tier A `project_drive-fuse-rsync-mtime-loop.md`.

## Gotchas
- The auto-mode classifier blocks launchd edits ("Unauthorized Persistence") and
  copies of athlete data ("PII Data Handling") even after Eric approves in chat.
  An exact allow rule in settings.json clears the copy. For launchd, Eric runs it with `!`.
- macOS rsync is openrsync. Its receiving child is named `rsync --server`.

## Files changed
- `~/.claude/settings.json` (S2 rsync allow rule)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_drive-fuse-rsync-mtime-loop.md` and that folder's `MEMORY.md`
- Drive S2 `data/`: ol_scores.csv, team_scores.csv added

## Still open (from hook log, not this session's work)
- perch-pull failed 10/01 (exit 1): `~/DEV/PlayerProfiles_FB_03-28-2026/logs/last_run.json`
- daily-backup 10/02: `manifest-unmanaged:42Analytics` (the repo-behind error should clear now that memory is pulled)
- aios-audit due: "audit my AI OS" in `~/DEV/KeystoneOS`

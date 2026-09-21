# Handoff: Windows dev-sync + data pulls moved to the Mac (2026-09-21)

Windows laptop, Claude Code background session "devsync". Worked alongside the Mac session
"Mac wake schedule and GPS pull setup", which did the Mac side.

## What happened and why

1. `/dev-sync` on Windows: config repos pulled (dotclaude +5, global-memory +5, skills 0), codex
   skills synced (41). 143 DEV repos checked, 5 pulled (claude-global-memory, DataBase_GPS_Reporting,
   graphify-out, TypeSafe_Sandbox, project-triage), SpeedProfiling local main fast-forwarded.
   `TOS_Evidence_Brief` had no repo: initialized and pushed as private `erash11/TOS_Evidence_Brief`.
2. Started the planned GPS move to Windows. Found nothing on Windows had pulled GPS since 09-09.
   Eric reversed: GPS stays on the Mac. Then decided the Mac owns Perch and VALD too - one machine
   runs every pull, so there is never a second writer to a local DuckDB.
3. Windows side switched off: `_INBOX/refresh_all_data.bat` steps 1 (ForcePlate/VALD) and 3 (Perch)
   REM'd, same pattern as GPS step 2. PR _INBOX#3 (Perch, this session), Mac commit 4cb92f7 (VALD).
   Eric then disabled the Task Scheduler task `\Refresh_All_Data` from an elevated shell. PR _INBOX#4
   records it in `_INBOX/docs/STATUS.md`.

## Decisions (with reasoning)

- Mac owns GPS (10:00/16:30), Perch (10:05/16:35, `com.keystone.perchpull`), VALD (10:10/16:40,
  `com.keystone.valdpull`). Reason: two machines each keep a gitignored local DuckDB, so two writers
  drift silently with no conflict ever shown. That is how GPS broke before.
- Windows VALD step was deliberately NOT repointed to `run_pipeline.py` before being REM'd: fixing it
  would have made Windows a second forceplate.db writer.
- VALD client secret rotation: skipped for now (Eric's call, recorded by the Mac in _INBOX STATUS).

## Files created or modified this session

- `DEV/TOS_Evidence_Brief/` - new git repo, pushed (no AGENTS.md / docs/STATUS.md yet; edit guard blocked writing them).
- `DEV/_INBOX/refresh_all_data.bat` - Perch step REM'd, GPS comment corrected, ForcePlate note (PR #3, merged).
- `DEV/_INBOX/docs/STATUS.md` - Perch done, Drive-backup gotcha (PR #3); task disabled (PR #4, merged cb68e2e).
- `DEV/DataBase_GPS_Reporting/gps_report/data/gps_history.duckdb` - Mac DB copied in (SHA afc5bbae..., gitignored, inert; nothing writes it).
- `DEV/DataBase_GPS_Reporting/gps_report/data/backups/gps_history_windows-stale_2026-08-01.duckdb` - old Windows copy moved aside.
- This handoff.

## Next actions

1. `TOS_Evidence_Brief`: run `/new-project` in it to add AGENTS.md + docs/STATUS.md.
2. `DEV/AthleticMedicineReviews/` holds only `Report_help.zip` (dropped 09-21), no repo. Eric decides; may be health data - do not push unseen.
3. Google Drive for Desktop backs up all of `C:\Users\eric_rash\Desktop\DEV` (3.1 GB in `.tmp.driveupload`). Less risky now Windows writes no DuckDBs; still Eric's call whether to keep it. It likely also holds the leftover `.claude/worktrees/*` folders open (git "Permission denied" on delete) in `_INBOX` and `DataBase_GPS_Reporting` - delete them once Drive lets go.
4. Settings: an `autoMode.allow` rule so `gh pr merge` inside compound commands is not blocked was refused as self-modification. `permissions.allow` already has `Bash/PowerShell(gh pr merge *)`, which works for standalone merge commands. Eric adds the autoMode rule himself if wanted.
5. Rotate the VALD client secret when convenient (exposed in VALD_analytics git history).

## Mid-flight

Nothing. Global MEMORY.md was rewritten by the Mac session (it owns the VALD line at its closeout).

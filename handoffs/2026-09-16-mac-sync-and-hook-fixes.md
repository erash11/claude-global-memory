# 2026-09-16 (Mac, evening) — dev-sync and three hook-failure fixes

## What this was
Eric ran `/dev-sync` on the Mac, then worked through what it surfaced: two stale
`.from-windows` merge blocks and the three hook failures in `.errors.log`.

## Done
- **dev-sync.** Config, skills (+`research-in-5`), and global-memory pulled and pushed.
  `Weekly_Research_Review` merged twice from Windows (3, then 4 commits). No conflicts, no
  clones. The "missing" GitHub repos already exist under other folder names:
  `AppliedPerformance-Site` = `~/DEV/Website`, `Linda_Projects` = `~/DEV/Linda Projects`,
  `AI_Analyst` = `~/DEV/_ARCHIVE/AI_Analyst`. Do not clone them.
- **sleep-scheduler/AGENTS.md.** Fixed 10 CP1252-mojibake em-dashes (`734856d`), targeted
  replace only because the file also held correct dashes and arrows. Removed the stale
  9/9 `.from-windows` block, which was the only place the "Paused design interview" text
  lived, and the matching STATUS to-do (`110f295`).
- **memsearch-sync crash.** Not a broken install. The session ended during a restart
  (crash 07:46:41, reboot 07:46:56); macOS refuses to dlopen libraries once shutdown starts
  ("system is shutting down"), and memsearch rewords that as "requires onnxruntime, pip
  install". Hook now treats that as transient and logs the first `Error:` line plus the
  log path instead of the first 300 chars (`~/.claude` commit `2ed1e54`). The Codex copy is
  a symlink, so both harnesses have it. Verified on the real crash log and a real run.
- **gps-pull network error.** Not Catapult, DNS, or code. Mac asleep on battery at 06:30;
  launchd ran the job during 2-second DarkWakes with no Wi-Fi. Recovered by running
  `pull.sh`: 2 imported (09-15, 09-16), 0 errors, coach reports built. Gotcha written into
  `DataBase_GPS_Reporting/docs/STATUS.md` (`9ae7f5d`); empty `.from-windows` block removed
  there too (`63dc43d`).
- **.errors.log** archived to `transcripts/errors-archive-2026-09-16.log` (all 5 lines
  explained and resolved) and reset to empty.

## Decisions
- Do not lengthen the Catapult client's 2/4/8s retry backoff: it would freeze across sleeps
  too and delay real-outage alerts.
- Old real-itinerary times stay in sleep-scheduler git history (Eric, earlier today).

## Open — Eric's call
1. Wake the Mac for the 06:30 pull? `sudo pmset repeat wakeorpoweron MTWRFSU 06:28:00`
   with the Mac plugged in overnight (recommended), or accept one alert on lid-shut mornings.
2. Rotate the Catapult token (carried over).

## Files changed
- `~/DEV/sleep-scheduler/AGENTS.md`, `~/DEV/sleep-scheduler/docs/STATUS.md`
- `~/.claude/hooks/memsearch-sync.js` (also live at `~/.codex/hooks/memsearch-sync.js` via symlink)
- `~/DEV/DataBase_GPS_Reporting/docs/STATUS.md`
- `~/DEV/DataBase_GPS_Reporting/coach_report/Reports/coach/2026-09-15/`, `.../2026-09-16/`
  (coach_report.html + .pdf, generated, not tracked) and `gps_report/data/gps_history.duckdb`
- `~/.claude/global-memory/MEMORY.md` (GPS line), `transcripts/.errors.log`,
  `transcripts/errors-archive-2026-09-16.log`, this handoff

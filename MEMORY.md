<!-- Cap: 2,500 chars. Working scratchpad; writes take effect next session. -->
# Working Memory

## Active Threads
- **Prioritization slate (9/14)**: LIVE, 5/5 (Fall). →Tier A prioritization-slate
- **Status report**: #3 by 9/25, biweekly to 12/18. →Tier A supervisor-log-pipeline
- **Personal site (9/2)**: NEXT: phone check; host or local? →Tier A personal-site-build-routes
- **RTP CLA (9/10)**: NEXT: .ris → Zotero; lesson 0002. →Tier A rtp-cla
- **ATH Tech**: shipped; ITS pending; run 9/29. →Tier A tech-inventory-refresh
- **Data pulls (9/21)**: Mac owns GPS/Perch/VALD (10:00-10:10, 16:30-16:40); Win writers off. →`DataBase_GPS_Reporting/docs/`
- **FB matchups (9/13)**: EPA = PFF; CFBD PPA cross-check. TRAP: `run_direction` != point of attack
- **PP Recruiting (9/22)**: 011 awaits Eric/staff; Jev pilot on draft PR #2, shadow only. →`PP_Recruiting/docs/`
- **Sleep scheduler (9/16)**: R1 merged. NEXT: night/early-kickoff itineraries. →`sleep-scheduler/`
- **RI5 #002 (9/21)**: v2 on Drive. NEXT: Eric sends `_v2` only.
- **TypeSafe (9/22)**: shadow gate log-only Win, review ~10/6; meeting→project tag shipped; spring traj failed. NEXT: Eric Y/Ns 22 surgeries (#21). →`TypeSafe_Sandbox/docs/`
- **PFF DB (9/22)**: 2026 thru wk3. Machines swap Parquet on Drive, never the DB: Mac loaded. BUG: load wipes local-only premium rows (restored). No load/2024-25 export till fixed. →`PFF_Data_Project/docs/`

## Environment Notes
- Hooks: patch both copies only for shared events; Codex has no prompt-submit event. →Tier A hook-two-copies-trap.
- daily-backup: manifest entries copy nothing alone; sweep nested `~/.claude` repos. →handoff 2026-09-19-backup-divergence-fix.
- `DEV/Linda Projects` = private I-983 repo; folder has a space, repo an underscore.
- `~/DEV` = THIN repo; `.gitignore` starts `/*` — never remove. →Tier A github-consolidation.
- Win: `Desktop\DEV` syncs via Drive (robocopy retired 9/22). No large DBs/junctions: renv via `RENV_PATHS_LIBRARY_ROOT`, PFF via `PFF_DB`. Stale `.git/worktrees`: read-only, then `Remove-Item -Force`.
- Stack doctor: both machines. Schedules →automation-cadence. CFB capture →cfb-forecast-capture. Portfolio dashboard →command-centre.
- **Mac TODO (9/22)**: `git pull` in `~/.claude/claude-memory-compiler` + `~/.claude/skills`, then delete this line.

## Pending Decisions
- **OKR gate (scored 9/14)**: AI integration buy-in + data governance (Anthony). Fold into NCAA charter or park?
- **Kitman vs MyLink**: MyLink (~half cost) + Kitman API. Blocks priority 3.

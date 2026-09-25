<!-- Cap: 2,500 chars. Working scratchpad; writes take effect next session. -->
# Working Memory

## Active Threads
- **Prioritization slate (9/14)**: LIVE, 5/5. →Tier A prioritization-slate
- **Status report**: #3 by 9/25, biweekly to 12/18. →Tier A supervisor-log-pipeline
- **Personal site (9/2)**: NEXT: phone check; host or local? →Tier A personal-site-build-routes
- **RTP CLA (9/10)**: NEXT: .ris → Zotero; lesson 0002. →Tier A rtp-cla
- **ATH Tech**: shipped; ITS pending; run 9/29. →Tier A tech-inventory-refresh
- **Machine split (9/24)**: Win=day, Mac=eve. Mac sole writer GPS/Perch/VALD → Parquet `athlete-snapshots/` on Drive; backup 21:00; nudges on Win. →handoff 2026-09-24-machine-split
- **FB matchups (9/23)**: EPA = PFF via `scripts/pff_epa_profile.py`. Wk4 COLO: EPA layer only, full profile? →`MatchupAnalysis_FB2026/docs/`
- **PP Recruiting (9/22)**: 011 awaits Eric/staff; Jev pilot on draft PR #2, shadow only. →`PP_Recruiting/docs/`
- **Sleep scheduler (9/16)**: R1 merged. NEXT: night/early-kickoff itineraries. →`sleep-scheduler/`
- **RI5 #002 (9/21)**: v2 on Drive. NEXT: Eric sends `_v2` only.
- **TypeSafe (9/22)**: shadow gate log-only Win, review ~10/6; spring traj failed. NEXT: Eric Y/Ns 22 surgeries (#21). →`TypeSafe_Sandbox/docs/`
- **PFF DB (9/22)**: Swap Parquet on Drive, never the DB (`load_snapshot.py`, PK merge since PR #4). Both machines: 2026 thru wk3 + video plays. →`PFF_Data_Project/docs/`

## Environment Notes
- Hooks: patch both copies only for shared events; Codex has no prompt-submit event. →Tier A hook-two-copies-trap.
- daily-backup: manifest entries copy nothing alone; sweep nested `~/.claude` repos. →handoff 2026-09-19-backup-divergence-fix.
- `DEV/Linda Projects` = private I-983 repo; folder has a space, repo an underscore.
- `~/DEV` = THIN repo; `.gitignore` starts `/*` — never remove. →Tier A github-consolidation.
- Win: `Desktop\DEV` syncs via Drive (robocopy retired 9/22). No large DBs/junctions: renv via `RENV_PATHS_LIBRARY_ROOT`, PFF via `PFF_DB`.
- Schedules →automation-cadence. CFB capture: Mac only →cfb-forecast-capture. Portfolio dashboard →command-centre.

## Pending Decisions
- **OKR gate (scored 9/14)**: AI integration buy-in + data governance (Anthony). Fold into NCAA charter or park?
- **No Kitman vs Myelin decision**: never real. Vendor is Myelin (startup AMS), not pursued. Kitman stays; don't resurface (9/24).

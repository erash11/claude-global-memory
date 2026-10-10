# Handoff: work-laptop restore (2026-10-10)

## What this was about
Restoring what lived only on the Baylor Windows laptop (BU-1979FJ4). The laptop is now hands-off: all 17 scheduled tasks are disabled. Plan: `My Drive/_FROM_WORK_LAPTOP/HANDOFF.md`, vault note `~/SecondBrain/Projects/work-laptop-handoff-2026-10-08.md`.

## Done
- Memory: Tier A `project_work-laptop-hands-off.md` written and pushed (dotclaude). Tier B line updated.
- To-do 1: four big DEV folders on Drive match the laptop (2 Mac `.DS_Store` extras only). Whole-DEV size count was started and never finished. The 2.8 GB gap is still unexplained.
- global-memory transcript merge (`transcripts/2026-10-08.md`) resolved on the Mac and pushed. Windows copy kept beside it as `transcripts/2026-10-08.from-windows.md`.

## In flight (paused)
- Unzip of `claude.zip` into `~/Restore/work-laptop-2026-10-08/claude/` (no-overwrite flag). Stopped with SIGSTOP at about 40k of 61,774 files. PID 12215. Resume: `kill -CONT 12215`. It is slow because the zip is read from Google Drive.
- A second unzip of the same zip into `~/handoff-staging/` (PID 16536) is NOT ours. It was paused by mistake and could not be resumed. Resume only after confirming who started it: `kill -CONT 16536`.
- `~/.claude` was NOT touched by any unzip. Do not unzip over it.

## Next
1. Decide on the paused unzips (resume 12215; check 16536).
2. To-do 2 remainder: review the extracted `claude/.claude` tree before any merge into `~/.claude`.
3. To-do 3: copy `pff-data\pff.db` to local disk; point `PFF_DB` at it. Never open a DB inside Drive.
4. To-do 4: merge Windows memory from `claude.zip` (`projects/C--Users-eric-rash-Desktop-DEV*/memory`, `global-memory`, compiler `daily`/`knowledge`). Use the dev-sync no-overwrite rule: save the Windows copy beside the Mac copy.
5. Rotate exposed keys (GitHub PAT, Gmail app password, Fireflies, TypeSafe).

## Open
- AI_Analyst (`~/DEV/_ARCHIVE/AI_Analyst`): submodule pointer change left local. Repo is archived on GitHub (403 on push).
- Registry drift (14 items from `portfolio.py crosswalk`): stray DEV folders with no row (WashingtonWebPage, Wilhelm_Brody_RTP, indiana-fever-schedule, LibraryProject/ZoteroInjestion, Linda Projects); rows pointing at missing folders (Linda_Projects, MatchupAnalysis_FB2026, PlayerPersonel, claude-global-memory); Drive projects with no row (_ACTIVE/2026-03-26_DexaProject, _STALLED/2026_Scouting_Academy, _STALLED/LinkedIn_Dash_Idea).
- 7-day rule, 4 projects on the clock, need a step 1: NCAA_BestPractices_Doc (1 day), HPI_Protocol (2), Education_Curriculum (2), cmj-traffic-light (2).
- Hook failures from 10-08 to 10-09: compiler backlog (5 logs), compiler budget tripped at 1.17M of 600k tokens, claude-files-digest send failed 10-09, memsearch-sync index exit null, gps-pull exit 4 (API listing failed).

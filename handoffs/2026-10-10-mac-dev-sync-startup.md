# Mac dev-sync and startup, 2026-10-10

Machine: Mac (`~/DEV`). Session: `/startup` (dev-sync, then closeout).

## What was done
- Config repos pulled and pushed: `~/.claude` (dotclaude), `~/.claude/skills` (claude-skills), `~/.claude/global-memory`.
- `global-memory` had a merge stopped from an earlier run, on `transcripts/2026-10-08.md`. Kept both sides (log file), removed markers, committed `eebb3b5`, pushed.
- Mods: 10 loaded, 0 disabled, 0 invalid.
- Skills synced to Codex (43 entries).
- Project memory mirror: 15 projects paired, 3 files copied, 2 replaced by newer version, 2 `MEMORY.md` merged. Pushed as `mac memory mirror`.
- Repos checked: 108 local folders. All were clean and pushed before the sync. Pulled `SpecialRequests` (2 commits) and `TOS_Evidence_Brief` (1 commit). No merge conflicts. No `.from-*` files.
- `project-triage/board.py --background` started. URL: http://127.0.0.1:7474/
- `graphify-out` committed and pushed (11 generated files refreshed).
- 7-day rule: 0 paused. 4 on the clock: `NCAA_BestPractices_Doc` (1 day), `HPI_Protocol`, `Education_Curriculum`, `cmj-traffic-light` (2 days each).
- `landed.py scan` ran: 69 entries in the ledger for the last day.

## Decisions
- Did NOT clone the 45 GitHub repos that have no local folder. Eric chose "clone none". Some are retired (`CommandCentre`, `morning-briefing`). `AI_Analyst` is already in `~/DEV/_ARCHIVE`. Many were created on 2026-09-09, the migration day. To clone one later: `gh repo clone erash11/<name> ~/DEV/<name>`.

## Open
- `SportScienceResearchRepo`: another Claude session is working there now, on branch `batch-96-103-staged`. That branch has no upstream and is unpushed. One file is modified (`scripts/haiku-batch/drafting-instructions.md`). Not committed here, on purpose. Batch 96 drafts are in `~/Library/Caches/sportsci-batch-96`. The repo's `master` branch status file is older than the working branch.
- `~/.claude/global-memory/transcripts/.errors.log` is NOT empty. 7 entries:
  - compiler-backlog (5 logs), needs `compile.py` run by hand.
  - compiler-budget-tripped (1 log deferred).
  - claude-files-digest send failed, 2026-10-08 and 2026-10-09. See `~/.claude/scripts/logs/claude-files-digest.log`.
  - memsearch-sync index exit null. See `~/.claude/global-memory/transcripts/.memsearch-index.log`.
  - gps-pull exit 4. See `~/DEV/DataBase_GPS_Reporting/gps_report/logs/last_run.json`.
  - daily-backup at 09:54: `repo-behind-blocked:global-memory`, `repo-diverged:dotclaude`. Both now in sync with origin. Check `~/.claude/scripts/logs/daily-backup.log` to confirm the backup succeeds tonight.
- Registry drift (`portfolio.py crosswalk`): 14 items. Examples: `Football` is not a git repo; `WashingtonWebPage`, `Wilhelm_Brody_RTP`, `indiana-fever-schedule` have no registry row; rows point at missing folders for `Linda_Projects`, `MatchupAnalysis_FB2026`, `PlayerPersonel`, `claude-global-memory`; Drive projects with no row: `_ACTIVE/2026-03-26_DexaProject`, `_STALLED/2026_Scouting_Academy`, `_STALLED/LinkedIn_Dash_Idea`.
- Missing next step: `Website` (worked 2026-10-03, STATUS has no Next).

## Next
1. Decide per item: 4 projects on the 7-day clock (see above).
2. Run `compile.py` by hand to clear the compiler backlog.
3. Check the other session's `batch-96-103-staged` work before the next sync touches `SportScienceResearchRepo`.
4. Optional: clone any of the 45 repos by name.

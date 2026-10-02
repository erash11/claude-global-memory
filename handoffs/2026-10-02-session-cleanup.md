# Handoff — 2026-10-02 — session cleanup, PR merges, "where was I" tooling (Windows)

## What and why
Eric had 79 background sessions on the home screen and kept losing track of where each
project stopped. This session audited every session against every repo, merged all open
PRs, cleaned up merged worktrees and branches, and built the two habits into tools.

## Decisions
- Sessions are scratchpads; the repo (commits + `docs/STATUS.md` `## Next`) is the record.
  Delete a session once its work is committed, pushed and in STATUS. Keep it while it is
  working/blocked, for 24 h after it ends (nightly backup), or while it owns a worktree.
- Delete sessions with `claude rm <id>` (supported CLI; refuses on unpushed work). Never
  `rm` `~/.claude/jobs/` folders by hand.
- Max 5 active threads in global MEMORY.md: Status report, SW/Tech Review, Ship queue,
  PP Recruiting, RTP CLA. The rest are Parked; their NEXT lives in each STATUS.md.
- closeout: `## Next` item 1 must be one concrete action (it is what where-was-i shows).
- Volleyball_GRID fix merged on Eric's go-ahead; Box copy is live, Mike's reply pending.

## Created or modified
- `~/.claude/scripts/where-was-i.py` — first `## Next` item per project, newest first.
- `~/.claude/scripts/session-sweep.py` — KEEP / SAFE TO DELETE / repos with unsaved work.
- `~/.claude/projects/C--Users-eric-rash-Desktop-DEV/memory/feedback_session-hygiene.md` (+ index line).
- `~/.claude/global-memory/MEMORY.md` — 5 active threads, Parked section.
- PRs merged: claude-skills #11, #12; TypeSafe_Sandbox #31, #33; Volleyball_GRID #2;
  ForcePlate_DecisionSystem #5; Kinexon_Volleyball #7; Risk_Stratification_Engine #2;
  Wilhelm_Brody_RTP #1; PP_Recruiting #3; Flint #3; sleep-scheduler #2.
- 19 worktrees + 22 merged branches removed. Gitignored files from them copied into each
  main checkout first (never overwriting); TypeSafe `drive_triage/private/` restored.
- `Kinexon_Volleyball/dashboards/coach-dashboard.from-post-practice-report.html` (differing copy kept).
- 7 handoffs rescued from `%TEMP%` into repo `docs/handoffs/` (Temp originals left in place).
- 4 old sessions deleted with `claude rm` (0ec3aa19, bc406500, 8f18aaef, 6f19cc8c).

## Next
1. Tomorrow: `python ~/.claude/scripts/session-sweep.py`, then `claude rm <id>` for each SAFE id
   (today's 9 sessions become safe after tonight's backup).
2. SW/Tech Review: build the Teams team per `SoftwareTech_Review/docs/TEAMS_PLAN.md` (was due 10/2).
3. Give a `## Next` item to RTP_WorkingGroup, PlayerPersonel, SpecialRequests, Life-OS, TOS_Evidence_Brief.

## Left alone on purpose
Flint `step1-triage` worktree (326 data files not in main), KeystoneOS
`pre-rebase-checkpoint-20260803` (1 unmerged commit), DexaProject (no remote by design),
`~/.claude` stash (settings.json), `_DRIVE/99_UNSORTED/PostGameReport/manifest.json` (untracked).

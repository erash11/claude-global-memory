# Handoff 2026-10-04 (Windows, Sunday): recall-eval fix, files digest, board URL, SSI plan

## What happened and why

1. **Startup sync** (`/startup` → dev-sync). Clean except CATES (draft PR #1's worktree folder, left for Eric). 41 GitHub-only repos are the 10/3 archived set, so not cloned.
2. **Missed scheduled job.** The weekly recall eval (step 2 of `\Eric\memsearch-drain-weekly`) died at 02:10 with 0xC0000142 (DLL init failed; it never ran a line), the same as 10/01. Re-ran by hand: OK.
3. **Fix:** the task now has ONE action, `~/.claude/audits/recall-eval/weekly-chain.ps1`, which runs drain → run-eval → after-run and retries a step that exits 0xC0000142 (4 tries, 30 s apart). Log: `audits/recall-eval/logs/weekly-chain.log`. Verified under Task Scheduler with a test label (all steps exit 0). The probe tasks were deleted.
   - Side finding, **not fixed:** the Milvus container crashed and restarted mid-drain during the test (exit 1, restart count 6, no panic in its logs). Left for the Friday harness slot. That `.errors.log` line is kept on purpose.
   - Side effect: a `chain-test` row was pushed to the recall ledger.
4. **Daily "files Claude created" email** (Eric asked). `\Eric\claude-files-digest`, daily 06:30, emails Eric_Rash@baylor.edu the files added the PREVIOUS day in Claude co-authored commits, across DEV, `~/.claude` and the vault. It fetches and reads `--all`, so Mac pushes count. Flint and SecondBrain are counts only (Eric's choice). Sends via the `gws` CLI. Script `~/.claude/scripts/claude-files-digest.py` (`--date`, `--dry-run`). First scheduled send: 2026-10-05 06:30.
5. **Gmail permission.** Eric approved MCP Gmail / gws sends to himself, at eric.rash11@gmail.com and Eric_Rash@baylor.edu. Others still get drafts. Recorded in Tier A `project_automation-cadence.md`.
6. **Board stable URL** (project-triage `8b7a699`). Port 7474 by default (falls back if taken); token kept in `%LOCALAPPDATA%\pm-board\token` / `~/.config/pm-board/token`. On Windows SO_REUSEADDR is off so a taken port is detected. Purpose: Safari → File → Add to Dock as a Mac app. Phone: no mobile board on purpose; use Claude on the repo.
7. **NCAA_BestPractices_Doc started** (slate 2 of 5, receiver Chris Ruf). Research pass → `docs/SOURCES.md`; plan → `docs/PLAN.md`; 3-page house-style plan → `deliverables/SSI_BestPractices_PLAN_ER_2026-10-04.docx/.pdf` (build `scripts/build_plan.py`). The PDF was emailed to Eric's Outlook.

## Decisions (and why)

- **One chain action, not three, for the weekly task.** A step that fails to start can only be retried from a running parent process. The cause of 0xC0000142 in the overnight session is unknown; it doesn't happen by hand or in a logged-in probe.
- **Digest = git + Claude co-author trailer only.** That is the only reliable attribution. Drive files are not listed. It reports the previous day at 06:30, so Mac evening work is included.
- **Recommendations in the SSI plan:**
  - A best-practices guide plus procedures and forms, not formal policy (the 7/30 preference).
  - The new doc becomes the SoftwareTech framework's "Version 1". The framework covers only SSI Rec 4.
  - The four areas plus a short education section.
  - Staff-transition continuity has no source anywhere and will be original work.

## Files created or changed

- `~/.claude/audits/recall-eval/weekly-chain.ps1` (new), `LATEST.md`, `ledger.md`, `results/2026-10-04-*-weekly.json`, `results/2026-10-04-*-chain-test.json`
- `~/.claude/scripts/claude-files-digest.py` (new)
- `~/.claude/projects/C--Users-eric-rash-Desktop-DEV/memory/project_automation-cadence.md`
- `~/Desktop/DEV/project-triage/`: `board.py`, `tests/test_board_server.py`, `README.md`, `docs/GUIDE.md`, `docs/STATUS.md`, `portfolio.json` (Eric's board edits + NCAA start)
- `~/Desktop/DEV/NCAA_BestPractices_Doc/`: `docs/PLAN.md`, `docs/SOURCES.md`, `docs/STATUS.md`, `scripts/build_plan.py`, `deliverables/SSI_BestPractices_PLAN_ER_2026-10-04.docx/.pdf`
- Task Scheduler: `\Eric\memsearch-drain-weekly` (actions replaced), `\Eric\claude-files-digest` (new)

## Next (most important first)

1. Eric: read `NCAA_BestPractices_Doc/docs/PLAN.md` (or the PDF in Outlook) and book Chris before 10/14.
2. Mac tonight: `git pull` in project-triage, `pm`, then Safari → File → Add to Dock. Plus the existing Mac items in project-triage STATUS.
3. 10/05 06:30: check that the first digest email arrived. If not, see `~/.claude/scripts/logs/claude-files-digest.log`.
4. 10/11 02:00: the first weekly run on the chain. Check `audits/recall-eval/logs/weekly-chain.log` for retries.
5. Friday harness slot: the Milvus mid-drain crash; the slate-check nag that still says "a slot is open" for NCAA_BestPractices_Doc (meta.slate next_up probably still names it).
6. CATES draft PR #1: merge or close (Eric).

## Mid-flight / open

- Board walkthrough steps 1–6 (GUIDE "first 30 minutes") were handed to Eric; not confirmed done.
- Friday sweep (10/09): 84 paused rows; first 10 listed in the session.

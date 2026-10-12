# House model closeout, 2026-10-12


## Landed ledger view

Project_Triage (10)
10-12 08:08  changed              /Users/kristinarash/DEV/project-triage/docs/STATUS.md
10-12 06:21  changed              /Users/kristinarash/DEV/project-triage/portfolio.json
10-11 20:13  changed              /Users/kristinarash/DEV/project-triage/docs/STATUS.md
10-11 20:12  new                  /Users/kristinarash/DEV/project-triage/docs/handoffs/2026-10-11-open-items.md
10-11 20:12  new                  /Users/kristinarash/DEV/project-triage/docs/handoffs/2026-10-11-open-items.md
10-11 20:12  changed              /Users/kristinarash/DEV/project-triage/portfolio.json
10-11 19:58  changed              /Users/kristinarash/DEV/project-triage/crosswalk.py
10-11 19:58  changed              /Users/kristinarash/DEV/project-triage/tests/test_crosswalk.py
10-11 19:58  changed              /Users/kristinarash/DEV/project-triage/crosswalk.py
10-11 19:58  changed              /Users/kristinarash/DEV/project-triage/tests/test_crosswalk.py

(DEV) house-model (12)
10-12 08:08  changed              /Users/kristinarash/DEV/house-model/docs/STATUS.md
10-12 08:08  changed              /Users/kristinarash/DEV/house-model/reports/predictions/2026-wk07.csv
10-12 08:08  changed              /Users/kristinarash/DEV/house-model/reports/backtest.md
10-12 08:08  changed              /Users/kristinarash/DEV/house-model/src/housemodel/cfbd_pull.py
10-12 08:08  changed              /Users/kristinarash/DEV/house-model/.gitignore
10-12 08:08  new                  /Users/kristinarash/DEV/house-model/docs/handoffs/2026-10-12-mac-run-closeout.md
10-12 08:08  new                  /Users/kristinarash/DEV/house-model/docs/handoffs/2026-10-12-mac-setup-week7.md
10-11 22:14  changed              /Users/kristinarash/DEV/house-model/README.md
10-11 22:14  new                  /Users/kristinarash/DEV/house-model/docs/BOOTSTRAP_PROMPT.md
10-11 22:11  new                  /Users/kristinarash/DEV/house-model/docs/USER_GUIDE.md
10-11 21:52  new                  /Users/kristinarash/DEV/house-model/reports/scorecard.md
10-11 21:52  new                  /Users/kristinarash/DEV/house-model/src/housemodel/grade.py


## Final closeout saves

- `/Users/kristinarash/.claude/docs/STATUS.md`
- `/Users/kristinarash/.claude/global-memory/docs/STATUS.md`
- Nested config sweep checked 15 repositories. Only dotclaude and global-memory had changes. A detached temporary job checkout was clean.
- House model pushed at `0edebec`. Project-triage pushed at `90072ba`. Dotclaude saved at `86b454c`.


## Result

House model setup and week 7 passed. Model: blend v2. TCU at Baylor on October 17: Baylor by 4.6, 63% win chance. No live grade yet. CFBD and PFF fields are in the ignored local `.env`. PFF sign-in is untested.

Closeout authorized commit and push. Repo handoff: `/Users/kristinarash/DEV/house-model/docs/handoffs/2026-10-12-mac-setup-week7.md`.

## Checks and issues

- Swept 123 DEV and config repos, including nested repos and worktrees. House model, project-triage, dotclaude, and global-memory required saving. No known CFBD or PFF key values matched the files to stage. No candidate files exceeded 95 MB.
- Archived AI_Analyst had 231 CRLF-only changes. Normalized-byte comparisons passed. Local core.autocrlf=input made the index clean without changing the files or pushing to the third-party remote.
- Seven-day rule: zero paused, zero near the limit.
- Registry drift, report only: house-model has no row; Football/CoachReport_Prototypes has no row; Football/WeeklyCoachReport has no row; Website has no Next step; Wilhelm_Brody_RTP has no Next step.
- Memory entry saved once, within the 2,500-byte cap. Today's transcript exists and was modified at 07:56. Docs harvested from 110 repos. No Tier A memory was written.
- One unresolved compiler-flush-failed log entry: October 12 at 07:31, maximum turns (2). Another save succeeded at 07:31:52. The error was kept. A compiler change is not a quick, proven fix.
- Card check passed: Flint and Project_Triage have no gaps. House model cannot appear on its own card until it has a registry row. Existing project decisions remain in project-triage STATUS. No new model question awaits Eric.
- No model jobs remain running. Wait for Eric before more model work.

## Landed: full file paths

This list combines the closeout Git file inventory with local-only model outputs. The shared landed ledger is `/Users/kristinarash/.claude/global-memory/landed/Kristinas-MacBook.local.jsonl`.

- `/Users/kristinarash/.claude/global-memory/MEMORY.md`
- `/Users/kristinarash/.claude/global-memory/handoffs/2026-10-12-house-model-closeout.md`
- `/Users/kristinarash/.claude/global-memory/landed/Kristinas-MacBook.local.jsonl`
- `/Users/kristinarash/.claude/global-memory/transcripts/.errors.log`
- `/Users/kristinarash/.claude/global-memory/transcripts/.memsearch-last-run`
- `/Users/kristinarash/.claude/global-memory/transcripts/.memsearch-timeout-streak-index-busy-lock-held-`
- `/Users/kristinarash/.claude/global-memory/transcripts/.memsearch-timeout-streak-milvus-unreachable`
- `/Users/kristinarash/.claude/global-memory/transcripts/2026-10-12.md`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/10dc068a-b11a-4acc-861d-dca59a5f6b67.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/527f35c0-1c3c-417a-bc85-1bbfff7f1c05.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/5cbf56f3-a908-4390-bb92-43d092c09625.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/67dec236-2685-4216-84dd-19d55b3bf58c.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/75f4cb83-a397-4b13-b121-e0c000ed7364.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/7efca76d-69c4-4fce-8906-d79dd88ab6c1.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/b3bbb2a2-4d83-413e-91de-e85447f791fb.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/cd267fb3-297b-41f2-a19b-eb69579d9739.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/da1bd06a-9c31-49c8-9f6e-3423e1f1814f.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-claude-memory-compiler/e4df5d4a-6255-40ee-8f86-09cc014e0c35.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash--claude-skills/81275c86-e520-4c3b-b3c1-982adde9baf4.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV-PlayCalls-SuccessRate-EPA/5f2ac916-6e52-43f6-bc78-4e7231c4afa0.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/0bc2c538-9790-43f3-bf93-4c789c9a13da.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/1e065549-abae-46b8-a97c-2985af8af00f.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/343438c1-750d-485d-95ef-df02e10a809b.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/343438c1-750d-485d-95ef-df02e10a809b/subagents/agent-a14410b327e78ee69.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/343438c1-750d-485d-95ef-df02e10a809b/subagents/agent-a14410b327e78ee69.meta.json`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/3494d934-eb42-4fbd-8a67-2b53bd2260ea.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/40af6584-c280-4198-bd2d-21982a9875e7.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/5e347c3c-75e5-4626-9815-84ca8d6240f4.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/624274f9-8197-4e2d-b93e-c2fbe2e410b6.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/788f361d-8aa2-49b2-ba0b-3402ca8b2f41.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/8b21e7a2-457c-482f-8dfd-13e15becbb30.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/91ebb91e-6719-45a0-bf54-2ae963973dc2.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/9ec9717e-c296-45d8-85c7-277bda57c708.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/b8143861-beec-4930-9c27-06bc9d94fa8b.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/b8143861-beec-4930-9c27-06bc9d94fa8b/subagents/agent-a5c3145ddf1f0dffe.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/b8143861-beec-4930-9c27-06bc9d94fa8b/subagents/agent-a5c3145ddf1f0dffe.meta.json`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/b8143861-beec-4930-9c27-06bc9d94fa8b/subagents/agent-aeff0892aa99b2532.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/b8143861-beec-4930-9c27-06bc9d94fa8b/subagents/agent-aeff0892aa99b2532.meta.json`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/bdf500ec-8172-4754-8253-9a35fb88a4d4.jsonl`
- `/Users/kristinarash/.claude/projects/-Users-kristinarash-DEV/bfae0a14-26c6-45c5-87bf-851780b7ca30.jsonl`
- `/Users/kristinarash/DEV/_ARCHIVE/AI_Analyst/ai-analyst/.git/config`
- `/Users/kristinarash/DEV/house-model/.env`
- `/Users/kristinarash/DEV/house-model/.gitignore`
- `/Users/kristinarash/DEV/house-model/.venv/`
- `/Users/kristinarash/DEV/house-model/data/model.duckdb`
- `/Users/kristinarash/DEV/house-model/data/raw/bcftoys_fei_2026_2026-10-12.html`
- `/Users/kristinarash/DEV/house-model/docs/STATUS.md`
- `/Users/kristinarash/DEV/house-model/docs/handoffs/2026-10-12-mac-run-closeout.md`
- `/Users/kristinarash/DEV/house-model/docs/handoffs/2026-10-12-mac-setup-week7.md`
- `/Users/kristinarash/DEV/house-model/reports/backtest.md`
- `/Users/kristinarash/DEV/house-model/reports/predictions/2026-wk07.csv`
- `/Users/kristinarash/DEV/house-model/reports/scorecard.md`
- `/Users/kristinarash/DEV/house-model/src/housemodel.egg-info/`
- `/Users/kristinarash/DEV/house-model/src/housemodel/cfbd_pull.py`
- `/Users/kristinarash/DEV/project-triage/docs/STATUS.md`

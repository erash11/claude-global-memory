# STATUS

## Current state
- 2026-11-06: touched by routine memory work only (transcripts, daily backup, `.errors.log` archived at closeout: two forceplate.db lock errors from 18:10).
- 2026-11-05: Hooks only: today's transcript and the landed ledger. `.errors.log` had 1 entry (performance-snapshot DB lock); archived to `.errors-ledger.log` and cleared in closeout.
- 2026-11-04: daily writes only: today's transcript and the landed ledger (every session). `.errors.log` is empty. Stays archived on the board (it is the memory store, not a project).
- 2026-11-03: touched only by the daily backup (343b7dd, 06:49) and the 06:51 Mac snapshot; transcripts and the landed ledger update every session. Stays archived on the board (it is the memory store, not a project).
- 2026-11-02 (archived on the board; system repo, touched every day by hooks and the backup): `.errors.log` cleared after its 11 lines were traced (aios-audit ran; lost transcripts came from a leaked Terminal, now quit), `63e71df`.
- 2026-10-31: daily writes only: today's transcript, `.errors-ledger.log` (`.errors.log` is empty), the memsearch run stamp, and a `MEMORY.md` working-memory update (Front Burner thread). The registry row stays archived: this repo is plumbing, not a project.
- 2026-10-30: `.errors.log` had 3 daily-backup entries. Cause 1: new folder `~/DEV/_to_delete` was not in the backup manifest (fixed in dotclaude). Cause 2: secret-scan warning on session `b1b9233e…jsonl` was a false hit (split words 'Risk-Stratification', 'one-task-one-agent' in git output). Archived to `.errors-ledger.log` and cleared at 15:31.
- 2026-10-29: routine writes only (today's transcript, landed ledger, memsearch stamp). `.errors.log` was archived to `.errors-ledger.log` and cleared at 15:31.
- 2026-10-19 (offline catch-up closeout): GPS/Perch/VALD pulls re-run, all ok. daily-backup re-run with CRASHBOX: OK, 93 jobs. GPS coach report archived (Eric's call). Error log archived to `transcripts/.errors.log.archived-2026-10-19` and cleared after checking the compiler. USER.md 87%, MEMORY.md 75% after consolidation. Handoff: `handoffs/2026-10-19-offline-catchup-and-coach-archive.md`.
- 2026-10-16 (BayCap development-plan closeout): Updated BayCap memory pointer to the standalone NODAL-style iOS goal; roadmap at BayCap/docs/DEVELOPMENT_PLAN.md is pushed. Account setup remains next. Project handoff and registry aligned. Today's transcript is recent; private histories stay local. Existing backup errors and 4 registry gaps remain open. DEV-only landed refresh used because the Drive mount previously stalled the full scan. This paused repo was touched for closeout maintenance only.
- 2026-10-16 (Phase 2 closeout): CFB review and resume notes are in the repo. The combined branch passed 248 tests. Docs were harvested from 140 repos. Today's transcript is recent. Backup errors remain open. The full ledger scan stalled; a DEV-only refresh captured 480 files. Drive and vault walks remain unchecked. Private transcripts stay local by instruction. This paused repo was touched for closeout records only.
- 2026-10-16 (BayCap closeout): BayCap pointer saved in MEMORY.md (2489 bytes, under 2500); OpenCap installed on both devices, guided account setup next. Handoff in BayCap/docs/handoffs/2026-10-16-baycap-setup.md. Docs harvested from 140 repos. Today's transcript exists and is recent; private transcript content stays local. Existing backup errors remain recorded; registry drift has 4 items, none introduced by BayCap.
- 2026-10-13 final sweep: replay work and PDF recovery are complete, but another Claude session is still writing the next Supertraining batch. Current drafts are checkpointed without review or promotion; full-workspace closeout remains partial until that writer finishes. Private histories remain local by instruction.
- 2026-10-13: Sport Science Network finished: 16 talks, four files per active folder, 64 files verified online; original resources preserved in an archive. Final handoff: `Flint/docs/handoffs/2026-10-13-sport-science-network-final-closeout.md`. Today's transcript exists and is recent. A GPS coach-PDF timeout was recovered by local export retry; original error archived and active error log cleared. Private history remains local under Eric's rule.
- The project remains paused; today's changes are routine handoff, harvest, and ledger maintenance. (Since 2026-10-24 `~/DEV/claude-global-memory` is a symlink to this repo, so there is no second checkout to pull.)
- 2026-10-12 (closeout 2): backup index step ran clean at 18:09 (263 chunks). The only backup error was the manifest entry above, now fixed. Error log archived to `transcripts/.errors.log.archived-2026-10-12b` and cleared. Open items fixed: three archived projects (`project-triage` `af79a87`), 22 dated STATUS lines, `.gitignore` for the stranded flush archive.
- 2026-10-12 (Mac closeout): `MEMORY.md` trimmed from 2438 to 2264 chars (cap 2500). All 5 Active Threads and all 10 Parked items kept; parked lines now carry only the NEXT step and a pointer. `.errors.log` archived to `transcripts/.errors.log.archived-2026-10-12` and cleared. The memsearch index database opens (43,452 chunks, no lock holder), so the rebuild is not needed.
- 2026-10-12: House-model state and handoff saved. MEMORY.md is 2438 bytes. Docs harvested from 110 repos; today's transcript exists. One compiler-flush-failed entry remains. The model's full handoff is `handoffs/2026-10-12-house-model-closeout.md`.
- 2026-10-20: Routine only (Windows). Merged the Mac's transcripts (`.memsearch-last-run` conflict kept the newer local timestamp); PP Recruiting thread line updated; landed ledger and today's transcript pushed. `transcripts/.errors.log` carries 6 Mac session-autopush failures from 05:06 UTC (git-remote-https killed, signal 9).
- 2026-10-11: Nightly backup still fails on `memsearch-index:full-set`. The memory index database is incompatible with Milvus Lite 3.x. Eric chose to wait before rebuilding it. `MEMORY.md` is compressed to 2440 of 2500 chars, so there is only about 60 chars of room. Details: `handoffs/2026-10-11-backup-index-and-memory-cap.md`.
- 2026-10-05: Routine only. The Windows sync merged the Mac's transcripts (`.memsearch-last-run` conflict resolved to the newer timestamp), plus the landed ledger and today's transcript. No project work in this repo.
- 2026-10-04: Routine only: transcripts, landed ledger, a resolved line cleared from `.errors.log`, handoff `handoffs/2026-10-04-windows-recall-digest-ssi-plan.md`. No project work in this repo.
- 2026-09-24: Sportsmith Part 2 video, transcript, and summary are saved in Drive. The automated transcript was compared with Vimeo captions and corrected; a human audio-listening pass remains open.
- This closeout handoff records the workflow, deliverables, and next steps for another harness.

## Next
- Run `launchctl list | grep dailybackup` after tonight's 21:00 run; exit 0 clears stack-doctor `task:com.keystone.dailybackup`.
- Open `/Users/kristinarash/DEV/Flint/docs/handoffs/2026-10-13-sport-science-network-final-closeout.md` for the final four-file layout, archive and resume steps; the existing requested portable processing skill is still pending.
- Create a portable video processing and transcript review skill in the canonical `~/.claude/skills` repo when returning to that task; sync generated Codex and `.agents` views.
- If exact verbatim accuracy is required, listen to ambiguous passages and update the transcript with a human review note.

## Open questions
ANSWERED 2026-10-12: no rebuild. The memsearch database opens and no process holds a lock. The `memsearch-index:full-set` error was stale. The 21:00 nightly backup should clear it. If that run still fails with the Milvus Lite 3.x message, check `lsof +D ~/.memsearch/milvus.db` first, then decide whether to rebuild.

## Gotchas
- The stop hook can add one final transcript entry after closeout.
- Push this repo at closeout so both laptops get the same memory.


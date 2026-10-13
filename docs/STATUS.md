# STATUS

## Current state
- 2026-10-13: Sport Science Network finished: 16 talks, four files per active folder, 64 files verified online; original resources preserved in an archive. Final handoff: `Flint/docs/handoffs/2026-10-13-sport-science-network-final-closeout.md`. Today's transcript exists and is recent. A GPS coach-PDF timeout was recovered by local export retry; original error archived and active error log cleared. Private history remains local under Eric's rule.
- The project remains paused; today's changes are routine handoff, harvest, and ledger maintenance. Pull the separate `~/DEV/claude-global-memory` checkout after this repo is pushed so the board card reads the same STATUS.
- 2026-10-12 (closeout 2): backup index step ran clean at 18:09 (263 chunks). The only backup error was the manifest entry above, now fixed. Error log archived to `transcripts/.errors.log.archived-2026-10-12b` and cleared. Open items fixed: three archived projects (`project-triage` `af79a87`), 22 dated STATUS lines, `.gitignore` for the stranded flush archive.
- 2026-10-12 (Mac closeout): `MEMORY.md` trimmed from 2438 to 2264 chars (cap 2500). All 5 Active Threads and all 10 Parked items kept; parked lines now carry only the NEXT step and a pointer. `.errors.log` archived to `transcripts/.errors.log.archived-2026-10-12` and cleared. The memsearch index database opens (43,452 chunks, no lock holder), so the rebuild is not needed.
- 2026-10-12: House-model state and handoff saved. MEMORY.md is 2438 bytes. Docs harvested from 110 repos; today's transcript exists. One compiler-flush-failed entry remains. The model's full handoff is `handoffs/2026-10-12-house-model-closeout.md`.
- 2026-10-11: Nightly backup still fails on `memsearch-index:full-set`. The memory index database is incompatible with Milvus Lite 3.x. Eric chose to wait before rebuilding it. `MEMORY.md` is compressed to 2440 of 2500 chars, so there is only about 60 chars of room. Details: `handoffs/2026-10-11-backup-index-and-memory-cap.md`.
- 2026-10-05: Routine only. The Windows sync merged the Mac's transcripts (`.memsearch-last-run` conflict resolved to the newer timestamp), plus the landed ledger and today's transcript. No project work in this repo.
- 2026-10-04: Routine only: transcripts, landed ledger, a resolved line cleared from `.errors.log`, handoff `handoffs/2026-10-04-windows-recall-digest-ssi-plan.md`. No project work in this repo.
- 2026-09-24: Sportsmith Part 2 video, transcript, and summary are saved in Drive. The automated transcript was compared with Vimeo captions and corrected; a human audio-listening pass remains open.
- This closeout handoff records the workflow, deliverables, and next steps for another harness.

## Next
- Open `/Users/kristinarash/DEV/Flint/docs/handoffs/2026-10-13-sport-science-network-final-closeout.md` for the final four-file layout, archive and resume steps; the existing requested portable processing skill is still pending.
- Create a portable video processing and transcript review skill in the canonical `~/.claude/skills` repo when returning to that task; sync generated Codex and `.agents` views.
- If exact verbatim accuracy is required, listen to ambiguous passages and update the transcript with a human review note.

## Open questions
ANSWERED 2026-10-12: no rebuild. The memsearch database opens and no process holds a lock. The `memsearch-index:full-set` error was stale. The 21:00 nightly backup should clear it. If that run still fails with the Milvus Lite 3.x message, check `lsof +D ~/.memsearch/milvus.db` first, then decide whether to rebuild.

## Gotchas
- The stop hook can add one final transcript entry after closeout.
- Push this repo at closeout so both laptops get the same memory.


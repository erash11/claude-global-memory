# STATUS

## Current state
- 2026-10-12: House-model state and handoff saved. MEMORY.md is 2438 bytes. Docs harvested from 110 repos; today's transcript exists. One compiler-flush-failed entry remains. The model's full handoff is `handoffs/2026-10-12-house-model-closeout.md`.
- 2026-10-11: Nightly backup still fails on `memsearch-index:full-set`. The memory index database is incompatible with Milvus Lite 3.x. Eric chose to wait before rebuilding it. `MEMORY.md` is compressed to 2440 of 2500 chars, so there is only about 60 chars of room. Details: `handoffs/2026-10-11-backup-index-and-memory-cap.md`.
- 2026-10-05: Routine only. The Windows sync merged the Mac's transcripts (`.memsearch-last-run` conflict resolved to the newer timestamp), plus the landed ledger and today's transcript. No project work in this repo.
- 2026-10-04: Routine only: transcripts, landed ledger, a resolved line cleared from `.errors.log`, handoff `handoffs/2026-10-04-windows-recall-digest-ssi-plan.md`. No project work in this repo.
- 2026-09-24: Sportsmith Part 2 video, transcript, and summary are saved in Drive. The automated transcript was compared with Vimeo captions and corrected; a human audio-listening pass remains open.
- This closeout handoff records the workflow, deliverables, and next steps for another harness.

## Next
- Create a portable video processing and transcript review skill in the canonical `~/.claude/skills` repo; sync generated Codex and `.agents` views.
- If exact verbatim accuracy is required, listen to ambiguous passages and update the transcript with a human review note.

## Open questions
- Rebuild the memsearch index now, or keep waiting? The nightly backup fails on `memsearch-index:full-set` until the index database is rebuilt (Milvus Lite 3.x cannot open the old file). Eric chose to wait on 2026-10-11. The rebuild moves the old `.db` aside, then runs `memsearch index`.
- Video processing skill: recorded as the next requested work item (see Next).

## Gotchas
- The stop hook can add one final transcript entry after closeout.
- Push this repo at closeout so both laptops get the same memory.




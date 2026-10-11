# Handoff: backup index failure and memory cap, 2026-10-11

## What was worked on
- Ran `~/.claude/skills/claude-stack-doctor/scripts/stack-check.ps1` on the Mac. It found 5 issues. Handoff between machines was healthy.
- The nightly backup fails on `memsearch-index:full-set`. The memsearch index database cannot be opened by Milvus Lite 3.x. The error says to move the old `.db` file aside and rebuild with `memsearch index`.
- Eric chose to WAIT on the rebuild (option B). The backup will keep failing each night until it is rebuilt.
- Eric asked for items 4 and 5 to be fixed. Item 4 (git "diverged") is no longer a problem: `~/.claude` is in sync with origin. Item 5 (`MEMORY.md` full) was fixed by compressing the file.

## Decisions
- Option B chosen for the memsearch rebuild (wait). Reason: Eric's choice.
- `MEMORY.md` compressed from 2491 to 2440 chars. No facts were dropped. Live threads and pointers were kept.

## Files changed
- `~/.claude/global-memory/MEMORY.md`: compressed. Verified at 2440 chars.
- `~/.claude/global-memory/docs/STATUS.md`: added the 2026-10-11 entry.
- `~/.claude/global-memory/handoffs/2026-10-11-backup-index-and-memory-cap.md`: this file.
- `~/.claude/global-memory/dev-docs/`: refreshed by the harvest script (108 repos).

## Next actions, most important first
1. Decide whether to rebuild the memsearch index. To rebuild: move the old `.db` file aside (do not delete it), then run `memsearch index`. Read the memory-write / memsearch notes first, because `memsearch index` is destructive.
2. Clear `~/.claude/global-memory/transcripts/.errors.log` after the rebuild. Archive first with `cp`. Use `cp /dev/null` to clear it, not shell redirects.
3. `MEMORY.md` has about 60 chars of room. Move some parked items into their project repos before the next big write.

## Open or mid-flight
- Memory index rebuild: waiting on Eric (option B).
- Registry drift from `portfolio.py crosswalk` (14 items). Not fixed during closeout. See the closeout report.
- 7-day rule: NCAA_BestPractices_Doc (0 days left), HPI_Protocol (1), Education_Curriculum (1), Performance_Playbook (2).

## Gotchas
- `python` is not on PATH on this Mac. Use `python3` (`/opt/homebrew/bin/python3`).
- The `dotclaude` repo lives at `~/.claude`, not `~/.claude/dotclaude`.

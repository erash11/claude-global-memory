# 2026-10-07 — Pocock skills routing; two Windows failures diagnosed (Mac)

## What and why
1. Eric asked the agent to learn the mattpocock-skills plugin (1.3.1) and defer to it.
2. Eric asked to fix the two hook failures in `.errors.log` (memsearch-sync, nightly-digest).
   Both turned out to be Windows-side; neither can be fixed from the Mac.
3. Both were queued for the Friday harness slot.

## Decisions (with reasoning)
- **Pocock skills win on overlap.** Saved as Tier A feedback memory. A later session the same day
  widened it ("default all the mattpocock skills"): overlapping superpowers/anthropic skills are
  now "off" in settings.json, and `mattpocock-skills:code-review` is ON.
- **memsearch failure is Windows, not Mac.** The `.errors.log` tracebacks show
  `C:\Users\eric_rash\...`; `.errors.log` syncs between machines. The Mac uses embedded Milvus
  Lite and is healthy (search OK; hook index 10:54 "Indexed 110 chunks"; streak file cleared).
  Windows runs Milvus in Docker; `milvus-standalone` was down ~4 h on 10-06 and also restarted on
  its own on 10-04, so it recurs.
- **nightly-digest is Windows-only** (new on 10-06; first run failed). The real stderr is only in
  the Windows log `~\.claude\scripts\logs\nightly-digest.log`. gws send flags and `-a` attachment
  verified with `--dry-run` on the Mac. Most likely cause: gws auth on Windows.
- `.errors.log` was NOT cleared: the causes are unconfirmed and the file syncs (a Mac truncate can
  clobber a Windows write).

## Files created or modified
- `~/.claude/projects/-Users-kristinarash-DEV/memory/feedback_defer-to-mattpocock-skills.md` (new)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/MEMORY.md` (index line)
- `~/.claude/HARNESS_FIXES.md` (items 9 and 10; dotclaude commit `c338868`)
- `~/.claude/docs/STATUS.md`
- this handoff

## Next
1. On Windows: read `Get-Content ~\.claude\scripts\logs\nightly-digest.log -Tail 5`
   (HARNESS_FIXES #10).
2. On Windows: `docker ps`, `curl http://localhost:9091/healthz` (HARNESS_FIXES #9).
3. Clear `.errors.log` once both are confirmed fixed.

## Mid-flight
- Waiting on the Windows nightly-digest log line to pick the fix.

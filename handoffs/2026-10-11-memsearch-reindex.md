# Handoff 2026-10-11 — memsearch reindex (Mac)

## What happened
- Full memsearch index failed nightly since 10-10 with a Milvus Lite 3.x incompatibility error.
- Fix taken: moved the old database aside, NOT deleted:
  `~/.memsearch/milvus.db` -> `~/.memsearch/milvus.db.broken-2026-10-11`
  Older backups still present: `milvus.db.pre-3x-2026-10-10`, `milvus.db.bak-2026-10-10`.
- Full rebuild over the 12 existing declared folders (codex memories folder absent on Mac, skipped).
  - Run 1: killed (exit 143) after ~6 h. Index held 33,561 chunks, NOT confirmed complete.
  - Run 2: failed at start, Milvus Lite lock held. No holder found on recheck.
  - Run 3: started at close; check its output file for the result.

## Open
- Confirm the index is complete: a run that finishes with no error and a stable chunk count.
- Daily-backup and .errors.log still show `memsearch-index:full-set` until a clean full run.
- Still open from the errors log: claude-files-digest send failure (10-09), compiler flush
  failure (10-10; check claude-memory-compiler sdk version if it repeats).

## Gotchas
- `memsearch index` deletes indexed sources outside the paths it is given. Always pass the full declared set.
- The dcg guard blocks `mv` on home paths and redirects to home paths. Run those by hand, not via the agent.

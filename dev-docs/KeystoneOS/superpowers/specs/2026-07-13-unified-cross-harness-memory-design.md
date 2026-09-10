# Unified Cross-Harness Memory Design

## Goal

Eric works across Claude Code and Codex (both terminal-based), with occasional
work in Antigravity (out of scope this round). He wants to open any tool and
have it already know about everything he's working on: all projects, ideas,
meetings, and past conversations, without re-explaining context or manually
choosing which memory system to query.

## Context and existing infrastructure

This is not a build-from-zero request. Investigation before this design found
a substantial existing stack:

- **Frozen snapshot (inject):** `~/.claude/global-memory/USER.md` + `MEMORY.md`,
  2,500-char cap, injected silently at Claude session start.
- **Curated writes (store):** the `memory-write` skill — dedups, respects the
  cap, triggered by "remember this" etc.
- **Full capture (store):** `claude-memory-compiler`'s SessionEnd/PreCompact
  hooks write daily distilled logs (`~/.claude/claude-memory-compiler/daily/`),
  present back to 2026-04-14.
- **Semantic recall:** `memsearch` (PyPI, v0.4.3) — a real, already-running,
  self-hosted stack: Milvus 2.6.4 in Docker, local ONNX bge-m3 embeddings, no
  external API or subscription. Callable as a plain CLI from any harness.
  Config already has separate `plugins.claude-code` / `plugins.codex` /
  `plugins.opencode` sections. Auto-reindexed after every Claude session by
  `~/.claude/hooks/memsearch-sync.js`.
- **Codex bridge:** KeystoneOS already ships `scripts/codex-hooks/` (
  `session-start.ps1`, `pre-compact.ps1`, `stop.ps1`) plus a fast/broad scoped
  memory retrieval command (`keystone.ps1 memory <terms> -Scope fast|broad`).
- **Meetings:** the `meeting-sync` skill pulls Fireflies transcripts into
  `SecondBrain/Inbox/meetings/` as structured markdown, idempotent via a state
  file.

## The actual gap

`memsearch`'s indexed corpus — the thing that makes cross-conversation recall
work — is incomplete, not broken:

1. **Codex is entirely absent from the corpus.** Codex's own memory
   (`~/.codex/memories/MEMORY.md`, `memory_summary.md`, `rollout_summaries/`)
   is never passed to `memsearch index`, and nothing runs indexing after a
   Codex session ends. Claude has no way to semantically recall anything
   Codex-side, and vice versa.
2. **Meetings are absent from the corpus.** `SecondBrain/Inbox/meetings/` is
   not in `memsearch-sync.js`'s indexed path list (only
   `SecondBrain/Knowledge/library` is).
3. **Meeting sync is manual/on-demand only,** so even what has been captured
   lags behind what Fireflies has actually recorded.
4. **The session-start snapshot is per-tool, not unified.** Claude's
   SessionStart injects Claude's own snapshot; Codex's SessionStart reads
   Claude's compiler context one-directionally. Neither tool shows "what
   happened everywhere" at a glance.

Closing these four points, not replacing any working system, satisfies the
goal.

## Decisions (confirmed with Eric during brainstorming)

- **Shared read layer, not single source of truth.** Each tool keeps writing
  to its own native memory (Claude's compiler, Codex's own memory files).
  Nothing changes about how either harness persists memory internally. What's
  shared is (a) the semantic index both can query and (b) a generated
  snapshot both inject at session start.
- **Antigravity is out of scope this round** — revisit once its extensibility
  model (hooks/rules-file/MCP) is confirmed.
- **Meeting sync runs on the daily morning cadence automatically**, not
  on-demand and not on every session start.

## Design

### 1. Shared corpus path config (new)

New file: `data/memory-index-paths.json` in KeystoneOS. Single source of
truth for "what belongs in the semantic corpus" — both the existing Claude
hook and the new Codex hook read from it instead of hardcoding their own
path list (today only `memsearch-sync.js` hardcodes one; a second hardcoded
list would silently drift from it over time).

```json
{
  "paths": [
    "~/.claude/global-memory/transcripts",
    "~/.claude/projects/C--Users-eric-rash/memory",
    "~/.claude/claude-memory-compiler/daily",
    "~/.claude/claude-memory-compiler/knowledge",
    "~/Desktop/SecondBrain/Knowledge/library",
    "~/Desktop/SecondBrain/Inbox/meetings",
    "~/.codex/memories"
  ]
}
```

`memsearch-sync.js` changes from a hardcoded `PATHS` array to reading and
resolving this file (`~` expansion, existence filtering unchanged).

### 2. Codex-side auto-index hook (new)

New `scripts/codex-hooks/memsearch-sync.ps1`, invoked from the existing
`stop.ps1` bridge after it writes its event breadcrumb. Mirrors
`memsearch-sync.js`'s already-debugged pattern rather than reinventing it:

- Reads the same `data/memory-index-paths.json`, filters to paths that exist.
- Acquires an atomic lock file (`New-Item -ItemType File` with exclusive
  create semantics) before indexing; skips if a fresh lock already exists;
  reclaims stale locks (>30s old) the same way `memsearch-sync.js` does.
- Runs `memsearch index <paths>` **synchronously** with a bounded timeout
  (45s internal, hook-level timeout above that) — the JS hook's own history
  shows detached/fire-and-forget indexing is unreliable on Windows here; do
  not repeat that mistake on the Codex side.
- Logs errors to `~/.claude/global-memory/transcripts/.errors.log` (the same
  file Claude's hook already uses) rather than failing the Codex `Stop`
  event. A missing/unreachable Milvus (Docker down) is a logged, non-fatal
  condition — Codex's session still ends normally.
- Confirms the Windows codepage env vars (`PYTHONIOENCODING=utf-8`,
  `PYTHONUTF8=1`) are present before invoking `memsearch`; these are already
  set at the user level per existing memory
  (`project_memsearch_setup.md`), so this is a check, not a new requirement.

### 3. Meeting sync on the morning cadence

The existing `meeting-sync` skill's steps (refresh Fireflies DB, list recent
transcripts, detect generic titles, export new ones, augment with the
structured header) get invoked as a step in KeystoneOS's morning routine,
before the unified snapshot generation step (#4) — so same-day meetings are
present in the corpus before the snapshot that summarizes "recent activity"
is built. No change to `meeting-sync`'s own logic or its idempotency
(state-file-based skip of already-exported transcripts) — only where it's
triggered from.

### 4. Unified snapshot generator (new)

New `keystone.ps1 snapshot` command (or folded into the existing `morning`
command as an additional step — implementation plan decides which fits
better given `morning`'s current structure). Produces one capped markdown
artifact, e.g. `outputs/dashboard/unified-snapshot.md`, with fixed sections:

- Recent Claude activity (last N days from `claude-memory-compiler/daily/`)
- Recent Codex activity (last N days from Codex's `memory_summary.md` /
  `rollout_summaries/`)
- Recent meetings (last N days from `SecondBrain/Inbox/meetings/`)
- Active project / pending decision highlights (from the existing project
  registry and `decisions/log.md`)

Same "frozen until next regeneration" philosophy as the existing Tier B
snapshot: capped size, regenerated once per morning-cadence run, not
regenerated on every session start (keeps session start fast and the
in-session picture stable).

### 5. Injection into both tools

- **Claude Code:** `settings.json` supports multiple `SessionStart` hooks.
  Add a second hook (do not touch the memory-compiler's existing one) that
  reads and injects `unified-snapshot.md` silently, same style as the
  existing frozen-snapshot injection (no greeting, no recap).
- **Codex:** `scripts/codex-hooks/session-start.ps1` already has a slot for
  "Claude memory compiler startup context, when available." Extend that slot
  to read the same `unified-snapshot.md` file, so both tools show the
  identical cross-harness picture.

### 6. Failure handling

- Milvus/Docker unreachable at index time: logged, non-fatal, session
  continues on native per-tool memory only (today's behavior).
- Snapshot file missing or stale (morning cadence didn't run): both
  SessionStart hooks fall back silently to each tool's own native snapshot —
  never block a session start on the unified layer.
- Ripgrep/memsearch missing entirely: consistent with the existing fast/broad
  memory retrieval contract (fails closed with an actionable message when
  invoked directly; background hooks log and skip rather than surfacing an
  error to the user).

## Verification

- After implementation, end a Codex session and confirm `memsearch stats`
  chunk count increases; `memsearch search "<phrase used only in that Codex
  session>"` returns a hit.
- Run meeting-sync (or wait for the morning cadence) and confirm a
  meeting-only fact is returned by `memsearch search`.
- Open a fresh Claude Code session and a fresh Codex session same-day;
  confirm both show the same unified snapshot content.
- Kill Docker (simulate Milvus down), confirm both `Stop` hooks and both
  `SessionStart` hooks complete without error or block.

## Out of scope this round

- Antigravity integration (revisit once its extensibility model is known).
- Consolidating `memsearch` with the `context-mode` MCP plugin's own
  session-scoped search — they serve different purposes (context-mode is a
  Claude-only in-session cache; memsearch is the persistent cross-harness
  corpus) and both continue to coexist.
- Migrating either harness's native memory format to a single store (ruled
  out — shared read layer was the chosen model, not single source of truth).

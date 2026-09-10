# agy Memory Bridge — Design Spec

**Date:** 2026-06-22
**Status:** Approved for implementation
**Author:** Eric (via Claude brainstorm)

## Problem

Eric has started using the Antigravity CLI (`agy`) as a coding/agent harness alongside
Claude Code and Codex. Conversations there generate context that should flow into the
existing second-brain + memory-compiler infrastructure, the same way Claude and Codex
sessions already do. Today nothing captures agy work.

## Goal

Make agy conversation context **(a)** searchable via `keystone.ps1 memory` and
**(b)** distilled into the Claude memory-compiler daily knowledge pipeline — without
modifying or depending on the lifecycle of `agy` itself.

## Key facts discovered (do NOT re-derive — and do NOT try to parse the `.db` files)

### agy CLI data store: `C:\Users\eric_rash\.gemini\antigravity-cli\`
- **`history.jsonl`** — the clean, reliable surface. One JSON object per line:
  ```json
  {"display":"<the user prompt text>","timestamp":1781288810029,"workspace":"C:\\...","conversationId":"fe77fca1-..."}
  ```
  - `timestamp` is epoch **milliseconds**.
  - Some early lines have **no `conversationId`** (pre-conversation REPL input) — bucket those under a synthetic id `_loose` or skip; do not crash on missing key.
- **`conversations/<conversationId>.db`** — full transcript, but stored as **Protocol Buffer blobs inside SQLite** (tables: `trajectory_meta`, `steps`, `gen_metadata`, …). Decoding requires an undocumented `.proto` schema. **We deliberately do NOT read these.** They are mentioned only so the implementer does not waste effort here.
- **`brain/<conversationId>/`** — scratch files `agy` generated while working (e.g. `summarize_shortcut_locations.py`). Use the **file listing** (names + sizes + mtimes) as the per-conversation artifact manifest. Do not parse contents.
- **`settings.json`** — has no `hooks` key. `agy` exposes **no lifecycle hook**, which is why capture is pull-based.

### Existing KeystoneOS infra to integrate with
- **`data/memory-sources.json`** — registry of queryable sources. Each entry: `{key,name,path,queryable,priority,globs,description}`. Read by `Get-MemorySources` (keystone.ps1 ~line 95) and searched by `Show-Memory`. Glob-based; only matches the listed globs (e.g. `*.md`).
- **`scripts/keystone.ps1`** — command dispatcher.
  - `param()` has a `[ValidateSet(...)]` for `$Command` (**line 3**) — new commands must be added here or they are rejected.
  - `switch ($Command)` dispatch block (**~line 2668**) maps command → function.
  - `$DryRun` switch and `$Rest` array params already exist.
- **Claude memory compiler:** `C:\Users\eric_rash\.claude\claude-memory-compiler\`
  - Entry point for ingestion: `scripts/flush.py`, invoked as:
    ```
    uv run --directory <compiler-root> python scripts/flush.py <context_file.md> <session_id>
    ```
  - `flush.py` reads the markdown context, distills it via the Claude Agent SDK, **appends** to `daily/<YYYY-MM-DD>.md`, and auto-triggers `compile.py` after 18:00 local.
  - **Critical:** its only dedup is "same `session_id` within 60 seconds." It will NOT prevent re-ingesting the same conversation across sync runs. **Idempotency is `agy-sync`'s responsibility** via a watermark.
- **Codex bridge** is the analog precedent: `docs/codex-memory-bridge.md`, hooks in `scripts/codex-hooks/`, breadcrumbs under `outputs/codex-hooks/` (git-ignored dir, tracked-but-empty). Mirror its conventions and operating rules.

## Operating contract (from AGENTS.md — non-negotiable)
- **Read** agy's store; **never write** into `~/.gemini/antigravity-cli/`.
- KeystoneOS produces only its **own derived artifacts**.
- Do not overwrite Claude/Codex/SecondBrain memory from this bridge.

## Design

### Component 1 — Capture store (derived artifact)
- Directory: `outputs/agy/` (inside KeystoneOS).
- `outputs/agy/conversations/<conversationId>.md` — one digest per conversation:
  - **Header:** conversation ID, workspace path(s), first/last activity (ISO local), prompt count, artifact count.
  - **Prompts:** chronological list of user prompts (the `display` field) with local timestamps.
  - **Artifact manifest:** files under `brain/<conversationId>/` — name, size, mtime.
- Markdown so `keystone.ps1 memory` (glob `*.md`) can grep it.

### Component 2 — `agy-sync` command
- New file `scripts/agy-sync.ps1` containing an `Invoke-AgySync` function (dot-sourced or pasted into keystone.ps1 — match how existing commands are organized; most logic lives inline in keystone.ps1, so add `Invoke-AgySync` there and keep any heavy helpers in `scripts/agy-sync.ps1` if cleaner).
- Wire-up in `keystone.ps1`:
  1. Add `"agy-sync"` to the `[ValidateSet(...)]` at line 3.
  2. Add `"agy-sync" { Invoke-AgySync }` to the `switch ($Command)` block (~line 2668).
- Behavior:
  1. Read `history.jsonl`; group entries by `conversationId` (missing → `_loose`).
  2. Load watermark `outputs/agy/.sync-state.json` = `{ "<conversationId>": <lastSeenTimestampMs>, ... }`.
  3. For each conversation whose max prompt `timestamp` > stored watermark (or new):
     - (Re)write its digest `.md` under `outputs/agy/conversations/`.
     - **Compiler feed:** build a temp context `.md` (prompts as `**User:** …` lines + an artifact-manifest note) and invoke `flush.py` with `session_id = agy-<conversationId>`. Locate the compiler root from `data/memory-sources.json` (`claude_memory_compiler` path) — do not hardcode if avoidable.
     - Advance that conversation's watermark to the max timestamp seen.
  4. Write watermark back.
- **Idempotent:** no conversation past its watermark ⇒ no digest writes, no `flush.py` calls.
- **Resilient:** wrap the `flush.py` invocation in try/catch — a failure (e.g. compiler venv down, a known past failure mode) is logged to `outputs/agy/agy-sync.log` and must NOT abort the digest writes or watermark update for the searchable layer. (Consider: only advance the watermark for the *digest* unconditionally, but if you want the compiler to retry on next run when flush failed, track a separate `lastFlushed` timestamp. Implementer's choice — document whichever is chosen.)
- Honor `-DryRun`: print what would be written/flushed, change nothing.

### Component 3 — Source registration
Add to `data/memory-sources.json`:
```json
{
  "key": "agy_cli",
  "name": "Antigravity CLI (agy)",
  "path": "C:\\Users\\eric_rash\\Desktop\\DEV\\KeystoneOS\\outputs\\agy\\conversations",
  "queryable": true,
  "priority": 88,
  "globs": ["*.md"],
  "description": "Antigravity CLI (agy) conversation digests: user prompts + artifact manifests per conversation, derived by 'keystone.ps1 agy-sync'."
}
```

### Component 4 — Scheduling
- `scripts/install-agy-sync-task.ps1`: registers a **Windows Task Scheduler** job running
  `keystone.ps1 agy-sync` every ~6 hours. Mirror `scripts/install-codex-hooks.ps1`
  conventions: **dry-run by default**, `-Apply` to commit, idempotent re-install (remove/replace
  any prior KeystoneOS agy task), print the resulting command for review.
- Opportunistic call: add a single `Invoke-AgySync` call into the `Show-Morning` path
  (keystone.ps1) so a morning run also refreshes agy context. Safe because idempotent.
  Wrap in try/catch so a sync failure never breaks `morning`.
- On-demand: `.\scripts\keystone.ps1 agy-sync`.

### Component 5 — Docs & router
- New `docs/agy-memory-bridge.md` mirroring `docs/codex-memory-bridge.md`: what agy gives,
  where breadcrumbs land (`outputs/agy/`), the pull-based/no-hook rationale, the scheduled
  heartbeat, and the read-only operating rule.
- Update `AGENTS.md`:
  - Add a "Where things live" row: `agy CLI memory bridge | docs/agy-memory-bridge.md, scripts/agy-sync.ps1`.
  - Add `agy-sync` to the `Commands` line.
- Keep `CLAUDE.md`/`GEMINI.md` thin (no change needed unless a pointer helps).

### Component 6 — gitignore
Follow the codex-hooks pattern in `.gitignore` so the dir is tracked-but-empty and contents ignored:
```
!outputs/agy/
outputs/agy/**
```
(Add a tracked `outputs/agy/.gitkeep` or short README if needed so the dir exists on clone.)

## Testing
- `tests/agy-sync.ps1` (match the style of `tests/codex-hooks.ps1`). Against a temp fixture
  `history.jsonl` + fake `brain/<id>/` dir (point the script at a fixture root via a parameter
  or env override — do NOT touch the real `~/.gemini` store in tests):
  1. First run produces expected digest `.md` with prompts + manifest; watermark file written.
  2. Second run with no new data is a **no-op** (no new digest writes, no flush invocation —
     stub/mock the flush call so tests don't require the compiler).
  3. A new prompt appended ⇒ only that conversation re-digested and re-flushed.
  4. Missing `conversationId` handled without error.

## Verification (per verification/default-checklist.md)
1. Run `.\scripts\keystone.ps1 agy-sync` once → digests appear under `outputs/agy/conversations/`.
2. `.\scripts\keystone.ps1 memory <term-from-a-real-prompt>` returns the agy hit.
3. A new entry appears in `~/.claude/claude-memory-compiler/daily/<today>.md`.
4. Re-run `agy-sync` → no-op (no new digests, no new daily entry).
5. `.\scripts\install-agy-sync-task.ps1` (dry-run) prints the intended scheduled task.
6. `tests/agy-sync.ps1` passes.

## Known tradeoff (accepted)
Fidelity is **prompts + artifact manifest**, not assistant text (the assistant side lives only
in the protobuf `.db`, which we chose not to decode for robustness). Daily-log entries for agy
work therefore describe *what was asked and what was produced*, not the agent's reasoning.

## Out of scope
- Decoding the agy trajectory protobuf / full assistant-text reconstruction.
- The Antigravity **IDE** (separate trajectory store in `state.vscdb`); this bridge covers the **CLI** only.
- SecondBrain vault synthesis notes (can be added later as a third destination layer).

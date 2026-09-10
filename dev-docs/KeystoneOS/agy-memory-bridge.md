# agy Memory Bridge

The agy memory bridge gives the Antigravity CLI (`agy`) a small, reliable adapter into KeystoneOS and the existing Claude memory infrastructure, the same way the Codex bridge does for Codex.

It does not replace Claude Code hooks, Claude memory compiler, Codex memories, Obsidian, SecondBrain, or Graphify. KeystoneOS remains the cross-harness control plane that points each agent to the right source of truth.

## Why Pull-Based

`agy`'s `settings.json` has no `hooks` key — it exposes no lifecycle hook to call out on session start/stop the way Claude Code and Codex do. Capture is therefore pull-based: KeystoneOS reads agy's own on-disk history on a schedule (or on demand) instead of being notified by agy itself.

## What agy Gives

agy's data store lives at `C:\Users\eric_rash\.gemini\antigravity-cli\`:

- `history.jsonl` — one JSON object per line: `{"display": "<prompt>", "timestamp": <epoch ms>, "workspace": "<path>", "conversationId": "<uuid>"}`. This is the clean, reliable surface agy-sync reads. Some early lines have no `conversationId` (pre-conversation REPL input); these are bucketed under a synthetic `_loose` conversation rather than skipped or crashed on.
- `conversations/<conversationId>.db` — the full transcript, but stored as Protocol Buffer blobs inside SQLite with an undocumented schema. **The bridge deliberately does not read these.** Fidelity is therefore prompts plus an artifact manifest, not assistant reasoning — see "Known Tradeoff" below.
- `brain/<conversationId>/` — scratch files agy generated while working. The bridge lists this directory recursively (names, sizes, modification times) as a per-conversation artifact manifest; it does not parse file contents.

## What KeystoneOS Produces

`keystone.ps1 agy-sync` (function `Invoke-AgySync`, core logic in `scripts/agy-sync.ps1`) derives:

- `outputs/agy/conversations/<conversationId>.md` — one digest per conversation: header (workspace, first/last activity, prompt count, artifact count), the chronological list of user prompts with local timestamps, and the artifact manifest. This file is what `keystone.ps1 memory` searches (registered as the `agy_cli` source in `data/memory-sources.json`).
- A feed into the Claude memory compiler: for each conversation with new activity, agy-sync builds a temporary context markdown (`**User:** ...` lines plus an artifact note) and invokes `flush.py` with `session_id = agy-<conversationId>`, so agy work lands in the daily knowledge log alongside Claude and Codex sessions.
- `outputs/agy/.sync-state.json` — the watermark file that makes repeated runs idempotent (see below).
- `outputs/agy/agy-sync.log` — append-only log of flush attempts/failures.

All of this is KeystoneOS's own derived artifact. The bridge only **reads** `~/.gemini/antigravity-cli/`; it never writes there.

## Idempotency: Watermark, Not Compiler Dedup

`flush.py`'s own dedup only suppresses a duplicate flush for the *same* `session_id` within 60 seconds — it does **not** prevent re-ingesting the same conversation across separate sync runs (e.g. one run per scheduled trigger, hours apart). Idempotency is therefore agy-sync's own responsibility, tracked per conversation in `outputs/agy/.sync-state.json`:

```json
{
  "<conversationId>": { "lastSeen": <epoch ms>, "lastFlushed": <epoch ms> }
}
```

- `lastSeen` advances whenever a conversation's digest is (re)written — this only depends on `history.jsonl`, so it is always safe to advance once the digest reflects the latest prompt.
- `lastFlushed` advances **only on a successful `flush.py` invocation**. If the compiler is unavailable (e.g. its venv is down — a known past failure mode), the digest is still written and the watermark for search still advances, but `lastFlushed` stays behind. The next sync run will retry the flush for that conversation (since `maxTimestamp > lastFlushed`) without re-writing or re-searching anything that hasn't changed.

A conversation with no new prompts past its watermark causes no digest write and no flush call on the next run.

## Scheduling

- On-demand: `.\scripts\keystone.ps1 agy-sync` (supports `-DryRun`, which prints what would be written/flushed and changes nothing).
- Opportunistic: `morning` (and therefore `today`) calls `Invoke-AgySync` as part of its startup, wrapped in try/catch so a sync failure never breaks the morning report.
- Scheduled heartbeat: `scripts\install-agy-sync-task.ps1` registers a Windows Task Scheduler job that runs `keystone.ps1 agy-sync` roughly every 6 hours. Dry-run by default; pass `-Apply` to actually register it. Re-running the installer is idempotent — it removes and replaces any prior KeystoneOS agy task rather than stacking duplicates.

```powershell
.\scripts\keystone.ps1 agy-sync
.\scripts\keystone.ps1 agy-sync -DryRun
.\scripts\install-agy-sync-task.ps1
.\scripts\install-agy-sync-task.ps1 -Apply
```

## Known Tradeoff (Accepted)

Fidelity is prompts plus artifact manifest, not assistant text — the assistant side of a conversation lives only in the protobuf `.db` files, which the bridge chose not to decode for robustness (undocumented schema, high churn risk). Daily-log entries for agy work describe *what was asked and what was produced*, not the agent's reasoning.

## Operating Rule

Keep the bridge narrow:

- Read agy's history and brain artifacts; never write into `~/.gemini/antigravity-cli/`.
- Write only KeystoneOS's own derived artifacts under `outputs/agy/`.
- Do not overwrite Claude memory, Codex memory, SecondBrain, or Obsidian from this bridge.
- Use `keystone.ps1 memory` for search and `agy-sync` for the heavier sync/flush work.

## Out of Scope

- Decoding the agy trajectory protobuf / full assistant-text reconstruction.
- The Antigravity **IDE** (a separate trajectory store in `state.vscdb`); this bridge covers the **CLI** only.
- SecondBrain vault synthesis notes (a possible third destination layer, not built here).

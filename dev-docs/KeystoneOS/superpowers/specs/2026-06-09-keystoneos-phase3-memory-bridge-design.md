# KeystoneOS Phase 3 Memory Bridge Design

## Purpose

Phase 3 upgrades KeystoneOS memory lookup from raw source listing to a usable cross-harness memory bridge.

The system should help any coding harness quickly retrieve relevant retained context from Claude memory, Codex memory, SecondBrain, and related markdown sources without mutating those systems.

## User Experience

```powershell
.\scripts\keystone.ps1 memory FaceComps
.\scripts\keystone.ps1 memory "Fall Camp"
.\scripts\keystone.ps1 memory "Risk Stratification"
```

When a query is provided, KeystoneOS should:

1. Search configured memory sources.
2. Rank results by source priority, term coverage, exact phrase hits, and recency.
3. Print the top results.
4. Generate a memory packet under `outputs/memory/`.

The memory packet is a temporary handoff artifact that can be pasted or referenced in Claude Code, Codex, Gemini, or other tools.

## Data Model

`data/memory-sources.json` is the machine-readable memory registry.

Each source has:

- key
- name
- path
- queryable
- priority
- globs
- description

Markdown remains the initial target because all current durable sources expose useful markdown files.

## Ranking

Initial scoring is deterministic:

- source priority
- exact phrase hit bonus
- number of query terms present
- recency bonus from file last-write time

This is not semantic search yet. It is an intentionally simple bridge that produces evidence-linked context.

## Non-Goals

- No vector database.
- No LLM-generated summary.
- No writes into Claude memory, Codex memory, or SecondBrain.
- No background sync.

## Verification

- PowerShell parser check.
- JSON parse check for `data/memory-sources.json`.
- Run `memory FaceComps`.
- Run `memory "Fall Camp"`.
- Confirm memory packet is created and ignored by git.
- Confirm output contains file paths and line numbers.


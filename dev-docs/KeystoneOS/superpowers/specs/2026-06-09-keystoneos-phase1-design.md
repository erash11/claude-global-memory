# KeystoneOS Phase 1 Design

## Purpose

Phase 1 turns KeystoneOS from a static operating repo into a usable daily command center.

The MVP already established the control-plane shape. Phase 1 makes it useful at workstation startup by adding structured project data and read-only commands that report live state from projects, memory sources, and Graphify registries.

## Design

KeystoneOS remains a small repo. It should not ingest or duplicate full project files. It reads canonical project locations and emits lightweight status reports.

The core source for project automation is `data/projects.json`. Markdown files remain the human-facing briefs.

```text
data/projects.json            machine-readable registry
projects/registry.md          human-readable registry
projects/active/*.md          human resume briefs
scripts/keystone.ps1          local command entrypoint
outputs/morning/*.md          generated daily reports, gitignored
```

## Commands

`.\scripts\keystone.ps1 morning`

Creates a dated morning report under `outputs/morning/` and prints the same high-level status to the terminal.

`.\scripts\keystone.ps1 projects`

Lists structured project keys, status, canonical path, and whether the path exists.

`.\scripts\keystone.ps1 resume <key>`

Prints the project brief and live git/path status.

`.\scripts\keystone.ps1 health`

Checks KeystoneOS, memory source paths, SecondBrain, Graphify registry, and project paths.

`.\scripts\keystone.ps1 memory [query]`

Without a query, lists memory sources and freshness. With a query, searches selected markdown memory sources with `rg` when available.

`.\scripts\keystone.ps1 graphify`

Shows graphify registry entries and usage policy.

## Verification

Phase 1 is verified by:

- PowerShell parser check for `scripts/keystone.ps1`.
- Running `morning`, `projects`, `resume FaceComps`, `health`, `memory`, and `graphify`.
- Confirming the morning report file is generated and remains ignored by git.
- Confirming no canonical external project files are modified.

## Non-Goals

- No dashboard UI yet.
- No background watcher yet.
- No memory writes from KeystoneOS yet.
- No Graphify regeneration from Phase 1 commands yet.
- No mutation of Claude or Codex memory systems.


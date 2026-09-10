# KeystoneOS Phase 4 Workspace Inventory Design

## Purpose

Phase 4 confirms KeystoneOS is not limited to the seeded active-project list.

The active registry is a curated operating list. Workspace inventory is the broad capture layer. It scans configured local roots and produces a generated map of project candidates, including dormant, archived, experimental, and not-yet-registered work.

## User Experience

```powershell
.\scripts\keystone.ps1 inventory
.\scripts\keystone.ps1 inventory -Limit 50
```

The command should:

1. Read configured roots from `data/discovery-roots.json`.
2. Scan project-like directories to a bounded depth.
3. Detect signals such as git repos, README files, AGENTS/CLAUDE/GEMINI adapters, Graphify output, package/config files, and docs.
4. Print a compact inventory summary.
5. Write generated markdown and JSON inventory files under `outputs/inventory/`.

## Architecture

```text
data/discovery-roots.json          configured scan roots
scripts/keystone.ps1               inventory command
outputs/inventory/YYYY-MM-DD.md    generated human inventory
outputs/inventory/YYYY-MM-DD.json  generated machine inventory
```

## Relationship To Active Projects

- `data/projects.json`: active or important projects KeystoneOS should know how to resume.
- `outputs/inventory/`: broad generated scan of project candidates.

Inventory output can be used to decide which projects deserve active briefs later.

## Non-Goals

- Do not automatically add every scanned folder to `data/projects.json`.
- Do not mutate external repos.
- Do not run Graphify automatically.
- Do not recursively scan dependency/vendor folders.

## Verification

- PowerShell parser check.
- JSON parse check for `data/discovery-roots.json`.
- Run `inventory -Limit 20`.
- Confirm generated markdown and JSON inventory files exist.
- Confirm generated inventory files are ignored by git.


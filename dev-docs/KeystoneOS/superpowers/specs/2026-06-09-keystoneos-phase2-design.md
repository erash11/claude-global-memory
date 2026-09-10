# KeystoneOS Phase 2 Design

## Purpose

Phase 2 makes KeystoneOS easier to use at the workstation. Phase 1 can report active projects and memory paths. Phase 2 adds project switching, start packets, status summaries, and VS Code task entrypoints.

## User Experience

The desired morning flow is:

```powershell
.\scripts\keystone.ps1 morning
.\scripts\keystone.ps1 status
.\scripts\keystone.ps1 start FaceComps
.\scripts\keystone.ps1 open FaceComps
```

`start <ProjectKey>` creates a generated project start packet under `outputs/start/`. The packet contains the canonical path, git state, startup checks, brief content, and suggested next commands. It is intentionally generated and ignored by git.

`open <ProjectKey>` opens the canonical project folder in VS Code when the `code` command is available. If `code` is unavailable, it opens the folder in Explorer and prints the path.

## Command Additions

- `status`: compact view of all active projects with path and git state.
- `start <key>`: generate a start packet for a project.
- `open <key>`: open a project folder.
- `where <key>`: print a project canonical path.

## Launcher Integration

Add `.vscode/tasks.json` with commands for:

- KeystoneOS morning startup
- KeystoneOS health
- KeystoneOS status
- Resume FaceComps

These tasks are intentionally simple and local. They make KeystoneOS easy to run from VS Code without adding background daemons.

## Non-Goals

- No automatic background scheduling yet.
- No mutation of external project repos.
- No automatic Graphify runs yet.
- No memory writes yet.

## Verification

Phase 2 is verified by:

- PowerShell parser check.
- Running `status`, `where FaceComps`, `start FaceComps`, and `open FaceComps -WhatIf` equivalent behavior through a dry-run flag.
- Confirming generated start packets are ignored.
- Confirming `.vscode/tasks.json` is valid JSON.


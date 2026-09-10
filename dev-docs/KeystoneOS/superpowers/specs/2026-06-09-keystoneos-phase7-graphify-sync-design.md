# KeystoneOS Phase 7 Graphify Sync Design

## Purpose

KeystoneOS needs a controlled bridge between active projects, repo-local Graphify outputs, and the Obsidian vault. The bridge should prepare each project for Graphify without dumping generated graph material into the wrong vault location or running expensive extraction automatically.

## Approach

Add a `keystone graphsync` command. The command reads active projects from `data/projects.json`, selects projects with `obsidianGraphPath`, creates those Obsidian-facing folders, writes a `GRAPHIFY_SYNC.md` manifest in each folder, and updates `graphify/registry.md`.

`graphsync` is setup-only. It does not run `/graphify`, call the Graphify package, or generate graph data. The manifest provides the exact command to run later.

## Command Behavior

```powershell
.\scripts\keystone.ps1 graphsync
.\scripts\keystone.ps1 graphsync FaceComps
```

- With no project key, sync all active projects that have `obsidianGraphPath`.
- With a project key, sync that project only.
- Skip projects without an Obsidian Graphify path.
- Keep repo-local graph outputs at `<project>\graphify-out`.
- Keep Obsidian-facing files under `C:\Users\eric_rash\Desktop\SecondBrain\Projects\Graphify\<ProjectKey>`.

## Manifest

Each Obsidian folder gets a `GRAPHIFY_SYNC.md` file containing:

- project key and name
- canonical project path
- repo-local `graphify-out` path
- Obsidian graph folder path
- suggested `/graphify` command
- sync notes and boundaries

## Verification

- A temp-fixture integration test should prove `graphsync <ProjectKey>` creates the Obsidian folder.
- The test should prove the manifest includes canonical path, graphify output path, and suggested command.
- The test should prove `graphify/registry.md` gets a row for the project.
- A live dry run should show which active projects will sync.

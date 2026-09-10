# KeystoneOS Phase 7 Graphify Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a setup command that links active KeystoneOS projects to controlled Obsidian Graphify folders and keeps the Graphify registry current.

**Architecture:** Extend `scripts/keystone.ps1` with a `graphsync` command. The command reuses `Get-Projects`, creates per-project Obsidian folders, writes `GRAPHIFY_SYNC.md` manifests, and upserts rows in `graphify/registry.md`.

**Tech Stack:** PowerShell, JSON, Markdown, Git.

---

### Task 1: Graphsync Test

**Files:**
- Create: `tests/keystone-graphsync.ps1`

- [x] Create a temporary KeystoneOS fixture.
- [x] Seed one active project with `canonicalPath` and `obsidianGraphPath`.
- [x] Seed a basic `graphify/registry.md`.
- [x] Run `keystone graphsync ActiveProject`.
- [x] Assert the Obsidian graph folder exists.
- [x] Assert `GRAPHIFY_SYNC.md` exists.
- [x] Assert the manifest includes canonical path, graphify output path, and `/graphify`.
- [x] Assert `graphify/registry.md` includes the active project row.

### Task 2: Graphsync Command

**Files:**
- Modify: `scripts/keystone.ps1`

- [x] Add `graphsync` to the command set.
- [x] Implement project selection by key or all eligible projects.
- [x] Create Obsidian Graphify folders.
- [x] Write project manifests.
- [x] Upsert Graphify registry rows.
- [x] Support `-DryRun`.

### Task 3: Documentation

**Files:**
- Modify: `README.md`
- Modify: `graphify/README.md`
- Modify: `graphify/registry.md`
- Create: `workflows/graphify-sync.md`

- [x] Add `graphsync` to quick start commands.
- [x] Explain setup versus extraction.
- [x] Document where Obsidian graph folders live.

### Task 4: Verify and Ship

- [x] Run parser check.
- [x] Run JSON parse checks.
- [x] Run `tests/keystone-graphsync.ps1`.
- [x] Run `tests/keystone-intake.ps1`.
- [x] Run `tests/keystone-promotion.ps1`.
- [x] Run live `.\scripts\keystone.ps1 graphsync -DryRun`.
- [x] Run live `.\scripts\keystone.ps1 graphsync`.
- [x] Run `git diff --check`.
- [x] Commit with message `feat: add KeystoneOS graphify sync`.
- [x] Push to `origin/main`.

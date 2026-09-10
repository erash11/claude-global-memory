# KeystoneOS Phase 5 Project Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a promotion path that turns generated inventory candidates into active KeystoneOS projects with durable resume behavior.

**Architecture:** Extend `scripts/keystone.ps1` with a `promote` command. The command resolves a literal path or unique inventory candidate, appends a project record to `data/projects.json`, creates a starter active brief, and keeps `projects/registry.md` aligned.

**Tech Stack:** PowerShell, JSON, Markdown, Git.

---

### Task 1: Promotion Test

**Files:**
- Create: `tests/keystone-promotion.ps1`

- [x] Create a temporary KeystoneOS fixture.
- [x] Copy the real CLI script into the fixture.
- [x] Assert promotion writes `data/projects.json`.
- [x] Assert promotion creates `projects/active/<ProjectKey>.md`.
- [x] Assert promotion appends the registry row.
- [x] Assert `-DryRun` leaves `data/projects.json` unchanged.

### Task 2: Promote Command

**Files:**
- Modify: `scripts/keystone.ps1`

- [x] Add `promote` to the command set.
- [x] Add named options for `-ProjectKey`, `-Name`, and `-Status`.
- [x] Resolve literal paths and unique inventory names.
- [x] Generate safe project keys.
- [x] Append to `data/projects.json`.
- [x] Create the active brief.
- [x] Append the registry row.

### Task 3: Documentation

**Files:**
- Modify: `README.md`
- Modify: `projects/registry.md`
- Modify: `outputs/README.md`
- Create: `workflows/project-promotion.md`

- [x] Add the promotion command to quick start docs.
- [x] Explain inventory versus active registry promotion.
- [x] Document the daily project-promotion workflow.

### Task 4: Verify and Ship

- [x] Run parser check.
- [x] Run promotion integration test.
- [x] Run inventory smoke check.
- [x] Run promotion dry run against a real discovered project.
- [x] Commit with message `feat: add KeystoneOS project promotion`.
- [x] Push to `origin/main`.

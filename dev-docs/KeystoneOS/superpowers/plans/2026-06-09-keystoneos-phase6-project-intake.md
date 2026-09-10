# KeystoneOS Phase 6 Project Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only project intake packet that organizes all discovered projects into active, candidate, watch, and review buckets.

**Architecture:** Extend `scripts/keystone.ps1` with an `intake` command that reuses `New-WorkspaceInventory`, classifies each item, writes markdown and JSON to `outputs/intake/`, and prints a concise summary. Add one integration test that runs against a temporary KeystoneOS fixture.

**Tech Stack:** PowerShell, JSON, Markdown, Git.

---

### Task 1: Intake Test

**Files:**
- Create: `tests/keystone-intake.ps1`

- [x] Create a temporary KeystoneOS fixture with copied `scripts/keystone.ps1`.
- [x] Seed one active project in `data/projects.json`.
- [x] Seed one high-signal unregistered code project.
- [x] Seed one SecondBrain-style project note.
- [x] Run `keystone intake -Limit 10`.
- [x] Assert markdown and JSON intake outputs exist.
- [x] Assert the active project is bucketed as `active`.
- [x] Assert the high-signal folder is bucketed as `daily_candidate`.
- [x] Assert the project note is bucketed as `knowledge_candidate`.
- [x] Assert `data/projects.json` is unchanged.

### Task 2: Intake Command

**Files:**
- Modify: `scripts/keystone.ps1`

- [x] Add `intake` to the command set.
- [x] Add `outputs\intake` path.
- [x] Implement bucket classification.
- [x] Implement promotion command recommendations.
- [x] Write markdown and JSON packets.
- [x] Print counts and top candidates.

### Task 3: Documentation

**Files:**
- Modify: `README.md`
- Modify: `outputs/README.md`
- Modify: `workflows/project-promotion.md`
- Create: `workflows/project-intake.md`

- [x] Add `intake` to quick start commands.
- [x] Document output location.
- [x] Explain the difference between inventory, intake, and promote.

### Task 4: Verify and Ship

- [x] Run parser check.
- [x] Run JSON parse checks.
- [x] Run `tests/keystone-intake.ps1`.
- [x] Run `tests/keystone-promotion.ps1`.
- [x] Run `.\scripts\keystone.ps1 intake -Limit 20`.
- [x] Run `git diff --check`.
- [x] Commit with message `feat: add KeystoneOS project intake`.
- [x] Push to `origin/main`.

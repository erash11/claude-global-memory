# KeystoneOS Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make KeystoneOS usable as a daily startup and project-resume command center.

**Architecture:** Add a structured project registry in JSON and extend the PowerShell helper with read-only commands for morning startup, project state, memory source freshness, and Graphify registry review. Generated morning reports go under gitignored `outputs/morning/`.

**Tech Stack:** Markdown, JSON, PowerShell, Git.

---

### Task 1: Add Structured Project Registry

**Files:**
- Create: `data/projects.json`
- Modify: `.gitignore`

- [x] Add project metadata for current active projects.
- [x] Keep paths local and explicit.
- [x] Ensure generated reports stay ignored.

### Task 2: Upgrade Keystone Helper

**Files:**
- Modify: `scripts/keystone.ps1`

- [x] Load `data/projects.json`.
- [x] Add `health`, `memory`, and `graphify` commands.
- [x] Make `morning` generate a dated report.
- [x] Make `resume` include live path/git state.

### Task 3: Verify Phase 1

**Files:**
- Generated only: `outputs/morning/YYYY-MM-DD.md`

- [x] Run PowerShell parser check.
- [x] Run `morning`.
- [x] Run `projects`.
- [x] Run `resume FaceComps`.
- [x] Run `health`.
- [x] Run `memory`.
- [x] Run `graphify`.
- [x] Confirm generated reports are ignored.

### Task 4: Commit and Push

**Files:**
- Commit all tracked Phase 1 changes.

- [x] Commit with message `feat: add KeystoneOS phase 1 operating commands`.
- [x] Push to `origin/main`.

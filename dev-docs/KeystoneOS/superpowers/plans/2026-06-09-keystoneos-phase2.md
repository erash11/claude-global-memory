# KeystoneOS Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add workstation-friendly project switching, status, generated start packets, and VS Code task entrypoints.

**Architecture:** Extend `scripts/keystone.ps1` with read-mostly commands using `data/projects.json`. Generated project start packets go to gitignored `outputs/start/`. VS Code tasks call the existing PowerShell helper.

**Tech Stack:** PowerShell, JSON, Markdown, VS Code tasks, Git.

---

### Task 1: Extend Output Ignore Rules

**Files:**
- Modify: `.gitignore`

- [x] Ignore generated start packets under `outputs/start/`.

### Task 2: Add Project Switching Commands

**Files:**
- Modify: `scripts/keystone.ps1`

- [x] Add `status`.
- [x] Add `where`.
- [x] Add `start`.
- [x] Add `open`.
- [x] Add `-DryRun` for open/start safety checks.

### Task 3: Add VS Code Tasks

**Files:**
- Create: `.vscode/tasks.json`

- [x] Add task for morning startup.
- [x] Add task for health.
- [x] Add task for status.
- [x] Add task for FaceComps start packet.

### Task 4: Update Documentation

**Files:**
- Modify: `README.md`
- Create: `workflows/workstation-startup.md`

- [x] Document the new daily command flow.
- [x] Explain generated start packets.

### Task 5: Verify and Ship

- [x] Run parser check.
- [x] Run `status`.
- [x] Run `where FaceComps`.
- [x] Run `start FaceComps`.
- [x] Run `open FaceComps -DryRun`.
- [x] Validate `.vscode/tasks.json` parses as JSON.
- [x] Confirm generated start packet is ignored.
- [x] Commit with message `feat: add KeystoneOS workstation commands`.
- [x] Push to `origin/main`.

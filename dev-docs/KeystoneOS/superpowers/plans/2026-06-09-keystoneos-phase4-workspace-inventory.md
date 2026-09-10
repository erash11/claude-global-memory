# KeystoneOS Phase 4 Workspace Inventory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add workspace discovery so KeystoneOS can see all project candidates, not only curated active projects.

**Architecture:** Add `data/discovery-roots.json` for configured scan roots. Extend `scripts/keystone.ps1` with an `inventory` command that scans bounded directory trees, detects project signals, prints a summary, and writes ignored markdown/JSON inventory outputs.

**Tech Stack:** PowerShell, JSON, Markdown, Git.

---

### Task 1: Add Discovery Roots

**Files:**
- Create: `data/discovery-roots.json`
- Modify: `.gitignore`

- [x] Add DEV root with bounded depth.
- [x] Add SecondBrain Projects root with bounded depth.
- [x] Ignore generated inventory outputs.

### Task 2: Implement Inventory Command

**Files:**
- Modify: `scripts/keystone.ps1`

- [x] Add `inventory` to the command set.
- [x] Load discovery roots from JSON.
- [x] Scan bounded directory trees while skipping vendor/generated folders.
- [x] Detect project signals.
- [x] Write markdown and JSON inventory outputs.

### Task 3: Document Inventory Layer

**Files:**
- Modify: `README.md`
- Modify: `projects/registry.md`
- Modify: `outputs/README.md`

- [x] Explain active registry versus generated inventory.
- [x] Document the inventory command.

### Task 4: Verify and Ship

- [x] Run parser check.
- [x] Parse `data/discovery-roots.json`.
- [x] Run `inventory -Limit 20`.
- [x] Confirm generated inventory files exist.
- [x] Confirm generated inventory files are ignored.
- [x] Commit with message `feat: add KeystoneOS workspace inventory`.
- [x] Push to `origin/main`.

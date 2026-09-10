# KeystoneOS MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first usable local KeystoneOS control-plane repo and push it to a private GitHub repository.

**Architecture:** KeystoneOS is a small operating repo that references canonical project, memory, Graphify, and Obsidian sources rather than duplicating them. Harness-specific files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) all point back to the same operating policy.

**Tech Stack:** Markdown, PowerShell, Git, GitHub CLI.

---

### Task 1: Scaffold Operating Repo

**Files:**
- Create: `README.md`
- Create: `AGENTS.md`
- Create: `CLAUDE.md`
- Create: `GEMINI.md`
- Create: `.gitignore`

- [x] Create the local repo skeleton under `C:\Users\eric_rash\Desktop\DEV\KeystoneOS`.
- [x] Add cross-harness operating instructions.
- [x] Add a README with MVP purpose and quick start.

### Task 2: Seed Registries and Workflows

**Files:**
- Create: `context/*.md`
- Create: `projects/registry.md`
- Create: `projects/active/*.md`
- Create: `memory/*.md`
- Create: `graphify/*.md`
- Create: `connections.md`
- Create: `workflows/*.md`
- Create: `verification/*.md`

- [x] Seed active project briefs from retained memory and live workspace paths.
- [x] Define memory source policy.
- [x] Define Graphify export policy.
- [x] Add morning startup, project resume, end-of-day capture, weekly audit, and level-up workflows.

### Task 3: Add PowerShell Helper

**Files:**
- Create: `scripts/keystone.ps1`

- [x] Add `morning`, `projects`, and `resume` commands.
- [x] Keep command behavior read-only.

### Task 4: Initialize Git and Push Private

**Files:**
- Modify: git metadata only.

- [x] Run `git init`.
- [x] Commit the MVP scaffold.
- [x] Create a private GitHub repo.
- [x] Push `main`.

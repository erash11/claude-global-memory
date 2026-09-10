# Codex Memory Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Windows-safe Codex hook bridge that injects KeystoneOS context and records Codex lifecycle events.

**Architecture:** Implement small PowerShell hook adapters under `scripts/codex-hooks/`, a backup-safe installer under `scripts/`, and end-to-end script tests under `tests/`. Keep KeystoneOS as the control plane and treat Claude/Codex memory stores as read-only inputs.

**Tech Stack:** PowerShell, JSON, Markdown, Codex hooks, KeystoneOS registries.

---

### Task 1: Test Hook Boundaries

**Files:**
- Create: `tests/codex-hooks.ps1`

- [x] Add a test that expects `session-start.ps1` to emit valid Codex hook JSON.
- [x] Add a test that expects `pre-compact.ps1` and `stop.ps1` to write event records.
- [x] Add a test that expects `install-codex-hooks.ps1` to preserve existing hooks, create a backup, and add KeystoneOS hooks with `commandWindows`.

### Task 2: Implement Hook Scripts

**Files:**
- Create: `scripts/codex-hooks/common.ps1`
- Create: `scripts/codex-hooks/session-start.ps1`
- Create: `scripts/codex-hooks/pre-compact.ps1`
- Create: `scripts/codex-hooks/stop.ps1`

- [x] Build compact KeystoneOS startup context.
- [x] Optionally include Claude memory compiler startup context.
- [x] Write compaction and stop events to ignored output folders.
- [x] Keep hook stdout valid JSON where Codex expects JSON.

### Task 3: Implement Installer

**Files:**
- Create: `scripts/install-codex-hooks.ps1`

- [x] Default to dry-run.
- [x] Merge hook groups without deleting existing non-Keystone hooks.
- [x] Add Windows-native command handlers through `commandWindows`.
- [x] Create a timestamped backup before writes.
- [x] Make repeated installs idempotent.

### Task 4: Document and Verify

**Files:**
- Create: `docs/codex-memory-bridge.md`
- Modify: `README.md`
- Modify: `.gitignore`

- [x] Document how Codex, Claude memory, and KeystoneOS fit together.
- [x] Add quick-start commands.
- [x] Ignore generated Codex hook event output.
- [x] Run all KeystoneOS tests and parser checks.

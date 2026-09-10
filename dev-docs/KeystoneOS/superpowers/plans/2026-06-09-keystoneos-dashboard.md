# KeystoneOS Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated local dashboard that surfaces KeystoneOS daily work state.

**Architecture:** Extend `scripts/keystone.ps1` with a `dashboard` command. The command composes dashboard data from existing registries and artifacts, writes `outputs/dashboard/dashboard-data.json`, and generates a static `outputs/dashboard/index.html` file.

**Tech Stack:** PowerShell, JSON, static HTML/CSS, KeystoneOS registries.

---

### Task 1: Dashboard Test

**Files:**
- Create: `tests/keystone-dashboard.ps1`

- [x] Create a temporary KeystoneOS fixture with one project.
- [x] Seed git, handoff, intake, project brief, and Graphify outputs.
- [x] Run `keystone dashboard`.
- [x] Assert `outputs/dashboard/index.html` exists.
- [x] Assert `outputs/dashboard/dashboard-data.json` exists.
- [x] Assert the HTML includes Today, Project Switcher, Knowledge Map, Agent Launch Packet, and Inbox/Triage.
- [x] Assert JSON includes the project key, git status, graph stats, latest handoff, and latest intake.

### Task 2: Dashboard Command

**Files:**
- Modify: `scripts/keystone.ps1`

- [x] Add `dashboard` to the command set.
- [x] Implement HTML escaping helpers.
- [x] Implement latest artifact lookup.
- [x] Implement Graphify summary lookup.
- [x] Implement dashboard data composition.
- [x] Implement static HTML rendering.
- [x] Print the generated dashboard path.

### Task 3: Documentation

**Files:**
- Modify: `README.md`
- Modify: `outputs/README.md`

- [x] Add `.\scripts\keystone.ps1 dashboard` to Quick Start.
- [x] Document generated dashboard outputs.

### Task 3.5: Project Launch Pages

**Files:**
- Modify: `scripts/keystone.ps1`
- Modify: `tests/keystone-dashboard.ps1`
- Modify: `README.md`
- Modify: `outputs/README.md`

- [x] Add a failing test for `outputs/dashboard/projects/<ProjectKey>.html`.
- [x] Add `launchPage` to dashboard JSON data.
- [x] Link each project card to its launch packet.
- [x] Render project state, commands, startup checks, graph context, latest handoff, and latest intake.
- [x] Regenerate and visually inspect a live launch packet.

### Task 4: Verify and Ship

- [x] Run PowerShell parser checks.
- [x] Run `tests/keystone-dashboard.ps1`.
- [x] Run existing KeystoneOS tests.
- [x] Generate the live dashboard.
- [x] Open or inspect the dashboard artifact.
- [x] Run `git diff --check`.
- [x] Commit and push.

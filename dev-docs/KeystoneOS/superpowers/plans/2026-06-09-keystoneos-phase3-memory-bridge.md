# KeystoneOS Phase 3 Memory Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add ranked, source-aware memory lookup and generated memory packets.

**Architecture:** Move memory source metadata into `data/memory-sources.json`, load it from `scripts/keystone.ps1`, search markdown files with PowerShell, score results deterministically, print top hits, and write generated packets to ignored `outputs/memory/`.

**Tech Stack:** PowerShell, JSON, Markdown, Git.

---

### Task 1: Add Memory Source Registry

**Files:**
- Create: `data/memory-sources.json`
- Modify: `.gitignore`

- [x] Add current memory sources with priorities and markdown globs.
- [x] Ignore generated memory packets under `outputs/memory/`.

### Task 2: Implement Ranked Memory Search

**Files:**
- Modify: `scripts/keystone.ps1`

- [x] Load memory sources from JSON.
- [x] Tokenize user query.
- [x] Search markdown files.
- [x] Score matches by source priority, phrase hit, term coverage, and recency.
- [x] Print top ranked hits with source, file, line, and score.

### Task 3: Generate Memory Packets

**Files:**
- Modify: `scripts/keystone.ps1`
- Modify: `outputs/README.md`

- [x] Write packets under `outputs/memory/`.
- [x] Include query, generated time, ranked results, and source paths.
- [x] Document memory packet output.

### Task 4: Verify and Ship

- [x] Run parser check.
- [x] Parse `data/memory-sources.json`.
- [x] Run `memory FaceComps`.
- [x] Run `memory "Fall Camp"`.
- [x] Confirm memory packet generated and gitignored.
- [x] Commit with message `feat: add KeystoneOS memory bridge`.
- [x] Push to `origin/main`.

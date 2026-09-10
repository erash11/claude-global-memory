# KeystoneOS Operational Command Center — Spec

**Date:** 2026-06-12
**Status:** Draft — awaiting Eric sign-off before planning
**Supersedes context:** extends the 2026-06-11 "Map, Don't Copy" decision

---

## Problem

Eric wants KeystoneOS to be a true command center: *"open it and start working on any project I reference, without navigating to it. Whatever harness I'm using just knows what I'm trying to do, has all my context, and has access to everything. I want to find things and operate on them with zero time loss."*

Today that experience is missing three things:

1. **Broken pointers.** `Find-Project` (keystone.ps1:882) does a pure key lookup and trusts the stored `canonicalPath`. When a folder moves or is nested differently than recorded, the path is silently wrong. Felt this session: `PlayerProfiles_FB` "not found," three others nested deeper than expected.
2. **Incomplete registry.** Four live projects (ai-analyst, FootballWeightTargetTool, SportScienceResearchRepo, token-dashboard) are not registered. No metadata distinguishes a project Eric owns from one he borrowed (token-dashboard is someone else's, meant to go public).
3. **No context auto-load.** `start`/`resume` emit path + git + brief, but never pull the project's *own* `CLAUDE.md`/`AGENTS.md`, recent memory, or recent decisions. The harness does not actually "just know."

## Decision (architecture)

**Federation, made operational. Not a monorepo.** Project files stay where they are; KeystoneOS becomes a frictionless front door over them.

Rejected: physical consolidation / monorepo. Eric's own constraints rule it out:
- **token-dashboard is borrowed and public-bound** — can't vendor a repo he doesn't own into a private monorepo, and can't make one subfolder public.
- **SecondBrain is in scope** — an Obsidian vault cannot live inside a code repo without breaking Obsidian.

A monorepo therefore cannot even hold "everything," while charging a migration + lifecycle-coupling tax. The command-center properties Eric wants (single entry point, full context, operate-on-anything) are **orchestration** properties, not disk-layout properties — the harness can already read/edit any absolute path on this machine. We deliver them in the orchestration layer.

## Non-goals

- No moving or copying project files. No monorepo. No git-submodules.
- No server or database. Stay file-backed (consistent with 2026-06-10 decision).
- No change to per-project git histories or their own agent-context files.

---

## Design

Three capabilities, sequenced so the pain-killers ship and verify before the magic.

### Capability 1 — Self-healing path resolution  *(Phase 1)*

When a project's recorded `canonicalPath` does not exist on disk, resolve it by re-scanning the discovery roots instead of failing.

- New function `Resolve-ProjectPath($Project)`:
  - If `Test-Path $Project.canonicalPath` → return it (fast path, no scan).
  - Else scan `discovery-roots.json` roots for directories, normalize each folder name via the existing `ConvertTo-ProjectKey` (keystone.ps1:1464), and match against the project key.
  - **Exactly one match** → return the healed path and emit `ℹ path healed: <old> → <new> (run 'keystone heal' to persist)`.
  - **Zero or multiple matches** → return `$null` healed path; caller reports clearly with candidates listed.
- `Find-Project` / `Require-Project` call `Resolve-ProjectPath` and hand callers a project object whose path is the resolved one **for the duration of the command** (in-memory; no silent registry rewrite).
- New command `keystone heal [<Key>]`: persists resolved paths into `data/projects.json` for one project or all drifted projects. The only place the registry is rewritten.
- `keystone health` reports drift: for each project, `Recorded`, `Exists`, `Resolved`, `Drifted?`.

**Why in-memory + explicit `heal`, not silent auto-write:** a folder that vanished may have been deliberately deleted/renamed. Silent rewrites would mask that. Resolve transparently so every command still works; persist only on explicit `heal`. Commits here are artifacts (autocommit authorized), so `heal` is cheap to run.

### Capability 2 — Registry completeness + ownership/visibility  *(Phase 1)*

Extend the `data/projects.json` project schema with optional, back-compatible fields:

| Field | Values | Default when absent | Purpose |
|---|---|---|---|
| `ownership` | `own` \| `vendored` | `own` | "vendored" = borrowed/third-party; never treat as Eric-authored |
| `visibility` | `private` \| `public` | `private` | publish-safety; gates any future "share" action |
| `sharesCode` | `true` \| `false` | `false` | informational; flags coupling for future tooling |
| `kind` | `repo` \| `vault-note` | `repo` | `vault-note` = lives in SecondBrain, not a movable repo |

Promotions to perform (Eric pre-approved the four):

- **token-dashboard** — `ownership: vendored`, `visibility: public`. `DEV\token-dashboard`.
- **SportScienceResearchRepo** — `own`/`private`. `DEV\SportScienceResearchRepo`.
- **ai-analyst** — `own`/`private`. `DEV\AI_Analyst\ai-analyst`.
- **FootballWeightTargetTool** — `own`/`private`. `DEV\Football\FootballWeightTargetTool`.
- **PlayerProfiles_FB** — dropped from the candidate list (no findable path).

Existing vault-scope rows (OKRs, AI_Integration) tagged `kind: vault-note` so they are never treated as relocatable repos. `Promote-Project` extended to accept and record the new fields; defaults preserve every current row unchanged.

### Capability 3 — Context auto-load + router wiring  *(Phase 2)*

The "you'll just know" payload. New command `keystone context <Key>` emits **one** consolidated block a harness ingests in a single hop:

1. Resolved path + live `git status --short` + branch.
2. The resume brief (`projects/active/<Key>.md`).
3. Pointers (paths) to the project's own `CLAUDE.md` / `AGENTS.md` / `.superpowers` if present — so the harness loads project-local rules.
4. Top memory hits for the key (reuse existing `Search-Memory`, keystone.ps1:1412).
5. Most recent decisions mentioning the key (scan `decisions/log.md`).

Router wiring: add a rule to `AGENTS.md` (canonical) so every harness's front-door behavior is defined — *when the user says "work on X" / "let's do X", run `keystone context X` first to load context in one hop* — with `CLAUDE.md`/`GEMINI.md` deferring to it as today.

---

## Acceptance criteria

**Phase 1**
- [ ] With a deliberately wrong `canonicalPath`, `keystone where <Key>` / `resume <Key>` still resolves the real folder and prints the heal notice.
- [ ] `keystone heal <Key>` rewrites only that key's path in `projects.json`; re-running is a no-op.
- [ ] `keystone health` shows a `Drifted?` column; clean registry shows no drift.
- [ ] All four candidates appear in `projects.json` + `registry.md` + have an `active/<Key>.md` brief, with correct ownership/visibility.
- [ ] token-dashboard row carries `ownership: vendored`, `visibility: public`.
- [ ] Existing nine rows are byte-unchanged except added default fields; `keystone projects` still lists them.

**Phase 2**
- [ ] `keystone context <Key>` outputs path, git, brief, project-local agent-file pointers, memory hits, and recent decisions in one block.
- [ ] `AGENTS.md` documents the "work on X → context X" front-door rule; `CLAUDE.md`/`GEMINI.md` still defer to AGENTS.md.

## Verification plan

- Add/extend `tests/*.ps1` for `Resolve-ProjectPath` (fast path, single-match heal, zero/multi-match) and schema back-compat (absent fields → defaults).
- Run the existing test suite green before and after.
- Run `keystone health`, `keystone where` on a drifted key, and `keystone context` on one project, pasting output into `verification/evidence-log.md`.
- Follow `verification/default-checklist.md` before claiming completion.

## Phasing

- **Phase 1** (pain-killers): Capabilities 1 + 2. Ship, verify, commit.
- **Phase 2** (magic): Capability 3. Ship, verify, commit.

Record the architecture decision in `decisions/log.md` as part of Phase 1.

## Resolved (Eric, 2026-06-12)

1. **`heal` auto-commits** the corrected `projects.json` path — autocommit is authorized for this repo.
2. **Morning cadence pre-loads context** for the day's top project — Capability 3 adds a cadence wiring task in Phase 2.

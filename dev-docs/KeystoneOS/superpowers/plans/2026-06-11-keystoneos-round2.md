# KeystoneOS Round 2 — Ingest, Sweep, Route, Schedule

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingest the Nate Herk second-brain video into the vault, sweep DEV and promote all genuinely active projects into the registry, harden the three harness router files into a one-hop routing tree, and stand up a deterministic morning cadence via Task Scheduler.

**Architecture:** KeystoneOS stays a file-backed map/control plane. All four phases operate the existing `scripts/keystone.ps1` machinery (`inventory`, `intake`, `promote`, `graphsync`, `morning`, `dashboard`); the only new build surfaces are the rewritten router files and one Windows scheduled task. No servers, no databases, no copied project files.

**Tech Stack:** PowerShell 7 (`keystone.ps1`), Windows Task Scheduler (`Register-ScheduledTask`), Obsidian markdown (SecondBrain vault), git.

**Out of scope (recorded from approved design):** Connections tier-1, moving any project files, touching the claude-memory-compiler (read-only integration stays as is), evening/weekly agent-tier routines (earn autonomy — add after the morning tier proves out for a week).

---

### Task 1: Phase A — Ingest the video into the second brain

**Files:**
- Create: `C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\frameworks\claude-code-second-brain.md`
- Modify: `C:\Users\eric_rash\Desktop\DEV\KeystoneOS\decisions\log.md` (append)
- Source: `C:\Users\eric_rash\Desktop\DEV\KeystoneOS\outputs\yt-8QQ_INxAhRs-transcript.txt` (read-only artifact)

- [ ] **Step 1: Read the existing framework note for format conventions**

Read `C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\frameworks\building-a-product-roadmap.md` and match its frontmatter/heading/wikilink style exactly.

- [ ] **Step 2: Extract the five frameworks from the transcript**

Read `outputs\yt-8QQ_INxAhRs-transcript.txt` (43 KB). Pull the speaker's actual definitions and at least one concrete example for each of:
1. **Four C's framework** (the video's core capture/organize loop)
2. **Router-CLAUDE.md pattern** (one root file that tells the agent where everything lives)
3. **Skills-iteration loop** (build a skill, use it, refine it from friction)
4. **Keys-not-prompts permission principle** (grant scoped capability instead of re-prompting)
5. **Other-worlds idea** (separate vaults/contexts per life domain)

- [ ] **Step 3: Write the knowledge note**

Create `claude-code-second-brain.md` with this structure (fill bodies from Step 2 extraction):

```markdown
---
source: "I Turned Claude Code Into The Ultimate Second Brain" — Nate Herk
url: https://www.youtube.com/watch?v=8QQ_INxAhRs
captured: 2026-06-11
type: framework
---

# Claude Code as a Second Brain (Nate Herk)

One-paragraph summary of the video's thesis.

## The Four C's
## Router-CLAUDE.md Pattern
## Skills-Iteration Loop
## Keys, Not Prompts
## Other Worlds — and our decision
We mapped, didn't copy: KeystoneOS is a control plane over DEV/SecondBrain,
not a parallel vault per domain. Rationale: projects already live in canonical
repos; duplicating them creates sync drift. See KeystoneOS decisions/log.md
2026-06-11 entry.

## How this maps to KeystoneOS
Table: video concept → KeystoneOS implementation (router files, keystone.ps1
commands, memory-sources.json, registry).

## Related
[[building-a-product-roadmap]]
```

- [ ] **Step 4: Append the decision to the KeystoneOS decisions log**

Append to `decisions\log.md`:

```markdown
## 2026-06-11 - Map, Don't Copy (Other-Worlds Decision)

Decision: Adopt the video's router and cadence patterns, but reject per-domain
vault duplication. DEV projects integrate into KeystoneOS by registry promotion
(`keystone.ps1 promote`), never by copying files in.

Rationale:

- Canonical sources stay in their repos; KeystoneOS links and briefs point at them.
- Duplication creates sync drift across harnesses.
- Source: outputs/yt-8QQ_INxAhRs-transcript.txt; synthesis note at
  SecondBrain/Knowledge/frameworks/claude-code-second-brain.md.
```

- [ ] **Step 5: Verify and commit**

Verify the note has no empty sections and the wikilink target exists. Then:

```powershell
git -C C:\Users\eric_rash\Desktop\DEV\KeystoneOS add decisions/log.md docs/superpowers/plans/2026-06-11-keystoneos-round2.md
git -C C:\Users\eric_rash\Desktop\DEV\KeystoneOS commit -m "feat: record map-don't-copy decision and round 2 plan"
```

(The SecondBrain note is outside the repo — no git action needed there.)

---

### Task 2: Phase B — Full DEV sweep + promote

**Files:**
- Generated: `outputs\inventory\2026-06-11-workspace.{md,json}`, `outputs\intake\2026-06-11-project-intake.{md,json}`
- Modified by `promote`: `data\projects.json`, `projects\registry.md`, `projects\active\<Key>.md` (one per promotion)

- [ ] **Step 1: Run inventory then intake**

```powershell
& C:\Users\eric_rash\Desktop\DEV\KeystoneOS\scripts\keystone.ps1 inventory
& C:\Users\eric_rash\Desktop\DEV\KeystoneOS\scripts\keystone.ps1 intake
```

Expected: both write dated files under `outputs\` and print bucket summaries (Active / Daily Candidates / Knowledge Candidates / Watch / Review).

- [ ] **Step 2: Review buckets and select promotions**

Read `outputs\intake\2026-06-11-project-intake.md`. Promotion criteria: project appears in the Active or Daily Candidates bucket AND is a known live workstream. Known-live from working memory: **ForcePlate_DecisionSystem** (the named gap — must promote), **Travel_Map** (CSV import in progress), **morning-briefing** (runs daily). Surface the full bucket list in the session summary so Eric can veto/add.

- [ ] **Step 3: Promote each selected project**

```powershell
& C:\Users\eric_rash\Desktop\DEV\KeystoneOS\scripts\keystone.ps1 promote C:\Users\eric_rash\Desktop\DEV\ForcePlate_DecisionSystem -Status "Active"
# repeat per selection from Step 2
```

Expected per run: a new `projects\active\<Key>.md` brief, a registry row, a `data\projects.json` entry.

- [ ] **Step 4: Run the promotion test suite**

```powershell
& C:\Users\eric_rash\Desktop\DEV\KeystoneOS\tests\keystone-promotion.ps1
& C:\Users\eric_rash\Desktop\DEV\KeystoneOS\tests\keystone-intake.ps1
```

Expected: PASS output from both.

- [ ] **Step 5: Graphsync large promoted projects**

For each promoted project with substantial code (ForcePlate_DecisionSystem qualifies; judge others by file count in the inventory JSON):

```powershell
& C:\Users\eric_rash\Desktop\DEV\KeystoneOS\scripts\keystone.ps1 graphsync ForcePlate_DecisionSystem
```

If graphsync requires a pre-existing `graphify-out` in the target repo and one is absent, skip and note it in the brief instead of generating a graph inline — graph generation is its own session-sized job.

- [ ] **Step 6: Commit**

```powershell
git -C C:\Users\eric_rash\Desktop\DEV\KeystoneOS add -A
git -C C:\Users\eric_rash\Desktop\DEV\KeystoneOS commit -m "feat: DEV sweep — promote active projects into registry"
```

---

### Task 3: Phase C — Router hardening

**Files:**
- Rewrite: `AGENTS.md` (canonical routing tree), `CLAUDE.md` (thin Claude adapter), `GEMINI.md` (thin Gemini adapter)

- [ ] **Step 1: Rewrite AGENTS.md as the canonical one-screen routing tree**

Structure (fill paths from the live repo — all verified to exist):

```markdown
# KeystoneOS Router

Cross-harness control plane. This file answers "where does X live?" in one hop.

## Where things live
| Need | Go to |
|---|---|
| Active project registry | `projects/registry.md` |
| Resume brief for project X | `projects/active/<Key>.md` |
| Project key list (machine) | `data/projects.json` |
| Memory sources (all harnesses) | `data/memory-sources.json` |
| Memory query | `scripts/keystone.ps1 memory <terms>` |
| Decisions + rationale | `decisions/log.md` |
| SecondBrain vault | `C:\Users\eric_rash\Desktop\SecondBrain` |
| Knowledge frameworks | `SecondBrain\Knowledge\frameworks\` |
| Workflows (rituals) | `workflows/*.md` |
| Daily outputs (morning/plan/closeout) | `outputs/<kind>/<date>.md` |
| Dashboard | `outputs/dashboard/index.html` |
| Graph maps | `<project>\graphify-out` + `graphify/registry.md` |
| Verification expectations | `verification/default-checklist.md` |
| Specs and plans | `docs/superpowers/{specs,plans}/` |

## Commands (scripts/keystone.ps1)
today · morning · projects · resume · paths · health · memory · graphify ·
graphsync · status · where · start · brief · plan · closeout · open ·
inventory · intake · promote · dashboard

## Operating rules
(carry forward the existing five rules verbatim: map-not-source-repo,
no copying project files, links over copies, spec before multi-step work,
verify before claiming completion, preserve existing memory systems)

## Harness adapters
CLAUDE.md (Claude) and GEMINI.md (Gemini) point here. This file is canonical.
```

- [ ] **Step 2: Rewrite CLAUDE.md and GEMINI.md as thin adapters**

Each ≤ 15 lines: name the harness, point to `AGENTS.md` as canonical, keep harness-specific notes only (Claude: memory-compiler preservation note and global-memory paths; Gemini: nothing extra currently).

- [ ] **Step 3: Cold-agent routing test**

Answer these 10 questions using ONLY the new AGENTS.md, each in one hop (the file names the exact path):
1. Where is the list of active projects? 2. How do I resume FaceComps? 3. Where are memory sources enumerated? 4. How do I search memory? 5. Where are decisions recorded? 6. Where does the morning report land? 7. How do I promote a new project? 8. Where is the dashboard? 9. Where do Graphify maps live? 10. What must I check before claiming completion?

Any miss → fix the routing table, re-test that question.

- [ ] **Step 4: Commit**

```powershell
git -C C:\Users\eric_rash\Desktop\DEV\KeystoneOS add AGENTS.md CLAUDE.md GEMINI.md
git -C C:\Users\eric_rash\Desktop\DEV\KeystoneOS commit -m "feat: harden router files into one-hop routing tree"
```

---

### Task 4: Phase D — Cadence layer (morning tier) + memsearch fix

**Files:**
- Create: `scripts\morning-cadence.ps1` (thin wrapper the scheduled task calls)
- Modify: `workflows\morning-startup.md` (document the automation)
- System: one Windows scheduled task `KeystoneOS Morning`

- [ ] **Step 1: Write the wrapper script**

Create `scripts\morning-cadence.ps1`:

```powershell
# Runs the KeystoneOS morning packet + dashboard refresh. Called by the
# 'KeystoneOS Morning' scheduled task; safe to run manually.
$ErrorActionPreference = "Stop"
$keystone = Join-Path $PSScriptRoot "keystone.ps1"
$log = Join-Path $PSScriptRoot "..\outputs\morning\cadence.log"
try {
    & $keystone morning *>> $log
    & $keystone dashboard *>> $log
    Add-Content $log "[$(Get-Date -Format o)] cadence OK"
} catch {
    Add-Content $log "[$(Get-Date -Format o)] cadence FAILED: $_"
    exit 1
}
```

- [ ] **Step 2: Run the wrapper manually to verify**

```powershell
pwsh -NoProfile -File C:\Users\eric_rash\Desktop\DEV\KeystoneOS\scripts\morning-cadence.ps1
```

Expected: exit 0, today's `outputs\morning\2026-06-11.md` regenerated, dashboard rebuilt, `cadence OK` line in the log.

- [ ] **Step 3: Register the scheduled task (weekdays 7:00 AM)**

```powershell
$action = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument '-NoProfile -WindowStyle Hidden -File "C:\Users\eric_rash\Desktop\DEV\KeystoneOS\scripts\morning-cadence.ps1"'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 7:00AM
Register-ScheduledTask -TaskName "KeystoneOS Morning" -Action $action -Trigger $trigger -Description "Deterministic KeystoneOS morning packet + dashboard refresh (zero tokens)."
```

Verify: `Get-ScheduledTask -TaskName "KeystoneOS Morning"` shows Ready; `Start-ScheduledTask -TaskName "KeystoneOS Morning"` then confirm a fresh `cadence OK` log line.

- [ ] **Step 4: Diagnose the memsearch index failure**

`~/.claude/global-memory/transcripts/.errors.log` shows `memsearch-sync: index exit 1` on 6/10 and 6/11 with empty stderr. Diagnose:

```powershell
node C:\Users\eric_rash\.claude\hooks\memsearch-sync.js   # reproduce
memsearch index 2>&1 | Select-Object -Last 20             # direct run
docker ps --filter "name=milvus"                          # Milvus 2.6.4 up?
```

Known prior failure mode (from CLAUDE.md errors-log note): the memsearch flush patch gets stripped after a pip upgrade. Fix what the reproduction reveals; if it needs a pip-level patch reapply, do it and re-run the hook to confirm exit 0. If the root cause is outside quick reach, write findings to the session summary instead of rabbit-holing.

- [ ] **Step 5: Document the cadence in the workflow file**

Append to `workflows\morning-startup.md`: the scheduled task name, schedule, wrapper path, log location, and the rule that the evening/weekly agent tier is added only after a week of clean morning runs (autonomy is earned).

- [ ] **Step 6: Commit**

```powershell
git -C C:\Users\eric_rash\Desktop\DEV\KeystoneOS add scripts/morning-cadence.ps1 workflows/morning-startup.md outputs/
git -C C:\Users\eric_rash\Desktop\DEV\KeystoneOS commit -m "feat: add deterministic morning cadence via Task Scheduler"
git -C C:\Users\eric_rash\Desktop\DEV\KeystoneOS push
```

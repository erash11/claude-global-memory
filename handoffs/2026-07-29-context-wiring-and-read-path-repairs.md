# Handoff — 2026-07-29 — Context wiring and read-path repairs

Written to global-memory rather than `KeystoneOS/docs/handoffs/` because the background-session
isolation guard blocks writes to the shared checkout. Content is repo-agnostic; copy it into
`KeystoneOS/docs/handoffs/` if you want it version-controlled there.

## What this session was

Started as a question ("should new projects be their own folder in DEV, or work out of
KeystoneOS?") and became: evict projects living inside the control plane, then repair the read
paths preventing project context from reaching agents.

Everything below is **merged to main and verified**. No open PRs in either repo.

## Decisions made, with the reasoning

**Projects live in `DEV`, one folder each; KeystoneOS maps them by reference.**
`data/discovery-roots.json` scans `Desktop\DEV` at `maxDepth 2` — `DEV\Project` and
`DEV\Group\Project` are discovered; three levels deep is invisible to inventory.

**Never store source under a gitignored subtree.** `outputs/presentation/` and
`outputs/website/` were real projects under `.gitignore`'s `outputs/**`. 53 of their 54 files
existed only on one laptop, including files edited three weeks prior. The gitignore was correct
for generated output; storing source there was the mistake.

**Rejected "raise memsearch timeouts to 180s".** A timeout streak of 16 looked like a broken
indexer. It was a transient backlog: `daily-backup.ps1:122-125` documents the 45s SessionEnd
hook as deliberately best-effort, with the uncapped nightly absorbing backlog and resetting the
counter. Raising it would lengthen every session exit and partially revert the 2026-07-27
decision.

**`worktree-plans-top5-leverage` NOT merged despite merging cleanly.** It would add five
`PLAN-*.md` at the repo root, against the root-hygiene rule the 2026-07-24 audit acted on, and
its `keystone.ps1` changes are 76 commits stale. Clean != safe.

**Three claims failed verification this session** — that the registry pointed at a stale clone,
that the reconciler wasted hours on redundant backups, and that the indexer was chronically
broken. All plausible from point-in-time readings; all wrong. State a claim about this system
only after re-running the check that produces it.

## Files created or modified

**KeystoneOS** — merged to `main`, HEAD `e4ba08f`
- `scripts/keystone.ps1` — snapshot decisions block now takes whole `## ` entries from the
  TAIL; budget 1200 -> 2600; overall cap 6000 -> 8000
- `tests/keystone-snapshot.ps1` — synthetic oldest->newest log; asserts newest present /
  oldest absent. Verified to FAIL against the pre-fix script.
- `data/memory-index-paths.json` — `Knowledge/library` -> `Knowledge` (202 -> 255 .md); added
  `KeystoneOS/decisions`
- `tests/keystone-memory-index-paths.ps1` — asserts `library/` is NOT listed separately
- `AGENTS.md` — job-completion routing row now points at
  `keystone-reconcile.ps1 -DryRun -Json`, not `run-ledger.json` alone
- `decisions/log.md` — appended "2026-07-28 - Evict Projects From outputs/ Into DEV"
- `audits/os-audit-2026-07-29.md` — full six-check audit (NEW)
- `data/projects.json`, `projects/registry.md`, `projects/active/RTP_DataCollection_Talk.md`,
  `projects/active/Website.md` — two new registry entries
- `zotero-photo-capture/**` — merged via PR #17 (31 files, +4,426)

**dotclaude** — merged to `main`, HEAD `525e042`
- `scripts/daily-backup.ps1` — nightly reindex reads
  `KeystoneOS/data/memory-index-paths.json` instead of its own hardcoded list, which had
  silently diverged (3 declared paths were never indexed). Falls back to the hardcoded list and
  records `memsearch-index-config-missing` if the JSON is unusable.

**New repos** — both private, both `0 dirty / 0 sync`
- `C:\Users\eric_rash\Desktop\DEV\RTP_DataCollection_Talk` -> `github.com/erash11/RTP_DataCollection_Talk`
- `C:\Users\eric_rash\Desktop\DEV\Website` -> `github.com/erash11/AppliedPerformance-Site`

**Memory** — gitignored; backed up via daily-backup's Google Drive snapshot
- `C:\Users\eric_rash\.claude\projects\C--Users-eric-rash-Desktop-DEV\memory\project_dev-layout-and-discovery.md`
- `C:\Users\eric_rash\.claude\projects\C--Users-eric-rash-Desktop-DEV\memory\project_keystoneos-verification-habits.md`
- same dir `MEMORY.md` — two index lines added

**Scratch, not in any repo**
- `C:\Users\eric_rash\.claude\jobs\ea41d487\tmp\refined-plan-option2.md` — 5-round adversarial plan, 49 KB
- `C:\Users\eric_rash\.claude\jobs\ea41d487\tmp\pr19-body.md`

**This handoff**
- `C:\Users\eric_rash\.claude\global-memory\handoffs\2026-07-29-context-wiring-and-read-path-repairs.md`

## Next actions, most important first

1. **Verify tonight's nightly took the path change.** In
   `~\.claude\scripts\logs\daily-backup.log`, `INDEX knowledge:` should rise from **889
   chunks**. If not, the JSON read did not take effect.
2. **Run `/harvest` on a finished project** (`SP2026_03_07_ReportingROI_Football` or
   `ValdReport`). Every output-ledger row has an empty Harvest column — zero articles is a
   legitimate outcome and a real signal about whether semantic retrieval beats memory here.
3. **Add a `## Prior art` block to `keystone.ps1 context`.** `memsearch` appears 0 times in
   that script, so the corpus is write-only. ~7s per invocation (measured). Gated until step 1.
4. **Extract `zotero-photo-capture/` to its own repo.** Its own
   `docs/extracting-to-its-own-repo.md` has the `git subtree split` recipe and says to run it
   after PR #17 merged — which it now is. Creates a new GitHub repo; needs Eric's OK.
5. **Decide on `worktree-plans-top5-leverage`.** Real value (automation watchdog for
   `keystone health`/`cockpit`, 5 ranked plans, a test). Merge only together with moving the 5
   `PLAN-*.md` into `docs/superpowers/plans/`.
6. **Resolve `speedprofiling-ticket-03`.** Genuine conflict in
   `.scratch/speedprofiling/issues/03-analysis-core-and-tests.md` — main has a different
   resolution of the same ticket.

## Recorded but not fixed — all in audits/os-audit-2026-07-29.md

- `Get-KeystoneDevRoot` resolves the DEV root as `<repoRoot>\..`, wrong from a worktree, so
  `tests/keystone-reconcile.ps1` always throws there. Main baseline: 23 pass / 1 fail
  (`skill-verification-contracts.ps1`, unrelated).
- `Football\FaceComps\CLAUDE.md` is 26.7 KB with coaching-staff rosters — situational data in
  an always-loaded file.
- `agent_context` at `keystone.ps1:2194` scores presence, not content, so
  `Tezino_CampPrep`'s 0.1 KB stub games it. Fix once a project template exists.

## Branch state

Deleted 11 fully-merged branches. Two remain with commits not in main whose content IS in main
verbatim (superseded; would need `-D`): `worktree-fix-cadence-rg-path`,
`worktree-athletics-performance-landing-spec`. `worktree-phase2-durability` is locked
deliberately per the 2026-07-24 audit — do not sweep.

## The open question

There is now a working retrieval path but no evidence anything compounds through it. Next
action 2 is the test of that thesis.

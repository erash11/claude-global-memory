# Handoff — CFB_Analytics_Lab entered into the portfolio inventory

**Date:** 2026-08-16 (work began 2026-08-14, session resumed 2026-08-16)
**Repos touched:** `~/DEV/project-triage` (registry + one commit), `~/DEV/CFB_Analytics_Lab` (read-only)
**Status:** Complete. Registry entry live, dashboard republished.

---

## What was asked, and the one correction to it

The ask was: "read `handoff-cfb-analytics-lab-2026-08-13.md`, then enter this as `/project` into
our inventory and update the status accordingly."

**No file by that name exists.** Searched `mdfind`, name globs across `~`, and
`~/.claude/global-memory/handoffs/` (which uses `YYYY-MM-DD-<slug>.md`, not `handoff-<slug>-<date>.md`).
The name was a paraphrase. The richer source was the project's own record, which is what was read:

- `~/DEV/CFB_Analytics_Lab/docs/superpowers/2026-08-13-execution-record.md` — the nine-task record with all 20 rulings
- `~/DEV/CFB_Analytics_Lab/MISSION.md`, `README.md`, `NOTES.md`
- `~/DEV/CFB_Analytics_Lab/learning-records/0001-starting-floor.md`
- git branch state and `gh pr list`

If a future session is asked for that filename again: it does not exist, do not re-search for it.

## What the project is

A learning workspace for fluency in football data science — the methods from Eager & Erickson's
*Football Analytics with Python and R*, ported from the book's NFL/nflfastR data onto
CollegeFootballData. Fluency is defined as choosing a method for a football question, fitting it,
and explaining where it breaks; each lesson ends in a drill done unaided, and the drill is the evidence.

Explicitly **out of scope**: beating the betting market, Baylor coaching deliverables, and any change
to `~/DEV/CFB_Victory_Model` (which has a hard weekly cron dependency).

## Registry entry

Added to `~/DEV/project-triage/portfolio.json`:

| Field | Value |
|---|---|
| name | `CFB_Analytics_Lab` |
| lane | `side` |
| rank | 7 at write time; re-ranked to **6** by the 2026-08-15 board session |
| stage | `building` |
| status | `active` |
| dev_folder | `CFB_Analytics_Lab` |

Schema matches the 11-key shape every other entry uses. Validated with `render.py --no-scan` (exit 0).

**Assumptions made rather than blocking** (all defensible, all worth revisiting if wrong):
- **`side` lane** — MISSION excludes Baylor deliverables, so this is self-directed upskilling,
  alongside KeystoneOS and Project_Triage.
- **`building` stage** — spec + plan + nine tasks executed, but unmerged and mid-curriculum.
- **`next_action` leads with the PR, not the drill** — the merge is mechanical and rots; the drill
  is gated on a human doing it.

## Status captured (as of 2026-08-13 foundation work)

1,495,005 plays pulled across 2019–2025 in 129 CFBD API calls. 49 tests passing offline. FBS
reconciliation against CFBD's own game list matches to 99.98% with zero join inflation.

Three fix-before-merge findings were caught in review and repaired in `02a190b`:
- **Ruling 17** — `/plays` ships FCS games mixed with FBS, and CFBD's coverage changes shape at the
  2022 boundary (FBS-only through 2021, full FCS from 2022). Every cross-2022 analysis in the
  curriculum was quietly invalid until the `attach_classification` + `fbs_only` wiring was documented
  and a `validate="m:1"` merge guard added. This is the single most important trap in the project.
- **Ruling 18** — postseason weeks are non-contiguous (1, then 11–15, then 20), so break-on-empty
  terminates at week 1. Measured blast radius: zero FBS-vs-FBS games. Documented, not backfilled.
- **Ruling 19** — the budget guard estimated the full pull regardless of what was already on disk,
  so a crashed pull would be refused by the very guard meant to protect it.

Lesson 0001 (stability / year-over-year) is built; its drill is pending. Lesson 0002 is gated on it.

## Correction made during closeout

The `next_action` originally read "merge the `foundation` branch into `main` (20 commits)". Verified
against the live repo three days later:

- **PR #1 is still OPEN** (opened 2026-08-13), not merged.
- `foundation` is **21** commits ahead of `main`, not 20.
- `main` is at `dd6a899` and holds **only the spec and plan** — none of the implementation.

Corrected in commit `7f9b3bb` (`data:` subject, per the registry-provenance convention). The Tier A
memory `project_cfb-analytics-lab.md` said "foundation shipped as PR #1", which reads as merged; it
now states the PR is open and that you must check out `foundation` or the workspace looks empty.

## Known cosmetic artifact — not a bug

The dashboard card shows stage `building` next to **0/59 plan-checkbox progress**. The plan doc
`docs/superpowers/plans/2026-08-13-cfb-analytics-lab-foundation.md` was never checked off during
execution even though all nine tasks completed, so the auto-detected progress understates reality.
Ticking the boxes was out of scope for an inventory update. Fix it by editing that plan file if the
mismatch is annoying.

## Files created or modified

- `~/DEV/project-triage/portfolio.json` — entry added, then `next_action` corrected (commit `7f9b3bb`)
- `~/DEV/project-triage/dashboard.html`, `pulse.md` — regenerated (both gitignored; never hand-edit)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_cfb-analytics-lab.md` — PR #1 status corrected
- `~/.claude/global-memory/handoffs/2026-08-16-cfb-analytics-lab-inventory.md` — this file

Dashboard artifact (same URL throughout): https://claude.ai/code/artifact/34fa148f-d840-4881-b3e8-0d174835615e

## Next actions, most important first

1. **Review and merge PR #1** on `erash11/CFB_Analytics_Lab`. The fix-before-merge rulings are already
   applied; nothing is blocking it but the review.
2. **Do Drill 0001** and report the result. Lesson 0002 will not be built until it is reported —
   that gate is deliberate, per `NOTES.md`.
3. Push `~/DEV/project-triage` — commit `7f9b3bb` is local-only (this session was not authorized to
   push any repo but KeystoneOS).

## Mid-flight / open questions

Nothing awaited from anyone. The only judgment left open is whether `side` lane and `building` stage
match how Eric actually thinks about this project — both were assumed, not confirmed.

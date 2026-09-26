# Handoff — 2026-09-25/26 — SCN sprint course: review, library ingest, Sprint Film Check

## What and why
Eric is feeding paid courses (Old Bull, Sportsmith On-Field RTP, now Strength Coach Network
*Fundamentals of Sprinting*) into his learning and the agent's knowledge base, to design
training and rehab and to evaluate movement better. This session reviewed the sprint course
(Jeff Moyer; lesson 16 is Alex Natera on run-specific isometrics), ingested it into the vault
library, and built the first practical piece: the Sprint Film Check.

## Decisions (and the reasoning)
- **Library placement:** strength-and-conditioning domain, beside Bompa, so the existing S&C
  advisor answers from it.
- **Confidence capped at `supported`** for the whole course: it is a practitioner course.
  Causal, injury and transfer claims are `untested`. Seven entries are `contested`: 4 on the
  motor-learning conflict with Myszka/CLA, 3 on biomechanics.
- **The ingest went through the review gate:** an independent reviewer returned GO-WITH-FIXES
  and every must-fix was applied. The NFL running back in the case entries was de-identified on
  purpose; do not add the name back.
- **The film check pairs S-MAS (Bramah 2024) for the number with Moyer's words for the talk.**
  S-MAS has reliability data; Moyer's language does not.
- **Moyer and Bramah go into `RTP_Constraints_Course/RESOURCES.md`**, because that repo cites
  only what is listed there.
- **Natera push-test norms are deferred to January winter testing** (WR/DB), not in season.
- **Standing permission:** after a merge, delete its worktrees and branches without asking,
  once verified merged and fully in git.

## Files created or modified
- Drive, `G:\My Drive\00_Primary_Storage_Drive\09_PRO_DEV\SCN_Course_Sprinting\`:
  - `Review and Plan - Fundamentals of Sprinting course.md`
  - `Sprint Film Check.pdf`
- Vault: `Knowledge/library/strength-and-conditioning/fundamentals-of-sprinting--moyer/`
  (58 entries plus `_book.md`), `strength-and-conditioning/_domain.md`, and
  `advisors/strength-and-conditioning.md`. Commits `23d0ad0` and `41a7f8d`, pushed.
- `RTP_Constraints_Course`:
  - PR #6 (merged): `reference/sprint-film-check.html`, `assets/course.css`, `RESOURCES.md`,
    `docs/STATUS.md`, `docs/handoffs/2026-09-26-sprint-film-check.md`
  - PR #7 (merged): the STATUS gotcha on the Windows worktree "Permission denied"
    (a read-only attribute, not a lock)
  - All merged branches deleted; the repo is `main` only.
- Memory:
  - Tier A `project_scn-sprint-course.md` and `feedback_post-merge-cleanup.md`, plus the index
  - Global `MEMORY.md`: the RTP thread and the post-merge line

## Next (most important first)
1. Eric shows the Sprint Film Check to Tim and Jacob, then runs
   `python scripts/export_for_joe.py` in `RTP_Constraints_Course` so Joe gets it.
2. Film skill players in fall testing, so each player has a pre-injury baseline clip.
3. January: Natera push-test norms. First rewatch lesson 16, 43:18–80:17, to confirm whether
   his ×BW benchmarks are total force.

## Mid-flight / watch
- The memsearch-sync hook shows an ETIMEDOUT streak of 4/6 (the laptop was short on memory
  on 9/26). It escalates at 6.
- The stale ENOBUFS entry was cleared: the maxBuffer fix landed on 9/25, after the error.

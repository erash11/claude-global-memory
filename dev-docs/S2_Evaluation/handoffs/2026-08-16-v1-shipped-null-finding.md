# Handoff — S2_Evaluation V1 shipped (null finding)

**Date:** 2026-08-16
**Repo:** `/Users/kristinarash/DEV/S2_Evaluation` → `github.com/erash11/S2_Evaluation` (private)
**State at handoff:** clean, 6 commits, 0 unpushed, V1 complete.

---

## What this project is

Mine existing S2 Cognition testing data for coach-facing insight that goes **beyond
normative percentiles**. Audience is sport science internal first, then position
coaches / S&C — not athletes. Self-initiated, side lane.

V1 was deliberately scoped to **one position room, shape only, no prescription**
(ADR 0002). The question was not "who is good" but "is there any structure in the
profile shape that a percentile table hides?"

## What V1 actually found

**The finding is null, and that is the result — not a failure.**

- The gate passed: mean category range across the OL room was **2.68 SD** against a
  pre-registered threshold of **2.50 SD**. Profiles are genuinely uneven.
- The delivery step found nothing: at 2.5 SD, **zero linemen** were flagged as
  deviating from the room, where chance alone predicts 1–2.
- **No offensive lineman is cognitively atypical for his room.**

### The error the pre-registration caught

Applied literally, the original 1.5 SD flagging rule marked **10 of 15 linemen** as
outliers. That would have become a list of "cognitively atypical" players handed to
a coach — built on nothing. Null-model simulation showed a room of pure noise flags
**7–13 of 15** at that threshold. The rule was measuring the threshold, not the
athletes.

This is recorded in **ADR 0013**. The threshold was **not retuned** after seeing the
data. It was reported as-is with its miscalibration documented, because retuning
post-hoc is exactly the move pre-registration exists to prevent.

## Decisions worth preserving (the reasoning, not just the choice)

Full record in `docs/adr/0001`–`0013`. The ones whose reasoning would be lost:

- **0003 — Unevenness gates, Room Deviation delivers.** These are two different
  things and collapsing them is the single easiest way to get this wrong.
  *Unevenness* is within-athlete spread across categories. *Room Deviation* is
  distance from the position-group mean. An athlete can be very uneven and perfectly
  typical for his room. OL was chosen over safeties purely on room size.
- **0004 — Compute spread in z-space.** Vendor percentiles are converted via inverse
  normal, arithmetic is done in z, and results are reported back in percentile
  language. Because the population SD is 1 by construction, the room SD is never
  estimated from 15 athletes — which would have been the biggest source of noise.
- **0006 — Per-category deviation, not Mahalanobis.** Mahalanobis needs a covariance
  matrix; with n=15 and 9 categories that matrix is not estimable.
- **0009 — Go/no-go is self-assessed.** Eric is his own reviewer here. That is
  *why* pre-registration in a timestamped commit is load-bearing rather than
  ceremonial.
- **0010 — Kill criterion is mean range vs a null.** The original criterion was
  vacuous: 89% of pure-noise athletes clear 2.0 SD when you take a max over 9
  categories. Caught **before** the data was on the machine.
- **0012 — Exclude the vendor-invalidated report.** One lineman's report failed S2's
  own validity check. Excluded from analysis, surfaced as a retest recommendation.
  Room stands at 15 of 16.

## Vendor data traps (not documented by S2)

- Percentiles are scored against **"NFL PROSPECTS — ALL POSITIONS"**. A percentile is
  only comparable within that reference group. Cross-position pooling is therefore
  legitimate (Baylor rooms range 42nd–82nd); if scores were position-normed, every
  room would sit near the 50th.
- The **P/K battery has 7 measures, not 9**, with zero N/A cells. Structural to the
  vendor's short battery — not a parse bug.
- Test years are mixed across the roster. Flagged as a diagnostic, not filtered on
  (ADR 0011).

## Files created or modified this session

**Repo — `/Users/kristinarash/DEV/S2_Evaluation/`**
- `CONTEXT.md` — glossary, 8 terms (Beyond Percentiles, Profile Shape, Profile
  Unevenness, Room Deviation, Position Fit, Room, Vendor Baseline, Kill Criterion)
- `docs/WORKFLOW.md` — `/ask-matt` routing brief
- `docs/V2-SCOPE.md` — V2 scope, three tracks
- `docs/adr/0001-…` through `docs/adr/0013-…` — 13 ADRs
- `build_report.py` — generates `report.html` from `data/ol_scores.csv` so the
  numbers in the report cannot drift from the source
- `report.html` — de-identified V1 report (~16 KB)
- `.gitignore` — `.DS_Store`, `.venv/`, `__pycache__/`, **`data/`**
- `docs/handoffs/2026-08-16-v1-shipped-null-finding.md` — this file

**Never committed, and must stay that way:**
- `data/ol_scores.csv`, `data/team_scores.csv` — athlete PII
- `/Users/kristinarash/DEV/COG_S2_Position_Reports/` — source vendor PDFs

**SecondBrain vault** (commit `2dd4189`, pushed)
- `Knowledge/frameworks/calibrate-the-threshold-against-a-null.md`
- `Knowledge/frameworks/when-you-are-your-own-reviewer-timestamp-the-threshold.md`
- `Knowledge/sport-science/vendor-percentiles-are-only-comparable-within-their-reference-group.md`
- `output/_ledger.md` — shipped row added

**Elsewhere**
- `/Users/kristinarash/DEV/project-triage/portfolio.json` — S2_Evaluation, side lane
  rank 6, stage `shipped`
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_s2-cognition-analysis.md`
- Published report artifact: `https://claude.ai/code/artifact/30d83487-f660-42d7-9810-408f8b622524`
- Portfolio dashboard artifact: `34fa148f-d840-4881-b3e8-0d174835615e`
- Gmail draft `r-7654854188196459454` — "S2 Cognition — request for reliability and
  reference group documentation" (unsent, `To:` deliberately blank)

## Next actions, most important first

1. **Send the S2 email.** Draft is written and sitting in Gmail drafts. It needs a
   recipient (no S2 contact exists anywhere in the vault) and should probably go from
   a `baylor.edu` address rather than the gmail one. Five asks, in priority order:
   test-retest reliability/SEM per category; normative database revisions 2022–2026;
   composition of the "NFL PROSPECTS — ALL POSITIONS" group; positional norms within
   the reference population; why the P/K battery has seven measures.
2. **Track A — pooled position-adjusted analysis.** Unblocked, needs nothing from S2.
   ~92 athletes. Requires: harden the extractor for the P/K layout and the invalid
   report, add the speed/accuracy dimensions, and — per the standing rule from
   ADR 0013 — **pre-register and commit Track A's thresholds before running it.**
3. **Run the `/research` track** on S2 construct validity against primary sources. It
   may answer ask #1 without waiting on the vendor. Recommended repeatedly, never run.
4. **Retest the lineman** whose report failed vendor validity checks.

Tracks B (individual-athlete secondary analysis) and C (position gradient) are
**blocked on S2's reply** — B specifically needs the SEM to compute a reliable change
index, without which any within-athlete comparison is uninterpretable.

## Mid-flight / open questions

- **Commit author name — resolved via `.mailmap`, do not rewrite history.**
  The first six commits carry the machine account name "Kristina Rash". The **email
  was correct throughout** (`eric.rash11@gmail.com`), so GitHub already attributes
  every commit to the `erash11` account; the wrong name only ever showed in raw
  `git log`. A `.mailmap` at the repo root now corrects it with zero rewrite.

  **Do not "fix" this with an amend or rebase.** `git commit --amend --reset-author`
  renews the *author date* along with the name. Those dates are the evidence that the
  design was pre-registered before the data was acquired — which, per ADR 0009
  (self-assessed go/no-go), is the only thing making the pre-registration
  demonstrable rather than merely claimed. Original author dates, for the record:

  | commit | author date | subject |
  |---|---|---|
  | `0d455a7` | 2026-08-08 22:46:32 -0500 | Pre-register S2 evaluation design before data acquisition |
  | `01ab48f` | 2026-08-11 12:57:36 -0500 | Revise kill criterion and settle cohort before extracting OL scores |
  | `90b856a` | 2026-08-11 12:59:47 -0500 | Exclude vendor-invalidated OL report; room stands at 15 |
  | `48d9450` | 2026-08-11 13:02:27 -0500 | Record null Room Deviation finding and threshold miscalibration |
  | `921e505` | 2026-08-11 13:09:24 -0500 | Add v1 report: de-identified null finding for the OL room |
  | `77355dc` | 2026-08-11 18:20:16 -0500 | Scope V2: pooled position-adjusted model, blocked individual track, S2 data request |

  The three-day gap between `0d455a7` and the rest is the point: thresholds were
  committed before the data was on the machine.
- No S2 vendor contact is known. This blocks action #1 entirely.
- `~/.claude/skills/_shared/config.json` still contains pre-migration Windows paths
  (`C:\Users\eric_rash\...`). Any skill trusting it will fail on this Mac. Unrelated
  to S2, flagged twice, still unfixed.

## Standing constraints — do not relax

- Athlete-level data (`data/`, CSVs, source PDFs) stays out of version control and off
  any published page.
- `report.html` and every future published artifact stays de-identified.
- **No threshold may be retuned after seeing results.** A change requires a new ADR
  stating what was wrong and why.

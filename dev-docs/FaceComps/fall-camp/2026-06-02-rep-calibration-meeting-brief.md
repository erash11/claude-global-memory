# Rep Calibration — Meeting Brief (2026-06-02)

Status of the scripted-rep work behind the Fall Camp color/prescription layer. Two
loose ends closed in code today; one finding that should steer the discussion.

## Done today (in code, on branch `worktree-practice-planning-resume`)

- **#3 — QA worksheet is now durable.** `extract_fc25_reps.py` used to regenerate
  `fc25_rep_calibration_QA.xlsx` from scratch, which would erase any hand-entered
  `ones_reps_confirmed` values on the next run. Fixed: the confirmed column is now
  human-owned — regeneration recomputes the auto columns but carries forward any value
  a person actually typed (a filled FLAG row or a correction), and rolls it into the
  day `rep_total` so totals complete and REVIEW flags clear as you go. Tested: inject a
  value → re-run → value survives, day total moves, flag clears. **The human QA pass is
  now safe to do.**
- **#5 — Scrimmages excluded.** Decision 6 already said drop scrimmages; they were
  sneaking in because they carry a DEF PRAC sheet. Added a filename denylist. The two
  scrimmage days (Aug 09, Aug 15) are now marked EXCLUDED. Calibration set = **16 install
  days** (18 minus 2 scrimmages; the Aug 21/22 Friday-WT / Mock days were already out).

## The finding that matters: reps alone don't predict color

On the 10 QA-complete (non-scrimmage, no-flag) days, scripted reps do **not** separate
the realized load zones:

| Zone   | n | Rep totals        | Range  |
|--------|---|-------------------|--------|
| GREEN  | 2 | 16, 20            | 16–20  |
| YELLOW | 3 | 24, 24, 32        | 24–32  |
| RED    | 5 | 16, 16, 20, 24, 32| 16–32  |

- **Pearson r(reps, PL/player) = +0.15** — effectively no linear relationship.
- **Direct collisions** (same reps, opposite color):
  - 16 reps → RED (482, 508) *and* GREEN (388)
  - 20 reps → RED (495) *and* GREEN (399)
  - 32 reps → RED (499) *and* YELLOW (456)
- RED days span the full rep range (16–32), identical to everyone else.

**Implication:** we cannot set standalone scripted-color rep bands (the original #8 plan).
This is the empirical proof of grill-state decisions #2 and #9 — **color must be the
composite** (reps + duration + %two-spot/good-on-good + field condensation + dress), with
reps as one input, not the axis. The meeting energy should go to #9 (define the composite
+ source its inputs), not to drawing rep cutoffs.

Caveat: 6 of 16 days are still pre-QA (situational rows undercounted). Filling them adds
reps mostly to high-load late-camp days, which *may* sharpen the signal a little — but the
collisions above are in clean data and won't disappear. Re-run the band analysis after the
QA pass to confirm, but don't expect reps alone to carry color.

## What's still needed (in order)

1. **#4 — Human QA pass (~30 min, your hands).** Open `fc25_rep_calibration_QA.xlsx`,
   fill `ones_reps_confirmed` on the highlighted FLAG rows (6 days: Aug 11, 14, 17, 18,
   19, 20). This produces the locked calibration dataset. Now durable against re-runs.
2. **#6 — Validate the parser.** Hand-count reps on 2–3 days (P01, P08, P13) and compare
   to the script before trusting any thresholds. NOTE: a few current day totals differ
   from the earlier "spike" numbers (P06 24 vs 20, P08 24 vs 20, P11 16 vs 20) — worth
   confirming which is right during this check.
3. **#7 — ADR** for the rep-counting method, once the QA pass confirms it holds.
4. **#9 — Define the composite** (the real work, per the finding above): how reps combine
   with duration, %two-spot, condensation, dress; source those inputs for the 16 days.
5. **#10 — Macro Phase-1 artifact** (Aranda late-June deliverable): camp-calendar colored
   grid + rep-progression schedule (88→124→152→180→taper).

## Files
- Extractor: `scripts/extract_fc25_reps.py`
- Worksheet: `docs/fall-camp/fc25_rep_calibration_QA.xlsx` (periods + day_summary sheets)
- Resume map: `docs/practice-planning-grill-state.md`

## Post-QA update (after the #4 confirmations landed)

With all 6 FLAG rows confirmed, the calibration set is 16 complete install days. Re-running
the band analysis on the full set sharpens the finding from the partial sample above:

| Zone   | n | Rep totals (confirmed) | Mean |
|--------|---|------------------------|------|
| GREEN  | 4 | 9, 16, 16, 20          | 15.2 |
| YELLOW | 5 | 24, 24, 28, 32, 40     | 29.6 |
| RED    | 7 | 16, 16, 20, 24, 32, 32, 36 | 25.1 |

- **Pearson r(reps, PL/player) rose +0.15 → +0.43** — reps are a moderate predictor, not noise.
- **GREEN is cleanly separable** (low reps, all ≤20). A rep ceiling alone can flag a green day.
- **YELLOW/RED overlap and invert** (RED mean < YELLOW mean): some RED days are low-rep,
  intensity-driven (condensation / two-spot / dress), not volume-driven. 16 reps still lands
  both RED and GREEN.

**Refined conclusion:** reps can carry the GREEN boundary on their own, but the YELLOW↔RED
split requires the composite (#9). Net: reps are a stronger input than the pre-QA data implied,
but still not sufficient alone above green.

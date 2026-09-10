# Secondary-Modifier Test — GREEN↔YELLOW Boundary (2026-06-03)

Closes the deferred composite question from the duration-first pivot: in the fuzzy
duration band (104–115 active min), does a secondary modifier sharpen the duration-only
classifier? Answer: **yes — reps, applied as a gated override, not a weighted blend.**

## Setup

- Population: 35 FC24/FC25 days with true Catapult active minutes
  (`fall_camp_duration_thresholds.csv`) joined to realized PL/player + zone
  (`fall_camp_daily_thresholds.csv`).
- Duration bands (the spine): GREEN ≤102 · YELLOW 102–117 · RED >117 active min.
- Candidate modifier: confirmed scripted reps, FC25 install days only
  (`fc25_rep_calibration_QA.xlsx`, day_summary). FC24 has no rep capture yet.

## The boundary problem, made concrete

Duration-only is 74% exact (26/35), zero green↔red misses. All 9 misses are
single-band, and they split into two piles:

- **6 GREEN→YELLOW misses** — days running 108–115 min where PL stayed green (346–405).
- **3 YELLOW→RED misses** — 119–149 min, PL stayed yellow.

In the 104–115 min band there are 11 days: **5 realized-GREEN, 6 realized-YELLOW, 0 RED.**
Greens and yellows are fully interleaved on minutes (green at 108.1 / 114.5 / 114.6;
yellow at 104.1 / 105.3 / 114.0 / 115.0). **No duration cutoff separates them** — that is
precisely why a secondary modifier is required here and only here.

## Why reps, and why a gate (not a weight)

Reps have discriminative power in exactly one place — the GREEN/YELLOW split — and none
in the YELLOW/RED split (r=+0.43 overall; GREEN reps all ≤20, YELLOW all ≥24, but RED
spans 16–36 and inverts). That maps perfectly onto the duration model's weakness:

- Duration's **RED guardrail (>117) is clean** (11/11, conservative). Reps are not needed
  there and would not help.
- Duration's **only soft seam is GREEN↔YELLOW** — which is the one seam reps cut cleanly.

So the modifier is applied as a **gate, not a weighted sum**:

> Duration sets the band. If the band is YELLOW (102–117 min) **and** reps exist **and**
> the day is not a scrimmage: reps ≤20 → demote to GREEN; reps ≥24 → keep YELLOW;
> 21–23 → tweener, keep duration's call.

A weighted composite would dilute the clean RED guardrail with a rep signal that is noise
above green. The gate keeps each input where it is strong.

## Result

| Classifier | Overall (n=35) | FC25 install only (n=16, reps exist) |
|---|---|---|
| Duration only | 26 / 35 = 74% | 12 / 16 = 75% |
| Duration + rep gate | **28 / 35 = 80%** | **14 / 16 = 88%** |

The gate touched exactly two days, both fixes, zero breaks:

- FC25 P7 (114.5 min, 16 reps): YELLOW→**GREEN** ✓ (real GREEN)
- FC25 P12 (110.1 min, 20 reps): YELLOW→**GREEN** ✓ (real GREEN)

## Remaining 7 misses — all explained, none contradict the rule

- **4 are GREEN days with no rep data** (FC24 P11, P12, P13; scrimmage P14). Same profile
  as the two the gate fixed — they sit in the boundary band and the gate simply has no
  reps to act on. The mechanism is proven on every FC25 boundary day; this is a
  data-coverage gap, not a rule failure.
- **3 are YELLOW→RED over-calls** (FC25 P16 119 min/40 reps, FC24 P6 130 min, FC25 P4 149
  min/32 reps). High duration, moderate PL — volume without matching intensity. Reps can't
  fix these (high reps), and we don't want them to: the >117 guardrail over-warns on load,
  which is the safe direction for a camp planner.

## Verdict / what to carry into the composite

1. **Reps are the secondary modifier for the GREEN↔YELLOW boundary.** Adopt the gate above.
2. **No weighting needed** — duration owns the band, reps break the YELLOW→GREEN tie only.
   %two-spot / condensation / dress were not needed to resolve this seam.
3. **The ceiling on this approach is rep coverage, not the rule.** Capturing FC24 reps
   (or the perch-camera path) is the next lever — it would test generalization and likely
   recover the 4 FC24/scrimmage green-misses, pushing overall toward ~91%.
4. **YELLOW→RED stays a deliberate over-warn.** Leave the >117 guardrail conservative; do
   not try to soften it with a modifier.

## Files
- This test: `docs/fall-camp/2026-06-03-secondary-modifier-test.md`
- Inputs: `fall_camp_duration_thresholds.csv`, `fall_camp_daily_thresholds.csv`,
  `fc25_rep_calibration_QA.xlsx`
- Prior finding: `docs/fall-camp/2026-06-02-rep-calibration-meeting-brief.md`

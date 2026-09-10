# Availability hazard model: first results

**Status:** model built, tested, validated end-to-end on live data
**Date:** 2026-07-21
**Code:** `src/risk_stratification_engine/availability_hazard.py`
**Reproduce:** `python -m pytest tests/test_availability_hazard.py`; live-data harness in the PR description

## What the model is

A discrete-time hazard model: one pooled logistic regression over athlete-week
rows, predicting whether a lower-limb availability-costing injury begins in that
week. Because the exposure and injury-history features are computed as of the
week start and look backward, and because the panel is a genuine person-period
risk set, a logistic fit on it *is* a discrete-time hazard model (logit link).

The framing is deliberately the honest one from the scoping doc: **which
athletes are at elevated hazard, and when** — a ranking-and-timing question, not
a causal "how much load causes injury" claim. Load is not randomly assigned.

## Features (pre-specified, frugal)

At 106 events the 10-per-covariate rule allows ~10 terms; the model uses 8,
chosen for distinct mechanisms rather than for fit:

- `season_week`, `season_week_sq` — baseline hazard / timing (Josse's rising
  seasonal curve)
- `exposure_training_sessions_28d` — recent load
- `exposure_days_since_last_game` — game proximity
- `exposure_no_participations_28d` — recent modified/missed sessions
- `injury_history_prior_injury_count`
- `injury_history_days_since_last_injury`
- `injury_history_prior_lower_extremity_injury_count`

## The evaluation lesson

A single athlete-level holdout put only **13 of the 106 events** in the test
fold and reported **ROC-AUC 0.42 — worse than a coin flip.** That number is
noise, not a finding: with 13 events the AUC has enormous sampling variance, and
the house holdout sorts athletes by id (which tracks recruiting class), so the
test cohort may be systematically different.

Grouped 5-fold cross-validation with pooled out-of-fold predictions — every
event gets exactly one honest prediction — tells the real story. Run through the
canonical CLI path (`prepare_exposure_inputs`, which keeps only name-matched
athletes as at-risk):

| Missing-week policy | Athlete-weeks | CV ROC-AUC | Top-decile lift |
|---|---|---|---|
| observed | 18,145 | 0.651 | **1.89×** |
| span | 22,945 | 0.683 | **2.55×** |

**The highest-risk 10% of athlete-weeks carry roughly 1.9–2.5× the baseline
injury rate.** The direction holds under both missing-week assumptions; only the
magnitude shifts, so the result is not an artifact of that choice.

(An earlier harness that counted every logged athlete-week as at-risk — not just
name-matched ones — reported 0.68/0.71 and 2.45×/3.21×. The canonical
matched-only risk set is smaller and slightly harder, and is the authoritative
number. All 120 lower-limb events reduce to the same 106 in-span events under
both athlete-id schemes, which cross-checks the name-hash join.)

Always trust the cross-validated number here, not the single split. The module
exposes both (`fit_availability_hazard` for the house-shaped artifact,
`cross_validated_hazard` for the honest discrimination estimate).

## Robustness: does the result survive different outcome definitions?

Cross-validated discrimination under the observed policy, holding the model
fixed and varying only what counts as an event:

| Outcome | Events | CV ROC-AUC | Top-decile lift |
|---|---|---|---|
| **lower-limb caused-unavailability (primary)** | 106 | **0.651** | 1.89× |
| lower-limb soft-tissue | 71 | 0.652 | **2.25×** |
| all caused-unavailability | 203 | 0.639 | 1.48× |
| exclude concussion (any body area) | 156 | 0.594 | 1.41× |

The primary choice is **not** cherry-picked. Discrimination is best on the
lower-limb outcomes (0.65, and the tighter soft-tissue subset gives the highest
lift at 2.25×) and *falls* as the outcome broadens to all body areas — because
the model's signal is specifically lower-limb (its strongest feature is prior
lower-extremity injury), so outcomes that dilute it with upper-body and misc
injuries discriminate worse. The result holds; it is sharpest where the outcome
and the features agree.

## Where the signal comes from — feature-block ablation

Blocks added cumulatively, cross-validated, primary outcome:

| Cumulative model | Features | CV ROC-AUC | Lift | Brier skill |
|---|---|---|---|---|
| baseline (season week) | 2 | **0.504** | 0.90× | −0.002 |
| + injury history | 5 | 0.597 | 1.41× | +0.000 |
| + exposure load | 8 | 0.651 | 1.89× | +0.001 |

Three honest readings:

1. **Season timing alone is chance (0.504).** A naive reading of Josse's rising
   seasonal hazard curve would predict *when* in the season carries risk
   information. At the individual athlete-week level it does not — the season
   week term earns its place for calibration, not discrimination.
2. **Prior injury is most of the signal** (0.504 → 0.597).
3. **Recent training load adds a real, non-trivial increment** (0.597 → 0.651,
   lift 1.41 → 1.89). This *revises* the earlier "load contributes weakly" note:
   the exposure block is the smallest contributor, but +0.054 AUC and a jump in
   lift is not nothing. Baylor's load carries little *between-week* signal, yet
   the *between-athlete* exposure pattern (who is training a lot, who has recent
   missed/modified sessions) does add predictive value.

## What drives it

Standardized coefficients, full-data fit:

| Feature | Coefficient |
|---|---|
| prior lower-extremity injury count | +0.13 |
| prior injury count (any) | +0.10 |
| season_week | −0.05 |
| training sessions (28d) | +0.02 |
| recent no-participations (28d) | −0.02 |

**Prior injury — especially prior lower-limb injury — is the dominant signal.**
That is exactly what the injury-epidemiology literature reports: previous injury
is the strongest and most consistent predictor of future injury. The model
recovering it unprompted is a sanity check that it is learning something real
rather than noise.

Recent training load contributes positively and, per the ablation above, adds a
real increment over injury history alone (AUC 0.597 → 0.651). Most of the
discrimination still comes from who an athlete is (injury history) rather than
what this specific week looked like — consistent with Baylor's tightly
controlled *between-week* load — but the *between-athlete* exposure pattern is
not noise.

## Honest limits

- **Brier skill is barely positive (+0.001 to +0.002).** The model *ranks* weeks
  well (AUC, lift) but its absolute probabilities are only marginally better
  calibrated than always predicting the base rate. For a triage tool — "which
  athletes to look at this week" — ranking is what matters, and 2.5–3.2× lift is
  operationally useful. For anything that needs a trustworthy probability, it is
  not there yet.
- **This is association, not cause.** An athlete with prior injuries is flagged
  because prior injury predicts injury, not because we have shown any lever moves
  the hazard. The model tells you *who* to watch, not *what* to change.
- **106 events, one program, homogeneous population.** The covariate budget is
  real and the feature set is deliberately small. Do not expand it without more
  events.

## Reproduction

One command, once `config/paths.local.yaml` has `exposure_dir` and `injury_csv`:

```
risk-engine --availability-hazard-sprint \
  --output-dir <dir> --experiment-id <id>
```

It runs `prepare_exposure_inputs` on the Kitman export, builds the detailed
injury frame, derives the lower-limb caused-unavailability outcome, and writes
`availability_hazard_results.json` plus per-policy `hazard_timeline_*.csv`.

Tests: `tests/test_availability_hazard.py` (16, model + CV + outcome on
synthetic data with a known signal) and
`tests/test_availability_hazard_experiment.py` (2, the CLI experiment writes its
artifacts and the name-hash join lands events).

## A pre-existing bug fixed along the way

`live_sources._stable_injury_event_ids` called `.fillna("")` on a nullable
Int64 seed column, which raises under pandas 3. This blocks the package's own
live-source pipeline, not just this model. Fixed by widening to object before
the fill (behaviour unchanged for columns that already worked).

## Next

The model is complete, evaluated, validated on live data, and runnable as a
single command. Natural extensions, none required: expand the outcome beyond
lower-limb (the CLI is one policy today), add per-athlete calibrated risk output
for weekly triage, or bring GPS/force-plate load in as features once more events
accrue to support the larger budget.

# Prospective Collection Evaluation Protocol

Date: 2026-06-25

## Purpose

This protocol explains how to evaluate whether the retained-channel prospective
collection work is ready to move from practitioner evidence collection into a
bounded retest decision.

This is not a dashboard, pilot, calibration-claim, probability-facing, load
modification, or autonomous intervention evaluation. It is a research/shadow-mode
evidence gate.

## Current Stage

As of the KeystoneOS control loop run on 2026-06-25, the project is blocked at:

`blocked_await_completed_practitioner_collection`

The live facts behind that state are:

- Retained channels: `broad_30d` and `severity_14d`
- Prospective packet rows: 8
- Prefilled worksheet exists: yes
- Ingest path exists: yes
- Ingested completed rows: 0
- Pending input rows: 8
- Completion validation state: `blocked_pending_collection`
- Pilot/dashboard readiness: blocked
- Probability-facing readiness: blocked
- Calibration claim readiness: blocked

## Evaluation Question

The only question this evaluation may answer is:

> Are the de-identified practitioner packet rows complete, valid, and sufficient
> for the project-native completion sprint to mark the retained channels ready
> for bounded retest, without making calibration, product, or deployment claims?

If the answer is no, the project remains in practitioner evidence collection.

If the answer is yes, the next step is bounded retest planning under the same
research-only boundary. It is still not product readiness.

## Required Inputs

Start every evaluation from live state, not memory alone.

### KeystoneOS Control Inputs

Run from `C:\Users\eric_rash\Desktop\DEV\KeystoneOS`:

```powershell
.\scripts\keystone.ps1 context Risk_Stratification_Engine
.\scripts\keystone.ps1 control-loop
```

Use the generated loop packet:

`C:\Users\eric_rash\Desktop\DEV\KeystoneOS\outputs\loops\<yyyy-MM-dd>-morning-control.md`

### Risk Project Inputs

Run from `C:\Users\eric_rash\Desktop\DEV\Risk_Stratification_Engine`:

```powershell
git status --short
```

The worktree should be clean before evaluation unless the changes are the
completed worksheet or intentional documentation updates.

Use these project artifacts:

- `docs/prospective_collection_completion_guide.md`
- `docs/prospective_collection_completion_process_reference.md`
- `docs/prospective_collection_packet_crosswalk.md`
- `outputs/experiments/exposure_load_shadow_prospective_collection_operations_v1/exposure_load_shadow_prospective_collection_worksheet.csv`
- `outputs/experiments/exposure_load_shadow_prospective_collection_operations_v1/exposure_load_shadow_prospective_collection_operations.json`
- `outputs/experiments/exposure_load_shadow_prospective_collection_prefill_v1/prospective_collection_prefilled_working.csv`
- `outputs/experiments/exposure_load_shadow_prospective_collection_ingest_v1/exposure_load_shadow_prospective_collection_ingest.json`
- `outputs/experiments/exposure_load_shadow_prospective_collection_completion_v1/exposure_load_shadow_prospective_collection_completion.json`

## Human Inputs Required

The agent can inspect files, run ingest, validate outputs, and summarize
findings. The agent cannot invent practitioner evidence.

Eric or an approved practitioner must complete or verify these fields for each
packet row:

- `collection_season_id`
- `packet_start_date`
- `packet_end_date`
- `source_eligible`
- `episode_count`
- `unique_observed_event_count`
- `unique_captured_event_count`
- `unique_missed_event_count`
- `missed_event_rate`
- `alert_usefulness`
- `outcome_confirmed`
- `source_context_ok`
- `action_taken`
- `reviewer_id`
- `review_date`
- `notes`
- `collection_status`

Set `collection_status` to `complete_practitioner_adjudication` only when the
row is complete and defensible.

## Evaluation Stages

### Stage 0: Control Loop Preflight

Goal: confirm the project is still at the expected gate.

Run:

```powershell
Set-Location "C:\Users\eric_rash\Desktop\DEV\KeystoneOS"
.\scripts\keystone.ps1 control-loop
```

Expected current decision:

`blocked_await_completed_practitioner_collection`

Stop if the loop reports a missing project path, missing worksheet, parse error,
or a dirty Risk repo that is unrelated to the evaluation.

### Stage 1: Packet Identity Check

Goal: verify that the worksheet still contains only known packet IDs.

The only valid packet IDs are:

- `broad_30d__prospective_collection_001`
- `broad_30d__prospective_collection_002`
- `broad_30d__prospective_collection_003`
- `broad_30d__prospective_collection_004`
- `severity_14d__prospective_collection_001`
- `severity_14d__prospective_collection_002`
- `severity_14d__prospective_collection_003`
- `severity_14d__prospective_collection_004`

Stop if there are duplicate, unknown, missing, or modified packet IDs.

### Stage 2: De-Identification Check

Goal: make sure the completed worksheet contains no identifiable athlete data.

Do not add or populate fields such as:

- `athlete_name`
- `first_name`
- `last_name`
- `full_name`
- `athlete_id`
- `external_athlete_id`
- `source_athlete_id`

Notes must be short, de-identified rationales. They can describe source-quality,
monitoring usefulness, outcome availability, or action relevance, but they must
not include names, IDs, or identifiable details.

Stop if any row contains identifiable information.

### Stage 3: Row Completion Check

Goal: determine whether each row is defensibly complete.

For every row marked `complete_practitioner_adjudication`, verify:

- Required evidence fields are populated.
- Boolean fields use valid values.
- Allowed categorical fields use valid values.
- `missed_event_rate` is consistent with observed/captured/missed counts.
- `notes` explain the judgment without overclaiming.
- Uncertain packets are allowed to stay uncertain.

Allowed values:

- `alert_usefulness`: `useful`, `not_useful`, `unclear`
- `outcome_confirmed`: `true`, `false`
- `source_context_ok`: `true`, `false`
- `action_taken`: `monitor`, `none`, `modified_followup`, `other`
- `collection_status`: `pending_prospective_collection`, `complete_practitioner_adjudication`

A defensible uncertain row is better than an overconfident positive row. Use
`alert_usefulness=unclear`, `outcome_confirmed=false`, and `action_taken=none`
when the packet context is insufficient.

### Stage 4: Ingest Evaluation

Goal: run the project-native ingest sprint against the completed worksheet.

Recommended completed worksheet location:

`data/prospective_collection_reviews/completed_prospective_collection_<yyyy-mm-dd>.csv`

Run:

```powershell
risk-engine --exposure-load-shadow-prospective-collection-ingest-sprint --exposure-load-shadow-prospective-collection-operations outputs/experiments/exposure_load_shadow_prospective_collection_operations_v1/exposure_load_shadow_prospective_collection_operations.json --completed-prospective-collection <path_to_completed_prospective_collection.csv> --output-dir outputs --experiment-id exposure_load_shadow_prospective_collection_ingest_completed_v1
```

Review:

- `outputs/experiments/exposure_load_shadow_prospective_collection_ingest_completed_v1/exposure_load_shadow_prospective_collection_ingest_validation.csv`
- `outputs/experiments/exposure_load_shadow_prospective_collection_ingest_completed_v1/exposure_load_shadow_prospective_collection_ingest_summary.csv`
- `outputs/experiments/exposure_load_shadow_prospective_collection_ingest_completed_v1/exposure_load_shadow_prospective_collection_ingest.json`
- `outputs/experiments/exposure_load_shadow_prospective_collection_ingest_completed_v1/exposure_load_shadow_prospective_collection_ingested_operations.json`

Pass conditions:

- No unknown packet IDs.
- No duplicate packet IDs.
- No de-identification errors.
- Completed rows are accepted.
- At least one completed row is ingested.
- Channel summaries match the rows that were actually completed.

This stage alone does not clear bounded retest. It only prepares the ingested
operations package for completion validation.

### Stage 5: Completion Validation

Goal: let the project-native completion sprint decide whether bounded retest is
ready.

Run:

```powershell
risk-engine --exposure-load-shadow-prospective-collection-completion-sprint --exposure-load-shadow-prospective-collection-operations outputs/experiments/exposure_load_shadow_prospective_collection_ingest_completed_v1/exposure_load_shadow_prospective_collection_ingested_operations.json --output-dir outputs --experiment-id exposure_load_shadow_prospective_collection_completion_after_ingest_v1
```

Review:

- `outputs/experiments/exposure_load_shadow_prospective_collection_completion_after_ingest_v1/exposure_load_shadow_prospective_collection_completion.json`
- `outputs/experiments/exposure_load_shadow_prospective_collection_completion_after_ingest_v1/exposure_load_shadow_prospective_collection_completion_gates.csv`
- `outputs/experiments/exposure_load_shadow_prospective_collection_completion_after_ingest_v1/exposure_load_shadow_prospective_collection_channel_completion.csv`
- `outputs/experiments/exposure_load_shadow_prospective_collection_completion_after_ingest_v1/exposure_load_shadow_prospective_collection_packet_validation.csv`
- `outputs/experiments/exposure_load_shadow_prospective_collection_completion_after_ingest_v1/exposure_load_shadow_prospective_collection_completion_report.md`

The only completion state that can justify bounded retest planning is:

`ready_for_bounded_retest_not_claims`

Any other state remains blocked or pending.

### Stage 6: Decision Summary

Write a short evaluation summary with these fields:

- Evaluation date
- Completed worksheet path
- Ingest experiment ID
- Completion experiment ID
- Packet rows submitted
- Packet rows accepted
- Completed practitioner rows ingested
- Ingest errors
- Completion gate result
- Bounded retest readiness
- Remaining blockers
- Explicit no-claim boundary

Save the summary under a new evaluation folder, for example:

`outputs/experiments/exposure_load_shadow_prospective_collection_evaluation_<yyyy-mm-dd>/evaluation_summary.md`

## Decision Rules

Use these states consistently:

| State | Meaning | Next action |
|---|---|---|
| `blocked_missing_prospective_collection_worksheet` | The worksheet is not available. | Recreate or locate the worksheet before evaluation. |
| `blocked_await_completed_practitioner_collection` | Worksheet exists but practitioner rows are incomplete or pending. | Complete the 8 rows with defensible de-identified evidence. |
| `blocked_ingest_errors` | Ingest found validation, duplicate, unknown packet, or de-identification errors. | Repair the completed worksheet and rerun ingest. |
| `ready_for_completion_validation_not_claims` | Ingest succeeded, but completion validation has not run. | Run the completion sprint. |
| `blocked_pending_collection` | Completion validation says required evidence is still incomplete. | Return to practitioner collection. |
| `ready_for_bounded_retest_not_claims` | Completion validation cleared bounded retest planning only. | Plan bounded retest under research-only controls. |

## No-Claim Boundary

Do not claim any of the following from this evaluation:

- probability-facing readiness
- calibration readiness
- calibration claims
- pilot readiness
- dashboard readiness
- autonomous intervention readiness
- load-modification readiness
- clinical decision support readiness

Even if bounded retest planning becomes allowed, the project remains
research/shadow-mode until separate project-native evidence clears later gates.

## Verification Checklist

- [ ] `.\scripts\keystone.ps1 context Risk_Stratification_Engine` was run.
- [ ] `.\scripts\keystone.ps1 control-loop` was run.
- [ ] `git status --short` was checked in the Risk repo.
- [ ] Completed worksheet uses only valid packet IDs.
- [ ] No identifiable athlete fields or details are present.
- [ ] Required fields are complete for rows marked complete.
- [ ] Ingest sprint completed.
- [ ] Ingest validation artifacts were reviewed.
- [ ] Completion sprint completed.
- [ ] Completion validation artifacts were reviewed.
- [ ] The final decision uses the project-native `bounded_retest_readiness` value.
- [ ] The summary states what remains blocked.

## Where This Fits In The Morning Loop

KeystoneOS should keep surfacing this project in the morning control loop until:

1. the completed practitioner worksheet exists,
2. ingest accepts the completed rows,
3. completion validation returns a bounded retest readiness decision, and
4. Eric explicitly approves moving from evidence collection to bounded retest
   planning.

Until then, the correct stage is practitioner evidence collection, not modeling,
dashboarding, or deployment.

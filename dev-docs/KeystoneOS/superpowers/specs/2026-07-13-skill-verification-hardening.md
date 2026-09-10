# Skill Verification Hardening

## Objective

Raise output reliability by adding objective, domain-specific completion gates to the highest-impact producer skills and by preventing the local `skill-evaluator` from reporting unsupported scores.

## Scope

Update the relevant personal skills under `C:\Users\eric_rash\.agents\skills`. Keep those directories canonical; do not copy the skills into KeystoneOS.

The implementation covers:

- Power BI, diagram, HTML explainer, and slide output verification
- Research, authored-content, and voice-preservation checks
- Requirement traceability for PRDs, specs, and tickets
- Read-back validation for handoffs, memory, and ingested resources
- Objective grading for fact checking, design review, humanization, and idea pressure-testing
- Fail-closed behavior for `skill-evaluator`

## Contracts

### Correctness and quality

Report correctness and quality separately. A quality pass cannot hide a correctness failure. Every final verdict must identify the evidence observed, the checks not run, and the resulting `PASS`, `FAIL`, or `DEGRADED` state.

### Domain verification

- Power BI: require `reports:pbir-cli` validation plus rendered-page inspection; use `reports:review-report` for design and accessibility.
- Slides and visual artifacts: require machine-readable validation plus render inspection at supported viewports.
- Research and factual prose: verify material claims before stylistic rewriting and recheck any claim changed afterward.
- Specs and tickets: require bidirectional requirement traceability and an acyclic blocker graph.
- Handoffs and memory: require destination read-back and live verification of volatile state.

### Verifier integrity

Fail when declared resources are absent. Award rubric points only for observable evidence and cite that evidence for every score. Missing evidence is `UNVERIFIED`, not an implicit pass.

## Verification Plan

1. Run the skill-creator `quick_validate.py` against every edited skill.
2. Check every borrowed skill name exists in the installed catalog.
3. Confirm each edited producer contains explicit pass, fail, and degraded-verification rules.
4. Confirm `skill-evaluator` references no nonexistent scripts.
5. Review the final diff for concise, imperative instructions and unrelated changes.

## Acceptance Criteria

- Every scoped producer has an explicit final verification gate.
- Correctness and quality are reported separately where both apply.
- A missing verifier or unavailable rendering surface cannot silently become a pass.
- `skill-evaluator` emits no ungrounded numeric scores or phantom-resource claims.
- All edited skill folders pass structural validation.

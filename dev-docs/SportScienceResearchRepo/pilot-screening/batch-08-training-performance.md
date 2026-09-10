# Pilot Full-Text Screening — Batch 08

**Screened:** 12 local source PDFs

**Decision:** 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED

**Publication:** PUBLISHED as stable paper IDs 516–527

## Gate Result

All 12 local PDFs were present, content-unique within the batch, identity-matched, and eligible for synthesis. The 2003 hamstring paper's embedded font prevented clean PyPDF extraction, so its readable text, methods, results, and discussion were recovered with a Poppler text-extraction fallback. DOI metadata, study design, controlled taxonomy, quantitative claims, limitations, and practitioner cautions are recorded in `batch-08-training-performance.json`.

## Reviewed Primary-Domain Distribution

| Primary domain | Papers |
|---|---:|
| Sports Medicine & Injury | 3 |
| Brain Health & Psychology | 2 |
| Monitoring & Technology | 2 |
| Nutrition & Hydration | 2 |
| Training & Performance | 1 |
| Recovery & Readiness | 1 |
| Athlete Wellbeing | 1 |

## Decision Notes

1. **Localized muscle mass and sprint mechanics:** Include as cross-sectional, position-specific profiling evidence; regression coefficients do not justify isolated hypertrophy prescriptions.
2. **Collision-sport career and gait:** Include as a null cross-sectional finding in healthy collegiate men; normal gait does not establish cumulative head-impact safety.
3. **GPS feedback in professional soccer:** Include as stakeholder-perception evidence showing that purpose, communication, and information volume determine monitoring usefulness.
4. **Preseason eccentric-overload hamstring training:** Include as a small randomized trial with fewer injured players and improved strength and speed, while preserving the high control injury rate and missing exposure detail.
5. **Weekly workload and match output:** Include as two-team observational modeling evidence, not a causal microcycle formula.
6. **Cannabis use and sport:** Include as a systematic review with prevalence evidence but sparse, inconsistent performance evidence and no direct recovery evidence.
7. **Retired field-athlete cardiovascular health:** Include as mixed long-term evidence supporting transition screening, particularly for former high-body-mass roles.
8. **Achilles tendinopathy risk factors:** Include because all ten cohorts were high risk of bias and many commonly proposed screening factors were unsupported.
9. **Core temperature in intermittent sport:** Include as descriptive evidence that meaningful competition heat strain is common, without a universal illness threshold.
10. **Jugular compression collars:** Include as preliminary surrogate-outcome evidence; no concussion-incidence benefit and substantial manufacturer linkage preclude a prevention claim.
11. **Dehydration and cognition:** Include as a meta-analysis showing small overall and task-specific effects, while treating 2% body-mass loss as a subgroup pattern rather than a hard threshold.
12. **Multi-ingredient protein supplements:** Include because pooled benefits versus mixed controls did not translate into superiority over protein alone.

## Verification Verdict

- **Correctness: PASS** — source identities, DOI and print metadata, designs, sample sizes, quantitative findings, null findings, conflicts, and limitations were checked against each full text. The two DOIs absent from extracted PDF text were matched to their exact title, author, journal, volume, and page metadata.
- **Quality: PASS** — practical translations distinguish association from causation, perception from behavior, surrogate outcomes from clinical benefit, null findings from proof of safety, and mixed-control supplement effects from protein-specific superiority.

## Publication Result

The 12 eligible records were converted into `docs/pilot-synthesis/batch-08.json`, published to `papers.json` as stable IDs 516–527, and verified against their screening provenance. The active queue was regenerated to 96 unrepresented title-screened candidates for Batch 09.

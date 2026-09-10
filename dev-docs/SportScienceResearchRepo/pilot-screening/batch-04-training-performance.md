# Pilot Full-Text Screening — Batch 04

**Screened:** July 21, 2026<br>
**Queue:** Positions 1–12 after Batch 03 publication<br>
**Result:** 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED<br>
**Publication:** PUBLISHED as stable paper IDs 469–480

## Gate Result

All 12 local PDFs were readable, matched their source identities, and were eligible for synthesis. DOI metadata, study design, controlled taxonomy, material quantitative claims, limitations, and practitioner cautions were checked against the full texts in `batch-04-training-performance.json`.

## Reviewed Primary-Domain Distribution

| Primary domain | Papers |
|---|---:|
| Monitoring & Technology | 7 |
| Sports Medicine & Injury | 3 |
| Training & Performance | 2 |

## Material Taxonomy Corrections

- Strength asymmetry, rolling-window peak demand, weekly exposure, deceleration testing, broad-jump asymmetry, force-platform agreement, and saliva osmolality moved primarily to **Monitoring & Technology** because their central contribution is measurement interpretation.
- NFL prophylactic knee bracing, preseason exposure and subsequent injury, and the load–injury systematic review moved primarily to **Sports Medicine & Injury**.
- Intrinsic-foot strengthening and integrative neuromuscular training remained primarily **Training & Performance**, with injury and rehabilitation dimensions retained as secondary domains.

## Decision Notes

1. **Youth strength asymmetry:** Include as cross-sectional, metric-specific association evidence without a universal 15% threshold.
2. **Intrinsic-foot strengthening:** Include as a four-study systematic review with heterogeneous, low-certainty outcome evidence.
3. **NFL knee bracing:** Include as a confounded retrospective association in professional offensive linemen, not causal prevention evidence.
4. **Rolling versus fixed epochs:** Include as evidence that fixed windows understate peak locomotor demand relative to rolling averages.
5. **Weekly soccer load:** Include for identifying likely exposure gaps by match minutes and position, not for a fixed top-up dose.
6. **Preseason sessions and injury:** Include with low model fit and team-level confounding attached to the favorable association.
7. **Deceleration threshold method:** Include as protocol-specific reliability evidence, not criterion validity or injury prediction.
8. **Standing broad-jump asymmetry:** Include because raw performance was generally reliable while derived asymmetry was not.
9. **Hawkin Dynamics validity:** Include with the two-participant design and variable-specific fixed and proportional bias made explicit.
10. **Saliva osmolality and body composition:** Include as a null cross-sectional association; this does not establish standalone hydration validity.
11. **Integrative neuromuscular training:** Include as a favorable but heterogeneous meta-analysis whose local source is an unedited early-access manuscript.
12. **Training load and injury:** Include as broad prospective association evidence without a universal workload ratio or threshold.

## Verification Verdict

- **Correctness: PASS** — source identities, metadata, quantitative claims, and material cautions were verified against each local full text.
- **Quality: PASS** — findings are separated from inference, null findings and measurement bias are preserved, and practical statements remain within study scope.

## Publication Result

The 12 eligible records were converted into `docs/pilot-synthesis/batch-04.json`, published to `papers.json` as stable IDs 469–480, and verified against their screening provenance. The active queue was regenerated to 96 unrepresented candidates for Batch 05.

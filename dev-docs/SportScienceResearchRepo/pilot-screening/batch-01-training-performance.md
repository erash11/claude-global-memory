# Pilot Full-Text Screening — Batch 01

**Screened:** July 21, 2026<br>
**Original queue:** Positions 1–12, initially allocated to Training & Performance<br>
**Result:** 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
**Publication:** PUBLISHED as stable paper IDs 434–445

## Gate Result

All 12 local PDFs were readable, matched their source identities, and were eligible for evidence synthesis. Every record has a verified DOI, study-design decision, controlled taxonomy, evidence summary, limitation statement, and synthesis caution in `batch-01-training-performance.json`.

The full-text review exposed an allocation problem in the title-screened queue: the controlled domains were being returned in vocabulary order rather than evidence-strength order, and Training & Performance was processed first. That caused multi-domain papers to be assigned to Training even when the evidence question was primarily monitoring, recovery, rehabilitation, sports medicine, or nutrition.

## Corrected Primary-Domain Distribution

| Primary domain | Papers |
|---|---:|
| Training & Performance | 3 |
| Monitoring & Technology | 2 |
| Recovery & Readiness | 3 |
| Rehabilitation & Return to Sport | 1 |
| Sports Medicine & Injury | 1 |
| Nutrition & Hydration | 2 |

## Study-Design Corrections

- Queue 1 changed from `Other` to `Cohort Study`.
- Queue 8 changed from `Systematic Review / Meta-analysis` to `Consensus / Position Statement` because the publication combines a systematic review with a three-round Delphi consensus and is presented as a consensus statement.
- The other ten inferred designs were confirmed.

## Decision Notes

1. **Hip/groin monitoring:** Include as an implementation cohort; thresholds are not validated injury-prediction rules.
2. **Chronic cannabis:** Include as a thin null evidence base; four cross-sectional studies do not establish safety or benefit.
3. **ACWR/training monotony:** Include for descriptive monitoring; do not publish universal causal risk thresholds.
4. **Temperature/altitude:** Include as context-dependent match-planning evidence with inconsistent effects.
5. **Patellar fracture:** Include under Rehabilitation & Return to Sport; avoid treatment-superiority claims.
6. **Evening smartphone exposure:** Include under Recovery & Readiness; the 16-player male soccer trial needs replication.
7. **Seasonal workload/hormones:** Include as correlational monitoring evidence, not a readiness diagnostic.
8. **Neck training/HAEs:** Include under Sports Medicine & Injury; separate Delphi consensus from demonstrated efficacy.
9. **Capsaicinoids:** Include under Nutrition & Hydration; mixed, protocol-dependent findings do not support a blanket recommendation.
10. **Low-level laser therapy:** Include as promising recovery evidence; a definite therapeutic effect is not established.
11. **Melatonin:** Include under Nutrition & Hydration; biomarker changes are not direct performance improvement.
12. **Longer-muscle-length training:** Include under Training & Performance; hypertrophy inference is stronger than the proposed sarcomerogenesis mechanism.

## Verification Verdict

- **Correctness: PASS** — every screening claim was checked against the corresponding local full text.
- **Quality: PASS** — the batch covers source identity, eligibility, design, taxonomy, limitations, and synthesis cautions.

## Publication Result

The reviewed records were converted into `docs/pilot-synthesis/batch-01.json`, published to `papers.json` as stable IDs 434–445, and verified against their screening provenance. The balanced queue was regenerated after publication.

# Pilot Full-Text Screening — Batch 05

**Screened:** July 21, 2026<br>
**Queue:** Positions 1–12 after Batch 04 publication<br>
**Result:** 11 INCLUDE, 1 EXCLUDE, 0 DEGRADED<br>
**Publication:** PUBLISHED as stable paper IDs 481–491

## Gate Result

Eleven local PDFs were readable, matched their source identities, and were eligible for synthesis. One file was excluded because its full text did not match the healthy-weight-gain paper named by the filename. DOI metadata, study design, controlled taxonomy, quantitative claims, limitations, and practitioner cautions are recorded in `batch-05-training-performance.json`.

## Reviewed Primary-Domain Distribution

| Primary domain | Papers |
|---|---:|
| Sports Medicine & Injury | 3 |
| Monitoring & Technology | 2 |
| Training & Performance | 2 |
| Brain Health & Psychology | 1 |
| Nutrition & Hydration | 1 |
| Athlete Wellbeing | 1 |
| Rehabilitation & Return to Sport | 1 |

## Source-Identity Exclusion

- `A randomized trial of healthy weight gain in athletic individuals.pdf` was excluded. The local PDF actually contains *A randomized, double-blind, placebo-controlled, repeated-dose pilot study of the safety, tolerability, and preliminary effects of a cannabidiol (CBD)- and cannabigerol (CBG)-based beverage powder to support recovery from delayed onset muscle soreness (DOMS)* (DOI `10.1080/15502783.2023.2280113`).

## Decision Notes

1. **Cannabis in young athletes:** Include as a level-4 clinical review that does not support performance enhancement and highlights health and mental-health risks.
2. **Healthy weight-gain filename:** Exclude because the full text is an unrelated cannabinoid recovery pilot.
3. **Hormones and sweat sodium:** Include as a small correlational study without a hormone-based sodium prescription.
4. **Change-of-direction versus deceleration deficit:** Include as task-specific measurement evidence; dominance and asymmetry did not transfer reliably.
5. **Starter versus nonstarter workload indices:** Include as one-team exposure evidence without injury prediction or universal cutoffs.
6. **Isokinetic ratios and hamstring prediction:** Include as a null prediction study; common and cohort-specific cutoffs failed.
7. **Hamstring exercises versus sprinting:** Include for exercise selection; electromyographic activity did not reproduce sprint muscle-length demands.
8. **Subjective-questionnaire honesty:** Include as qualitative evidence that compassion, emotion, and staff relationships shape disclosure.
9. **Pectoralis-major tackle cluster:** Include as a three-case implementation warning, not causal technique evidence.
10. **Hamstring-training practice:** Include as qualitative implementation evidence rather than comparative efficacy evidence.
11. **Blood-flow-restriction safety:** Include with rare events, reporting gaps, screening, and knee-dominant evidence made explicit.
12. **Resistance training for lower-body power:** Include as a heterogeneous method review supporting multiple context-dependent options.

## Verification Verdict

- **Correctness: PASS** — source identities, metadata, quantitative claims, null findings, adverse events, and cautions were checked against each local full text.
- **Quality: PASS** — practical translations remain within study scope and distinguish measurement, association, qualitative experience, safety reporting, and efficacy.

## Publication Result

The 11 eligible records were converted into `docs/pilot-synthesis/batch-05.json`, published to `papers.json` as stable IDs 481–491, and verified against their screening provenance. The active queue was regenerated to 96 unrepresented candidates for Batch 06.

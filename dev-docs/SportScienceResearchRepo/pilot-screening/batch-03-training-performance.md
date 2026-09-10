# Pilot Full-Text Screening — Batch 03

**Screened:** July 21, 2026<br>
**Queue:** Positions 1–12 after Batch 02 publication<br>
**Result:** 11 INCLUDE, 1 EXCLUDE, 0 DEGRADED<br>
**Publication:** PUBLISHED as stable paper IDs 458–468

## Gate Result

Eleven local PDFs were readable, matched their source identities, and were eligible for synthesis. One file was excluded after full-text verification showed that its content did not match the paper named by the filename. The reviewed records include DOI verification, controlled taxonomy, study-design decisions, evidence summaries, limitations, and synthesis cautions in `batch-03-training-performance.json`.

## Reviewed Primary-Domain Distribution

| Primary domain | Papers |
|---|---:|
| Training & Performance | 2 |
| Sports Medicine & Injury | 4 |
| Monitoring & Technology | 2 |
| Rehabilitation & Return to Sport | 1 |
| Recovery & Readiness | 1 |
| Nutrition & Hydration | 1 |

## Source-Identity Exclusion

- `Metabolic power in team and racquet sports - A systematic review with best-evidence synthesis.pdf` was excluded. The local PDF actually contains *Metabolic Consequences of Anabolic Steroids, Insulin, and Growth Hormone Abuse in Recreational Bodybuilders: Implications for the World Anti-Doping Agency Passport* (DOI `10.1186/s40798-024-00697-6`). Publishing it under the filename identity would misrepresent the source.

## Decision Notes

1. **NFL multi-sport participation:** Include as a selected first-round-pick cohort; high-school multi-sport status was common, but the study did not show career or injury differences.
2. **Performance-enhancing drugs:** Include as an umbrella review; agent-specific benefits and harms must remain separated, and evidence quality was limited.
3. **Metabolic power review filename:** Exclude because the full text is an unrelated hormone-doping study.
4. **Biologics in NFL athletes:** Include as expert consensus, not comparative efficacy evidence.
5. **Association-football performance analysis:** Include as a map of 2012–2016 research themes rather than validation of specific practitioner methods.
6. **First-time sprinting hamstring strains:** Include as a small elite-sprinter case series; proximal free-tendon involvement and injury extent were associated with longer recovery.
7. **Hip-groin pain and strength:** Include as cross-sectional association evidence without causal or predictive thresholds.
8. **Sleep, load, and illness:** Include as a small observational Australian-football cohort; acute sleep quantity remained associated with illness after adjustment.
9. **Isometric neck strength reliability:** Include as measurement-reliability evidence; devices and early force-development measures are not interchangeable.
10. **Elite-team-sport acceleration and deceleration:** Include as a heterogeneous systematic review without a universal optimal dose.
11. **Mediterranean diet and performance:** Include as a low-certainty systematic review with a null pooled performance estimate.
12. **Strength-training adherence and injury:** Include with studied-program context; the pooled injury reduction does not establish a single best component or dose.

## Verification Verdict

- **Correctness: PASS** — eligibility, source identity, quantitative claims, and cautions were checked against each local full text.
- **Quality: PASS** — all included records separate study findings from practitioner translation and preserve material limitations; the mislabeled source was excluded.

## Publication Result

The 11 eligible records were converted into `docs/pilot-synthesis/batch-03.json`, published to `papers.json` as stable IDs 458–468, and verified against their screening provenance. The active queue was regenerated to 96 unrepresented candidates for Batch 04.

# QB accuracy analysis and the 2025 national benchmark (2026-09-07)

Deliverables in `Week_1_AUB/`:
- `2026-09-07_Auburn-Baylor_QB-Accuracy-Review_Baylor-Design_AgencyFB.docx`
- `2026-09-07_Auburn-Baylor_QB-Accuracy-Review.html` (static, self-contained, validated charts)
- `2026-09-07_Auburn-Baylor_PFF-Charting-Review-v4_Baylor-Design_AgencyFB.docx`

**All PFF premium feeds for game 31098 are complete.** `quarterback_charting` finished at
102 rows (59 Baylor / 43 Auburn) on the evening of 2026-09-07. It populated one team at a
time: Auburn only that morning.

## The answer to "why 52% catchable"
**Man coverage.** Auburn played Single on 29 of 55 charted Baylor dropbacks (53%) against a
30.4% 2025 baseline, paired with a 48% blitz rate.

| | vs man (29) | vs zone (26) |
|---|---|---|
| Yards per attempt | **4.4** | 7.9 |
| Catchable rate | **31%** | 77% |
| On-target rate | **28%** | 65% |
| Tight-window rate | **59%** | 4% |

Chain: man coverage → tight windows on 59% of snaps → **Lagway 1 of 18 on-target into tight
windows** (18 of 28 with separation) → first read on 88% of dropbacks so no second answer.

Other: pressured on-target 25% vs clean 51%. Misses skew high/long 12 to 6. Iso looks (the man
beaters) produced 2.3 y/att right and 0% on-target in the middle of the field. Half left was the
best neighborhood at 8.6.

## Keys change
Man-coverage key **restored** in `keys_grader.py` via `quarterback_charting.coverage_type`
(Single, Single with help = man). Week 1: **explosives vs man = 2, HITS the target of 2.**
Added companion **catchable rate vs man, 65%+**, which MISSES at 33%. The lesson: a key that
passes while the thing it measures is failing needs a process companion.

## 2025 BENCHMARK (new, 2026-09-07)
`GET /v1/premium/ncaa/2025/quarterback_charting` returns the **whole season nationally**:
73,838 rows, 846 passers, 38 MB in one response. Cached at `/tmp/qc2025.json`; move it into
the project before relying on it. Script: `data/week1_auburn/bench2025.py`.

**Lagway was at Florida (FLUN) in 2025, 399 charted dropbacks.**

### Lagway 2025 vs Week 1 2026
| Metric | 2025 (399) | Wk1 2026 (59) | Change |
|---|---|---|---|
| On-target | 49.0% | 43.9% | -5.1 |
| **Man coverage faced** | 26.1% | **52.7%** | **+26.6** |
| **Tight-window rate faced** | 17.5% | **32.7%** | **+15.2** |
| On-target into tight | 8.5% | 5.6% | -2.9 |
| On-target vs man | 36.4% | 27.6% | -8.8 |
| First read | 78.5% | 87.9% | +9.4 |

### National rank, 141 qualified passers (200+ charted dropbacks)
| Metric | Value | Rank | Percentile |
|---|---|---|---|
| On-target | 49.0% | 73 of 141 | 49th |
| **On-target into tight windows** | **8.5%** | **121 of 141** | **15th** |
| On-target vs man | 36.4% | 39 of 141 | 73rd |
| First-read rate (lower better) | 78.5% | 91 of 141 | 36th |
| Tight-window rate faced (lower better) | 17.5% | 46 of 141 | 68th |

**The headline: the tight-window weakness is not new.** He was 15th percentile nationally at
it in 2025. What changed is that Auburn doubled how often he faced one, by doubling man
coverage. **Auburn did not discover a weakness, they found it on 2025 tape and attacked it
twice as often.** Every opponent can now do the same.

### Sawyer Robertson 2025 (Baylor, 589 dropbacks), the QB Lagway replaced
On-target 43.0%, **man faced 42.5%**, on-target vs man 26.8%, first read 73.0%,
tight rate 24.8%, on-target into tight 11.3%.

**Baylor's offense already saw 42.5% man in 2025 with a different quarterback.** So the man
problem is at least partly systemic to the scheme and the receivers, not only the QB. Auburn's
52.7% is elevated but not out of character for what this offense gets.

### Top 5 by on-target rate, 2025 qualified
1. Carson Beck (Miami) 60.7 · 2. Julian Sayin (Ohio St) 60.3 · 3. Brad Jackson (TXSW) 60.1 ·
4. Haynes King (Georgia Tech) 56.8 · 5. Derek Robertson (NJMO) 56.8. Lagway 73rd at 49.0.

**Caveat on ranking basis:** raw on-target rate rewards checkdown-heavy quarterbacks who never
throw into traffic. Beck at #1 faced tight windows on 16.1%; Derek Robertson at #5 faced 20.0%
and was 18.2% on-target into them. A fair benchmark needs the tight-window rate faced alongside
the accuracy number, which is why the table above carries both.

## Open items
- Decide the ranking basis for the ongoing benchmark.
- Move `/tmp/qc2025.json` into the project and build a reusable percentile table.
- Season endpoints exist for every premium category, so this benchmark approach generalizes
  beyond the quarterback.

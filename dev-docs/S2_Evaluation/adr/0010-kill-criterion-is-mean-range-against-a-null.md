# The kill criterion is mean category range tested against a null, not a share of "dispersed" athletes

ADR 0001 fixed the *form* of the kill criterion as "fewer than roughly 30% of
athletes showing meaningful dispersion falsifies the premise," leaving the
number pending the schema. With the schema known — nine skill categories plus an
S2 composite, on a percentile scale — that form turns out to be vacuous.

Simulating nine independent categories with no real profile at all: the expected
range is **2.97 SD**, and **89% of pure-noise athletes clear a 2.0 SD range**.
A gate on "athletes show spread" would therefore have passed even if the
instrument measured nothing but random error. It would have rubber-stamped the
project rather than tested it.

**Revised criterion.** Gate on the **mean category range across the room**,
proceeding only if it is **>= 2.5 SD**. Reference points from simulation:

| Structure | Mean range |
|---|---|
| Categories independent — composite hides a great deal | 2.97 SD |
| Moderately redundant, r ~ 0.5 | 2.10 SD |
| One dominant factor, r ~ 0.8 — composite says it all | 1.33 SD |

2.5 SD sits near the point where average inter-category redundancy reaches
roughly 30%. Below it, the composite substantially captures the profile and the
premise of this project is false.

## Relationship to earlier ADRs

This supersedes the *form* of the criterion in ADR 0001, not its principle: the
threshold is still fixed in advance of examining any athlete's results, and this
ADR is committed before extraction for that reason.

It deliberately relies on the mean of sixteen numbers rather than a nine-by-nine
correlation matrix, which would repeat the small-n instability that ADR 0006
rejected Mahalanobis distance for.

## Consequences

This tests whether the composite **hides** variation. It does not test whether
that variation is **valid** — construct validity remains an open question for
the parallel research track, and the write-up must not blur the two.

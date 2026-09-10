# The 1.5 SD flagging threshold was uncalibrated; the Room Deviation finding is null

ADR 0008 fixed the flag at 1.5 population SD from the room mean on any single
category. Applied literally to the fifteen linemen, it flags ten.

Ten of fifteen is not a finding. The threshold repeats the error ADR 0010 caught
in the original kill criterion: it takes a **maximum across nine categories**
without accounting for the inflation that maximum introduces.

Simulating a homogeneous room — same n, same nine categories, same observed
within-room spread, containing no atypical athlete by construction — a 1.5 SD
rule flags **69%** of athletes, with a central 90% interval of 7 to 13 of 15.
The observed 10 sits squarely inside that interval and carries no information.

At stricter thresholds the room is *less* extreme than chance:

| Threshold | Null flag rate | Observed |
|---|---|---|
| 1.5 SD | 69% | 10 / 15 |
| 2.0 SD | 33% | 2 / 15 |
| 2.5 SD | 11% | 0 / 15 |
| 3.0 SD | 3% | 0 / 15 |

**The finding is null.** No offensive lineman deviates from the room beyond what
normal variation produces. This is reported as the result, exactly as ADR 0008's
consequences pre-committed: "An absolute threshold can return zero flagged
athletes. That is a real result."

## What is NOT being done

The threshold is not being retuned to produce a more interesting answer. The
pre-registered rule was applied, its output is reported, and its calibration is
reported alongside. Any future flagging rule must be calibrated against a
homogeneous-room null *before* use — a threshold chosen on intuition is
worthless when the statistic is a maximum over many categories.

## Consequences

The room's within-category spread is about as wide as the general population
(mean SD 0.98), so position selection has not compressed these traits. What is
absent is any individual standing outside that spread.

The surviving result is at room level, not individual level, and it is weak:
of nine categories, only visual learning approaches a difference from the
NFL-prospect norm (z=-0.40, p=0.009), and that does not survive Bonferroni
correction across nine comparisons (alpha 0.0056). The room composite sits at
the 44th percentile.

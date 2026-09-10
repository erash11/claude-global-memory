# The go/no-go reviewer is the author

Sports science internal — the tier-1 audience — resolves to a single person, who
is also the person performing the analysis. There is no external requester and
no second reader. The go/no-go on whether this work continues is self-assessed.

This is recorded because it explains why an analysis of one position group
carries this much pre-registration machinery. ADRs 0001, 0007 and 0008 are not
ceremony. With no outside reviewer, those fixed thresholds are the only thing
standing between exploratory analysis and motivated reasoning.

## Consequences

The thresholds are load-bearing and must be committed to version control
**before** the CSV is obtained. A timestamped commit converts "the threshold was
set in advance" from a claim into a verifiable fact — which matters most when
the only person who could verify it is the same person who set it.

Recruiting even a light-touch second reader before v1 is published would
materially strengthen the result, and remains open.

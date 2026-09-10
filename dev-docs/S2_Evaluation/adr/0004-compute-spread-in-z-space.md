# Compute spread in z-space, report in percentile language

Percentile scales are non-linear: a ten-point gap near the 95th represents a far
larger true difference than the same gap near the 50th. Computing any spread
measure directly on percentile values systematically understates it in the
extreme athletes — precisely the ones the project exists to find.

All spread and deviation arithmetic is therefore done on percentiles converted
to z-scores via the inverse normal, with results translated back into percentile
language for the reader.

## Consequences

This assumes the underlying normative distribution is approximately normal. That
is standard for instruments of this kind but is an assumption, and it must be
stated in the write-up rather than buried.

A useful second-order effect: in z-space the normative population standard
deviation is 1 by construction, so Room Deviation can be expressed in
population-SD units from the room mean alone. The room's own standard deviation
— which would be badly estimated from a single position group — never needs to
be computed.

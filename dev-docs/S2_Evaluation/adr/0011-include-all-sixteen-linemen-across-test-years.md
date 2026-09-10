# Include all sixteen linemen despite mixed test years; flag year as a diagnostic

Eleven offensive linemen tested on 2026-07-08. The remaining five tested in
2022, 2024 and 2025. The design assumed a contemporaneous room and did not
anticipate a four-year spread.

All sixteen are included. Test year is recorded as an attribute and checked
against Room Deviation as a diagnostic.

This follows the principle already settled in ADR 0005 — flag, do not filter —
and restricting to the 2026 cohort would discard five of sixteen athletes, about
30% of the room, weakening the very room mean the finding depends on.

## Consequences

Four years is real developmental time for a nineteen-year-old, and this is a
genuine confound rather than a hypothetical one. If Room Deviation turns out to
track test year, that finding is reported and the cohort decision is revisited —
it is not to be explained away. The diagnostic must be run and its result stated
whichever way it comes out.

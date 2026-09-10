# Exclude the one vendor-invalidated report; surface it as a retest recommendation

One of the sixteen offensive line reports is stamped INVALID by S2 itself:
"Report did not pass data validity checks - 6 task(s) did not pass validity
checks." Seven of its ten values, including the composite, are N/A. It is the
only flagged report among all ninety-nine.

That athlete is excluded from the analysis. A nine-category range cannot be
computed from three categories, so this is a forced consequence of the data
rather than a choice between alternatives. The room stands at fifteen, which
still clears the floor of ten set in ADR 0007.

## Why this does not contradict ADR 0005

ADR 0005 refuses to filter on roster status because doing so would define the
typical lineman as whoever the staff already selected — a circularity. Vendor
validity is an external, instrument-level fact carrying no selection bias.
Excluding on it does not encode anyone's judgement about who is good.

## Consequences

The athlete is excluded from analysis but not made invisible. The write-up
reports that sixteen linemen have S2 data, that one report failed the vendor's
own validity checks, and that a retest is recommended. An athlete silently
dropped is a worse outcome than one openly flagged.

No threshold set in ADR 0007, 0008 or 0010 is altered by this.

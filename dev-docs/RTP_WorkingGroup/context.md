# RTP Working Group — transferred project context

Carried over from the Claude cloud project, Sept 2026.

## Two connected domains

The work is not one project. It is data infrastructure and reporting for force plate
athlete monitoring, plus organizational frameworks (OKRs) that standardize assessment,
benchmarking, and staff operations across the working group. They constrain each other.

Collaborators are Applied Performance staff. Athlete population is multi-sport.

## Supporting documentation that exists

`context.md` covering project scope and architecture, spec files for each report
template, and a Word metric appendix covering 12 metrics with plain-language descriptions.

## Current OKR state

OKR development for the Intake/Assessment pillar is underway, using Andy Grove /
John Doerr methodology.

## The timing pressure

Near-term pressure to evaluate current athletes for year-end player valuations while
simultaneously establishing the benchmarks that make those evaluations meaningful.

This is the bootstrap problem: benchmarks have to exist before evaluations mean anything.
The phased answer is an emergency assessment sprint, then benchmark development, then
full workflow. Do not skip to full workflow.

## Data resolution rules

ForceDecks exports contain ambiguities that need explicit rules rather than case-by-case
judgment. Duplicate same-date entries with different rep counts: default to the
higher-rep session.

Asymmetry gets reported with direction, "X.X% L" or "X.X% R", never magnitude alone.

Plain-language translation of complex metrics is a priority for anything that reaches a
practitioner or coach.

## Working patterns

- Concise documentation over verbose
- Build in layers: automation first, then visualization, then integration
- Fireflies for meeting transcript retrieval, using keyword plus date filter syntax

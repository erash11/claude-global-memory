# Ask the Library Product Contract

**Status:** Confirmed through `grill-with-docs` on July 22, 2026; interaction prototype approved July 23, 2026

This document is the consolidated product contract for prototyping Ask the Library. Canonical language lives in [`../CONTEXT.md`](../CONTEXT.md), and durable trade-off decisions live under [`adr/`](adr/).

## Product promise

Ask the Library is a Baylor-staff-only decision-support workspace built on the public Baylor Athletics Health & Performance Evidence Library. A staff member submits a Practical Question and optional de-identified Decision Context; the workspace returns a structured, source-grounded Decision Brief rather than a free-form chatbot answer.

The brief informs professional judgment. It does not diagnose, prescribe treatment, make clearance decisions, or become Baylor policy merely because it was generated or reviewed.

## Access and context

- The Public Evidence Library remains openly accessible.
- The Ask the Library Workspace requires authenticated Baylor staff access.
- Staff may provide de-identified context such as sport, population, training or rehabilitation phase, injury category, intended outcome, and operational constraints.
- Athlete names, medical records, clinical notes, protected health information, and other identifying athlete data are prohibited.
- On-Demand Briefs are private to the requester by default.

## Evidence and trust contract

- V1 is grounded only in evidence resources already included in the Evidence Library.
- All published Evidence Library records may support retrieval, but every substantive claim must be checked against original source text before inclusion.
- Reviewed Zotero publications may resolve original source pages through the read-only bridge; unreviewed Zotero
  records, metadata-only records, and Reference Stubs are not Evidence Library sources.
- Existing summaries and taxonomy are retrieval aids, not sufficient evidence for a claim.
- Sources whose original text cannot be accessed may be presented as relevant leads but cannot support the synthesis.
- If the library lacks sufficient relevant evidence, the result is a Coverage Gap rather than an answer supplemented by model knowledge or unreviewed web content.
- Material Evidence Tension is shown explicitly and never averaged into artificial consensus.

## Guided interaction

- Guided Intake starts with a plain-language Practical Question.
- Population, sport, phase, intended outcome, and constraints are optional structured fields.
- The workspace may ask at most one optional clarifying question when missing Decision-Critical Context could materially change the answer.
- If clarification is skipped, the brief states its assumptions and adjusts applicability or confidence when necessary.
- V1 does not include open-ended follow-up chat. Editing the question or context creates a versioned Brief Revision.

## Decision Brief

The default Operational View is designed for approximately two minutes of reading and presents:

1. Bottom line
2. Recommended Direction when permitted
3. Evidence Confidence and its visible rationale
4. Applicability to the supplied Decision Context
5. Immediate actions, guardrails, and monitoring considerations
6. Critical limitations and what could change the conclusion
7. Evidence Tension when present
8. Traceable supporting sources

Expandable sections contain the deeper synthesis, source excerpts, confidence rationale, and full citations.

Evidence Confidence uses explained tiers rather than a numerical score:

- **Higher:** may support a Recommended Direction.
- **Moderate:** may support a conditional Recommended Direction.
- **Limited:** presents options without selecting a preferred course.
- **Coverage Gap:** makes no recommendation and identifies missing evidence.

Material Evidence Tension prevents Higher confidence. Context-resolved tension may support a conditional direction with at most Moderate confidence; unresolved tension results in Limited confidence and no Recommended Direction.

## Lifecycle and governance

- An On-Demand Brief is immediately available without human approval and is marked as not expert-reviewed.
- A requester may create a Controlled Share that permanently preserves review status, creation date, Decision Context, Evidence Confidence, and citations. Public anonymous links are disabled.
- A requester may submit an On-Demand Brief as a Review Candidate.
- Automated gates verify source identity, citations, and required fields.
- One accountable Domain Reviewer confirms interpretation, applicability, and practical language before promotion; no committee or second sign-off is required.
- A Reviewed Brief becomes reusable organizational knowledge but is not automatically Baylor policy.
- The workspace offers a close Reuse Match before generating another brief.
- Reviewed Briefs retain reviewer, review date, evidence provenance, and version history.
- A Reviewed Brief is marked Refresh Due after 12 months or when newly added, directly relevant evidence could materially change it. Older versions remain visible.

## Learning loop

Each brief may collect lightweight Use Signals:

- Was this useful? Yes or no.
- Did this influence a decision? Yes, not yet, or no.
- Optional comment or submission for review.

Use Signals improve the product and prioritize reviewed knowledge. They are not athlete outcomes, validation evidence, or staff-performance metrics. Usage volume and time in the application are diagnostic rather than primary success measures.

## Minimum Viable Pilot

The smallest credible pilot is:

- Three staff
- At least two functional disciplines
- Nine real Practical Questions, three per participant
- Two weeks

The pilot warrants expansion only when:

- All nine briefs receive a claim-and-citation audit.
- No unresolved critical Evidence Integrity failure remains.
- At least seven briefs are rated useful.
- At least two participants would use the tool again.
- At least one brief informs or confirms a real decision.

This pilot tests whether the concept merits broader evaluation. It does not establish department-wide readiness or athlete-level effectiveness.

The first implementation will use the Concierge Pilot defined in [`ask-library-pilot/README.md`](ask-library-pilot/README.md). This preserves real questions, the approved Decision Brief experience, and complete evidence auditing while leaving authentication, storage, retrieval, and model choices reversible until the expansion gates are met.

## V1 non-goals

- Open-ended chatbot interaction
- Web-wide evidence search
- Athlete-identifying data or clinical-record ingestion
- Diagnosis, treatment prescription, or clearance decisions
- Automatic publication of briefs or evidence sources
- Treating an On-Demand or Reviewed Brief as institutional policy
- Measuring staff performance or athlete outcomes

## Deferred implementation choices

The prototype should keep these choices reversible until technical research and usability evidence justify them:

- Baylor authentication provider and authorization model
- AI model and orchestration framework
- Full-text extraction, retrieval, and citation architecture
- Private question and brief storage
- Hosting and operational monitoring
- Cost controls and usage limits

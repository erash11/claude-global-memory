# Ask the Library minimum credible pilot

**Status:** Ready for controlled operator use
**Issue:** [#1 — Operationalize the Ask the Library minimum credible pilot](https://github.com/erash11/SportScienceResearchRepo/issues/1)

## Start here

- Begin with [`START-HERE.md`](START-HERE.md). It reduces the entire workflow to **staff asks → Codex prepares → staff reviews** and gives the exact local files and buttons.
- Share the ready-to-send [`Ask-the-Library-Pilot-Participant-Quick-Start.docx`](Ask-the-Library-Pilot-Participant-Quick-Start.docx) with pilot participants. The plain-text source is [`participant-quick-start.md`](participant-quick-start.md).
- Select three of the four discipline tracks in [`Ask-the-Library-Pilot-Stress-Test-Question-Bank.docx`](Ask-the-Library-Pilot-Stress-Test-Question-Bank.docx). Each selected track contributes one simple, one applied, and one complex question, preserving the nine-question pilot. Its source is [`stress-test-question-bank.md`](stress-test-question-bank.md), with structured copy-ready fields in [`examples/stress-test-question-bank.json`](examples/stress-test-question-bank.json).
- Use [`pilot-lead-distribution-runbook.md`](pilot-lead-distribution-runbook.md) to deliver the pilot without asking staff to install software or use the repository.
- Use [`codex-request-handoff.md`](codex-request-handoff.md) for the exact request-to-Codex prompt and file handoff.

## Why this is the next step

The approved interaction prototype establishes the desired experience, but it does not establish that staff will use Decision Briefs or trust them enough to inform real decisions. The smallest honest test is therefore a concierge pilot: preserve the staff-facing experience while a named operator handles synthesis and evidence auditing behind it.

This avoids premature investment in authentication, private storage, cloud retrieval, and an AI provider. It tests the two outcomes that determine whether those investments are warranted:

1. **Decision Utility** — staff find the briefs useful, would reuse the tool, and use at least one brief to inform or confirm a real decision.
2. **Evidence Integrity** — every substantive claim and citation remains faithful to original source text.

## Pilot contract

| Dimension | Minimum |
|---|---|
| Duration | 14 calendar days |
| Participants | 3 staff |
| Functional breadth | At least 2 disciplines |
| Questions | 9 real Practical Questions, 3 per participant |
| Audit | All 9 briefs receive claim-and-citation audit |
| Utility | At least 7 of 9 briefs rated useful |
| Reuse | At least 2 of 3 participants would use Ask the Library again |
| Decision influence | At least 1 brief informs, confirms, or changes a real decision |
| Integrity stop rule | No unresolved critical Evidence Integrity failure |

Passing these gates warrants a secure self-service build; it does not validate department-wide rollout or athlete outcomes.

## Roles

- **Pilot lead:** selects three participants, assigns anonymous participant IDs, protects the scope, and makes the expansion decision.
- **Brief operator:** receives de-identified request packets, retrieves Evidence Library sources, drafts the brief, and runs automated gates.
- **Claim auditor:** checks whether each claim is supported by the cited source excerpt and whether the interpretation is faithful. The operator and auditor may be the same person for this pilot, but the audit must be recorded.
- **Participant:** submits three real questions and supplies the lightweight Use Signals.

A Domain Reviewer is needed only if a brief is later promoted to a Reviewed Brief. Pilot delivery does not confer reviewed status.

## Private-data rule

Use anonymous participant IDs such as `P01`. Do not enter or retain athlete names, medical records, clinical notes, dates of birth, contact information, or other identifying data. If identifying data appears:

1. Stop processing the request.
2. Delete the private working copy.
3. Ask the participant to resubmit a de-identified Practical Question.
4. Do not include the incident content in the scorecard.

Private pilot material belongs under `pilot-data/ask-library/private/`, which Git ignores. Do not commit it. Synthetic examples belong under `examples/`.

## Operating workflow

### 1. Capture the request

Start the approved local experience by double-clicking `START-ASK-THE-LIBRARY.cmd` in the repository root. The command-line equivalent is:

```powershell
npm run pilot:start
```

The main page has three different actions:

- **Open practice answer** opens the same canned congested-week example every time. It is practice only and does not process the question entered on the page.
- **Save question for Codex** packages the real question and Decision Context into a de-identified request JSON.
- **Choose finished answer file** is used later for the finished answer JSON. It does not accept a request packet or the question-bank JSON.

For a real question, copy an assigned Practical Question and its five Decision Context fields from the question bank, or enter another relevant de-identified question. Select **Save question for Codex** and save the resulting `ATL-R-*.json` file under:

```text
pilot-data/ask-library/private/requests/
```

The structured question-bank JSON is a copy source only. It is not itself a request packet and is not uploaded to the prototype.

Validate it:

```powershell
npm run pilot:request -- pilot-data/ask-library/private/requests/<request>.json
```

As long as the prototype command remains running, select **New question** for the next request. There is no need to rerun the command for every question.

### 2. Give the request to Codex and prepare the Decision Brief

Attach the request JSON to a Codex task, drag it into the message, or provide its exact local path. Use the prompt in [`codex-request-handoff.md`](codex-request-handoff.md). The request is not sent automatically when it is downloaded.

Use `examples/brief.example.json` as the structural template.

- Retrieve from the Evidence Library only.
- Use summaries and taxonomy to locate candidates, never as the sole support for a claim.
- Record the source-library ID, exact local source filename, PDF page, and a short verbatim excerpt for each substantive claim.
- Use a Coverage Gap when accessible library sources cannot support a brief.
- Keep the Recommended Direction `null` for Limited confidence or a Coverage Gap.
- Preserve On-Demand / Not Expert-Reviewed status.

Validate policy and structure:

```powershell
npm run pilot:brief -- pilot-data/ask-library/private/briefs/<brief>.json
```

Check excerpts against the local PDFs:

```powershell
npm run pilot:audit-source -- pilot-data/ask-library/private/briefs/<brief>.json
```

`pdftotext` must be available on `PATH` for the source-text audit.

### 3. Complete the human claim audit

Codex can perform the structural validation and the mechanical original-source excerpt audit. That does not replace the named human claim audit.

For every bottom line, direction, action, guardrail, and material limitation:

- Is the cited excerpt present on the recorded page?
- Does the source support the claim as written?
- Is applicability to the Decision Context stated honestly?
- Is Evidence Tension visible?
- Is the confidence tier explained and policy-compliant?
- Would a reasonable reader mistake the direction for diagnosis, prescription, clearance, or Baylor policy?

Do not deliver a brief with an unresolved critical failure.

### 4. Deliver and collect Use Signals

Run the local prototype, select **Choose finished answer file**, and choose the finished brief JSON from `private/briefs/` only after validation, source-excerpt audit, and the human claim audit:

```powershell
npm run pilot:start
```

The Operational View renders the brief generically from that file. Use **Print / Save PDF** when a portable copy is needed. Preserve:

- On-Demand / Not Expert-Reviewed status
- creation date and version
- Decision Context
- Evidence Confidence and rationale
- claim-level excerpts, page locations, citations, and source links

Ask the participant to complete the feedback ledger at the end of the brief. It captures:

- whether the brief was useful
- whether it informed, confirmed, or changed a decision
- whether the recommended direction was clear
- whether the confidence felt too cautious, about right, or too confident
- what was missing or misapplied
- time to understanding
- on the third brief only: reuse intent, useful question types, and largest friction

Save the downloaded feedback JSON under:

```text
pilot-data/ask-library/private/feedback/
```

Validate it:

```powershell
npm run pilot:feedback -- pilot-data/ask-library/private/feedback/<feedback>.json
```

Participant IDs must use the anonymous `P01` format. Feedback remains on the local device until the downloaded file is deliberately transferred to the pilot operator.

The participant who asked the question is the pilot practitioner evaluating usefulness and fit. A separate Domain Reviewer is needed only if the brief is later promoted from On-Demand / Not Expert-Reviewed to a Reviewed Brief.

### 5. Score the pilot

Copy `examples/scorecard.example.json` to the ignored private folder. Add each validated feedback file to `useSignals`; `informed`, `confirmed`, and `changed` each satisfy the decision-influence signal. Copy each participant's third-brief `wouldReuse` response into the participant row, then run:

```powershell
npm run pilot:score -- pilot-data/ask-library/private/scorecard.json
```

The command returns `PASS` only when every confirmed expansion gate is met.

## What this pilot does not test

- Baylor authentication
- secure multi-user storage
- self-service response time
- automatic retrieval or generation
- Controlled Share links
- Reviewed Brief promotion
- department-wide adoption
- athlete health or performance effects

Those belong to the secure implementation phase only if this pilot warrants expansion.

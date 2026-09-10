# Ask the Library Pilot

## Lowest-friction distribution runbook

### Recommended access model

Run this as an **operator-hosted concierge pilot**. Participants should not receive the repository, install Node, run terminal commands, or manage JSON files. The pilot is testing Decision Utility and Evidence Integrity—not software setup, authentication, or self-service delivery.

Use one of these access modes:

1. **Shared Baylor laptop — recommended.** Start the prototype before the participant arrives and let the participant enter the question and feedback directly.
2. **Baylor Teams screen share — best remote option.** Share the prototype window and give the participant control when practical. Otherwise, read each prompt and enter their response exactly as stated.
3. **Private PDF follow-up — asynchronous fallback.** Send the de-identified brief through a private Baylor Teams conversation, then schedule a five-minute follow-up to capture feedback in the prototype. Do not publish the prototype or send a public link.

### Pilot launch checklist

1. Select three participants from at least two disciplines.
2. Assign anonymous IDs `P01`, `P02`, and `P03`.
3. Send each participant `participant-quick-start.md` or the shareable Word version.
4. Match each participant to one of four tracks: Physical Therapy, Performance Nutrition, Sports Science, or Sports Performance.
5. Select three tracks for the three-person pilot. The fourth remains an alternate; do not expand the scorecard beyond nine questions without intentionally changing the pilot contract.
6. Assign the simple, applied, and complex question from the selected track to that participant.
7. Schedule one 10-minute orientation and three question cycles per participant during the 14-day window.
8. Agree on a realistic brief return time at orientation. Do not promise automated or immediate answers.
9. Keep all private files under `pilot-data/ask-library/private/`.

Recommended folder structure:

```text
pilot-data/ask-library/private/
├── requests/
├── briefs/
├── feedback/
├── audits/
└── scorecard.json
```

### Copy-and-send invitation

> You are invited to a 14-day Ask the Library pilot. The goal is to test whether short, source-grounded Decision Briefs help with real Health & Performance decisions. You do not need to install anything. Please bring three practical questions during the pilot. Each question must be de-identified and should relate to a decision you are currently considering. We will use the tool together on a shared laptop or through a short Baylor Teams screen share. Reviewing a brief should take about two minutes, followed by about one minute of feedback.

### Question session: about five minutes

1. Start the prototype before the participant joins:

   ```powershell
   npm run pilot:start
   ```

2. Confirm the participant's anonymous ID.
3. Open the participant's assigned question and context from the stress-test question bank.
4. Ask whether the scenario is relevant to a current or recent decision in the participant's work. If not, replace it with another question at the same complexity tier.
5. Confirm that the question contains no identifying athlete information.
6. Copy the Practical Question and all five Decision Context fields into the main page. The question-bank JSON is a copy source; it is not uploaded into the prototype.
7. Select **Save question for Codex**. Do not use **Open practice answer**, which always opens the canned example and does not process the entered question.
8. Save the downloaded `ATL-R-*.json` request under `private/requests/`.
9. Validate the request:

   ```powershell
   npm run pilot:request -- pilot-data/ask-library/private/requests/<request>.json
   ```

### Operator work between sessions

1. Give the `ATL-R-*.json` request to Codex by attaching it, dragging it into the task, or providing the exact local path. Use the prompt in `codex-request-handoff.md`.
2. Retrieve relevant Evidence Library sources and draft the On-Demand / Not Expert-Reviewed brief using the approved JSON structure.
3. Save the finished brief JSON under `private/briefs/`.
4. Validate the brief:

   ```powershell
   npm run pilot:brief -- pilot-data/ask-library/private/briefs/<brief>.json
   ```

5. Audit all source excerpts:

   ```powershell
   npm run pilot:audit-source -- pilot-data/ask-library/private/briefs/<brief>.json
   ```

6. Complete the human claim audit. Codex's structure and source-excerpt checks do not replace this named human review. Do not deliver a brief with an unresolved critical failure.

### Brief delivery session: about five minutes

1. Keep the prototype running or start it, then select **Choose finished answer file**.
2. Choose the finished brief JSON from `private/briefs/`. Do not choose the Pilot Request, question-bank, audit output, or feedback JSON.
3. Let the participant read the Operational View in this order:
   - Bottom Line
   - Recommended Direction or Decision Boundary
   - Evidence Confidence
   - Actions and Guardrails
   - Evidence excerpts when desired
4. Use **Print / Save PDF** only when the participant needs a portable copy.
5. Ask the participant to complete the feedback ledger in the prototype.
6. Save the downloaded file under `private/feedback/`.
7. Validate it:

   ```powershell
   npm run pilot:feedback -- pilot-data/ask-library/private/feedback/<feedback>.json
   ```

8. On the participant's third brief, complete the reuse and friction questions.

After each brief, use one additional verbal prompt without adding another scoring form:

> What, if anything, is useful, wrong, missing, misapplied, or potentially unsafe for your practice?

Capture the answer in the existing **missing or misapplied** feedback field.

### Structured question assignment

Use `Ask-the-Library-Pilot-Stress-Test-Question-Bank.docx` as the assignment sheet:

- **Physical Therapy:** PT01 simple, PT02 applied, PT03 complex
- **Performance Nutrition:** PN01 simple, PN02 applied, PN03 complex
- **Sports Science:** SS01 simple, SS02 applied, SS03 complex
- **Sports Performance:** SP01 simple, SP02 applied, SP03 complex

Assign the track that best matches each participant's role. Use only three tracks in the current three-person pilot, for nine submitted questions total. The unused track is an alternate, not an additional scored participant.

These generated questions reduce participant burden and give the pilot deliberate coverage. They do not replace the Decision Utility requirement. A participant must confirm that each scenario maps to a current or recent decision; otherwise, substitute another question at the same tier within that discipline.

The “intended stress” note is for the pilot lead only. It describes the capability being tested, not the answer the operator should produce.

### Friction controls

- Keep one pilot lead as the single point of contact.
- Start the prototype and open the correct screen before each participant joins.
- Keep the prototype running across question cycles; use **New question** rather than restarting it for every request.
- Never ask participants to manage files or commands.
- Use the same anonymous ID for all three briefs from one participant.
- Keep sessions short; do not turn the brief delivery into an evidence lecture.
- Capture feedback immediately while the decision context is fresh.
- Treat a Coverage Gap as an honest result, not a failed session.

### Do not distribute during this pilot

- A repository clone or ZIP
- Terminal setup instructions
- A public or unauthenticated hosted prototype
- Raw private request, brief, audit, or feedback files
- Any brief containing identifying athlete information

If the pilot passes, a secure self-service experience can become the next development phase. It should not be introduced during this concierge test.

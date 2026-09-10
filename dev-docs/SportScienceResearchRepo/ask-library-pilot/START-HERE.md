# Ask the Library: start here

## The whole idea in one sentence

**A staff member asks one question, Codex prepares a research-based answer, and the staff member reads and rates that answer.**

The staff member should not need to understand JSON, GitHub, commands, or repository folders. The pilot lead handles the files between the question and the answer.

## Think of it like ordering food

| Ask the Library item | Plain-English meaning |
|---|---|
| Question bank | The menu of sample questions |
| `ATL-R-...json` | The order ticket containing one question |
| Codex | The kitchen that prepares the answer |
| `ATL-B-...json` | The finished answer |
| Feedback file | The staff member's rating |

## What the staff member does

1. **Ask:** Enter or paste one de-identified question.
2. **Read:** Review the finished answer when the pilot lead opens it.
3. **Rate:** Complete the short feedback form.

That is the participant's entire job.

## What the pilot lead does

### 1. Start the prototype once

Double-click this file:

```text
<repo-root>\START-ASK-THE-LIBRARY.cmd
```

Keep the PowerShell window open. The prototype opens in the browser. You do **not** restart it for every question.

### 2. Save one question

The staff member can paste a question from:

```text
<repo-root>\docs\ask-library-pilot\Ask-the-Library-Pilot-Stress-Test-Question-Bank.docx
```

They can also enter a different real, de-identified question. Complete the context fields, confirm that no identifying information is included, and select **Save question for Codex**.

The browser downloads a file whose name starts with:

```text
ATL-R-
```

This is the **question file**. It is not the answer.

### 3. Give the question file to Codex

Attach the downloaded `ATL-R-...json` file to a Codex task and paste this request:

> Work in the repository root containing `START-ASK-THE-LIBRARY.cmd`. Process the attached Ask the Library Pilot Request as private, de-identified material. Validate the request; create an On-Demand / Not Expert-Reviewed Decision Brief using only admissible Evidence Library sources; record claim-level excerpts and page locations; return a Coverage Gap rather than inventing support; run the brief validator and original-source excerpt audit; and save the finished brief JSON under `pilot-data/ask-library/private/briefs/`. Report the saved path and whether each gate passed. Do not promote the result to a Reviewed Brief.

Codex will report the path to a finished file whose name should start with:

```text
ATL-B-
```

This is the **finished answer file**.

### 4. Complete the backstage quality check

Before the staff member sees the answer, the named pilot lead or claim auditor confirms that the cited excerpts support the important claims, the limits are honest, and there is no unresolved critical failure. Use the checklist in:

```text
<repo-root>\docs\ask-library-pilot\pilot-lead-distribution-runbook.md
```

This check belongs to the pilot lead. The participant does not perform it.

### 5. Open the finished answer

Return to the prototype's main page. Under **Open Codex's finished answer**, select **Choose finished answer file** and choose the `ATL-B-...json` file Codex created.

Do not choose the `ATL-R-...json` question file.

### 6. Let the staff member read and rate it

The staff member reads the Decision Brief and completes the feedback form. Save the downloaded feedback file under:

```text
<repo-root>\pilot-data\ask-library\private\feedback
```

For another question, select **New question** in the prototype. Do not restart the prototype.

## Four things not to do

- Do not upload the full question-bank JSON. It is only a source for copying questions.
- Do not choose the `ATL-R-...json` question file as the finished answer.
- Do not ask participants to use Codex, PowerShell, GitHub, or repository folders.
- Do not enter athlete names, records, clinical notes, or other identifying information.

## If something is unclear

Remember the three-step test:

**Staff asks → Codex prepares → Staff reviews**

If a step does not fit one of those three actions, it belongs to the pilot lead—not the participant.

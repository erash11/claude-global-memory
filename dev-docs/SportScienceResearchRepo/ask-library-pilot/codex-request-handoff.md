# Ask the Library pilot

## Giving a request to Codex

Use this handoff only after the prototype has downloaded a real Pilot Request JSON. The prototype does not send the question to Codex automatically.

### Know which file you have

| File | Purpose | What to do with it |
|---|---|---|
| `stress-test-question-bank.json` | Copy-ready question and Decision Context source | Copy one question and its five context fields into the main page. Do not upload or open this file in the prototype. |
| `ATL-R-*.json` | Real Pilot Request downloaded from **Save question for Codex** | Give this file to Codex. Do not choose it as the finished answer. |
| Finished brief JSON under `private/briefs/` | On-Demand answer prepared from the request | Use **Choose finished answer file** only after all operator gates and the human claim audit are complete. |
| Feedback JSON | Participant's evaluation downloaded after reading the brief | Return it to the pilot lead and validate it. Do not open it as a brief. |

**Open practice answer is practice only.** It always opens the canned congested-week example and does not answer the question typed on the main page.

### Step 1 — save and validate the request

Move the downloaded `ATL-R-*.json` file to:

```text
<repo-root>\pilot-data\ask-library\private\requests\
```

From the Research Repo, validate it:

```powershell
npm run pilot:request -- pilot-data/ask-library/private/requests/<request>.json
```

Stop if the request contains identifying information or fails validation.

### Step 2 — give the request to Codex

In a Codex task, either:

- drag the `ATL-R-*.json` file into the message;
- use the attachment button; or
- paste the exact local file path if Codex is working on the same machine.

Then send:

> Work in the repository root containing `START-ASK-THE-LIBRARY.cmd`. Process the attached Ask the Library Pilot Request as private, de-identified material. Validate the request; create an On-Demand / Not Expert-Reviewed Decision Brief using only admissible Evidence Library sources; record claim-level excerpts and page locations; return a Coverage Gap rather than inventing support; run the brief validator and original-source excerpt audit; and save the finished brief JSON under `pilot-data/ask-library/private/briefs/`. Report the saved path and whether each gate passed. Do not promote the result to a Reviewed Brief.

If the file was not attached, replace “attached” with its exact local path.

### Step 3 — complete the human claim audit

Codex prepares the brief and can run the mechanical structure and source-excerpt checks. Before delivery, the named claim auditor must still confirm:

- the cited excerpt supports the claim as written;
- applicability to the stated population and setting is honest;
- evidence tension, uncertainty, and limits are visible;
- the direction cannot reasonably be mistaken for diagnosis, prescription, clearance, or Baylor policy.

Do not deliver a brief with an unresolved critical integrity failure.

### Step 4 — open the finished brief

Keep the prototype running. On its main page:

1. Select **Choose finished answer file**.
2. Choose the finished brief JSON from `pilot-data\ask-library\private\briefs\`.
3. Have the participant who supplied the question review the Operational View.
4. Ask the participant to complete the feedback form and download the feedback JSON.

The participant is evaluating usefulness and fit for practice. A separate Domain Reviewer is needed only if the team later promotes the On-Demand brief into a Reviewed Brief.

### Step 5 — save and validate feedback

Save the feedback file under:

```text
pilot-data\ask-library\private\feedback\
```

Then run:

```powershell
npm run pilot:feedback -- pilot-data/ask-library/private/feedback/<feedback>.json
```

All request, brief, audit, and feedback files remain local and private until deliberately transferred. Never commit them to Git.

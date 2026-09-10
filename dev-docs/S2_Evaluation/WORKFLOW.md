# S2_Evaluation — recommended workflow

**Project:** Mine existing S2 Cognition testing data for actionable, coach-facing
insights that go beyond normative percentiles.
**Lane:** side · **Stage:** idea · **Registered:** 2026-08-08
**Routed via:** `/ask-matt` (router doc at `~/.agents/skills/ask-matt/SKILL.md`)

---

## The framing problem to solve first

The request as stated — "mine the data for insights" — is open-ended exploration
with no decision anchor. That is the single biggest risk to this project, and your
own material already says so:

- **EOY Kitman Utilization (2026-06-08)**, logged under *Decisions*: "Collecting
  data without a clear plan often leads to unutilized information, reducing
  effective injury prevention."
- **JFrazier Presentation Brief (2026-06-12)**, logged under *Decisions* as a
  "Decision-First Data Approach": "Collect data only after defining specific RTP
  questions to simplify and speed up analysis."
- Robertson et al. 2017 in your library argues athlete monitoring fails without
  *decision-support systems* — more numbers is not the fix.

You have already decided this twice, in writing, in two separate meetings. This
project should not be the exception.

"Beyond percentiles" is a real goal, but an insight that isn't tied to a decision a
coach actually makes is just a prettier percentile. **Step 1 is framing, not
analysis.**

Concretely, the grilling should force answers to: *which coaching decisions should
an S2 insight change?* Candidates worth pressuring — install/rep allocation,
position fit, communication load in complex packages, individualized coaching cues,
pre-snap processing under time pressure. Pick the few that a coach would act on.

---

## Recommended path

### 0. Precondition (gate, not a step)
`/setup-matt-pocock-skills` configures the issue tracker, triage labels, and doc
layout the later steps assume. **No Matt tracker config was found on this machine.**
It is not needed for steps 1–3. Run it only if you reach step 4 (`/to-tickets`).

### 1. `/grill-with-docs` — sharpen the idea, statefully
Run this in `S2_Evaluation/`. Purpose: nail the decision-first frame above, and
build the glossary.

Strictly, `/ask-matt` routes an empty folder to `/grill-me` (no codebase). Use
`/grill-with-docs` anyway — `/grill-me` is **stateless and saves nothing**, and
this project will accumulate decisions worth a paper trail (`CONTEXT.md` + ADRs).
Precedent: `SportScienceResearchRepo`, `ZoteroInjestion`, and `PlayerProfiles_FB`
all carry a `CONTEXT.md` from this flow.

Expect `/domain-modeling` to get pulled in underneath: **"S2 score" is an
overloaded term** doing at least four jobs — raw subtest value, subtest percentile,
composite, and normative-population percentile. Resolving that is a prerequisite to
saying anything precise about "beyond percentiles."

### 2. `/research` — run in the background, in parallel with step 1
Delegate to a background agent, against **primary sources**: what each S2 subtest
actually claims to measure, and the published evidence on predictive validity for
on-field performance. It leaves a cited Markdown file in the repo.

This is not optional politeness. If you mine a pattern that contradicts the
instrument's known construct validity, you will present it to a coach and be wrong.
Pair with your own `sports-science-research-grounding` and
`pp-zotero-research-library` skills.

### 3. `/prototype` — answer "is there signal?" with throwaway code
The question *"is there anything beyond percentiles in this data?"* cannot be
settled on paper. It needs a runnable answer, which is exactly the step-2 detour in
the main flow.

`/prototype` fits exploratory data analysis almost perfectly: **throwaway from day
one — keep the answer, delete the code.** Probe intra-athlete profile *shape*
(strength/weakness dispersion, not rank), change across testing cycles,
position-relevant subtest weighting, and subtest interactions.

Bridge with `/handoff` in both directions — out of the grilling session into a
fresh prototype session, then back with what you learned.

### 4. Branch — only after step 3 finds signal
- **Multi-session build** (likely, if this becomes a recurring per-testing-cycle
  deliverable) → `/to-spec`, then `/to-tickets`, then `/implement` per ticket,
  **clearing context between each one**.
- **Small enough** → `/implement` directly.

`/implement` drives `/tdd` internally and closes with `/code-review` before
committing.

**Context hygiene:** keep steps 1–4 through `/to-tickets` in one unbroken context
window. If you approach the smart zone (~120k tokens) first, `/handoff` rather than
push on degraded.

---

## The last mile `/ask-matt` does not cover

`/ask-matt` routes **engineering** work. Your actual deliverable is **coach-facing**,
which is a data-storytelling problem, not a code problem. Once you have findings:

- **`design-academy-skill`** — audience-first data storytelling; it triggers exactly
  on "showing data to an audience."
- **`dataviz`** — read *before* writing the first line of chart code.
- **`five-slides-generator`** — if the output should land in the Performance School
  "5 Slides in 5 Minutes" format.

---

## Explicitly not recommended

- **`/triage`** — only for issues *you didn't create*. Nothing inbound here.
- **`/diagnosing-bugs`** — nothing is broken.
- **`/improve-codebase-architecture`** — no codebase yet.
- **`/wayfinder`** — the escalation, not the start. It charts investigation tickets
  for efforts too big for one session. Reach for it only if step 1 reveals the fog
  is deeper than a single grilling session; with data already in hand, grill +
  prototype is right-sized for a side-lane project.

---

## Immediate next action

Run `/grill-with-docs` in `S2_Evaluation/` to fix the decision-first frame — name
the specific coaching decisions an S2 insight should change, before touching the
data. Kick off `/research` in the background at the same time.

**Still unknown:** where the S2 Cognition data actually lives, its format, athlete
count, and how many testing cycles deep it goes. The grilling should surface this
early — it bounds what step 3 can attempt.

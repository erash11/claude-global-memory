---
title: Book Advisors for Obsidian + KeystoneOS
date: 2026-06-12
status: approved
domain-pilot: strength-and-conditioning
supersedes: none
---

# Book Advisors — turning a library of books into grounded AI advisors

## Problem & intent

Eric has a large body of books (strength & conditioning, business, etc.) he wants
to consult as **advisors** — specialist collaborators that answer *only* from
curated knowledge he trusts, cite their sources, and explicitly flag when a question
falls outside what they actually know. This is the pattern demonstrated in the
"books as advisors" YouTube video (https://www.youtube.com/watch?v=OAgU6sOmih0),
which builds it in Notion. Eric wants it in **Obsidian**, integrated with his
existing stack — **not Notion**.

The existing stack the design must reuse, not duplicate:

- **SecondBrain vault** at `C:\Users\eric_rash\Desktop\SecondBrain\` — plain-markdown
  Obsidian vault. Existing `ingest-resource` skill already handles
  acquisition/routing/wikilinking; the book pipeline builds on its conventions.
- **memsearch** — local hybrid (vector + keyword) recall over markdown, backed by
  Milvus in Docker, ONNX bge-m3 embeddings. Re-indexed by a SessionEnd hook
  (`~/.claude/hooks/memsearch-sync.js`). **Currently indexes only four memory paths,
  NOT the vault** — this design adds the library path.
- **KeystoneOS** — `AGENTS.md` is the canonical one-hop routing table; CLAUDE.md /
  GEMINI.md are thin adapters. Commits here are authorized to be autonomous.
- **Skills system** — `~/.claude/skills/<name>/SKILL.md`.
- **Task Scheduler cadence** — morning task already registered; evening tier gated
  on a week of clean runs. Sets the precedent: manual-first, promote to scheduled
  only after the manual version proves useful.

## Chosen approach

**Approach A — advisor-as-skill, knowledge-as-notes, memsearch as the entry gate.**
Knowledge lives as plain-markdown atomized notes in the vault. Advisors are **data**
(persona notes) read by **one generic skill**, not code. Ingestion and review are
two more skills. memsearch is the retrieval substrate.

Rejected for now (saved as future enrichment):
- **B — Dataview/Bases database views** replicating Notion's UI. Cosmetic for the
  agent's purposes; adds a plugin dependency. Optional later garnish.
- **C — graph-first via graphify/KeystoneOS.** Heavier, less inspectable in Obsidian.
  **Deferred as the agreed future hybridization round**: once the flat-note library
  exists, graphify it to surface cross-book community structure and power
  synthesis-level advisor reasoning.

Future direction (explicitly agreed): hybridize A + C — keep flat markdown as the
source of truth, layer a knowledge graph over it for cross-book synthesis — once the
pilot library proves the pipeline.

## Section 1 — Data model

New subtree:

```
SecondBrain/Knowledge/library/
  advisors/                        ← persona notes (Section 2)
  <domain>/                        ← e.g. strength-and-conditioning/
    _domain.md                     ← domain index: books, advisor link, miss-log
    <book-slug>/                   ← e.g. supertraining--verkhoshansky/
      _book.md                     ← chapter map, ingest tier, per-chapter status
      <kind>--<slug>.md            ← one atomized entry per idea
```

**Entry note** — one atomized idea per file. Name: `<kind>--<slug>.md` where
`kind ∈ {principle, framework, case-study, heuristic, claim}`.

Frontmatter (the video's Notion schema, as YAML):

```yaml
---
type: library-entry
kind: principle
domain: strength-and-conditioning
book: <book-slug>
chapter: "4"
topic: recovery timing
category: [programming, adaptation]
confidence: proven         # proven | supported | untested | contested
ingest-tier: full-text     # full-text | highlights | framework-only
created: 2026-06-12
---
```

Body shape (short — one idea, ~150–300 words):
**What it is / Why it works / When to apply / When NOT to apply / Example.**
The *When NOT to apply* section is mandatory — it forces honest scoping.

**Confidence is bounded by ingest-tier** (honesty rule):
- `full-text` entries may claim up to `proven`.
- `highlights` entries cap at `supported` (partial context).
- `framework-only` entries cap at `untested` until verified against the real text.
- `contested` is set manually when sources conflict.

**Cross-book convergence** is a `[[wikilink]]` + one explanatory line, e.g.
"Issurin reaches the same conclusion from fatigue management: [[framework--block-periodization]]".

**`_book.md`** holds the chapter list (the "work plan"), per-chapter ingest status,
and the tier — making ingestion **resumable** across sessions and **upgradeable**
(framework-only → full-text if the file is later acquired).

**`_domain.md`** lists the domain's books, links its advisor, and carries the
**miss-log**: a one-line append every time the advisor answers "not covered by your
library" (feeds the review loop in Section 5).

## Section 2 — Advisor layer

**Persona note** at `Knowledge/library/advisors/<domain>.md` — the video's
"job description" as vault data:

```yaml
---
type: advisor
domain: strength-and-conditioning
status: active
books: [<book-slug>, ...]
---
```

Body (all short): **Role & voice**, **Scope** (incl. explicit *don't-pick-when*
boundaries — e.g. "not for medical decisions; not for Catapult GPS analysis"),
**Entry gate** (the contract below), **Standing biases** (e.g. "Eric works in
collegiate American football").

**One generic `advisor` skill** (`~/.claude/skills/advisor/SKILL.md`) — the only
new code in the advisor layer. Invoked `/advisor <domain> <question>` or by natural
language ("ask my performance advisor…"). Procedure:

1. Load persona note; refuse gracefully if the domain has no advisor.
2. **Entry gate (mandatory, in order):** `memsearch search` over the library with
   2–3 query phrasings → `expand` top hits → Read the matched entry notes →
   follow `[[wikilinks]]` one hop when relevant.
3. Answer **only from gathered entries**, citing each claim as
   `(Book, ch. N — [[entry-note]])`, respecting `confidence` (lead with proven,
   flag contested).
4. **Grounding disclosure footer** (the load-bearing behavior): e.g.
   *"Grounded: 6 entries from 2 books. Not covered by your library: X, Y — the
   following is general knowledge, not your curated sources: …"* Ungrounded material
   is always separated and labeled, never blended.
5. If the library has essentially nothing: say so first (the "empty knowledge base"
   test), suggest which book/domain would fill the gap, then optionally give clearly
   labeled general advice. Append the miss to `_domain.md`.

Adding a new advisor = writing one persona note. The skill never changes.

**Routing:** the `advisor` skill registers with trigger phrases; `AGENTS.md` gets
one routing line sending library-consultation questions to it (one-hop convention).

## Section 3 — Ingestion pipeline (`ingest-book` skill)

New skill `~/.claude/skills/ingest-book/SKILL.md`, sibling to `ingest-resource`,
reusing its conventions (kebab-case slugs, never-overwrite, wikilink-on-first-mention).
Four phases:

1. **Intake.** Identify book, source type, target domain (create domain folder +
   `_domain.md` if new). Build `_book.md` chapter map (from the file's ToC for
   digital; from the book's public listing for physical). This is the resumable
   work plan.
2. **Extract, by tier:**
   - *Full-text (PDF/EPUB):* chapter-by-chapter through the file (EPUB unzipped to
     HTML; PDF via paged reads — both processed in the sandbox so raw chapter text
     never floods context). Per chapter: extract → atomize → write entries →
     **update `_book.md` after each chapter** (checkpoint).
   - *Kindle highlights:* parse `My Clippings.txt` / highlights export, cluster by
     theme, write entries capped at `supported`.
   - *Framework-only (physical):* brief interview with Eric for his takeaways +
     verified public chapter summaries → 5–15 framework-level entries capped at
     `untested`.
3. **Quality gate (per batch):** one idea per note (split compounds); *When NOT to
   apply* present; no near-duplicate — if an existing entry covers it, **cross-link
   and enrich** rather than duplicate (this is where convergence links are created).
4. **Close-out.** Update `_book.md` status; add book to its advisor's `books:` list;
   run `memsearch index <library-path>` so entries are immediately searchable; report
   counts (entries by kind/confidence, links created).

Full-text atomization is token-hungry — a 300-page book is a multi-session job by
design; chapter-level checkpointing is what makes that safe.

## Section 4 — Indexing

One change to `~/.claude/hooks/memsearch-sync.js`: add
`C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library` to the `PATHS` array, so
the SessionEnd hook keeps the library indexed automatically.

- **Timeout safety:** hook has a 20s budget (2026-06-11 redesign). The ingestion
  skill's Phase 4 runs `memsearch index` itself, so the SessionEnd hook only ever
  sees an already-indexed library — no timeout change needed.
- **Scope:** only `Knowledge/library/` is indexed, not the whole vault — keeps
  meeting notes / drafts out of advisor retrieval.

## Section 5 — Review loop, failure modes, validation

**`library-review` skill** (the video's self-improving loop; manual-first per the
evening-tier precedent). Invoked on demand: picks a domain, scans entry distribution
(category/confidence/book), reports — gaps (from the `_domain.md` miss-log),
contested entries needing a second source, and 2–3 suggested additions. Proposes;
Eric approves. Promotion to a scheduled Task is a later decision, gated on the
manual version proving useful.

**Failure modes:**
- *Un-parseable PDF (scanned/image):* skill detects no extractable text → falls back
  to framework-only tier and says so; never produces thin entries at full-text
  confidence.
- *Mid-ingestion interruption:* `_book.md` checkpointing makes any session resumable;
  worst case loses one chapter's work.
- *memsearch/Milvus down:* advisor skill falls back to Grep over the library subtree,
  with a keyword-only notice.
- *Slug collisions:* inherited never-overwrite rule — enrich or suffix.

**Pilot validation (acceptance test)** — domain `strength-and-conditioning`, pilot
book a PDF/EPUB Eric provides (named at ingest time). Three checks mirror the video:
1. On-library question → grounded, cited answer.
2. Off-library question → explicit "not covered" disclosure, no blended generic
   advice.
3. (If ≥2 books ingested) cross-book question → answer cites both via a convergence
   link.

## Out of scope (this round)

- Dataview/Bases views (Approach B).
- Graph hybridization (Approach C) — the agreed *next* round once the library exists.
- Scheduled/automated review — manual `library-review` first.
- Indexing the whole vault into memsearch — only `Knowledge/library/`.
- Obsidian-plugin consultation surface — Claude Code is the surface.

## Pilot acceptance result (2026-06-12)

Pilot book: **Periodization: Theory and Methodology of Training, 5th ed.** (Bompa &
Haff). Full-text tier, Ch1–2 ingested → 12 atomized entries (5 proven / 7 supported;
6 principles, 4 frameworks, 2 heuristics), memsearch-indexed and committed.

- **Check 1 — on-library question → grounded, cited answer: PASS.** "How to load a
  4-week block and time recovery" grounded in 5 entries (step-loading, progressive
  overload, supercompensation, fatigue–fitness 3:1, concentrated loading), each cited
  to Bompa ch. with `[[wikilinks]]`.
- **Check 2 — off-library question → explicit gap disclosure, no blended advice: PASS.**
  "Post-training protein quantity/timing" — memsearch returned high *scores* (0.98)
  because recovery entries mention nutrition/glycogen, but no entry prescribes protein
  amount/timing. Advisor judged grounding by *content*, disclosed the gap, kept general
  advice clearly labeled, and appended a miss-log line to `_domain.md`.
  **Lesson:** retrieval score ≠ grounding; the advisor must read entries and judge
  whether they answer the question. The grounding footer is what makes this safe.
- **Check 3 — cross-book convergence: DEFERRED** (only one book ingested). Re-run when
  a second S&C book joins the domain.

System validated end-to-end: ingest → index → grounded advisor with honest disclosure.

## Build order

1. memsearch path addition (Section 4) — unblocks retrieval.
2. Data-model scaffolding: create `Knowledge/library/strength-and-conditioning/`
   and `advisors/`.
3. `ingest-book` skill (Section 3).
4. Ingest the pilot book (Eric provides file).
5. `advisor` skill + S&C persona note (Section 2) + AGENTS.md routing line.
6. Run the three-check acceptance test (Section 5).
7. `library-review` skill (Section 5).

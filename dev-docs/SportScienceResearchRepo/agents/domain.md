# Domain Docs

This repository uses a **single-context** domain-documentation layout.

## Before exploring

Read these when they exist and are relevant to the work:

- `CONTEXT.md` at the repository root for the product glossary and domain boundaries.
- Decisions under `docs/adr/` that touch the area being changed.

If either location does not yet exist, proceed silently. `grill-with-docs`, `domain-modeling`, and architecture work create or extend these documents when terminology or durable decisions are actually resolved; do not create speculative placeholders.

## Expected layout

```text
/
├── CONTEXT.md
├── docs/adr/
│   └── NNNN-decision-name.md
└── application and data files
```

Do not introduce `CONTEXT-MAP.md` or per-module context files unless the repository later develops genuinely independent domains, such as a separately operated Ask the Library backend.

## Vocabulary contract

Use the terms defined in `CONTEXT.md` in issue titles, specifications, tests, interfaces, and implementation notes. Do not drift to synonyms that the glossary explicitly rejects.

If a needed concept is missing, first determine whether the proposed term is unnecessary or whether the domain model has a real gap. Resolve genuine gaps through `domain-modeling` or `grill-with-docs`.

## ADR conflicts

Surface any conflict with an existing ADR explicitly rather than silently overriding it. Name the ADR, explain the conflict, and state why reopening the decision may be justified.

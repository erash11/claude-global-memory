# Paper Brief Contract

A Paper Brief represents one fully reviewed Source Paper. If Usable Full Text or verifiable Evidence Locators are unavailable, use a Reference Stub instead.

## Required frontmatter

```yaml
---
type: paper-brief
status: ingested
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: zotero
zotero-item-key: ABCD1234
zotero-attachment-key: EFGH5678
zotero-version: 1234
citekey: authorShortTitle2024
doi: 10.xxxx/example
domain: [sport-science]
tags: [topic-one, topic-two]
full-text-status: usable
evidence-locator: page
cross-linked: false
---
```

Use an empty string for an unavailable DOI or citekey. Never omit the Zotero item key.

## Required body

```markdown
# Author et al. YEAR — Short descriptive title

> **Citation**
> Complete formatted citation.

## Why it was promoted

The concrete question, project, or recurring decision this paper informs.

## Research question

What the study actually sought to determine.

## Population and context

- Participants:
- Sport and level:
- Training or return-to-play context:
- Inclusion and exclusion boundaries:

## Study design and methods

- Design:
- Exposure or intervention:
- Comparator:
- Measurements and outcomes:
- Analysis:

## Key findings

- Finding with numerical result and uncertainty where reported. `[p. X]`
- Finding with numerical result and uncertainty where reported. `[Table Y, p. X]`

## Limitations and applicability

- Limitations reported by the authors. `[p. X]`
- Additional transfer limitations, explicitly labeled as interpretation.

## Practitioner interpretation

An applied interpretation that preserves the population, design, outcome, and uncertainty. It must not be phrased as a direct study finding.

## Evidence map

| Claim | Locator | Evidence type |
|---|---|---|
| Short claim identifier | p. X or Table Y, p. X | result, method, limitation |

## Related knowledge

- `[[existing-note]]` — relationship
```

## Validation rules

- Every substantive finding has an Evidence Locator.
- Numerical results reproduce units, denominators, and uncertainty when reported.
- Correlation, prediction, association, and causation are not treated as synonyms.
- Practitioner Interpretation is visibly distinct from author claims.
- Abstract-only evidence cannot satisfy the Paper Brief contract.
- Quotations are brief and necessary; paraphrase is the default.
- The brief does not include a copy of the PDF or long reconstructed passages.

## Reference Stub minimum

A Reference Stub contains citation, Zotero identity, why it may matter, full-text blocking reason, and `status: reference-stub`. It contains no substantive findings, methods claims, or practice recommendations.

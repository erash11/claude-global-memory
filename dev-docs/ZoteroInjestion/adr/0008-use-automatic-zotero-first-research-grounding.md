# ADR 0008: Use automatic Zotero-first research grounding

**Status:** Accepted
**Date:** 2026-07-22

## Context

The bridge initially required an agent or user to name papers and treated `SecondBrain Queue` as the only
Knowledge Promotion lane. The intended experience is broader: normal conversations about sport science,
return to play, rehabilitation, strength and conditioning, workload, testing, or athlete health should benefit
from the user's Zotero library without requiring a paper title or a special command. The long-term processing
goal is every eligible research record in the library, while queued papers should still receive attention first.

## Decision

1. A `ResearchGroundingService` will turn a normal question into bounded query variants, rank results across
   Zotero metadata and cached full text, and return a multi-paper evidence pack.
2. Every pack reports its coverage as `sufficient`, `thin`, or `none`, distinguishes page-located evidence from
   indexed text and metadata, and carries an answer contract for population, methods, limitations, and
   practitioner interpretation. When the question specifies a sport code, sex, age group, competition level,
   injury region, or injury type, the pack reports each paper as aligned, partial, unknown, or conflicting. Local coverage is
   `sufficient` only when at least two full-text papers align with every explicit applicability dimension.
3. Zotero is searched first. When local coverage is `thin` or `none`, each agent harness may use its native web
   research capability to find primary peer-reviewed sources. Those sources must be labeled `External` and not
   represented as part of the user's library.
4. The full eligible library is a derived, resumable backlog. `SecondBrain Queue` remains the priority lane.
   Promotion scope is an explicit setting: `queue` for the original gate or `library` for the approved full-library
   goal.
5. The research corpus remains a retrieval system. Existing personal, project, and workflow memory systems are
   not replaced or bulk-filled with paper text. Durable Paper Briefs and reviewed syntheses belong in SecondBrain;
   durable user decisions continue through the existing memory workflow.

## Consequences

- Substantive domain conversations can be research-grounded without a paper-specific prompt.
- Retrieval works identically over MCP in Codex, Claude Code, and Antigravity, with CLI parity for operations.
- External fallback is portable because it is a harness policy, not a browser dependency inside the bridge.
- Metadata or an abstract alone cannot silently become a strong finding. Evidence readiness remains visible.
- Full-library processing can resume by status and offset without moving papers between Zotero collections.

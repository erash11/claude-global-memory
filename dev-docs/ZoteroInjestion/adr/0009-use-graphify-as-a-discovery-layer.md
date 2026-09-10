# ADR 0009: Use Graphify as a downstream discovery layer

**Status:** Accepted
**Date:** 2026-07-22

## Context

Graphify can turn Paper Briefs and syntheses into a persistent graph with extracted, inferred, and ambiguous
relationships. This can make cross-paper structure easier to discover, but a graph edge does not carry the same
epistemic weight as a result verified in the source paper.

## Decision

Graphify is optional and downstream of validated Paper Briefs. It may be used to:

- cluster papers by population, intervention, outcome, method, or applied domain;
- identify repeated or contradictory relationships across papers;
- surface bridge concepts, research gaps, and candidate synthesis questions;
- provide a GraphRAG discovery surface over the reviewed corpus.

Graphify will not be used as the authority for a claim. Inferred or ambiguous edges must remain labeled as such,
and any connection used in an answer must be verified against Zotero evidence and original PDF page locators.
Generated artifacts remain under `SecondBrain/Projects/Graphify/ZoteroResearchBridge/`, not in general Knowledge.

## Consequences

- The graph can improve discovery and synthesis without contaminating evidence provenance.
- Ordinary question answering does not depend on Graphify being installed or up to date.
- Running `/graphify` is a deliberate enrichment operation, not part of every Zotero sync or conversation.

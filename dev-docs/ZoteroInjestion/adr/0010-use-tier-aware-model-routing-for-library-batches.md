# ADR 0010: Use tier-aware model routing for library batches

**Status:** Accepted
**Date:** 2026-07-23

## Context

Full-library processing combines two different workloads. Backlog selection, extraction, reconciliation, hashing,
and regression checks are bounded and strongly validated. Paper Brief promotion requires scientific judgment about
methods, results, limitations, evidence locators, and applicability. Running every stage on the flagship model
spends unnecessarily, while moving the entire workflow to a balanced model weakens the quality boundary where
errors are hardest to detect.

The bridge does not invoke language models and must remain portable across Codex, Claude Code, Gemini, and
Antigravity. Model selection therefore belongs to the harness workflow rather than the CLI, MCP server, batch
ledger, or Promotion Record.

## Decision

1. Use GPT-5.6 Terra at high reasoning for Codex batch operations: backlog inspection, batch creation, extraction,
   metadata audit, Reference Stubs, reconciliation, integrity checks, tests, lint, and documentation.
2. Use GPT-5.6 Sol at high reasoning for full-text scientific review, applicability judgment, Evidence Locator
   selection, Paper Brief writing, and final scientific approval.
3. Allow Luna only for strictly deterministic, read-only status or hash validation when the harness exposes it as
   an ephemeral worker. Luna cannot create or approve research artifacts.
4. Run the stages sequentially with one owner per mutable surface. Model routing cannot introduce concurrent writes
   to a batch ledger, Promotion Record, or SecondBrain file.
5. Store the routing policy in the shared research-grounding skill. Keep the bridge model-agnostic and preserve the
   same evidence and promotion contracts regardless of model.
6. If a harness cannot select worker models, use the current model and disclose that no automatic switch occurred.
   Other harnesses may map the roles to verified equivalent tiers without inventing provider-specific model IDs.
7. An explicit user model choice for a particular task overrides the default route.

## Consequences

- Routine batch work can use the lower-cost balanced tier without moving scientific judgment away from Sol.
- The quality gate remains attached to full-text evidence review rather than to extraction or file operations.
- Codex can route with ephemeral model-selectable workers while the same skill remains safe in other harnesses.
- The CLI, MCP schema, local database, batch ledgers, and Promotion Records remain free of provider-specific model
  configuration.
- Savings and quality must be evaluated from representative batches; the policy does not claim model equivalence.

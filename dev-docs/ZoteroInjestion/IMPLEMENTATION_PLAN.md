# Zotero Research Bridge Implementation Plan

Implementation begins only after the design is confirmed as shared understanding.

## Current status

- Phases 1–7 are implemented and pass automated tests.
- The MCP server is registered globally in Codex and at user scope in Claude Code.
- Live production verification passes with a read-only key, enabled local API, 2,917 current items, and 803 API-indexed full-text records.
- The Phase 6 cohort is complete: all ten papers produced validated Paper Briefs, the plugin gate recommends remaining MCP/CLI-only, and negative full-text gates remain automated-test verified rather than live-observed.
- Phase 7 adds automatic Zotero-first research grounding, explicit external fallback, a resumable all-library
  backlog, and a portable Codex/Claude Code/Antigravity skill without replacing existing memory systems.

## Phase 1 — Reproducible project foundation

- Initialize Git without modifying unrelated repositories.
- Create a Python 3.12 `uv` project with locked dependencies.
- Add configuration models, secret exclusions, structured logging, and test fixtures.
- Add an HTTP transport wrapper that rejects every method except `GET` and `HEAD`.
- Verify the existing write-enabled key is rejected by production-readiness checks.

**Exit:** clean install, unit tests pass, and no credential can enter Git.

## Phase 2 — Zotero retrieval and Paper Index

- Implement authenticated Web API reads, backoff handling, and conditional requests.
- Implement local API availability detection and supported read endpoints.
- Build the SQLite schema and FTS index.
- Implement full and incremental synchronization with library-version checkpoints.
- Resolve collections, tags, parent items, attachments, and deletions.

**Exit:** the local index reproduces live library counts and incremental sync changes without a Zotero write request.

## Phase 3 — Page-aware evidence access

- Resolve local and Web API PDF sources without copying them into either repository.
- Extract page-aware text with PyMuPDF and cache by attachment hash/version.
- Classify Usable Full Text and record precise blocking reasons.
- Implement metadata search, full-text search, paper-scoped evidence search, and bounded page retrieval.

**Exit:** representative PDFs return verifiable page-located evidence; missing or inadequate files fail closed.

## Phase 4 — Shared MCP and CLI surfaces

- Implement the small MCP tool contract from `DESIGN.md` using the official Python MCP SDK and stdio transport.
- Implement operational CLI commands over the same services.
- Add token-bounded result models and clear provenance in every response.
- Register the same MCP server with Codex and Claude Code using absolute Windows paths.

**Exit:** both agents can run health checks, search the library, retrieve the same paper, and cite the same evidence locators.

## Phase 5 — Knowledge Promotion

- Detect the user-created `SecondBrain Queue` collection.
- Implement Promotion Records and deterministic output paths.
- Implement Paper Brief and Reference Stub validation.
- Add atomic SecondBrain writes, duplicate detection, and update review behavior.
- Preserve the SecondBrain and Graphify folder boundaries.

**Exit:** one eligible queued paper produces a conforming Paper Brief and one ineligible paper produces only a Reference Stub, with no Zotero mutation.

## Phase 6 — Pilot and plugin gate

- Run a ten-paper pilot spanning sport science, return to play, and strength and conditioning.
- Include at least one missing-PDF case, one poor-extraction case, and one paper with tables or complex results.
- Spot-check every numerical claim and Evidence Locator.
- Measure search usefulness, promotion effort, duplicate behavior, and cross-agent consistency.
- Decide whether the observed friction justifies a Zotero plugin.

**Exit:** a written pilot result supports either remaining MCP/CLI-only or defining a narrowly scoped plugin.

## Phase 7 — Automatic grounding and full-library scale

- Add a deep research-grounding module behind one question-to-evidence-pack interface.
- Use deterministic domain query expansion and rank fusion over the existing SQLite/FTS index.
- Report local coverage and evidence readiness; trigger clearly labeled external peer-reviewed fallback when thin.
- Derive a priority-aware backlog over every eligible Zotero research record.
- Preserve the queue as a priority lane while supporting explicit `library` promotion scope.
- Install one harness-neutral grounding skill for Codex, Claude Code, Antigravity, and the canonical `.agents` path.
- Keep existing memory stores intact and define Graphify as downstream discovery rather than evidence authority.

**Exit:** an ordinary sport-science question produces the same bounded Zotero evidence pack in every harness, and
full-library processing can resume without manual collection cleanup.

## Acceptance criteria

- Zotero remains unchanged by automated tests and live use.
- The production key has no write permission.
- No direct `zotero.sqlite` access exists.
- All 2,918 current items are discoverable after initial sync.
- Incremental sync uses Zotero version checkpoints.
- Search works when Zotero is closed; local evidence resolution improves when it is open.
- Every Paper Brief has Usable Full Text and verifiable Evidence Locators.
- Missing or inadequate full text can produce only a Reference Stub.
- Codex, Claude Code, and Antigravity expose the same MCP tools.
- SecondBrain contains derived Markdown only, not copied PDFs.
- Graphify and SportScienceResearchRepo remain separate downstream consumers.

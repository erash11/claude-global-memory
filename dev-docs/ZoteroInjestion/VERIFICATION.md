# Verification Status

Verified on July 24, 2026.

## Passing

- Python source and MCP verification script compile under Python 3.12.
- Ruff reports no lint violations.
- All 42 automated tests pass.
- A real MCP stdio client initializes the server, lists all thirteen expected tools, and calls `zotero_health`,
  `audit_promotion_queue`, `list_library_backlog`, and `build_research_evidence_pack`.
- Codex reports `zotero-research` enabled globally.
- Claude Code reports `zotero-research` connected at user scope.
- The live Zotero library exposes the `SecondBrain Queue` collection with key `NC8TKL4K`.
- The transport rejects non-read HTTP methods and does not forward the API key to attachment-storage redirects.
- The dedicated credential permits library and file reads and has write access disabled.
- Zotero's local API is enabled and responds successfully.
- Initial synchronization completed at library version `6314` with 2,918 current items and 809 full-text records.
- Full-text synchronization completed with zero failures and approximately 40.3 million searchable characters.
- Live searches for return to play and strength and conditioning return relevant full-text-backed papers.
- The shared CLI/MCP pilot audit classifies queued papers without Zotero or SecondBrain writes and optionally builds page-aware evidence caches.
- The latest incremental sync reached library version `6387`; the live index contains 2,930 current items and 803 API-indexed full-text records.
- The ten-paper deep audit resolved Usable Full Text for all ten papers with zero extraction failures.
- Guarded promotion saved ten validated Paper Briefs with page Evidence Locators under `SecondBrain/Knowledge/library/research-papers`.
- Re-running the complete promotion preserved all ten deterministic paths and content hashes.
- The post-promotion Zotero sync reported zero item changes, zero deletions, and zero full-text failures.
- The MCP verification script prints Unicode Zotero titles safely on Windows.
- The live all-library backlog identifies 1,165 eligible research records: 135 ingested, zero ready for review,
  1,028 pending PDF extraction, and two remaining Reference Stub candidates. It separately reports 45 excluded
  non-research or standalone records by Zotero item type.
- The backlog query completes in approximately 0.7 seconds against the current index and resumes from a stable
  offset without requiring collection cleanup.
- A normal return-to-play/load question produced a three-paper `sufficient` Zotero evidence pack; all three had
  indexed full text and two returned page-located evidence.
- `promotion_scope` resolves to `library` while `SecondBrain Queue` remains the priority lane.
- The harness-neutral grounding skill has identical SHA-256 content in `.agents`, `.codex`, `.claude`, and
  `.gemini` skill directories.
- Full-library batch requests now apply tier-aware model routing in the harness layer: Terra handles deterministic
  operations, Sol handles scientific full-text review and Paper Brief promotion, and Luna is restricted to
  deterministic read-only checks when the harness exposes it. The bridge remains model-agnostic.
- The source `SKILL.md` and `references/batch-model-routing.md` both pass skill validation, and their installed
  copies in `.agents`, `.codex`, `.claude`, and `.gemini` have identical SHA-256 hashes.
- Antigravity's MCP config preserves its existing `notebooks` and `visualization` servers and adds the same
  `zotero-research` executable used by Codex and Claude Code.
- Six additional ready records were reviewed from page-located full text and saved through the guarded writer,
  bringing tracked Paper Briefs to 22. Their generated frontmatter and Promotion Record hashes were rechecked.
- Batch `2026-07-22-pending-001` froze ten exact item keys and versions at library version `6333`. All ten PDFs
  extracted to usable page caches with zero failures, received page-reviewed Paper Briefs, and reconciled to ten
  `ingested` outcomes with deterministic paths and content hashes.
- Re-running that completed batch processed zero records, skipped all ten, and preserved one extraction attempt
  per item. Unit tests also cover frozen selection, Reference Stub and explicit failure outcomes, Promotion Record
  reconciliation, and path-traversal rejection.
- Batch `2026-07-23-pending-002` froze twenty exact item keys and versions at library version `6333`. All twenty
  PDFs extracted to usable page caches with zero failures and were manually reviewed into full Paper Briefs with
  page-located findings, limitations, and practitioner interpretation.
- Reconciliation classified all twenty records as `ingested`; a completed-batch rerun processed zero records,
  skipped all twenty, and reported zero failures. Every generated file exists, has exactly one frontmatter block,
  and matches the SHA-256 content hash stored in its Promotion Record.
- Batch `2026-07-24-pending-003` froze the next twenty exact item keys and versions at library version `6333`.
  All twenty PDFs extracted to usable page caches with zero failures and received full-text-reviewed Paper Briefs
  with page-located findings, methods, limitations, and practitioner interpretation.
- Reconciliation classified all twenty records as `ingested`; all artifact, Promotion Record, and ledger hashes
  match, frozen versions match the current index, and every extraction attempt remains exactly one. The completed
  rerun processed zero records, skipped all twenty, and reported zero failures.
- The batch used the staged operations/review/verification workflow, but bridge, MCP, and ledger outputs do not
  expose model telemetry; therefore, the requested Terra/Sol model switch cannot be independently verified and is
  not claimed as an observed runtime fact.
- Batch `2026-07-24-pending-004` froze the next twenty exact item keys and versions at library version `6333`.
  Nineteen records extracted to usable page caches and received full-text-reviewed Paper Briefs. One record
  (`8M3BHVBE`) extracted only one page, failed the two-page evidence threshold, and was correctly limited to a
  claims-free Reference Stub.
- Reconciliation classified all twenty records as `ingested`; all artifact, Promotion Record, and ledger hashes
  match, frozen versions match the current index, and every extraction attempt remains exactly one. The completed
  rerun processed zero records, skipped all twenty, and reported zero failures.
- The staged workflow assigned operations and deterministic verification to Terra and scientific review to Sol,
  but bridge, MCP, ledger, and harness outputs do not independently verify the worker-model switch. The route is
  therefore recorded as requested assignment rather than observed runtime telemetry.
- Batch `2026-07-24-pending-005` refreshed Zotero to library version `6387`, prioritized all seven records newly
  present in `SecondBrain Queue`, and then froze the next thirteen standard backlog records. Nineteen records had
  usable page-aware full text and received full-text-reviewed Paper Briefs; the sole no-PDF record (`W5RBTJMN`)
  was limited to a claims-free Reference Stub.
- Two queued records (`C4QH8W4I` and `IHUQWG7G`) had gained PDFs since their earlier Reference Stub promotion.
  Guarded reconciliation upgraded both artifacts in place to Paper Briefs without rerunning extraction. Their
  attempt counts therefore remain zero by the existing update-only semantics; the other eighteen records have
  one attempt each.
- Reconciliation classified all twenty records as `ingested`; all files exist with exactly one YAML frontmatter
  block, and artifact, ledger, and Promotion Record hashes and versions match. The completed rerun processed zero
  records, skipped all twenty, and reported zero failures. The queue now contains seventeen records, all promoted.
- The staged workflow again assigned operations and deterministic verification to Terra and scientific review to
  Sol, but the available runtime surfaces do not expose model-switch telemetry. The route is recorded as an
  assignment rather than an independently observed runtime fact.
- Batch `2026-07-23-reference-stubs-001` froze all 25 records classified as Reference Stub candidates. All 25
  lacked PDF attachments; their linked objects were metadata aids such as Notion links, snapshots, PubMed entries,
  and a ResearchGate link rather than reviewable full text.
- All 25 were promoted as claims-free `reference-stub` artifacts and reconciled to `ingested`. Every artifact
  retains the explicit `No substantive claims were extracted` warning and matches its Promotion Record hash.
- The live cohort exposed transient Windows `PermissionError` failures during atomic batch-ledger replacement.
  The writer now retries a bounded five times with exponential backoff and removes abandoned temporary files;
  regression tests cover both transient recovery and cleanup after a persistent lock.
- The close review caught one malformed Zotero title (`UYI3N3W8`) inherited from a ResearchGate cover page. Its
  Brief preserves the Zotero key for provenance but identifies and cites the verified McGuigan et al. 2006 paper
  from PDF page 2.

## Promotion state

Production readiness is true. The `SecondBrain Queue` contains seventeen records, and all seventeen have tracked
`status: ingested` artifacts in SecondBrain. Across the library, 110 Paper Briefs and 25 Reference Stubs are
ingested. The first five Paper Brief batches and the first Reference Stub batch are fully promoted, leaving 1,030
of 1,165 eligible records not yet promoted. The backlog is an explicit resumable workflow rather than a manual
collection-management task.

## Remaining evidence limitation

The live Reference Stub path is now exercised across 24 current no-PDF candidates and one naturally occurring
poor-extraction record that failed the two-page evidence threshold. External fallback policy is installed in each
harness, but actual tool discovery in already-open Codex, Claude Code, or Antigravity sessions requires a restart.
The pilot decision remains MCP/CLI-only unless repeated native-Zotero workflow friction appears.

## Conversational acceptance test 1

**Question:** How should training-load history and current football exposure influence return-to-training and
return-to-play decisions after a lower-extremity injury?

**Verdict:** Pass. The retrieval-relevance and population-alignment defects are both resolved.

- The initial run returned two off-topic top-five papers because the query planner crossed stopwords to create
  weak fragments (`history and`, `and current`) and unweighted BM25 allowed repeated full-text mentions to outrank
  title matches.
- Two red-capable regression tests reproduced both failure modes before the fix.
- The corrected planner segments at stopwords, adds football/load/lower-extremity phrases, and weights title,
  abstract, and tags above full-text-only matches.
- The corrected live result returned four directly relevant, page-located football/load/RTS papers in the top five;
  the fifth was a broader football physiology review available as metadata only.
- The evidence pack now extracts explicit applicability requirements for sport code, sex, age group, competition
  level, injury region, and injury type. Each paper reports aligned dimensions and conflicts; metadata rather than full
  text is used for this classification so cited references cannot create false population alignment.
- Coverage now requires at least two aligned full-text papers when applicability context is explicit. Regression
  tests confirm that one American-football paper plus soccer and Australian-football papers remains `thin`, while
  two aligned full-text papers restore `sufficient` coverage.
- The live explicit American-football rerun detected `sport=american_football` and
  `injury_region=lower_extremity`. Five local papers matched, but only one aligned paper had page/full-text evidence,
  so the bridge correctly returned `thin` and recommended external search without an agent override.
- The cross-harness skill now contextualizes unqualified `football` as collegiate American football in the user's
  Baylor performance setting unless another football code is stated. Its source and all four installed copies have
  one identical SHA-256 hash.
- The answer was additionally checked against the local RTP decision model, ACWR systematic review, and training
  load methodological critique. ACWR was treated as contextual monitoring information, not a clearance threshold,
  injury predictor, or established causal control variable.

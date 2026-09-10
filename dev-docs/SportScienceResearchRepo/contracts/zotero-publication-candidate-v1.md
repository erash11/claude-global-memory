# Zotero Publication Candidate v1

The Evidence Library owns this interface. ZoteroInjestion is the producer adapter; the candidate validator and
publication workflow in this repository are the consumer adapter.

## Admission sequence

1. A Zotero Source Paper receives a current, validated Paper Brief with Usable Full Text and page Evidence
   Locators.
2. An agent prepares the same public synthesis fields used by `papers.json` and selects controlled taxonomy.
3. `zotero-bridge publication-candidate ITEM_KEY synthesis.json` verifies Zotero identity, version, full text,
   Paper Brief integrity, and synthesis identity before exporting a candidate.
4. `npm run candidate:check -- candidate.json` validates the interface and checks existing publications for
   DOI, citation, item-key, and candidate conflicts, including other staged candidates.
5. An accountable library reviewer confirms interpretation, applicability, and public language.
6. `npm run candidate:stage -- candidate.json --paper-id ID --reviewed-by NAME --reviewed-on YYYY-MM-DD`
   records approval without changing `papers.json`. `ID` must be the next unused stable ID after both published
   and already staged reservations.
7. `npm run candidate:apply -- docs/zotero-synthesis/PUBLICATION.json --published-on YYYY-MM-DD` performs the
   local publication mutation and rolls back if taxonomy or publication audits fail.
8. Commit, push, and deployment remain separate deliberate actions.

## Interface invariants

- `schemaVersion` is `ask-library-publication-candidate.v1`.
- `status` is `READY_FOR_LIBRARY_REVIEW`; this is not reviewer approval.
- `candidateId` is `zotero-<itemKey>-v<itemVersion>`.
- JSON object property order is irrelevant; missing and unexpected properties are rejected.
- The Paper Brief is current, unchanged, and backed by Usable Full Text.
- Every Evidence Locator page is within the verified attachment page count.
- DOI, year, title, and citation identity agree across Zotero and the public synthesis.
- `paper` uses the persisted Evidence Library fields except `id` and `driveUrl`, which belong to publication.
- `taxonomy` uses the controlled values exported by `evidence-taxonomy.mjs`.
- `publicSourceUrl` is a public HTTP(S) DOI or publisher URL without credentials or private-network hosts,
  never a local PDF path.
- Staff-only source locators preserve item version and attachment identity as
  `zotero:<itemKey>@<itemVersion>#<attachmentKey>`. The bridge must confirm that identity before returning
  cached page text for an audit.

The machine-readable schema is
[`zotero-publication-candidate-v1.schema.json`](./zotero-publication-candidate-v1.schema.json).

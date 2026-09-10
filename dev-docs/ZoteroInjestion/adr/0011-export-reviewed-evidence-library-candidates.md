# Export reviewed Evidence Library candidates

**Status:** Accepted

## Context

Ask the Library is grounded only in curated Evidence Library resources, while the Zotero Library contains a
larger private research corpus. Directly querying unreviewed Zotero summaries from Ask the Library would bypass
the Evidence Library's publication, taxonomy, source-identity, and original-text requirements. Copying Zotero
PDFs into the public repository would also combine private research access with public distribution.

## Decision

The bridge may export a versioned `ask-library-publication-candidate.v1` JSON artifact only when:

1. the Zotero item has a current promoted Paper Brief rather than a Reference Stub;
2. Usable Full Text and page Evidence Locators remain available;
3. the Paper Brief hash still matches its Promotion Record;
4. the reviewed synthesis matches a present, parseable current Zotero DOI, year, and title; and
5. the artifact contains the Evidence Library's 13-field synthesis content (excluding the library-assigned
   `id` and `driveUrl`) plus reviewed taxonomy.

The export status is `READY_FOR_LIBRARY_REVIEW`. It is not publication approval and does not write to
SportScienceResearchRepo. The Evidence Library remains responsible for duplicate checks, controlled-taxonomy
validation, accountable reviewer approval, stable ID assignment, and publication.

Ask the Library may audit a published Zotero-backed source through the bridge's cached page-text interface.
The public record points to a public DOI or publisher landing page without credentials or private-network
hosts; it does not expose or copy the private PDF.

## Consequences

- Zotero and SecondBrain retain their existing source-ownership roles.
- Ask the Library gains access to reviewed Zotero evidence without bypassing Evidence Library governance.
- Candidate files stay under the bridge's derived `publication-candidates` directory; an export cannot target
  the public repository or another arbitrary path.
- The candidate JSON interface is intentionally small and versioned; the two repositories remain separately
  deployable.
- Publication remains a deliberate reviewed action. No command commits, pushes, or deploys automatically.

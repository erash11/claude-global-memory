# Admit reviewed Zotero publication candidates

Ask the Library may use a Zotero source only after it enters the curated Evidence Library through the
versioned `ask-library-publication-candidate.v1` interface. Zotero search results, metadata-only records, and
Reference Stubs are not Evidence Library sources.

A candidate must preserve the current Zotero item and attachment identity, Zotero version, Paper Brief hash,
Usable Full Text status, page Evidence Locators, the public 13-field synthesis content, and controlled taxonomy.
The candidate is only `READY_FOR_LIBRARY_REVIEW`; one accountable library reviewer must confirm its
interpretation, applicability, and public language before assigning a stable Evidence Library ID.

Approved candidates are staged under `docs/zotero-synthesis/`. Applying a staged publication updates
`papers.json` and reviewed taxonomy locally, runs the publication audits, and rolls back if verification fails.
It never commits, pushes, or deploys.
Staging reserves only the next unused stable ID across the public corpus and all other staged publications;
candidate and publication audits reject duplicate reservations and cross-candidate DOI, citation, or item-key
conflicts.

The public paper record uses a DOI or publisher landing page rather than copying the private Zotero PDF.
Original-source claim auditing in the staff-only Ask the Library workflow resolves published Zotero provenance
through the read-only bridge, confirms the preserved Zotero item version and attachment key, and only then
checks cached page text. The public GitHub Pages Evidence Library remains a separate deployment.

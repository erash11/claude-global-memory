# Use hybrid retrieval without direct database access

The Retrieval Gateway will use Zotero's Web API for always-available metadata and indexed-text access, and Zotero's local API or attachment files when the desktop client is running and local evidence access is needed. It will not read `zotero.sqlite` directly, avoiding coupling to Zotero's internal schema while retaining both remote availability and richer local access.

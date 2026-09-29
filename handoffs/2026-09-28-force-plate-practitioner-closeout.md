# Force Plate Practitioner course closeout — 2026-09-28

## Purpose and state

Archived the Applied Performance Force Plate Practitioner course for offline use and prepared its bibliography and resources in Zotero. The course capture and Zotero import are complete on the Windows machine. Direct Flint ingestion was not part of the verified closeout.

## Verified deliverables

- Drive archive: `G:\My Drive\00_Primary_Storage_Drive\09_PRO_DEV\Force_Plate_Practitioner`. It has 76 lesson sets, each with one MP4, checked transcript, and summary, across 14 sections; 9 course PDF resources; 8 offline article Markdown files; and the README and course resource index. The delivery script checked copied file hashes.
- Zotero collection: `Force Plate Practitioner`, key `AE56U77Q`. The live local API showed 71 top-level records on 2026-09-27. The original import package covered 43 new course bibliography records and 9 course PDF records; the collection also holds other records.
- The nine course PDF originals all exist in the Drive archive. Their SHA-256 hashes match nine child PDF attachments in Zotero. All nine linked targets exist under Zotero's linked-attachment base directory, `G:\My Drive\Zotero_PDFs`. Eric opened a sample PDF in Zotero.
- Zotero's local API is enabled. On this Windows environment, Python `requests` with `Session.trust_env=False` reached `127.0.0.1:23119` after proxy-aware PowerShell calls failed.
- The Zotero research bridge saw the course records after an index refresh. Its `get_paper_pages` call returned page text from the linked `IMTP Protocol` PDF. This verifies on-demand page access in the research bridge, not full indexing of every course PDF.

## Decisions and limits

- Keep the material in the renamed `Force Plate Practitioner` collection; do not move it to `APC_JumpsCourse`.
- Keep linked PDFs in the user's Google Drive/ZotMoov workflow. Zotero metadata sync does not itself sync linked PDF bytes. Other machines need the linked-attachment base directory and Drive files available.
- Transcripts were checked against captions/ASR, with focused reviews and corrections, but were not fully proofread word by word against audio. Summaries describe course teaching; cited scientific claims were not independently validated.
- Flint ingestion and independent Ask the Library ingestion were not directly tested. Treat either as a separate integration task if required.

## Paths created or modified in this course session

- `C:\Users\eric_rash\Documents\Codex\2026-09-26\sim\work\rename_force_plate_zotero.py`
- `C:\Users\eric_rash\Documents\Codex\2026-09-26\sim\work\audit_zotero_links.py`
- `C:\Users\eric_rash\Documents\Codex\2026-09-26\sim\work\audit_zotero_live.py`
- Drive archive root above; final lesson files are in its 14 section folders. See its README and `COURSE_RESOURCES.md` for inventory and verification notes.
- This handoff: `C:\Users\eric_rash\.claude\global-memory\handoffs\2026-09-28-force-plate-practitioner-closeout.md`.

## Next

1. If Flint must contain the course itself, run and verify a separate Flint import from the Drive archive while retaining provenance and transcript verification labels.
2. On the Mac or another machine, confirm Google Drive has synced `Zotero_PDFs` and the Zotero linked-attachment base directory resolves there before assuming PDF access.

## Closeout environment note

The 2026-09-28 closeout sweep found no dirty or unpushed repos directly under `Desktop\DEV`, `Desktop\DEV\Football`, or `Desktop\DEV\SpecialRequests`. The dotclaude and global-memory repos had unrelated transcript changes. `global-memory/transcripts/.errors.log` was nonempty with earlier compiler flush and memsearch errors; do not erase those errors without confirming recovery.

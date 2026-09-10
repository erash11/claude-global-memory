# Zotero photo capture — design spec

**Date:** 2026-07-26
**Status:** Prototype built (`zotero-photo-capture/`), pipeline proven, runners pending
**Problem:** Photograph a research article with a phone → the article lands in the Zotero library with correct metadata, reachable from the Zotero mobile app and the web library.

---

## 1. Prior-art research — does this already exist?

Short answer: **no**, and the reason is architectural, not neglect.

### 1.1 The blocking constraint

**Zotero plugins cannot run on mobile.** The desktop client is a Firefox/XUL-derived application that loads bootstrapped `.xpi` extensions; the iOS and Android clients are native apps with no extension host. The Zotero developers have said directly that there is no way to support plugins on iOS — the comparison users make to Obsidian fails because Obsidian's mobile app is largely a web view and Zotero's is not.

Consequence: **a "Zotero plug-in" in the literal sense cannot be the thing that does this.** Anything triggered from a phone must run either (a) on a desktop Zotero that syncs, or (b) as a service talking to the Zotero Web API.

### 1.2 What the mobile app already does

| Capability | Status |
|---|---|
| Add by identifier (type/paste DOI, ISBN, PMID) | ✅ Built in |
| **Scan** a barcode or a DOI with the camera | ✅ Built in (iPhone and iPad, under the `+` menu) |
| Attach a **PDF** from Files | ✅ Built in |
| Attach a **photo / JPEG** | ❌ Attachment picker is PDF-only |
| Retrieve metadata for an attached PDF | ✅ Recently added to iOS |
| Plugins | ❌ Not supported, no roadmap |

So the mobile app covers the easy case: if the paper prints its DOI on page 1 and the camera can resolve that text, "Scan → Add by identifier" already works today. That is worth knowing before building anything.

### 1.3 What exists on desktop

- **`UB-Mannheim/zotero-ocr`** — OCRs an *already-attached* PDF via Tesseract and attaches the text layer. Desktop-only, requires local Tesseract + pdftoppm paths configured. Does not create items, does not resolve metadata, does not touch photos.
- **`T-Dane/zotero-embedded-ocr`**, **`EdiEco/zotero-ocr-extras`** — forks of the above.
- **`fr-meyer/zotero-docai-pipeline`** — PDF → Markdown via a document-AI provider, saved as a Zotero note. Post-processing of existing items.
- **`ydeng11/zotero-zotadata`**, **`bwiernik/zotero-shortdoi`** — metadata repair / DOI validation on existing items.
- **Zotero's own "Retrieve Metadata for PDF"** — sends the first pages of a PDF to Zotero's recognizer service, which uses extraction heuristics plus Crossref and ISBN lookup to build a parent item. **It operates on the extractable text layer.** A camera photo, or a scan with no OCR layer, has no text — so this silently fails on exactly the input we care about.

### 1.4 The gap

Every component exists separately. Nothing chains them:

```
photo → (OCR)          zotero-ocr does this, on desktop, for PDFs already in the library
      → (identify)     Zotero's recognizer does this, but only with a text layer
      → (resolve)      shortdoi/zotadata do this, but only for items that already exist
      → (create item)  nothing does this from a photo
```

There is no tool — plugin, app, or script — that takes a phone photo of a paper and produces a Zotero item. **We're building the missing chain.**

### 1.5 Deliberate scope note

Zotero desktop already handles the "born-digital PDF" path well. This project is aimed at the case Zotero handles badly: **an image-only capture** — a phone photo of a printed page, a conference handout, a book chapter opener, a poster, a screenshot with no text layer.

---

## 2. Architecture

The plugin framing has to change, because the plugin surface doesn't exist on mobile. What replaces it:

```
  CAPTURE                 INGEST              PIPELINE                    WRITE
┌───────────┐        ┌──────────────┐   ┌──────────────────┐      ┌─────────────────┐
│ phone     │───────▶│ CLI (built)  │──▶│ 1 extract        │─────▶│ Zotero Web API  │
│ camera    │        │ folder watch │   │ 2 resolve        │      │ v3              │
│           │        │ shortcut/POST│   │ 3 match+score    │      │  · parent item  │
└───────────┘        └──────────────┘   │ 4 map            │      │  · PDF attach   │
                                        │ 5 dedup          │      └────────┬────────┘
                                        └──────────────────┘               │
                                                                      sync ▼
                                                        Zotero mobile app + web library
```

**The Zotero Web API is the write surface, not a desktop plugin.** That is what makes "from the mobile app or the web" work: items written to the API appear in the mobile app and at zotero.org/mylibrary on next sync, with no desktop machine involved.

### 2.1 Pipeline stages

| # | Stage | Implementation | Purity |
|---|---|---|---|
| 1 | **Extract** | Claude (`claude-opus-5`) vision call over the page images, structured-output JSON schema. One call does OCR *and* field extraction — strictly better than Tesseract + regex on a skewed, shadowed phone photo. | I/O |
| 2 | **Resolve** | Crossref REST. DOI present → `GET /works/{doi}` (authoritative, done). No DOI → `GET /works?query.bibliographic=...` for candidates. OpenAlex as fallback. Both free, no key. | I/O |
| 3 | **Match** | Score candidates against the extracted fields: trigram-Dice title similarity + author-surname overlap + year proximity. Auto-accept above threshold, otherwise surface for confirmation. | **Pure** |
| 4 | **Map** | Crossref work → Zotero item JSON (type mapping, creator splitting, JATS abstract stripping, date normalisation). | **Pure** |
| 5 | **Dedup** | Search the target library for the DOI before creating. Existing item → attach the photos to it instead of creating a duplicate. | I/O |
| 6 | **Write** | Create parent item; build a PDF from the source images; three-step Zotero file upload (authorise → S3 → register). | I/O |

Stages 3 and 4 are pure functions and carry the unit tests. They're also where the interesting failure modes live (a confident wrong match is worse than no match).

### 2.2 Why the extraction step is a vision model

A phone photo of a journal page is a hard OCR target: perspective skew, page curl, uneven lighting, two-column layout, ligatures, a DOI printed in 6pt grey. Classical OCR gets the characters roughly right and then loses completely on *structure* — which line is the title, which names are authors versus affiliations, which number is the volume.

A vision model reads the page and returns typed fields in one pass. It also self-reports confidence per field, which feeds the match threshold. The cost is a few cents per capture; the alternative is a brittle regex layer over Tesseract output.

**The extraction output is treated as a search key, never as final metadata.** Final metadata always comes from Crossref/OpenAlex. This is the key design decision: the model's job is to find the paper, not to describe it. A hallucinated page range never reaches the library because the page range is taken from the registry record, not the photo.

### 2.3 Runner options (the "how does the phone reach it" layer)

The core is runner-agnostic. In rough order of effort:

| Runner | Trigger | Needs | Status |
|---|---|---|---|
| **CLI** | `zotero-snap add p1.jpg p2.jpg` | Nothing | ✅ Built |
| **Folder watch** | Photos sync into a watched dir (iCloud/Dropbox/Drive) | A machine that stays on | Planned |
| **iOS Shortcut → HTTP** | Share sheet from Photos → POST to a small service | Hosting | Planned |
| **Zotero 7 desktop plugin** | Watches a "Camera Inbox" collection; user attaches PDFs from the mobile app | Desktop Zotero running | Optional |

The desktop-plugin option is worth noting because it *is* buildable as a real Zotero plugin and needs no hosting or API key — but it inverts the constraint: capture is instant, processing waits for a desktop. It's a wrapper around the same core, not a different product.

---

## 3. Failure modes and how they're handled

| Failure | Handling |
|---|---|
| No DOI visible on the page | Fall through to bibliographic search on title+author+year |
| Title OCR'd with errors | Trigram Dice tolerates character-level noise |
| Crossref returns a plausible-but-wrong paper | Combined score must clear the threshold; below it, report candidates rather than write |
| Paper genuinely not in Crossref | Fall back to OpenAlex; if still nothing, create an item from extracted fields, flagged in `extra` as unverified |
| Same paper photographed twice | DOI dedup before create; second capture attaches to the existing item |
| HEIC input | Not handled by `pdf-lib` — convert to JPEG at capture (iOS Shortcuts does this natively) |

---

## 4. Verification

- Unit tests over the pure stages (`match`, `map`) — scoring behaviour, type mapping, creator splitting, JATS stripping, date normalisation. Run with `npm test`.
- End-to-end requires a real photo, an `ANTHROPIC_API_KEY`, and a Zotero API key against a scratch library. `--dry-run` prints the resolved item without writing.

---

## 5. Decisions

1. **Write via the Zotero Web API, not a desktop plugin.** Only path that satisfies "from the mobile app or the web".
2. **Vision model for extraction, registry for metadata.** The photo finds the paper; Crossref describes it.
3. **Refuse to guess.** Below-threshold matches report candidates instead of writing a wrong item. A silently wrong reference is the expensive failure in a citation manager.
4. **Core is a library; runners are thin.** CLI first because it's testable today with zero infrastructure.

## 6. Open questions for the user

- Phone platform (iOS vs Android) — determines whether the Shortcuts path is available.
- Willingness to host a small always-on service vs. preferring a desktop-dependent path.
- Target library: personal vs. a group library.

# Scaled Research Library Architecture Design

**Date:** 2026-03-24
**Project:** Baylor Football Sport Science Research Library
**Lead:** Eric Rash, Director of Applied Performance
**GitHub:** github.com/Erash11
**Status:** Approved

---

## Problem Statement

The research library currently stores all paper data in `window.storage` (5MB limit, ~80–100 paper capacity). The `SourcePapers/` directory now contains 2,182 PDFs, and 20+ papers will be added per month. The current architecture cannot scale.

---

## Goals

1. Support 2,000+ papers today with room to grow indefinitely
2. Maintain shared real-time visibility for all staff
3. Keep the batch AI import workflow (Eric processes PDFs with AI agents)
4. Keep the in-app form for staff to submit individual papers
5. Notify Eric when pending papers need to be committed to GitHub
6. Preserve the existing UI, table columns, search, and filter behavior

---

## Architecture: GitHub JSON + Pending Queue

### Data Sources

| Source | Contents | Capacity |
|--------|----------|----------|
| GitHub `papers.json` (public repo) | All permanently committed papers | Unlimited |
| `window.storage` key `fb-research-lib-pending-v1` | Papers submitted via in-app form, not yet committed | ~50–100 papers |

The app merges both sources on every load. GitHub papers load first; pending papers with IDs not already in GitHub append at the end. Pending papers whose `id` matches a GitHub paper are automatically removed from the queue on next load (deduplication — no manual "Clear Queue" step).

### GitHub Repository

- **Repo:** `https://github.com/Erash11/baylor-sport-science-library` (public)
- **File:** `papers.json` — a bare JSON array `[...]` of paper objects
- **Fetch URL:** `https://raw.githubusercontent.com/Erash11/baylor-sport-science-library/main/papers.json`
- **Auth:** None required (public repo, read-only fetch)
- **Known limitation:** The fetch URL is hardcoded to the `main` branch. If future workflow requires staging on a branch before promoting (e.g., reviewing a batch import), the URL in the component will need to be updated manually. This is acceptable for the current workflow.

### Caching Strategy

The full GitHub JSON (2,000+ papers × ~2KB each ≈ 4–5MB) is too large to cache in `window.storage` (which shares the same 5MB limit being escaped). Therefore:

- **No `window.storage` cache.** The browser's built-in HTTP cache handles fetch caching automatically. `raw.githubusercontent.com` serves responses with appropriate `Cache-Control` headers, so repeat loads within a session hit the browser cache, not the network.
- **Fallback:** If the fetch fails and the browser has no cached response, the app shows a warning banner and displays pending queue papers only.
- **`window.storage` is used only for the pending queue** (`fb-research-lib-pending-v1`), which stays small (staff form submissions only).

### Storage Keys

| Key | Purpose | Status |
|-----|---------|--------|
| `fb-research-lib-v2` | Old bulk storage | **Retired** — migrated on first load |
| `fb-research-lib-pending-v1` | Pending queue (in-app form submissions) | **Active** |

### Paper Schema

Unchanged. Each paper object has exactly 12 persisted fields:

```
id, year, citation, doi, driveUrl, abstract, tldr, methods,
findings, limitations, practicalImplications, athleteDev, rtp
```

A `source` field is added at runtime only (never persisted, stripped on export):
- `"github"` — loaded from GitHub
- `"pending"` — loaded from `window.storage` pending queue

`driveUrl` is not a visible table column — it is rendered inline as an "Open →" link inside the citation cell, consistent with the current implementation. This behavior is preserved for pending papers as well.

**ID constraint for deduplication:** Paper `id` values must be preserved exactly when committing pending papers to GitHub. Do not regenerate IDs during batch import or copy-paste. Deduplication matches on `id` string equality; a regenerated ID will cause the pending paper to persist in the queue indefinitely.

A `submittedBy` field may be added to pending papers in a future release. This would require bumping the pending queue key to `fb-research-lib-pending-v2`. Deferred — out of scope for this release.

### Migration from Previous Architecture

On first load after the update — detected when `fb-research-lib-v2` exists in storage AND its parsed value is a non-empty array:

1. Read papers from `fb-research-lib-v2`
2. Read existing contents of `fb-research-lib-pending-v1` (may already have entries from a previous partial migration attempt)
3. Merge: combine the two arrays, deduplicated by `id` (existing pending entries take precedence to avoid overwriting newer data). This prevents duplicate accumulation if migration is retried after an ambiguous write failure.
4. **Await** the write of the merged result back to `fb-research-lib-pending-v1`
5. **Only if step 4 succeeded (no exception thrown):** write `"[]"` back to `fb-research-lib-v2` to mark it as migrated. If step 4 threw, abort migration, leave `fb-research-lib-v2` untouched, and let the next load retry.
6. Continue with normal load sequence (step 3 of the App Load Sequence reads the now-updated pending key)

On all subsequent loads, the `fb-research-lib-v2` check finds an empty array and skips migration.

The 8 existing `DEFAULT_PAPERS` hardcoded in the component are moved into the initial `papers.json` on GitHub. The `DEFAULT_PAPERS` constant is removed from the component.

### papers.json Top-Level Structure

```json
[
  { "id": "1", "year": 2025, "citation": "...", ... },
  { "id": "2", "year": 2024, "citation": "...", ... }
]
```

Plain array. No wrapper object.

---

## UI Changes

### 1. Pending Badge (Header)

- Shown only when pending queue count > 0
- Label: `⏳ N Pending Papers`
- Red/amber styling to draw attention
- Clicking opens the Pending Panel

### 2. Pending Panel

- Lists all pending papers (citation, date added), each with a **×** remove button to cancel a pending submission
- **"Download papers.json for GitHub"** button:
  - **Disabled** until the full app load sequence (steps 1–5) has completed. Also disabled when `fetchFailed = true`.
  - **When enabled:** generates **exactly the merged array from step 5** — GitHub papers first, then deduplicated pending papers appended — with the runtime `source` field stripped from every object. The output conforms exactly to the 12-field paper schema (no extra fields, no missing fields), making it directly re-importable as a future baseline. This file, when committed to GitHub, becomes the new source of truth. Eric downloads it, opens `baylor-sport-science-library` on GitHub, replaces `papers.json` content with the downloaded file, and commits.
  - **When `fetchFailed = true`:** button remains **disabled**, tooltip reads: `"Cannot generate complete papers.json — GitHub data unavailable. Resolve the connection issue first."`
- **"Close"** button
- After Eric commits to GitHub, auto-dedup removes matching papers from the pending queue on the next app load

> **Why file download instead of clipboard:** The merged JSON at 2,000+ papers is 4–6MB — too large for a reliable clipboard write across all browsers. A file download is unambiguous and directly uploadable to GitHub's file editor.

### 3. Pagination

- 50 papers per page
- Row numbers are **global** (page 1 shows rows 1–50, page 2 shows 51–100, etc.)
- Controls: Prev / page numbers (with ellipsis for large sets) / Next
- Status line: `Showing 1–50 of 2,182 papers` or `12 matches for "hamstring"`
- Search and filter changes reset to page 1 automatically

### 4. Pending Row Tag

- Papers from the pending queue display a `⏳ PENDING` badge in the table row (inline with the citation)
- Distinguishes committed vs. pending papers for all staff

### 5. Remove Button Behavior

- **Pending papers:** Remove button works as before — deletes the paper from `fb-research-lib-pending-v1`
- **GitHub papers:** Remove button is **disabled** (greyed out, tooltip: "Committed papers can only be removed by editing papers.json on GitHub"). GitHub is the source of truth; client-side removal would be overwritten on the next fetch.

### 6. Fetch Status Banner

- When GitHub fetch fails (offline, rate limit, network error):
  - Yellow warning banner directly below the header
  - Text: `"Could not load library data from GitHub. Showing locally submitted papers only. Check your connection or try refreshing."`
  - Banner persists until the page is reloaded successfully
  - Pending queue papers still display below the banner
- While fetching: a loading spinner replaces the table until data is ready

### 7. Form Submission Error Handling

- If the `window.storage` write fails during form submission, the user sees an inline error message: `"Could not save paper. Storage may be unavailable — please try again or contact Eric."`
- The form does not close on failed write

---

## App Load Sequence

1. Fetch `papers.json` from GitHub raw URL (browser HTTP cache handles repeat-load performance)
   - On success: set `githubPapers` to parsed array; set `fetchFailed = false`
   - On failure: set `githubPapers` to `[]`; set `fetchFailed = true`; show warning banner
2. **Migrate** (if `fb-research-lib-v2` exists AND parses to a non-empty array):
   a. Read papers from `fb-research-lib-v2`
   b. Merge into `fb-research-lib-pending-v1` (await write before continuing)
   c. Write `"[]"` to `fb-research-lib-v2` (marks as migrated)
3. Load pending queue from `fb-research-lib-pending-v1`
4. **Deduplicate** (only if `fetchFailed = false`): remove any pending papers whose `id` exists in `githubPapers`; write cleaned queue back to storage. **Skip this step entirely if `fetchFailed = true`** — never dedup against an empty array from a failed fetch, as this would incorrectly preserve papers that are actually committed.
5. Merge arrays: `githubPapers` first, remaining pending papers appended
6. Render paginated table (50/page, global row numbers)

---

## Workflows

### Staff Adds a Paper (In-App Form)

1. Staff fills out "+ Add Paper" form → submits
2. Paper saved to `fb-research-lib-pending-v1` (shared: true) — all staff see it immediately with `⏳ PENDING` tag
3. If write fails: user sees error message (paper not saved)
4. Eric sees the pending badge the next time he opens the app
5. Eric clicks badge → reviews pending papers → clicks "Download papers.json for GitHub"
6. File downloads as `papers.json`
7. Eric opens `github.com/Erash11/baylor-sport-science-library` → opens `papers.json` → replaces file content → commits
8. On next app load: dedup detects committed papers → auto-removes them from pending queue

### Monthly Batch Import (Eric + AI Agents)

1. AI agents process PDFs from `SourcePapers/` → generate array of paper objects (12-field schema, IDs preserved)
2. Eric merges new objects into `papers.json` on GitHub → commits
3. App picks up new papers on next load (browser HTTP cache expires, or hard refresh)
4. No in-app action needed — batch imports go directly to GitHub, not through pending queue

---

## Non-Goals (Out of Scope)

- Automatic GitHub commits from the browser (requires embedded auth token — security risk)
- PDF upload or storage within the app
- Role-based access control
- Full-text search on PDF content (metadata search only)
- Backend server or database
- Submitter identity in the permanent schema (deferred to future release)
- Branch-based staging for batch imports (known limitation of hardcoded main URL)

---

## Implementation Checklist

### GitHub Setup
- [ ] Create `baylor-sport-science-library` public repo under `Erash11`
- [ ] Create initial `papers.json` with the 8 existing `DEFAULT_PAPERS` + all AI-processed `SourcePapers/` PDFs

### Component Changes (`football-research-library.jsx`)
- [ ] Remove `DEFAULT_PAPERS` constant
- [ ] Add GitHub fetch logic on load (`useEffect`); track `fetchFailed` state; handle failure with warning banner and empty array fallback
- [ ] Add loading spinner while fetch is in progress
- [ ] Add migration logic: if `fb-research-lib-v2` parses to non-empty array → read → await write to `fb-research-lib-pending-v1` → write `"[]"` to `fb-research-lib-v2`
- [ ] Update storage key to `fb-research-lib-pending-v1`
- [ ] Add deduplication logic: skip entirely when `fetchFailed = true`; otherwise remove pending papers with IDs in GitHub array and write cleaned queue back
- [ ] Add Pending Badge to header (conditional, shows count)
- [ ] Add Pending Panel: list of pending papers (citation + date + per-paper × remove button), Download button (disabled when `fetchFailed`), Close button
- [ ] Add "Download papers.json for GitHub" function: merge arrays, strip `source` field, trigger Blob file download as `papers.json`; disabled when `fetchFailed = true`
- [ ] Disable Remove button for GitHub-sourced papers with tooltip; keep functional for pending papers
- [ ] Add pagination (50/page, global row numbers, prev/next/page-number controls, result count line)
- [ ] Add `⏳ PENDING` row badge for pending-source papers
- [ ] Add fetch failure warning banner
- [ ] Add form submission error handling (show inline error on storage write failure)

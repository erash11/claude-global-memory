# Scaled Research Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the research library from a 5MB `window.storage` architecture to a GitHub-backed unlimited-capacity system with a pending queue for staff submissions.

**Architecture:** GitHub hosts `papers.json` (fetched on load via raw URL, no auth). Staff form submissions go to `window.storage` key `fb-research-lib-pending-v1` as a pending queue. The app merges both on every load, deduplicates, and displays a paginated table with a pending badge/panel for Eric to commit submissions to GitHub.

**Tech Stack:** React functional component (hooks), inline CSS, `window.storage` async API (get/set only, shared: true), native `fetch()` API, Blob file download.

**Spec:** `docs/superpowers/specs/2026-03-24-scaled-research-library-design.md`

**Single file:** All changes are in `football-research-library.jsx`. No new files are created in the repo.

---

## Constants Reference

```
GITHUB_URL = "https://raw.githubusercontent.com/Erash11/baylor-sport-science-library/main/papers.json"
PENDING_KEY = "fb-research-lib-pending-v1"
OLD_KEY     = "fb-research-lib-v2"
SCHEMA_FIELDS = ["id","year","citation","doi","driveUrl","abstract","tldr","methods","findings","limitations","practicalImplications","athleteDev","rtp"]
```

---

## Task 0: Create GitHub Repository (Manual Prerequisite)

**Files:** None in this repo — action is on GitHub.com

- [ ] **Step 1: Create the GitHub repository**

  Go to https://github.com/new and create a public repository:
  - Owner: `Erash11`
  - Repository name: `baylor-sport-science-library`
  - Visibility: Public
  - Initialize with a README: No

- [ ] **Step 2: Create initial `papers.json`**

  In the new repo, create a file named `papers.json` at the root. Its content is the 8 existing DEFAULT_PAPERS from `football-research-library.jsx` lines 3–116, formatted as a bare JSON array. Use exactly this structure (no wrapper object):

  ```json
  [
    {
      "id": "1",
      "year": 2025,
      "citation": "Baylor Applied Sport Science. DEXA Data in Football Analytics: The Gridiron Blueprint.",
      "doi": "",
      "driveUrl": "https://docs.google.com/document/d/1gxa6u7lbla3P7c_g26kQUl_K8t3YBLkbCBXtL5vEo8c/edit",
      "abstract": "...",
      "tldr": "...",
      "methods": "...",
      "findings": "...",
      "limitations": "...",
      "practicalImplications": "...",
      "athleteDev": "...",
      "rtp": "..."
    }
  ]
  ```

  **Important:** Copy the actual full field values from `football-research-library.jsx` lines 3–116 for all 8 papers. Do not commit the literal `"..."` placeholder strings shown in the example above — those are illustrative only.

- [ ] **Step 3: Verify the raw URL works**

  Open this URL in a browser and confirm it returns a JSON array:
  `https://raw.githubusercontent.com/Erash11/baylor-sport-science-library/main/papers.json`

---

## Task 1: Add Constants and New State Variables

**Files:**
- Modify: `football-research-library.jsx:1–2` (add constants before DEFAULT_PAPERS)
- Modify: `football-research-library.jsx:123–135` (component state)

- [ ] **Step 1: Add constants at the top of the file (line 1, before DEFAULT_PAPERS)**

  Insert these three lines at the very top of `football-research-library.jsx`, before the `DEFAULT_PAPERS` line:

  ```javascript
  const GITHUB_URL = "https://raw.githubusercontent.com/Erash11/baylor-sport-science-library/main/papers.json";
  const PENDING_KEY = "fb-research-lib-pending-v1";
  const OLD_KEY = "fb-research-lib-v2";
  const SCHEMA_FIELDS = ["id","year","citation","doi","driveUrl","abstract","tldr","methods","findings","limitations","practicalImplications","athleteDev","rtp"];
  ```

- [ ] **Step 2: Replace the state declarations inside the component**

  Find the current state block (lines 124–135) and replace it with:

  ```javascript
  const [papers, setPapers] = useState([]);          // merged: github + pending (with runtime source tags)
  const [pendingPapers, setPendingPapers] = useState([]); // pending subset only (no source tag)
  const [fetchFailed, setFetchFailed] = useState(false);
  const [loadComplete, setLoadComplete] = useState(false);
  const [search, setSearch] = useState("");
  const [yearFilter, setYearFilter] = useState("all");
  const [sortCol, setSortCol] = useState("year");
  const [sortDir, setSortDir] = useState("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [showUpload, setShowUpload] = useState(false);
  const [showPendingPanel, setShowPendingPanel] = useState(false);
  const [toast, setToast] = useState(null);
  const [formError, setFormError] = useState(null);
  const [uploadForm, setUploadForm] = useState({
    citation:"",doi:"",driveUrl:"",year:"2025",abstract:"",tldr:"",
    methods:"",findings:"",limitations:"",practicalImplications:"",athleteDev:"",rtp:""
  });
  ```

- [ ] **Step 3: Verify the file is syntactically valid**

  The component should have no unused `loading` state — it's replaced by `!loadComplete`. The `papers` state now holds the merged array tagged with `source`. Confirm no TypeScript/JSX errors are visible in your editor.

---

## Task 2: Replace Load Sequence (useEffect)

**Files:**
- Modify: `football-research-library.jsx:137–147` (replace entire useEffect)

This is the most critical task. Replace the current `useEffect` (lines 137–147) with the new 5-step load sequence.

- [ ] **Step 1: Replace the useEffect block**

  Remove lines 137–147 (the existing useEffect) and replace with:

  ```javascript
  useEffect(() => {
    (async () => {
      // ── Step 1: Fetch from GitHub ────────────────────────────────────────
      let ghPapers = [];
      let failed = false;
      try {
        const res = await fetch(GITHUB_URL);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        ghPapers = await res.json();
      } catch (e) {
        failed = true;
      }
      setFetchFailed(failed);

      // ── Step 2: Migrate old storage key if present ───────────────────────
      try {
        const oldR = await window.storage.get(OLD_KEY, true);
        if (oldR?.value) {
          const oldArr = JSON.parse(oldR.value);
          if (Array.isArray(oldArr) && oldArr.length > 0) {
            // Read existing pending (may already have entries from prior partial migration)
            const pendR = await window.storage.get(PENDING_KEY, true);
            const existingPending = (pendR?.value ? JSON.parse(pendR.value) : null) || [];
            // Merge: existing pending takes precedence (dedup by id)
            const existingIds = new Set(existingPending.map(p => p.id));
            const fromOld = oldArr.filter(p => !existingIds.has(p.id));
            const migrated = [...existingPending, ...fromOld];
            try {
              await window.storage.set(PENDING_KEY, JSON.stringify(migrated), true);
              await window.storage.set(OLD_KEY, "[]", true); // sentinel: migration complete
            } catch (e) {
              // write failed — leave OLD_KEY untouched so next load retries
            }
          }
        }
      } catch (e) {}

      // ── Step 3: Load pending queue ───────────────────────────────────────
      let pending = [];
      try {
        const pendR = await window.storage.get(PENDING_KEY, true);
        if (pendR?.value) {
          const parsed = JSON.parse(pendR.value);
          if (Array.isArray(parsed)) pending = parsed;
        }
      } catch (e) {}

      // ── Step 4: Dedup pending against GitHub (only if fetch succeeded) ───
      // NEVER dedup against an empty array from a failed fetch — that would
      // permanently remove legitimately pending papers.
      if (!failed && ghPapers.length > 0) {
        const ghIds = new Set(ghPapers.map(p => p.id));
        const clean = pending.filter(p => !ghIds.has(p.id));
        if (clean.length !== pending.length) {
          pending = clean;
          try {
            await window.storage.set(PENDING_KEY, JSON.stringify(pending), true);
          } catch (e) {}
        }
      }

      // ── Step 5: Merge and set state ──────────────────────────────────────
      const tagged = [
        ...ghPapers.map(p => ({ ...p, source: "github" })),
        ...pending.map(p => ({ ...p, source: "pending" })),
      ];
      setPapers(tagged);
      setPendingPapers(pending);
      setLoadComplete(true);
    })();
  }, []);
  ```

- [ ] **Step 2: Verify load logic mentally**

  Walk through these scenarios:
  - **First run (no storage):** GitHub fetch succeeds → migration skipped (OLD_KEY empty) → pending empty → dedup no-op → papers = GitHub papers.
  - **Existing user (OLD_KEY has data):** Migration runs → OLD_KEY papers move to pending → OLD_KEY set to `[]` → pending loaded (includes migrated) → dedup runs → papers = GitHub + remaining pending.
  - **Offline:** GitHub fetch fails → `failed = true` → migration still runs → pending loaded → dedup skipped (guard) → papers = pending only + banner shown.

---

## Task 3: Replace `save` with `savePending` and Update `handleUpload`

**Files:**
- Modify: `football-research-library.jsx:149–191` (save function and handleUpload)

- [ ] **Step 1: Replace the `save` function with `savePending`**

  Remove the old `save` function (lines 149–152) and replace with:

  ```javascript
  const savePending = useCallback(async (newPending) => {
    // Update both pendingPapers and the merged papers state
    const ghPapers = papers.filter(p => p.source === "github");
    const taggedPending = newPending.map(p => ({ ...p, source: "pending" }));
    setPendingPapers(newPending);
    setPapers([...ghPapers, ...taggedPending]);
    // Throws on failure — callers must handle the error
    await window.storage.set(PENDING_KEY, JSON.stringify(newPending), true);
  }, [papers]);
  ```

- [ ] **Step 2: Replace `handleUpload`**

  Remove the old `handleUpload` (lines 185–191) and replace with:

  ```javascript
  const handleUpload = async (e) => {
    e.preventDefault();
    setFormError(null);
    const np = { ...uploadForm, id: Date.now().toString(), year: Number(uploadForm.year) };
    const newPending = [np, ...pendingPapers];
    try {
      await savePending(newPending);
      setUploadForm({ citation:"",doi:"",driveUrl:"",year:"2025",abstract:"",tldr:"",
        methods:"",findings:"",limitations:"",practicalImplications:"",athleteDev:"",rtp:"" });
      setShowUpload(false);
      flash("Paper added to the library!");
    } catch (err) {
      setFormError("Could not save paper. Storage may be unavailable — please try again or contact Eric.");
    }
  };
  ```

- [ ] **Step 3: Add `downloadPapersJson` function** (after `handleUpload`)

  ```javascript
  const downloadPapersJson = () => {
    // Output must conform exactly to 12-field schema: no source field, no extras
    const clean = papers.map(p => {
      const obj = {};
      SCHEMA_FIELDS.forEach(f => { obj[f] = p[f] !== undefined ? p[f] : ""; });
      return obj;
    });
    const blob = new Blob([JSON.stringify(clean, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "papers.json";
    a.click();
    flash("papers.json downloaded — commit it to GitHub to make it permanent!");
  };
  ```

- [ ] **Step 4: Add `getPaginationPages` helper** (after `downloadPapersJson`)

  ```javascript
  const getPaginationPages = (current, total) => {
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    if (current <= 4) return [1, 2, 3, 4, 5, "...", total];
    if (current >= total - 3) return [1, "...", total-4, total-3, total-2, total-1, total];
    return [1, "...", current - 1, current, current + 1, "...", total];
  };
  ```

---

## Task 4: Update Derived State and Add Pagination

**Files:**
- Modify: `football-research-library.jsx:154–167` (flash, years, filtered)

- [ ] **Step 1: Add page-reset effect after `flash`**

  After the `flash` function (line 154), add:

  ```javascript
  useEffect(() => { setCurrentPage(1); }, [search, yearFilter]);
  ```

- [ ] **Step 2: Update `filtered` computation and add pagination vars**

  The `years` and `filtered` lines (155–167) are unchanged in logic. Add these three lines immediately after the `filtered` definition:

  ```javascript
  const PAPERS_PER_PAGE = 50;
  const totalPages = Math.ceil(filtered.length / PAPERS_PER_PAGE);
  const startIndex = (currentPage - 1) * PAPERS_PER_PAGE;
  const pagedPapers = filtered.slice(startIndex, startIndex + PAPERS_PER_PAGE);
  ```

---

## Task 5: Replace Loading Screen and Add Fetch Banner

**Files:**
- Modify: `football-research-library.jsx:215` (loading return)
- Modify: `football-research-library.jsx:218–229` (after hero, add fetch banner)

- [ ] **Step 1: Update the loading screen**

  Find the loading early-return (line 215):
  ```javascript
  if (loading) return ...
  ```
  Replace it with:
  ```javascript
  if (!loadComplete) return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#FAF8F5", fontFamily: "'DM Sans',sans-serif" }}>
      <p style={{ color: "#555", fontSize: 15 }}>Loading research library...</p>
    </div>
  );
  ```

- [ ] **Step 2: Add fetch failure banner after the closing `</div>` of the hero section**

  The hero section ends around line 229 with `</div>`. Immediately after it, add:

  ```jsx
  {/* Fetch failure banner */}
  {fetchFailed && (
    <div style={{ background: "#FFF8E1", borderBottom: "2px solid #F9A825", padding: "12px 24px", textAlign: "center", fontSize: 13, color: "#795548" }}>
      ⚠️ Could not load library data from GitHub. Showing locally submitted papers only. Check your connection or try refreshing.
    </div>
  )}
  ```

---

## Task 6: Add Pending Badge to Controls Bar

**Files:**
- Modify: `football-research-library.jsx:231–245` (controls section)

- [ ] **Step 1: Add the pending badge button to the controls bar**

  In the controls `<div>` (lines 232–245), add this button after the `"+ Add Paper"` button:

  ```jsx
  {pendingPapers.length > 0 && (
    <button onClick={() => setShowPendingPanel(true)}
      style={{ padding: "9px 16px", borderRadius: 6, border: "none", background: "#E65100", color: "#fff", fontSize: 13, fontWeight: 600, cursor: "pointer", fontFamily: "'DM Sans',sans-serif" }}>
      ⏳ {pendingPapers.length} Pending
    </button>
  )}
  ```

---

## Task 7: Add Pending Panel Modal

**Files:**
- Modify: `football-research-library.jsx` — add after the Upload form section (~line 272)

- [ ] **Step 1: Add the Pending Panel modal**

  After the closing `)}` of the upload section (around line 272), add:

  ```jsx
  {/* Pending Panel */}
  {showPendingPanel && (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)", zIndex: 500, display: "flex", alignItems: "flex-start", justifyContent: "center", paddingTop: 60 }}>
      <div style={{ background: "#fff", borderRadius: 10, padding: 24, maxWidth: 620, width: "90%", maxHeight: "70vh", overflowY: "auto", boxShadow: "0 8px 32px rgba(0,0,0,0.2)" }}>
        <h3 style={{ fontFamily: "'DM Serif Display',serif", fontSize: 20, margin: "0 0 4px" }}>📋 Pending Papers</h3>
        <p style={{ fontSize: 13, color: "#777", margin: "0 0 16px" }}>
          {pendingPapers.length} paper{pendingPapers.length !== 1 ? "s" : ""} waiting to be committed to GitHub.
          {fetchFailed && <span style={{ color: "#C62828", marginLeft: 6 }}>GitHub unavailable — download disabled.</span>}
        </p>
        {pendingPapers.map(p => (
          <div key={p.id} style={{ background: "#FFF8E1", border: "1px solid #F9A825", borderLeft: "4px solid #F9A825", borderRadius: 6, padding: "10px 12px", marginBottom: 8, display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 600, lineHeight: 1.4 }}>{p.citation}</div>
              <div style={{ fontSize: 11, color: "#999", marginTop: 2 }}>ID: {p.id}</div>
            </div>
            <button
              onClick={async () => {
                const updated = pendingPapers.filter(x => x.id !== p.id);
                try { await savePending(updated); flash("Removed from pending queue."); }
                catch (e) { flash("Could not remove paper — please try again."); }
              }}
              style={{ marginLeft: 12, color: "#C62828", background: "none", border: "none", cursor: "pointer", fontSize: 20, lineHeight: 1, flexShrink: 0, padding: 0 }}>×</button>
          </div>
        ))}
        <div style={{ marginTop: 16, display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button
            onClick={downloadPapersJson}
            disabled={fetchFailed || !loadComplete}
            title={fetchFailed ? "Cannot generate complete papers.json — GitHub data unavailable. Resolve the connection issue first." : "Download a complete papers.json ready to commit to GitHub"}
            style={{ padding: "9px 16px", borderRadius: 6, border: "none", background: (fetchFailed || !loadComplete) ? "#ccc" : "#1565C0", color: "#fff", fontSize: 13, fontWeight: 600, cursor: (fetchFailed || !loadComplete) ? "not-allowed" : "pointer", fontFamily: "'DM Sans',sans-serif" }}>
            📥 Download papers.json for GitHub
          </button>
          <button onClick={() => setShowPendingPanel(false)}
            style={{ padding: "9px 16px", borderRadius: 6, border: "1px solid #d0ccc5", background: "#fff", color: "#555", fontSize: 13, cursor: "pointer", fontFamily: "'DM Sans',sans-serif" }}>
            Close
          </button>
        </div>
        <p style={{ marginTop: 12, fontSize: 11, color: "#aaa", lineHeight: 1.5 }}>
          After downloading: open github.com/Erash11/baylor-sport-science-library, open papers.json, replace file contents, and commit. The pending papers will be automatically removed from this queue on next load.
        </p>
      </div>
    </div>
  )}
  ```

---

## Task 8: Update Table Rendering (Pagination, Pending Tag, Remove Button)

**Files:**
- Modify: `football-research-library.jsx:284–316` (tbody and table)

- [ ] **Step 1: Update the tbody to use `pagedPapers` instead of `filtered`**

  Find line 287:
  ```jsx
  } : filtered.map((p, i) => {
  ```
  Change it to:
  ```jsx
  } : pagedPapers.map((p, i) => {
  ```

- [ ] **Step 2: Update the row number to use global numbering**

  Find line 292:
  ```jsx
  <td style={{ ...td, textAlign: "center", fontWeight: 700, color: "#1565C0", fontSize: 14 }}>{i+1}</td>
  ```
  Replace with:
  ```jsx
  <td style={{ ...td, textAlign: "center", fontWeight: 700, color: "#1565C0", fontSize: 14 }}>{startIndex + i + 1}</td>
  ```

- [ ] **Step 3: Add the ⏳ PENDING badge in the citation cell**

  Find the citation `<div>` (line 294):
  ```jsx
  <div style={{ fontWeight: 600, lineHeight: 1.45, marginBottom: 4 }}>{p.citation}</div>
  ```
  Replace with:
  ```jsx
  <div style={{ fontWeight: 600, lineHeight: 1.45, marginBottom: 4 }}>
    {p.citation}
    {p.source === "pending" && (
      <span style={{ display: "inline-block", fontSize: 10, fontWeight: 700, color: "#E65100", background: "#FFF3E0", border: "1px solid #FFB74D", borderRadius: 10, padding: "1px 7px", marginLeft: 6, verticalAlign: "middle" }}>⏳ PENDING</span>
    )}
  </div>
  ```

- [ ] **Step 4: Update the Remove button to be disabled for GitHub papers**

  Find the Remove button (line 298):
  ```jsx
  <button onClick={() => { save(papers.filter(x=>x.id!==p.id)); flash("Removed."); }} style={{ fontSize: 10, color: "#C62828", background: "none", border: "none", cursor: "pointer", fontFamily: "'DM Sans',sans-serif", fontWeight: 600, padding: 0 }}>Remove</button>
  ```
  Replace with:
  ```jsx
  <button
    onClick={async () => {
      if (p.source === "github") return;
      const updated = pendingPapers.filter(x => x.id !== p.id);
      try { await savePending(updated); flash("Removed."); }
      catch (e) { flash("Could not remove paper."); }
    }}
    disabled={p.source === "github"}
    title={p.source === "github" ? "Committed papers can only be removed by editing papers.json on GitHub" : "Remove this pending paper"}
    style={{ fontSize: 10, color: p.source === "github" ? "#ccc" : "#C62828", background: "none", border: "none", cursor: p.source === "github" ? "default" : "pointer", fontFamily: "'DM Sans',sans-serif", fontWeight: 600, padding: 0 }}>
    Remove
  </button>
  ```

- [ ] **Step 5: Add the no-results message update**

  Find line 286:
  ```jsx
  <tr><td colSpan={COLS.length+1} style={{ padding: 40, textAlign: "center", color: "#999" }}>No papers match your search.</td></tr>
  ```
  This condition checks `filtered.length === 0` (line 285). This is still correct — no change needed.

---

## Task 9: Add Pagination Controls and Result Count

**Files:**
- Modify: `football-research-library.jsx` — add after the `</table>` closing tag (~line 314)

- [ ] **Step 1: Add the pagination controls and result count after `</table>` and inside the outer scroll div**

  Find the closing `</table>` tag and the `</div>` that closes the scroll container. After `</table>` and before the outer table-wrapper `</div>`, add:

  ```jsx
  {/* Pagination controls */}
  {totalPages > 1 && (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderTop: "1px solid #d0ccc5", background: "#fff" }}>
      <span style={{ fontSize: 13, color: "#666" }}>
        {search || yearFilter !== "all"
          ? `${filtered.length} match${filtered.length !== 1 ? "es" : ""} · Showing ${startIndex + 1}–${Math.min(startIndex + PAPERS_PER_PAGE, filtered.length)}`
          : `Showing ${startIndex + 1}–${Math.min(startIndex + PAPERS_PER_PAGE, filtered.length)} of ${filtered.length} papers`}
      </span>
      <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
        <button
          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
          disabled={currentPage === 1}
          style={{ padding: "5px 11px", borderRadius: 4, border: "1px solid #d0ccc5", background: currentPage === 1 ? "#f5f5f5" : "#fff", color: currentPage === 1 ? "#bbb" : "#333", cursor: currentPage === 1 ? "default" : "pointer", fontSize: 13 }}>
          ← Prev
        </button>
        {getPaginationPages(currentPage, totalPages).map((item, i) =>
          item === "..." ? (
            <span key={`ellipsis-${i}`} style={{ padding: "0 4px", color: "#888", fontSize: 13 }}>…</span>
          ) : (
            <button key={item} onClick={() => setCurrentPage(item)}
              style={{ padding: "5px 10px", borderRadius: 4, border: "1px solid", borderColor: item === currentPage ? "#1565C0" : "#d0ccc5", background: item === currentPage ? "#1565C0" : "#fff", color: item === currentPage ? "#fff" : "#333", cursor: "pointer", fontSize: 13, minWidth: 32 }}>
              {item}
            </button>
          )
        )}
        <button
          onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
          disabled={currentPage === totalPages}
          style={{ padding: "5px 11px", borderRadius: 4, border: "1px solid #d0ccc5", background: currentPage === totalPages ? "#f5f5f5" : "#fff", color: currentPage === totalPages ? "#bbb" : "#333", cursor: currentPage === totalPages ? "default" : "pointer", fontSize: 13 }}>
          Next →
        </button>
      </div>
    </div>
  )}
  ```

---

## Task 10: Add Form Error Display and Update Upload Form

**Files:**
- Modify: `football-research-library.jsx:266–271` (form submit area)

- [ ] **Step 1: Add formError display inside the upload form**

  Find the form submit button area (lines 266–270). After the `<div style={{ marginTop: 16, display: "flex", gap: 10 }}>` block (the one containing the Save and Cancel buttons), add:

  ```jsx
  {formError && (
    <div style={{ marginTop: 8, fontSize: 13, color: "#C62828", background: "#FFEBEE", padding: "8px 12px", borderRadius: 4 }}>
      {formError}
    </div>
  )}
  ```

- [ ] **Step 2: Clear formError when upload form is toggled open**

  Find the "+ Add Paper" button (line 242):
  ```jsx
  <button onClick={() => setShowUpload(!showUpload)} ...>
  ```
  Replace its `onClick` with:
  ```jsx
  onClick={() => { setShowUpload(!showUpload); setFormError(null); }}
  ```

---

## Task 11: Remove `DEFAULT_PAPERS` Constant

**Files:**
- Modify: `football-research-library.jsx:3–116` (remove DEFAULT_PAPERS array)

- [ ] **Step 1: Delete the DEFAULT_PAPERS constant**

  Remove lines 3–116 (the entire `const DEFAULT_PAPERS = [...]` block). The file now starts with:
  ```javascript
  import { useState, useEffect, useCallback, useRef } from "react";

  const GITHUB_URL = ...
  const PENDING_KEY = ...
  ```

  Confirm no remaining references to `DEFAULT_PAPERS` exist in the file. There should be none — the load sequence no longer falls back to it.

- [ ] **Step 2: Full file verification checklist**

  Confirm each of the following in the component:
  - [ ] No reference to `DEFAULT_PAPERS`
  - [ ] No reference to `fb-research-lib-v2` as a write target (only read for migration)
  - [ ] `filtered` still uses `papers` (the merged state)
  - [ ] `handleUpload` calls `savePending`, not `save`
  - [ ] Remove button is disabled for `source === "github"` papers
  - [ ] `pagedPapers` is used in the tbody map, not `filtered`
  - [ ] Row numbers use `startIndex + i + 1`
  - [ ] Pending Panel renders when `showPendingPanel === true`
  - [ ] Download button is disabled when `fetchFailed || !loadComplete`

---

## Task 12: End-to-End Manual Verification

No test runner is available — verification is done in the Claude artifact browser.

- [ ] **Step 1: Load the app fresh (no prior storage)**

  Open the artifact. Expected:
  - Loading screen shows briefly
  - Papers from GitHub appear (at least the 8 initial papers)
  - No fetch failure banner
  - No pending badge in header

- [ ] **Step 2: Verify pagination**

  If the GitHub repo has only 8 papers, pagination controls should not appear (only shown when totalPages > 1). To test: add 50+ papers to papers.json (or temporarily lower `PAPERS_PER_PAGE` to 3 in code). Expected:
  - Pagination controls appear below the table
  - Page 1 shows rows 1–N
  - Page 2 shows rows N+1–2N
  - Row numbers are global (page 2 starts at N+1, not 1)
  - Searching resets to page 1

- [ ] **Step 3: Submit a paper via the form**

  Click "+ Add Paper", fill in the required fields (Citation, Year, Abstract, TL;DR, Practical Implications), click "Save to Library". Expected:
  - Toast: "Paper added to the library!"
  - New paper appears in the table with ⏳ PENDING badge
  - Pending badge appears in the header: "⏳ 1 Pending"
  - Form closes

- [ ] **Step 4: Test Pending Panel**

  Click the "⏳ 1 Pending" badge. Expected:
  - Modal opens listing the paper
  - "Download papers.json for GitHub" button is enabled (blue)
  - Clicking download triggers a file download of `papers.json`
  - Downloaded file is valid JSON array containing all papers (GitHub + pending) with no `source` field

- [ ] **Step 5: Test per-paper remove in Pending Panel**

  With the panel open, click the × next to a pending paper. Expected:
  - Paper removed from list
  - Pending count in badge decrements
  - Paper removed from main table

- [ ] **Step 6: Test Remove button behavior**

  In the main table:
  - GitHub paper: Remove button is greyed out; hovering shows tooltip
  - Pending paper (if any remain): Remove button is red and functional

- [ ] **Step 7: Simulate fetch failure**

  Temporarily change `GITHUB_URL` to an invalid URL (e.g., append `-broken`). Reload. Expected:
  - Yellow fetch failure banner appears below header
  - Download button in Pending Panel is greyed out with tooltip
  - Dedup does NOT run (pending papers stay in queue)
  - Pending papers still visible in table

- [ ] **Step 8: Test migration from old storage**

  This requires manually writing to `fb-research-lib-v2` via browser devtools. In the Claude artifact's console:
  ```javascript
  await window.storage.set("fb-research-lib-v2", JSON.stringify([{id:"legacy-1",year:2020,citation:"Legacy test paper",doi:"",driveUrl:"",abstract:"test",tldr:"test",methods:"",findings:"",limitations:"",practicalImplications:"test",athleteDev:"",rtp:""}]), true)
  ```
  Then reload. Expected:
  - The legacy paper appears in the table with ⏳ PENDING badge
  - Pending badge shows "⏳ 1 Pending" (or more if other pending papers exist)
  - `fb-research-lib-v2` is now empty (check: `(await window.storage.get("fb-research-lib-v2", true))?.value` should return `"[]"`)
  - On second reload, migration does not run again

---

## Commit Sequence

```bash
# After Task 0 (GitHub repo) — no git commit in this repo

# After Tasks 1–4 (state + load + pending writes + pagination state)
git add football-research-library.jsx
git commit -m "feat: add github fetch, pending queue, migration, pagination state"

# After Tasks 5–7 (UI: banner, badge, panel)
git add football-research-library.jsx
git commit -m "feat: add fetch banner, pending badge, and pending panel UI"

# After Task 8 (table rendering)
git add football-research-library.jsx
git commit -m "feat: update table with pagination, pending tag, and remove button guards"

# After Tasks 9–11 (pagination controls, form error, remove DEFAULT_PAPERS)
git add football-research-library.jsx
git commit -m "feat: add pagination controls, form error display, remove DEFAULT_PAPERS"
```

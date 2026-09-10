# Book Advisors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn a library of books into grounded, citing AI advisors usable from Claude Code sessions, with knowledge stored as plain-markdown notes in the existing Obsidian SecondBrain vault and retrieved via memsearch.

**Architecture:** Approach A — knowledge is atomized markdown notes under `SecondBrain/Knowledge/library/`; advisors are *data* (persona notes) read by one generic `advisor` skill; ingestion and review are two more skills; memsearch is the retrieval substrate. No application server, no database beyond memsearch/Milvus (already running).

**Tech Stack:** Markdown + YAML frontmatter (Obsidian vault), Claude Code skills (`~/.claude/skills/<name>/SKILL.md`), memsearch CLI (hybrid recall), Node.js (the one hook edit), Python (extraction/verification helpers run in the context-mode sandbox). Windows 11, PowerShell primary.

**Spec:** `docs/superpowers/specs/2026-06-12-book-advisors-design.md`

**Key absolute paths (used throughout):**
- Vault root: `C:\Users\eric_rash\Desktop\SecondBrain`
- Library subtree: `C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library`
- Skills dir: `C:\Users\eric_rash\.claude\skills`
- memsearch sync hook: `C:\Users\eric_rash\.claude\hooks\memsearch-sync.js`
- KeystoneOS repo (specs/plans live here): `C:\Users\eric_rash\Desktop\DEV\KeystoneOS`
- KeystoneOS router: `C:\Users\eric_rash\Desktop\DEV\KeystoneOS\AGENTS.md`

**Commit convention:** The SecondBrain vault is its own git repo (commit vault changes there). Skills and the hook live under `~/.claude` (commit there if it is a repo; otherwise the change is a working-tree edit — note this and move on). Specs/plans and the routing line live in the KeystoneOS repo, where autonomous commit+push is authorized.

---

## File Structure

**Created:**
- `~/.claude/skills/ingest-book/SKILL.md` — book → atomized entries pipeline
- `~/.claude/skills/ingest-book/lib/extract_epub.py` — EPUB → per-chapter plaintext (sandbox helper)
- `~/.claude/skills/ingest-book/lib/extract_pdf.py` — PDF → per-page/chapter text + scanned-PDF detection
- `~/.claude/skills/advisor/SKILL.md` — generic advisor consultation skill
- `~/.claude/skills/library-review/SKILL.md` — gap/review loop skill
- `SecondBrain/Knowledge/library/strength-and-conditioning/_domain.md` — domain index + miss-log
- `SecondBrain/Knowledge/library/advisors/strength-and-conditioning.md` — S&C advisor persona
- `SecondBrain/Knowledge/library/README.md` — explains the subtree's conventions

**Modified:**
- `~/.claude/hooks/memsearch-sync.js` — add library path to `PATHS`
- `KeystoneOS/AGENTS.md` — one routing line for library consultation

**Generated at run time (not authored here):**
- `SecondBrain/Knowledge/library/strength-and-conditioning/<book-slug>/_book.md`
- `SecondBrain/Knowledge/library/strength-and-conditioning/<book-slug>/<kind>--<slug>.md`

---

## Task 1: Add the library path to memsearch indexing

Unblocks all retrieval. Without this, advisor entries are invisible to memsearch.

**Files:**
- Modify: `C:\Users\eric_rash\.claude\hooks\memsearch-sync.js` (the `PATHS` array)

- [ ] **Step 1: Read the current hook to confirm the PATHS array shape**

Run:
```bash
node -e "const t=require('fs').readFileSync('C:/Users/eric_rash/.claude/hooks/memsearch-sync.js','utf8'); const m=t.match(/const PATHS = \[[\s\S]*?\];/); console.log(m?m[0]:'PATHS NOT FOUND');"
```
Expected: prints the `const PATHS = [ ... ];` block containing four `path.join(...)` lines (global-memory/transcripts, projects/.../memory, claude-memory-compiler/daily, claude-memory-compiler/knowledge).

- [ ] **Step 2: Write the verification check FIRST (it must fail now)**

Run:
```bash
node -e "const t=require('fs').readFileSync('C:/Users/eric_rash/.claude/hooks/memsearch-sync.js','utf8'); process.exit(t.includes('Knowledge','library') && /Knowledge[\\\\/]+.*library|'Knowledge', 'library'/.test(t) ? 0 : 1);" && echo "PRESENT" || echo "ABSENT"
```
Expected: `ABSENT` (the library path is not yet in the file).

- [ ] **Step 3: Add the library path to PATHS**

Use Edit to insert one line into the `PATHS` array. The vault is on the Desktop, not under `.claude`, so use an absolute path via `path.join` from the Desktop. Add as the last entry before the closing `];`:

```js
  path.join(os.homedir(), 'Desktop', 'SecondBrain', 'Knowledge', 'library'),
```

(The existing `existing = PATHS.filter(p => fs.existsSync(p))` guard means this is harmless until the directory exists — created in Task 2.)

- [ ] **Step 4: Verify the line is present and the file still parses**

Run:
```bash
node -e "const t=require('fs').readFileSync('C:/Users/eric_rash/.claude/hooks/memsearch-sync.js','utf8'); if(!t.includes(\"'SecondBrain', 'Knowledge', 'library'\")) {console.error('LINE MISSING'); process.exit(1);} require('vm').compileFunction(t); console.log('PRESENT + PARSES');"
```
Expected: `PRESENT + PARSES` (no syntax error thrown).

- [ ] **Step 5: Commit (if ~/.claude is a git repo; else note working-tree edit)**

```bash
cd "C:/Users/eric_rash/.claude" && git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git add hooks/memsearch-sync.js && git commit -m "feat(memsearch): index SecondBrain library subtree" || echo "~/.claude not a git repo — edit saved to working tree, no commit"
```
Expected: either a commit hash, or the "not a git repo" notice.

---

## Task 2: Scaffold the library subtree

Creates the directory structure and the two human-authored index/README notes. Makes the memsearch path from Task 1 real.

**Files:**
- Create dir: `SecondBrain/Knowledge/library/strength-and-conditioning/`
- Create dir: `SecondBrain/Knowledge/library/advisors/`
- Create: `SecondBrain/Knowledge/library/README.md`
- Create: `SecondBrain/Knowledge/library/strength-and-conditioning/_domain.md`

- [ ] **Step 1: Create the directories**

Run (PowerShell):
```powershell
New-Item -ItemType Directory -Force "C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library\strength-and-conditioning" | Out-Null
New-Item -ItemType Directory -Force "C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library\advisors" | Out-Null
Test-Path "C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library\advisors"
```
Expected: `True`.

- [ ] **Step 2: Write `README.md` (the subtree conventions)**

Create `C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library\README.md`:

```markdown
# Library — books as advisors

Atomized, citable knowledge from curated books. Consulted via the `advisor` skill.

## Layout
- `<domain>/_domain.md` — domain index + miss-log
- `<domain>/<book-slug>/_book.md` — chapter map, ingest tier, per-chapter status
- `<domain>/<book-slug>/<kind>--<slug>.md` — one atomized idea per file
- `advisors/<domain>.md` — advisor persona ("job description")

## Entry kinds
`principle | framework | case-study | heuristic | claim`

## Confidence is bounded by ingest tier
- `full-text` → up to `proven`
- `highlights` → cap `supported`
- `framework-only` → cap `untested`
- `contested` → set manually when sources conflict

## Rules
- One idea per entry note.
- Every entry has a "When NOT to apply" section.
- Cross-book agreement = `[[wikilink]]` + one explanatory line.
- Never overwrite; enrich or suffix `-2`.
- Only this subtree is indexed by memsearch for advisors.
```

- [ ] **Step 3: Write the S&C `_domain.md`**

Create `C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library\strength-and-conditioning\_domain.md`:

```markdown
---
type: domain-index
domain: strength-and-conditioning
advisor: "[[strength-and-conditioning]]"
books: []
created: 2026-06-12
---

# Strength & Conditioning — domain index

Pilot domain for the book-advisors system.

## Books in this domain
_None ingested yet. `ingest-book` appends each book here on close-out._

## Miss-log
_The `advisor` skill appends one line here each time it answers a question the
library could not ground. Feeds `library-review`._
```

- [ ] **Step 4: Verify structure**

Run (PowerShell):
```powershell
Get-ChildItem -Recurse "C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library" | Select-Object -ExpandProperty FullName
```
Expected: lists `README.md`, `advisors\` (empty), `strength-and-conditioning\_domain.md`.

- [ ] **Step 5: Commit (vault repo)**

```bash
cd "C:/Users/eric_rash/Desktop/SecondBrain" && git add Knowledge/library && git commit -m "feat(library): scaffold book-advisors subtree + S&C domain index"
```
Expected: commit hash.

---

## Task 3: Build the EPUB extraction helper

A sandbox-run Python helper that turns an EPUB into per-chapter plaintext, so raw book text never floods the agent's context. Pure function over a file path → JSON on stdout.

**Files:**
- Create: `C:\Users\eric_rash\.claude\skills\ingest-book\lib\extract_epub.py`

- [ ] **Step 1: Create the skill lib dir**

Run (PowerShell):
```powershell
New-Item -ItemType Directory -Force "C:\Users\eric_rash\.claude\skills\ingest-book\lib" | Out-Null; Test-Path "C:\Users\eric_rash\.claude\skills\ingest-book\lib"
```
Expected: `True`.

- [ ] **Step 2: Write the extractor**

Create `C:\Users\eric_rash\.claude\skills\ingest-book\lib\extract_epub.py`:

```python
"""Extract an EPUB into ordered (title, text) chapters as JSON.
Usage: python extract_epub.py <book.epub> [--chapter N] [--list]
Stdlib only (zipfile + html parsing) so it runs anywhere.
"""
import sys, zipfile, re, json, html
from html.parser import HTMLParser

class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"): self.skip += 1
        if tag in ("p", "br", "div", "h1", "h2", "h3", "li"): self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)
    def text(self):
        t = html.unescape("".join(self.parts))
        return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", t)).strip()

def _spine_docs(z):
    # Find the OPF, read spine order -> list of html hrefs.
    container = z.read("META-INF/container.xml").decode("utf-8", "replace")
    opf_path = re.search(r'full-path="([^"]+)"', container).group(1)
    opf = z.read(opf_path).decode("utf-8", "replace")
    base = opf_path.rsplit("/", 1)[0] + "/" if "/" in opf_path else ""
    ids = dict(re.findall(r'<item[^>]*id="([^"]+)"[^>]*href="([^"]+)"', opf))
    ids.update(dict((m[1], m[0]) for m in re.findall(r'<item[^>]*href="([^"]+)"[^>]*id="([^"]+)"', opf)))
    order = re.findall(r'<itemref[^>]*idref="([^"]+)"', opf)
    docs = []
    for ref in order:
        href = ids.get(ref)
        if href and href.lower().endswith((".html", ".xhtml", ".htm")):
            docs.append(base + href)
    return docs

def chapters(path):
    out = []
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        for href in _spine_docs(z):
            if href not in names:  # tolerate path normalization
                href = href.replace("../", "")
                if href not in names: continue
            raw = z.read(href).decode("utf-8", "replace")
            p = _Text(); p.feed(raw)
            txt = p.text()
            if len(txt) < 200:  # skip nav/title slivers
                continue
            title = ""
            m = re.search(r"<h[1-3][^>]*>(.*?)</h[1-3]>", raw, re.S | re.I)
            if m:
                title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            out.append({"title": title or href.rsplit("/",1)[-1], "chars": len(txt), "text": txt})
    return out

def main():
    args = sys.argv[1:]
    if not args:
        print("usage: extract_epub.py <book.epub> [--chapter N] [--list]", file=sys.stderr); sys.exit(2)
    path = args[0]
    chs = chapters(path)
    if "--list" in args:
        print(json.dumps([{"i": i, "title": c["title"], "chars": c["chars"]} for i, c in enumerate(chs)], ensure_ascii=False))
        return
    if "--chapter" in args:
        n = int(args[args.index("--chapter") + 1])
        print(json.dumps(chs[n], ensure_ascii=False))
        return
    print(json.dumps([{"i": i, "title": c["title"], "chars": c["chars"]} for i, c in enumerate(chs)], ensure_ascii=False))

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Create a tiny synthetic EPUB and verify `--list` works**

Run via context-mode sandbox (`ctx_execute`, language python) — keeps the test artifact out of the repo:
```python
import zipfile, subprocess, sys, os, tempfile
d = tempfile.mkdtemp()
epub = os.path.join(d, "t.epub")
with zipfile.ZipFile(epub, "w") as z:
    z.writestr("META-INF/container.xml", '<?xml version="1.0"?><container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
    z.writestr("content.opf", '<package><manifest><item id="c1" href="c1.xhtml"/><item id="c2" href="c2.xhtml"/></manifest><spine><itemref idref="c1"/><itemref idref="c2"/></spine></package>')
    z.writestr("c1.xhtml", "<html><body><h1>Chapter One</h1><p>" + ("alpha "*60) + "</p></body></html>")
    z.writestr("c2.xhtml", "<html><body><h2>Chapter Two</h2><p>" + ("beta "*60) + "</p></body></html>")
r = subprocess.run([sys.executable, r"C:\Users\eric_rash\.claude\skills\ingest-book\lib\extract_epub.py", epub, "--list"], capture_output=True, text=True)
print("STDOUT:", r.stdout.strip())
print("STDERR:", r.stderr.strip())
```
Expected STDOUT: a JSON array with two objects, titles `Chapter One` and `Chapter Two`, each with `chars` > 200.

- [ ] **Step 4: Verify `--chapter 1` returns the second chapter's full text**

Append to the same sandbox run (or rerun with):
```python
r = subprocess.run([sys.executable, r"C:\Users\eric_rash\.claude\skills\ingest-book\lib\extract_epub.py", epub, "--chapter", "1"], capture_output=True, text=True)
import json
obj = json.loads(r.stdout)
print("TITLE:", obj["title"], "| HAS_BETA:", "beta" in obj["text"])
```
Expected: `TITLE: Chapter Two | HAS_BETA: True`.

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/eric_rash/.claude" && git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git add skills/ingest-book/lib/extract_epub.py && git commit -m "feat(ingest-book): EPUB chapter extractor" || echo "~/.claude not a git repo — saved to working tree"
```
Expected: commit hash or the notice.

---

## Task 4: Build the PDF extraction helper (with scanned-PDF detection)

Per-page text plus a "is this a scanned/image PDF?" check that drives the failure-mode fallback in the spec.

**Files:**
- Create: `C:\Users\eric_rash\.claude\skills\ingest-book\lib\extract_pdf.py`

- [ ] **Step 1: Write the extractor**

Create `C:\Users\eric_rash\.claude\skills\ingest-book\lib\extract_pdf.py`:

```python
"""Extract a PDF into per-page text as JSON, and detect scanned/image PDFs.
Usage: python extract_pdf.py <book.pdf> [--pages A-B] [--probe]
Prefers pypdf; if absent, attempts pip install into user site at runtime.
--probe prints {"pages": N, "text_pages": K, "scanned": bool} and exits.
"""
import sys, json, subprocess

def _ensure_pypdf():
    try:
        import pypdf  # noqa
        return
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--user", "pypdf"], check=False)

def load(path):
    _ensure_pypdf()
    from pypdf import PdfReader
    return PdfReader(path)

def page_texts(reader):
    out = []
    for pg in reader.pages:
        try: out.append(pg.extract_text() or "")
        except Exception: out.append("")
    return out

def main():
    args = sys.argv[1:]
    if not args:
        print("usage: extract_pdf.py <book.pdf> [--pages A-B] [--probe]", file=sys.stderr); sys.exit(2)
    path = args[0]
    reader = load(path)
    texts = page_texts(reader)
    if "--probe" in args:
        text_pages = sum(1 for t in texts if len(t.strip()) > 40)
        n = len(texts)
        scanned = n > 0 and (text_pages / n) < 0.2
        print(json.dumps({"pages": n, "text_pages": text_pages, "scanned": scanned}))
        return
    lo, hi = 0, len(texts)
    if "--pages" in args:
        rng = args[args.index("--pages") + 1]
        a, b = rng.split("-")
        lo, hi = int(a), int(b)
    print(json.dumps([{"page": i, "text": texts[i]} for i in range(lo, min(hi, len(texts)))], ensure_ascii=False))

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify `--probe` flags a scanned PDF correctly**

Run via `ctx_execute` (python). Builds a text PDF and an image-only PDF with reportlab (install if needed), probes both:
```python
import subprocess, sys, os, tempfile
subprocess.run([sys.executable,"-m","pip","install","--quiet","--user","reportlab","pypdf"],check=False)
from reportlab.pdfgen import canvas
d = tempfile.mkdtemp()
text_pdf = os.path.join(d,"text.pdf")
c = canvas.Canvas(text_pdf)
for _ in range(5):
    c.drawString(72,720,"This page has a real sentence of extractable text content here."); c.showPage()
c.save()
img_pdf = os.path.join(d,"img.pdf")
c = canvas.Canvas(img_pdf)
for _ in range(5):
    c.rect(72,72,200,200,fill=1); c.showPage()   # filled rectangle, no text
c.save()
ex = r"C:\Users\eric_rash\.claude\skills\ingest-book\lib\extract_pdf.py"
for label,p in [("TEXT",text_pdf),("IMAGE",img_pdf)]:
    r = subprocess.run([sys.executable,ex,p,"--probe"],capture_output=True,text=True)
    print(label, r.stdout.strip(), r.stderr.strip()[:120])
```
Expected: `TEXT` line shows `"scanned": false`; `IMAGE` line shows `"scanned": true`.

- [ ] **Step 3: Verify `--pages 0-2` returns two pages of text**

Append:
```python
r = subprocess.run([sys.executable, ex, text_pdf, "--pages", "0-2"], capture_output=True, text=True)
import json; pages = json.loads(r.stdout)
print("NPAGES:", len(pages), "| HAS_TEXT:", "extractable text" in pages[0]["text"])
```
Expected: `NPAGES: 2 | HAS_TEXT: True`.

- [ ] **Step 4: Commit**

```bash
cd "C:/Users/eric_rash/.claude" && git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git add skills/ingest-book/lib/extract_pdf.py && git commit -m "feat(ingest-book): PDF extractor + scanned-PDF probe" || echo "~/.claude not a git repo — saved to working tree"
```
Expected: commit hash or the notice.

---

## Task 5: Write the `ingest-book` skill

The orchestration prompt that ties the extractors, the entry schema, the quality gate, and close-out together. This is the procedure the agent follows; the extractors are its tools.

**Files:**
- Create: `C:\Users\eric_rash\.claude\skills\ingest-book\SKILL.md`

- [ ] **Step 1: Write the skill**

Create `C:\Users\eric_rash\.claude\skills\ingest-book\SKILL.md`:

````markdown
---
name: ingest-book
description: Ingest a book (PDF/EPUB full-text, Kindle highlights, or framework-only from a physical book) into the SecondBrain library as atomized, citable advisor entries. Use when the user wants to "ingest a book", "add a book to my library/advisors", "/ingest-book", or points at a book file for the advisor system. For articles/transcripts/general resources use ingest-resource instead.
---

# Ingest Book

Turn a book into atomized, citable entries under the library subtree, grouped by domain and book, ready for the `advisor` skill.

**Library root:** `C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library`
**Extractors:** `~/.claude/skills/ingest-book/lib/extract_epub.py`, `extract_pdf.py`
Run extractors inside the context-mode sandbox (`ctx_execute`, language python) so raw book text never enters the conversation — only the atomized entries you write do.

## Schema for every entry note

Filename: `<kind>--<kebab-slug>.md`, `kind ∈ {principle, framework, case-study, heuristic, claim}`.

```yaml
---
type: library-entry
kind: principle
domain: <domain-slug>
book: <book-slug>
chapter: "N"            # or section label; "" if highlights with no location
topic: <2-5 word topic>
category: [tag, tag]
confidence: proven      # proven | supported | untested | contested
ingest-tier: full-text  # full-text | highlights | framework-only
created: <YYYY-MM-DD>
---

# <Human title of the idea>

**What it is** — one tight paragraph.
**Why it works** — mechanism, not restatement.
**When to apply** — concrete triggers.
**When NOT to apply** — scope limits. (MANDATORY — never omit.)
**Example** — one concrete instance.
```

**Confidence is bounded by tier:** full-text ≤ proven; highlights ≤ supported;
framework-only ≤ untested. Set `contested` by hand when sources conflict.

## Phase 1 — Intake

1. Identify: book title, author, source type (PDF/EPUB | Kindle highlights | physical), target domain.
2. Compute `<book-slug>` = `kebab(title)--kebab(lastname)` (e.g. `supertraining--verkhoshansky`).
3. If the domain folder/`_domain.md` doesn't exist, create them (mirror the S&C `_domain.md` format).
4. Build `_book.md` chapter map:
   - EPUB/PDF: run the extractor with `--list` / `--probe` to get the chapter or page structure.
   - Physical: ask the user for the chapter list, or assemble from a verified public listing.
   Write `_book.md` (template below) with every chapter `status: pending`.

`_book.md` template:
```markdown
---
type: book-index
book: <book-slug>
title: <full title>
author: <author>
domain: <domain-slug>
ingest-tier: full-text | highlights | framework-only
source: "<file path or 'physical' or 'kindle-highlights'>"
created: <YYYY-MM-DD>
---

# <title> — ingest map

| # | Chapter | Status | Entries |
|---|---------|--------|---------|
| 0 | <title> | pending | 0 |
```

## Phase 2 — Extract (by tier)

**Full-text (PDF/EPUB):**
- First run `extract_pdf.py --probe`. If `scanned: true`, STOP the full-text path:
  tell the user the PDF is image-only, and fall back to framework-only tier (set
  `ingest-tier: framework-only`, cap confidence at untested). Never emit full-text-
  confidence entries from a scanned file.
- Work **one chapter at a time** (EPUB `--chapter N`; PDF `--pages A-B`). For each:
  extract candidate ideas → atomize per the schema → write entry notes.
- **After each chapter**, update that row in `_book.md` to `status: done` with the
  entry count. This is the resume checkpoint — never batch this update.

**Kindle highlights:**
- Parse `My Clippings.txt` or the highlights export in the sandbox. Cluster highlights
  by theme; write one entry per theme. `ingest-tier: highlights`, confidence ≤ supported.
- Attribute `chapter` from the highlight's location metadata when present, else "".

**Framework-only (physical / scanned):**
- Briefly interview the user for their takeaways. Supplement with *verified* public
  chapter summaries. Write 5–15 framework-level entries. `ingest-tier: framework-only`,
  confidence ≤ untested.

## Phase 3 — Quality gate (run before writing each batch)

- One idea per note. If an extracted point is compound, split it.
- "When NOT to apply" present and non-trivial.
- **Dedup + converge:** before writing, `memsearch search` the library for the same
  concept. If an existing entry (any book) covers it, DON'T duplicate — instead add a
  `[[wikilink]]` + one line to both notes recording the agreement, and only add a new
  note if it contributes a genuinely new angle.
- Never overwrite an existing file; on slug collision append `-2`.

## Phase 4 — Close-out

1. Set all done rows in `_book.md`; if partial, leave pending rows for next session.
2. Add the book to `_domain.md`'s `books:` list and the "Books in this domain" section.
3. Add the book-slug to the advisor persona's `books:` list (`advisors/<domain>.md`)
   if an advisor exists.
4. Run `memsearch index "C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library"`
   so entries are searchable immediately (don't wait for the SessionEnd hook).
5. Commit the vault: `git -C "C:/Users/eric_rash/Desktop/SecondBrain" add Knowledge/library && git commit -m "ingest(<book-slug>): <N> entries, ch X-Y"`.
6. Report: entries by kind and confidence, links created, chapters remaining.

## Rules
- Raw book text stays in the sandbox; only atomized entries enter context/the vault.
- Resumable by design: `_book.md` is the source of truth for "where am I".
- A 300-page book is a multi-session job — stop at a chapter boundary, never mid-chapter.
````

- [ ] **Step 2: Verify the skill is discoverable and well-formed**

Run:
```bash
node -e "const fs=require('fs');const t=fs.readFileSync('C:/Users/eric_rash/.claude/skills/ingest-book/SKILL.md','utf8');const fm=t.startsWith('---')&&t.indexOf('---',3)>0;const hasName=/^name:\s*ingest-book$/m.test(t);const hasDesc=/^description:\s*.+/m.test(t);const phases=['Phase 1','Phase 2','Phase 3','Phase 4'].every(p=>t.includes(p));console.log('frontmatter:',fm,'name:',hasName,'desc:',hasDesc,'phases:',phases);process.exit(fm&&hasName&&hasDesc&&phases?0:1);"
```
Expected: `frontmatter: true name: true desc: true phases: true` and exit 0.

- [ ] **Step 3: Commit**

```bash
cd "C:/Users/eric_rash/.claude" && git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git add skills/ingest-book/SKILL.md && git commit -m "feat(ingest-book): orchestration skill" || echo "~/.claude not a git repo — saved to working tree"
```
Expected: commit hash or the notice.

---

## Task 6: Ingest the pilot book

Run the `ingest-book` skill on the PDF/EPUB the user provides. This is a runtime execution, not authored code — but it gates the acceptance test, so it's a tracked task.

**Files:**
- Generated: `SecondBrain/Knowledge/library/strength-and-conditioning/<book-slug>/_book.md` + entry notes

- [ ] **Step 1: Get the book file path from the user**

The user drops pilot books in `C:\Users\eric_rash\Desktop\DEV\BookInbox\`. Check there first:
```powershell
Get-ChildItem "C:\Users\eric_rash\Desktop\DEV\BookInbox" -Include *.pdf,*.epub,*.txt -Recurse | Select-Object -ExpandProperty FullName
```
If a book file is present, use it. If the folder has only `README.md` (no book yet),
STOP here and ask the user to drop the pilot S&C PDF/EPUB in `BookInbox` — do not
fabricate a book. Confirm the chosen file exists with `Test-Path "<path>"` → `True`.

- [ ] **Step 2: Invoke the ingest-book skill on the file**

Run the `ingest-book` skill (Skill tool) with the file path. For the pilot, ingest **the first 2–3 chapters only** (enough to prove the pipeline and measure token cost before committing to the whole book).

- [ ] **Step 3: Verify entries were produced and are well-formed**

Run via `ctx_execute` (python) — checks every entry note has the mandatory schema fields and a "When NOT to apply" section:
```python
import os, glob, re
base = r"C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library\strength-and-conditioning"
notes = [p for p in glob.glob(os.path.join(base, "**", "*.md"), recursive=True)
         if os.path.basename(p) not in ("_domain.md", "_book.md")]
print("entry notes:", len(notes))
bad = []
for p in notes:
    t = open(p, encoding="utf-8", errors="replace").read()
    ok = all(k in t for k in ["type: library-entry", "confidence:", "ingest-tier:", "When NOT to apply"])
    if not ok: bad.append(os.path.basename(p))
print("malformed:", bad if bad else "none")
```
Expected: `entry notes:` ≥ 5 (a couple of chapters yield several ideas), `malformed: none`.

- [ ] **Step 4: Verify memsearch can find an entry**

Run:
```bash
memsearch search "strength conditioning periodization" --top-k 5
```
Expected: at least one hit whose path is under `Knowledge\library\strength-and-conditioning`. (If zero hits, run `memsearch index "C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library"` and retry — Phase 4 should have done this.)

- [ ] **Step 5: Confirm the vault commit landed**

```bash
git -C "C:/Users/eric_rash/Desktop/SecondBrain" log --oneline -1
```
Expected: a recent `ingest(<book-slug>): ...` commit. If absent, commit now.

---

## Task 7: Write the S&C advisor persona

The "job description" note the generic skill reads. Data, not code.

**Files:**
- Create: `SecondBrain/Knowledge/library/advisors/strength-and-conditioning.md`

- [ ] **Step 1: Write the persona note**

Create `C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library\advisors\strength-and-conditioning.md`. Set `books:` to the pilot book-slug ingested in Task 6:

```markdown
---
type: advisor
domain: strength-and-conditioning
status: active
books: [<pilot-book-slug>]
created: 2026-06-12
---

# Strength & Conditioning Advisor

## Role & voice
Evidence-first strength & conditioning advisor. Speaks like a senior S&C coach who
reads the primary literature: distinguishes mechanism from outcome, separates what a
source *demonstrated* from what it *claimed*, quantifies (loads, intensities,
timeframes) when the sources allow, and is comfortable saying "the evidence is thin".

## Scope
Advises on: programming, periodization, adaptation, strength/power/speed development,
recovery and monitoring, exercise selection — grounded in the ingested library.

Do NOT pick this advisor when:
- The question is medical / injury-diagnosis (refer to a clinician).
- The question is about live Catapult GPS data or force-plate analysis — that's the
  ForcePlate/Catapult tooling's job, not this advisor.
- The question is general business/marketing — that's a different domain advisor.

## Entry gate (mandatory, in order)
1. `memsearch search` the library with 2–3 phrasings of the question.
2. `expand` the top hits; Read the matched entry notes in full.
3. Follow `[[wikilinks]]` one hop where relevant.
4. Answer ONLY from gathered entries. Cite each claim as `(Book, ch. N — [[entry-note]])`.
5. Respect `confidence`: lead with `proven`/`supported`, flag `contested`, caveat `untested`.

## Standing biases
- Eric works in collegiate American football performance — bias examples and
  applications toward that population and calendar when relevant.
- Prefer training-age-appropriate recommendations over one-size-fits-all maxima.
```

- [ ] **Step 2: Verify frontmatter and required sections**

Run:
```bash
node -e "const fs=require('fs');const t=fs.readFileSync('C:/Users/eric_rash/Desktop/SecondBrain/Knowledge/library/advisors/strength-and-conditioning.md','utf8');const ok=['type: advisor','Entry gate','Do NOT pick','Standing biases'].every(s=>t.includes(s));console.log('persona ok:',ok);process.exit(ok?0:1);"
```
Expected: `persona ok: true`.

- [ ] **Step 3: Commit (vault)**

```bash
cd "C:/Users/eric_rash/Desktop/SecondBrain" && git add Knowledge/library/advisors && git commit -m "feat(advisor): strength-and-conditioning persona"
```
Expected: commit hash.

---

## Task 8: Write the generic `advisor` skill

The one skill that powers every domain advisor by reading its persona note and enforcing the entry gate.

**Files:**
- Create: `C:\Users\eric_rash\.claude\skills\advisor\SKILL.md`

- [ ] **Step 1: Write the skill**

Create `C:\Users\eric_rash\.claude\skills\advisor\SKILL.md`:

````markdown
---
name: advisor
description: Consult a grounded domain advisor built from your curated book library. Answers ONLY from ingested library entries, cites every claim, and explicitly separates grounded knowledge from general knowledge. Use when the user says "ask my <domain> advisor", "/advisor <domain> <question>", "what would my library say about…", or consults a standing advisor. Domains live in SecondBrain/Knowledge/library/advisors/.
---

# Advisor

Answer as a domain advisor grounded strictly in the user's curated book library.

**Library root:** `C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library`
**Personas:** `…\library\advisors\<domain>.md`

## Procedure

1. **Resolve the domain.** From the user's request pick `<domain>`. Read
   `advisors/<domain>.md`. If it doesn't exist, list the available persona files and
   ask which advisor — do NOT answer from general knowledge under an advisor's name.

2. **Run the persona's entry gate (mandatory, in order):**
   - `memsearch search "<2-3 phrasings of the question>" --top-k 8`.
   - `memsearch expand <hash>` for the top hits; Read the matched entry notes in full.
   - Follow `[[wikilinks]]` one hop when relevant.
   - If memsearch/Milvus errors, fall back to `Grep` over the library subtree and say
     retrieval was keyword-only.

3. **Answer ONLY from gathered entries.** Adopt the persona's role & voice. Cite every
   claim as `(Book, ch. N — [[entry-note]])`. Respect `confidence`: lead with
   proven/supported, flag contested, caveat untested. Honor the persona's
   "Do NOT pick when" boundaries — if the question is out of scope, say so and stop.

4. **Grounding disclosure footer (always, verbatim shape):**
   ```
   ---
   **Grounded:** <N> entries from <M> book(s): <book-slugs>.
   **Not covered by your library:** <topics the question needed but the library lacked — or "none">.
   <If you added anything from general knowledge, put it in its own clearly labeled
   paragraph ABOVE this footer, never blended into the cited answer.>
   ```

5. **Empty-library handling.** If the entry gate returns essentially nothing on-topic:
   say so first ("Your library has no grounded material on X"), name which book/domain
   would fill the gap, then optionally give clearly labeled general advice.
   **Append the miss** to `…library/<domain>/_domain.md` under "## Miss-log" as:
   `- YYYY-MM-DD — <short question> — gap: <what was missing>`
   (Use the harness date; do not invent one.)

## Rules
- The persona note is the source of voice and boundaries — read it every time.
- Never present general knowledge as grounded. The footer's separation is the contract.
- One hop on wikilinks — don't spider the whole vault.
````

- [ ] **Step 2: Verify the skill is well-formed**

Run:
```bash
node -e "const fs=require('fs');const t=fs.readFileSync('C:/Users/eric_rash/.claude/skills/advisor/SKILL.md','utf8');const ok=/^name:\s*advisor$/m.test(t)&&t.includes('Grounding disclosure footer')&&t.includes('entry gate')&&t.includes('Miss-log');console.log('advisor skill ok:',ok);process.exit(ok?0:1);"
```
Expected: `advisor skill ok: true`.

- [ ] **Step 3: Commit**

```bash
cd "C:/Users/eric_rash/.claude" && git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git add skills/advisor/SKILL.md && git commit -m "feat(advisor): generic grounded-advisor skill" || echo "~/.claude not a git repo — saved to working tree"
```
Expected: commit hash or the notice.

---

## Task 9: Add the KeystoneOS routing line

One-hop routing per the AGENTS.md convention, so a cold agent sends library-consultation questions to the advisor skill.

**Files:**
- Modify: `C:\Users\eric_rash\Desktop\DEV\KeystoneOS\AGENTS.md`

- [ ] **Step 1: Find the routing table in AGENTS.md**

Run:
```bash
grep -n -i "route\|when the user\|->\|skill" "C:/Users/eric_rash/Desktop/DEV/KeystoneOS/AGENTS.md" | head -40
```
Expected: prints the routing table rows so you can match the existing format (the repo describes AGENTS.md as a one-hop routing table).

- [ ] **Step 2: Add one routing row in the existing format**

Using the format observed in Step 1, add a row that routes book/advisor consultation to the `advisor` skill and book ingestion to `ingest-book`. Match the surrounding table's exact columns/style. Semantic content:
- Trigger: "consult a book advisor / ask my <domain> advisor / what would my library say" → `advisor` skill.
- Trigger: "ingest a book / add a book to the library" → `ingest-book` skill.

- [ ] **Step 3: Verify the line is present**

Run:
```bash
grep -n -i "advisor\|ingest-book" "C:/Users/eric_rash/Desktop/DEV/KeystoneOS/AGENTS.md"
```
Expected: at least one line mentioning `advisor` and one mentioning `ingest-book`.

- [ ] **Step 4: Commit + push (KeystoneOS — autonomous push authorized)**

```bash
cd "C:/Users/eric_rash/Desktop/DEV/KeystoneOS" && git add AGENTS.md && git commit -m "feat(router): route book-advisor consultation and ingestion" && git push
```
Expected: commit hash + push confirmation.

---

## Task 10: Acceptance test (the three checks)

Validates the whole pipeline against the spec's acceptance criteria. No new files — this is a behavioral gate.

- [ ] **Step 1: On-library question → grounded, cited answer**

Invoke the `advisor` skill: ask an S&C question the pilot book demonstrably covers
(pick a topic you saw while ingesting in Task 6).
Expected: answer cites at least one `(Book, ch. N — [[entry]])`, and the grounding
footer reports ≥1 entry from the pilot book. PASS if both hold.

- [ ] **Step 2: Off-library question → explicit "not covered", no blended advice**

Ask the advisor something clearly outside the ingested chapters (e.g. a nutrition or
sport-psychology question if the pilot book doesn't cover it).
Expected: the advisor states the library has no grounded material, names the gap, and
any general advice is in its own labeled paragraph above the footer — NOT cited as
library knowledge. Verify a miss-log line was appended:
```bash
grep -n "Miss-log" -A 5 "C:/Users/eric_rash/Desktop/SecondBrain/Knowledge/library/strength-and-conditioning/_domain.md"
```
Expected: a dated miss-log entry for the off-library question.

- [ ] **Step 3: Cross-book check (conditional)**

If only one book is ingested, SKIP and note "deferred until a second book is ingested".
If ≥2 books are ingested, ask a question both cover; expected: the answer cites both
and references a convergence `[[wikilink]]`.

- [ ] **Step 4: Record the result**

Append a short "Pilot acceptance" result block to the spec file
`docs/superpowers/specs/2026-06-12-book-advisors-design.md` (PASS/FAIL per check),
then commit in KeystoneOS:
```bash
cd "C:/Users/eric_rash/Desktop/DEV/KeystoneOS" && git add docs/superpowers/specs/2026-06-12-book-advisors-design.md && git commit -m "docs: record book-advisors pilot acceptance result" && git push
```
Expected: commit hash + push.

---

## Task 11: Write the `library-review` skill

The manual-first gap/review loop. Manual now; promote to scheduled later (gated like the evening tier).

**Files:**
- Create: `C:\Users\eric_rash\.claude\skills\library-review\SKILL.md`

- [ ] **Step 1: Write the skill**

Create `C:\Users\eric_rash\.claude\skills\library-review\SKILL.md`:

````markdown
---
name: library-review
description: Review a book-library domain for gaps, contested entries, and missing coverage, and propose new entries. Manual loop — proposes, you approve. Use when the user says "review my library", "/library-review <domain>", "what's missing from my <domain> advisor", or after a batch of ingestion.
---

# Library Review

Audit one domain of the book library and propose improvements. You PROPOSE; the user
APPROVES. Never add entries silently.

**Library root:** `C:\Users\eric_rash\Desktop\SecondBrain\Knowledge\library`

## Procedure

1. **Pick the domain** from the request (default: ask if ambiguous). Read `<domain>/_domain.md`.

2. **Scan distribution** (run in the sandbox to keep raw notes out of context). Report:
   - entry count by `kind`, by `confidence`, by `book`;
   - entries with `confidence: contested` (need a second source);
   - entries missing a "When NOT to apply" section (quality debt);
   - the "## Miss-log" — questions the advisor couldn't ground.

3. **Identify gaps** from the miss-log and from obviously thin categories.

4. **Propose 2–3 additions.** For each: the topic, which existing book chapter could
   supply it (or that a new source is needed), and the draft `kind`/`category`.
   Cite only reputable sources if proposing material beyond the ingested books, and
   mark such proposals `confidence: untested` until verified.

5. **On approval**, either: enrich existing notes (add the missing section / second
   source / convergence link), or hand the user an `ingest-book` plan for a new source.
   Re-run `memsearch index "…\library"` after any writes. Commit the vault.

## Rules
- Propose, don't auto-write. The user is the editor.
- A "gap" is something the advisor was actually asked (miss-log) or a category with
  near-zero coverage — not speculative completeness.
- Keep it cheap: this is the manual alternative to a paid scheduled agent.
````

- [ ] **Step 2: Verify the skill is well-formed**

Run:
```bash
node -e "const fs=require('fs');const t=fs.readFileSync('C:/Users/eric_rash/.claude/skills/library-review/SKILL.md','utf8');const ok=/^name:\s*library-review$/m.test(t)&&t.includes('Miss-log')&&t.includes('Propose');console.log('review skill ok:',ok);process.exit(ok?0:1);"
```
Expected: `review skill ok: true`.

- [ ] **Step 3: Smoke-test against the real domain**

Invoke the `library-review` skill on `strength-and-conditioning`.
Expected: it reports the entry distribution from the pilot ingest, reads the miss-log
(should contain the Task 10 Step 2 entry), and proposes at least one concrete addition
tied to that miss. No silent writes.

- [ ] **Step 4: Commit**

```bash
cd "C:/Users/eric_rash/.claude" && git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git add skills/library-review/SKILL.md && git commit -m "feat(library-review): manual gap/review loop" || echo "~/.claude not a git repo — saved to working tree"
```
Expected: commit hash or the notice.

---

## Done criteria

- memsearch indexes the library subtree (Task 1).
- Library scaffolding + S&C domain index exist (Task 2).
- `ingest-book` skill + two extractors work on synthetic inputs (Tasks 3–5).
- Pilot book ingested; entries well-formed and searchable (Task 6).
- S&C advisor persona + generic `advisor` skill answer with grounding footers (Tasks 7–8).
- KeystoneOS routes to both skills (Task 9).
- Three-check acceptance test passes (or cross-book check formally deferred) (Task 10).
- `library-review` proposes from real miss-log data (Task 11).

## Deferred (future rounds, per spec "Out of scope")
- Graph hybridization (Approach C) — graphify the library once it exists.
- Dataview/Bases views (Approach B).
- Scheduled/automated review (promote `library-review` after manual proves out).
- Additional domain advisors (business-strategy, etc.) — each = ingest + one persona note.

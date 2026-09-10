# Setup and Operation

## Prerequisites

- Zotero personal-library API key with **library read**, **file read**, and **no write** permission.
- A Zotero collection named `SecondBrain Queue`.
- Zotero setting enabled at **Settings → Advanced → Allow other applications on this computer to communicate with Zotero** for local file access while the desktop app is running.
- Python 3.12 managed by `uv`.

## Install

```powershell
Set-Location 'C:\Users\eric_rash\Desktop\DEV\ZoteroInjestion'
uv sync --extra dev
```

## Configure the read-only key

Run this interactively so the key is never placed in shell history:

```powershell
uv run zotero-bridge configure --user-id 13524464
```

The key is validated before being stored. A key with write permission is rejected. The config is user-local and excluded from Git.

If visually similar characters make manual transcription unreliable, copy the key directly from Zotero's green one-time display and run:

```powershell
uv run zotero-bridge configure --user-id 13524464 --from-clipboard
```

The command reads the exact clipboard value, validates and stores it without displaying it, and then clears the Windows clipboard.

## Verify and synchronize

```powershell
uv run zotero-bridge doctor
uv run zotero-bridge sync --full
uv run zotero-bridge sync --fulltext
```

The first metadata sync builds the Paper Index. Full-text synchronization may be run separately and resumed incrementally.

## Research commands

```powershell
uv run zotero-bridge search 'return to play'
uv run zotero-bridge show ITEMKEY
uv run zotero-bridge queue
uv run zotero-bridge backlog --limit 50 --offset 0
uv run zotero-bridge ground 'How should training load inform return to play?'
uv run zotero-bridge pilot-audit
uv run zotero-bridge pilot-audit --extract
uv run zotero-bridge prepare ITEMKEY
```

## MCP verification

```powershell
uv run python scripts\verify_mcp.py
```

Expected tools:

- `zotero_health`
- `sync_zotero_library`
- `search_papers`
- `get_paper`
- `search_paper_evidence`
- `get_paper_pages`
- `list_promotion_queue`
- `list_library_backlog`
- `build_research_evidence_pack`
- `audit_promotion_queue`
- `prepare_paper_brief`
- `save_paper_brief`
- `save_reference_stub`

## Client registration

The same stdio server should be registered globally in Codex, at user scope in Claude Code, and in Antigravity.
The portable skill is installed into all four harness skill locations by the repository installer:

```powershell
codex mcp add zotero-research -- 'C:\Users\eric_rash\Desktop\DEV\ZoteroInjestion\.venv\Scripts\zotero-bridge-mcp.exe'
claude mcp add --scope user zotero-research -- 'C:\Users\eric_rash\Desktop\DEV\ZoteroInjestion\.venv\Scripts\zotero-bridge-mcp.exe'
pwsh -NoProfile -File .\scripts\install_harness_integrations.ps1
```

Restart existing agent sessions after registration so their tool lists refresh.

## Safety behavior

- Every Zotero HTTP method except `GET` and `HEAD` is blocked at the transport layer.
- A write-enabled API key fails production readiness and live synchronization.
- Evidence page retrieval is bounded to three pages per tool call.
- `promotion_scope = "queue"` limits artifacts to queued papers; `promotion_scope = "library"` enables the approved
  full-library goal while preserving the queue as the priority lane.
- Existing locally edited artifacts are never overwritten.
- The bridge never commits SecondBrain changes automatically.

## Memory and Graphify boundary

The Zotero index is a shared retrieval source, not a replacement for existing memory stores. Paper text is not
copied into agent memory. Reviewed Paper Briefs and syntheses live in SecondBrain; user context and decisions keep
using the existing memory workflow. Graphify is an optional downstream discovery layer over reviewed briefs. Its
inferred connections must be verified against Zotero evidence before appearing as research-backed claims.

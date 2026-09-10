# Handoff — zotero-snap live verification

**Date:** 2026-07-27
**Repo:** `C:\Users\eric_rash\Desktop\DEV\KeystoneOS`
**Branch:** `origin/claude/zotero-photo-library-plugin-mcivyg` (PR #17, OPEN, not merged)
**Project dir on that branch:** `zotero-photo-capture/`

---

## What the next session is for

Run the **live verification** that the cloud session structurally could not. Everything is built; nothing has made a real network request. That is the whole job.

Do not start deployment (Fly), the iOS Shortcut, or extracting the project to its own repo. All three are packaging work that is downstream of a successful round trip.

---

## Read these first — do not re-derive them

Both live on the branch, not on `main`. Read via `git show <branch>:<path>` or after checkout.

| Document | Path | Covers |
|---|---|---|
| Design spec | `docs/superpowers/specs/2026-07-26-zotero-photo-capture-design.md` | Prior-art research, why this is not a Zotero plugin, pipeline architecture, failure modes, the 4 locked decisions |
| README | `zotero-photo-capture/README.md` | Usage, env vars, component status table, known limitations, what has not been verified |
| Local run guide | `zotero-photo-capture/docs/running-locally.md` | Windows step-by-step |
| iOS Shortcut | `zotero-photo-capture/docs/iphone-shortcut.md` | Deferred — not this session |
| Repo extraction | `zotero-photo-capture/docs/extracting-to-its-own-repo.md` | Deferred — not this session |

The README's "What has not been verified" section is the authoritative statement of current state. Trust it over any summary.

---

## Context established this session (not written down elsewhere)

- **The framing changed and the name is misleading.** Eric refers to this as "the Zotero plug-in project." The design spec concluded a plugin is architecturally impossible — Zotero's mobile apps are native with no extension host. It writes through the **Zotero Web API v3** instead. Don't let the branch name (`zotero-photo-library-plugin-*`) mislead you.
- **Prerequisites verified on this machine:** Node **v26.4.0** (needs ≥20.12 for `--env-file-if-exists`), npm **12.0.1**. `ANTHROPIC_API_KEY`, `ZOTERO_API_KEY`, `ZOTERO_USER_ID` are **not** set in the user/machine environment — expected, the project reads a local `.env` via `cp .env.example .env`. A Zotero key with **write** access is needed from zotero.org/settings/keys.
- **The branch has two writers.** Cloud sessions push to it. `git pull` before starting; `git pull --rebase` if it has diverged. This stops mattering once PR #17 merges.
- **The branch is not checked out locally yet** as of this handoff.

---

## The plan (agreed, ~30–45 min)

1. Check out the branch locally — pull first.
2. `npm install && npm test` — confirm the 77 tests still pass on Windows/Node 26, not just in the Linux sandbox.
3. `npm run snap -- --verify` — cheapest live call; proves the Zotero key and library target resolve.
4. `npm run snap -- <photo> --dry-run` — first honest test of extract → Crossref resolve → match scoring. Writes nothing. **Requires a real photo of a paper from Eric.**
5. Full run into a **scratch** library, then open the attachment on the phone. **Blocked on a decision — see below.**

Note the `--` in the npm scripts; it passes flags to the script rather than to npm.

### Where to look when it breaks

The **Zotero three-step file upload** (authorise → push bytes to S3 → register) is the highest-risk stage. It is the one place where partial success looks like full success: miss the final registration call and the API returns a clean-looking attachment item with no file behind it. Step 5's real pass/fail is *the attachment rendering on the phone*, not the API response.

Secondary: HEIC is unsupported (`pdf-lib` can't embed it) and is the iPhone camera default. Test photos must be JPEG.

---

## Open — needs Eric

1. **Scratch library for step 5.** A throwaway Zotero *group* library was recommended over writing test items into his personal library. Dedup keys on DOI, so a half-written test item in the main library can quietly poison a later real capture. Not yet answered.
2. **A real photo of a paper** (JPEG, not HEIC) — gates steps 4 and 5.
3. Three questions the design spec left open and Eric has not answered: phone platform (iOS assumed throughout the docs but unconfirmed), willingness to host an always-on service, and personal vs. group target library for real use.

---

## Suggested skills

- **`superpowers:systematic-debugging`** — invoke the moment step 2, 3, 4 or 5 fails. This session is expected to surface real integration bugs; the failure mode to avoid is guessing at the Zotero upload handshake instead of tracing the actual request/response.
- **`superpowers:verification-before-completion`** — before reporting any step as passing. Eric's stated preference is an explicit distinction between "repair proposed" and "runtime-verified fix"; a green `--verify` is not the same as a working capture.
- **`superpowers:test-driven-development`** — if fixes to `zotero.ts`, `resolve.ts` or `extract.ts` are needed. The existing suite covers the pure stages (`match`, `map`); integration fixes should extend it rather than be spot-checked by hand.
- **`memory-write`** — if the live run produces a durable gotcha about the Zotero Web API (auth scheme, upload handshake, rate limits). This is exactly the class of fact Eric keeps in project memory; compare the existing Catapult/Perch API-auth memory entries.
- **`code-review:code-review`** or **`mattpocock-skills:code-review`** — only once verification passes and PR #17 is ready to merge.

Skip `superpowers:brainstorming` — the design is settled and recorded in the spec. Reopening it would be re-litigating a closed decision.

---

## Do not

- Deploy to Fly or build the iOS Shortcut before a successful local round trip.
- Extract the project to its own repo yet (it does belong out of KeystoneOS eventually — `AGENTS.md` says the control plane shouldn't hold large project files — but not before the code is proven).
- Write test items into Eric's personal Zotero library without an explicit go-ahead.

# Codex Memory Retrieval Design

## Goal

Make KeystoneOS an effective Codex adapter without replacing Claude Code's memory compiler, Codex memory, SecondBrain, project repositories, or Graphify.

## Decisions

1. Keep source ownership distributed. KeystoneOS routes and retrieves; it does not copy or rewrite upstream memory systems.
2. Add `fast` and `broad` retrieval scopes. Fast is for startup/context; broad is explicit and includes large or derived sources.
3. Use ripgrep to return matching lines without materializing every source file. Missing ripgrep fails closed with an actionable message.
4. Add authority, content type, sensitivity, scope, and freshness metadata to each source. Results expose that provenance and label stale sources.
5. Load the agy bridge only when agy-sync or the optional morning sync runs. Core commands work without that script.
6. Mark stale startup artifacts instead of presenting old handoffs as current.

## Retrieval Contract

`Search-Memory -Query <string> -ResultLimit <int> -Scope fast|broad` returns ranked matches with source key, authority, sensitivity, relative file, line number, last write time, and freshness status. Scope defaults to `fast`. The `memory` command accepts `-Scope broad` for an intentional wide search.

Fast sources are Codex memory, Claude global memory, and SecondBrain. Broad sources additionally include the Claude compiler, Baylor WorkDrive, Graphify, and agy digests.

## Error Handling

- Missing optional sources are reported and skipped.
- Missing ripgrep does not fall back to an unbounded recursive scan.
- Missing agy bridge is a non-fatal morning skip and a clear explicit-command message.
- Stale sources and artifacts remain searchable but are labeled `STALE`.

## Verification

- Existing command fixtures run without copying agy-sync into every fixture.
- Tests prove fast scope excludes broad sources, broad scope includes them, and canonical/synthesis sources outrank working/derived sources on relevance ties.
- A real fast query completes without recursive file enumeration.

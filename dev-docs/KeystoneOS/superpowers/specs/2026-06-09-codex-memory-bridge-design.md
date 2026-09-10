# Codex Memory Bridge Design

## Purpose

This phase gives Codex a Windows-safe, KeystoneOS-aware bridge into the same knowledge infrastructure that Claude Code already uses.

The bridge should not replace Claude memory, Codex memories, Obsidian, Graphify, or KeystoneOS project registries. It should give Codex a compact startup packet, preserve context before compaction, and leave a lightweight stop record that future sessions can find.

## Architecture

KeystoneOS owns the Codex-facing scripts:

- `scripts/codex-hooks/session-start.ps1` emits Codex hook JSON with `hookSpecificOutput.additionalContext`.
- `scripts/codex-hooks/pre-compact.ps1` stores a raw hook event under `outputs/codex-hooks/pre-compact/`.
- `scripts/codex-hooks/stop.ps1` stores a raw hook event under `outputs/codex-hooks/stop/`.
- `scripts/install-codex-hooks.ps1` merges those hooks into `~/.codex/hooks.json` after creating a backup.

Session-start context includes KeystoneOS commands, active project registry entries, latest handoff notes, latest intake output, and optionally the Claude memory compiler session-start packet. The script must keep output compact and must still emit valid JSON if any optional source is missing.

## Safety Rules

- Do not overwrite Claude memory or Codex memory files.
- Do not delete existing hooks.
- Preserve existing `~/.codex/hooks.json` entries.
- Back up `~/.codex/hooks.json` before applying changes.
- Default the installer to dry-run unless `-Apply` is passed.
- Use `commandWindows` so Codex runs the PowerShell scripts reliably on Windows.

## Verification

- Run `tests/codex-hooks.ps1`.
- Run `scripts/codex-hooks/session-start.ps1 -NoClaude` and confirm valid JSON.
- Run `scripts/install-codex-hooks.ps1` and confirm dry-run does not mutate `~/.codex/hooks.json`.
- Run `scripts/install-codex-hooks.ps1 -Apply` only after backup behavior is verified against a temporary Codex home.

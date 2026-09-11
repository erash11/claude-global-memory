# Handoff 2026-09-10: two-machine, provider-neutral workflow

## What was being worked on and why
Eric wanted one system so context, projects, and files survive switching between the Mac (personal, ~/DEV) and the Baylor Windows laptop (Desktop\DEV), and survive losing any LLM provider. Built over Sep 9-10 from Cowork on the Windows machine.

## Decisions
- No VPS/home server. GitHub (erash11, private) is the transport; Google Drive (5 TB) holds documents; local disk holds working copies. Nothing lives only in a provider's cloud.
- Every project = one folder in DEV, one git repo. AGENTS.md is the real context file (Codex reads it), CLAUDE.md is `@AGENTS.md`. Every repo carries a Session routine: pull + read docs/STATUS.md at start; update STATUS, commit, push at end.
- Windows DEV stays on the Desktop (Eric's preference); C:\DEV projects were moved in. _DRIVE junction inside DEV points at the Google Drive primary storage drive so one connected folder covers both.
- Primary storage drive moved off Baylor OneDrive (university-owned) to personal Google Drive. Originals parked online-only in OneDrive\..\_MIGRATED_to_GoogleDrive.
- DexaProject (identifiable health data) must never be pushed; its GitHub repo is to be deleted by Eric.
- ~/.claude (dotclaude) made two-machine aware: gitignored machine.md imported by CLAUDE.md (templates machine.macos.md / machine.windows.md), hook commands use $HOME, dcg hook guarded, "Windows retired" note corrected.
- memsearch indexes DEV repo docs via ~/.claude/global-memory/dev-docs, filled by ~/.claude/scripts/harvest-dev-docs.(sh|ps1). memsearch-sync.js resolves DEV root on both machines and supports {DEV} in memory-index-paths.json.
- Skills: new-project, dev-sync, closeout in Cowork (account) and in ~/.claude/skills (claude-skills repo) with sync-to-codex.(sh|ps1) copying shared skills into ~/.agents/skills and ~/.codex/skills.

## Files created or modified (Windows)
- C:\Users\eric_rash\Desktop\DEV\* : 130 repos synced/cloned; every repo has AGENTS.md (session routine), CLAUDE.md, docs/STATUS.md
- C:\Users\eric_rash\Desktop\DEV\_DRIVE (junction -> G:\My Drive\00_Primary_Storage_Drive)
- C:\Users\eric_rash\Desktop\DEV\_INBOX\backup_ai_sessions.ps1, backup_dev.ps1, docs\STATUS.md, migration-tools\*
- C:\Users\eric_rash\.claude\CLAUDE.md, AGENTS.md, machine.md, machine.macos.md, machine.windows.md, settings.json, .gitignore, hooks\memsearch-sync.js, scripts\harvest-dev-docs.ps1|.sh
- C:\Users\eric_rash\.claude\skills\new-project, dev-sync, closeout, sync-to-codex.ps1|.sh
- C:\Users\eric_rash\Desktop\DEV\KeystoneOS\data\memory-index-paths.json, discovery-roots.json, memory-sources.json, projects.json, projects\registry.md
- C:\DEV\_tools\*.ps1 (one-off migration scripts, not a repo; copied to _INBOX\migration-tools)
- Windows scheduled tasks: "Eric\Backup AI Sessions to Drive" (daily 17:30), "Eric\Backup DEV to Drive" (Sun 19:00)
- G:\My Drive\00_Primary_Storage_Drive\* (full migration), 04_RESEARCH\_INBOX\drive-zotero-import_2026-06, 05_SYSTEMS\AI_Sessions_Backup, 05_SYSTEMS\DEV_Backup

## Next actions
1. Mac one-time: cd ~/.claude && git pull && cp machine.macos.md machine.md; cd ~/.claude/skills && git pull && bash sync-to-codex.sh; bash ~/.claude/scripts/harvest-dev-docs.sh; ln -s "<Drive path>/00_Primary_Storage_Drive" ~/DEV/_DRIVE
2. Run /migrate-project-to-disk in the 7 remaining Cowork projects.
3. Delete OneDrive _MIGRATED_to_GoogleDrive after spot-check; delete GitHub repo erash11/DexaProject.
4. Reconcile .from-mac files (CFB_Victory_Model, KeystoneOS, project-triage).

## Mid-flight / open
- Confirm Ath_Medicine, Baylor_Exposure_Data, Risk_Stratification_Engine contain no identifiable athlete data.
- SecondBrain vault not on Windows; memsearch there skips those paths.
- Project memory slugs differ per machine (known limitation; repo docs/ is the cross-machine channel).

# KeystoneOS Morning Control Risk Loop

Date: 2026-06-25

## Purpose

Add a read-only morning control loop to KeystoneOS that keeps stale evidence-gated projects visible, starting with `Risk_Stratification_Engine`.

The loop is not an automation escalation. It creates a durable control packet, checks live artifacts, and points to the next safe manual action.

## Loop Card

- Name: KeystoneOS morning control loop for stale research projects
- Trigger: `.\scripts\keystone.ps1 today` or `.\scripts\keystone.ps1 control-loop`
- Discovery inputs: KeystoneOS project registry, project git state, Risk prospective collection worksheet, Risk ingest JSON, Risk completion JSON
- State location: `outputs\loops\<yyyy-MM-dd>-morning-control.md`
- Generator task: write the current control packet and one conservative next action
- Evaluator checks: verify paths, worksheet row count, project-native readiness fields, and no-claim boundaries
- Human checkpoint: Eric approves any ingest, bounded retest, dashboard/pilot, external send, merge, or publication step
- Allowed actions: read project state, write KeystoneOS packet, print next commands
- No-go actions: edit Risk repo artifacts, invent practitioner evidence, claim readiness, send data externally, or schedule automation without repeated manual evidence
- Caps: one Risk gate decision per run; no parallel agents until the packet has been manually reviewed

## Risk Evidence Gate

The loop checks these project-native artifacts:

- `outputs\experiments\exposure_load_shadow_prospective_collection_prefill_v1\prospective_collection_prefilled_working.csv`
- `outputs\experiments\exposure_load_shadow_prospective_collection_ingest_v1\exposure_load_shadow_prospective_collection_ingest.json`
- `outputs\experiments\exposure_load_shadow_prospective_collection_ingest_v1\exposure_load_shadow_prospective_collection_ingested_operations.json`
- `outputs\experiments\exposure_load_shadow_prospective_collection_completion_v1\exposure_load_shadow_prospective_collection_completion.json`

Current boundary: the Risk project remains research/shadow-mode only. The morning loop must preserve blocked states for probability-facing output, pilot/dashboard readiness, autonomous intervention, load modification, and calibration claims unless the project-native artifacts explicitly change and are manually reviewed.

## First Manual Dry Run

```powershell
.\scripts\keystone.ps1 context Risk_Stratification_Engine
.\scripts\keystone.ps1 control-loop
Get-Content .\outputs\loops\$(Get-Date -Format yyyy-MM-dd)-morning-control.md
```

## Verification

- `.\tests\keystone-control-loop.ps1`
- `.\tests\keystone-today.ps1`
- `git status --short` in KeystoneOS
- `git status --short` in `C:\Users\eric_rash\Desktop\DEV\Risk_Stratification_Engine`

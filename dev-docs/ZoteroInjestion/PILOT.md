# Ten-Paper Pilot

## Status

Completed on July 22, 2026. The Library Steward added all ten Source Papers to the live `SecondBrain Queue`; the bridge extracted page-aware evidence and promoted ten validated Paper Briefs into SecondBrain.

## Cohort

| Zotero key | Source Paper | Pilot role |
|---|---|---|
| `25NCHHVZ` | Return-to-Play in Sport: A Decision-based Model | Foundational RTP decision framework |
| `SK32YKG2` | Contextual considerations using the control-chaos continuum for return to sport in elite football — Part 1: Load planning | Applied elite-football RTP progression |
| `T2J46UF6` | Strength and Power Training in Rehabilitation: Underpinning Principles and Practical Strategies to Return Athletes to High Performance | Rehabilitation-to-performance translation |
| `DPALTQLF` | A longitudinal investigation of landing biomechanics following anterior cruciate ligament reconstruction | Longitudinal ACL biomechanics and complex results |
| `UQNXNVRF` | The Association Between the Acute:Chronic Workload Ratio and Injury and its Application in Team Sports: A Systematic Review | Systematic-review evidence synthesis |
| `RATET6AR` | Training Load and Injury Part 2: Questionable Research Practices Hijack the Truth and Mislead Well-Intentioned Clinicians | Methodological criticism and claim calibration |
| `T83B4S2M` | Identifying and reporting position-specific countermovement jump outcome and phase characteristics within rugby league | Force-time metrics, tables, and position-specific interpretation |
| `SWPE37N4` | Resisted Sled Sprint Training to Improve Sprint Performance: A Systematic Review | Sprint-programming evidence |
| `PRJPTSAD` | Menstrual Cycle Phase–Based Strength & Conditioning Training for Elite Team Sport Female Athletes | Female-athlete application and practitioner interpretation |
| `4BIP46BT` | Systematic Review and Meta-analysis of Linear and Undulating Periodized Resistance Training Programs on Muscular Strength | Zotero-API-unindexed full text; local-PDF fallback |

## Audit commands

Run a non-mutating cached-readiness audit:

```powershell
uv run zotero-bridge pilot-audit
```

Run page-aware PDF extraction and classify final readiness:

```powershell
uv run zotero-bridge pilot-audit --extract
```

The deep audit may open local Zotero PDFs or download them read-only from Zotero storage. It writes only disposable evidence pages to the local Paper Index.

## Required checks

For each paper:

1. Confirm queue membership and Zotero version.
2. Resolve the source PDF without copying it into SecondBrain.
3. Classify Usable Full Text and record any blocking reason.
4. Extract page-aware text and spot-check methods, results, limitations, and all numerical claims.
5. Produce a Paper Brief only when Evidence Locators are verifiable.
6. Produce only a Reference Stub when full text is absent or inadequate.
7. Verify Codex and Claude return consistent metadata and evidence locators.
8. Confirm no Zotero mutation and no overwrite of locally edited SecondBrain artifacts.

## Plugin decision gate

After the cohort is complete, record search usefulness, promotion effort, extraction failures, duplicate/update behavior, and any interaction that would materially improve if performed inside Zotero. Build a native plugin only if repeated Zotero-UI friction remains after the MCP and CLI workflow is proven.

## Results

| Measure | Result |
|---|---|
| Queue recognition | 10 of 10 selected parent records detected |
| Usable Full Text | 10 of 10 |
| Paper Briefs | 10 validated and saved |
| Reference Stubs | 0 required |
| Extraction failures | 0 |
| Structural warnings | 2 narrative papers lacked an explicit methods heading; both remained usable after review |
| Local fallback | `4BIP46BT` was not indexed through Zotero full text, but its local PDF resolved and passed the evidence gate |
| Duplicate/update behavior | A complete re-run preserved all ten paths and content hashes |
| Zotero mutation | None; the post-promotion sync remained at library version `6333` with zero item changes |
| Cross-agent access | Codex is enabled and Claude Code is connected to the same stdio MCP executable |

Metadata and full-text search were sufficient to find and review the cohort. The only required Zotero interaction was manually adding parent records to `SecondBrain Queue`; after that, synchronization, extraction, validation, and promotion were handled outside Zotero.

The planned missing-full-text case became a successful fallback-path test because a usable local PDF existed. Reference Stub and poor-extraction fail-closed behavior therefore remain automated-test verified rather than live-observed in this cohort.

## Decision

Remain MCP/CLI-only. The pilot did not expose recurring friction that justifies the version coupling and maintenance surface of a native Zotero plugin. Reconsider a narrowly scoped plugin only if manual queue selection becomes high-volume, promotion status must be visible inside Zotero, or immediate event-driven processing becomes operationally important.

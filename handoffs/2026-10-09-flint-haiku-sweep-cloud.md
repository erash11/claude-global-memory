# Handoff 2026-10-09 (cloud): Haiku sweep, vault-path fix, Wave 1 source check

## What and why
Eric asked to resume Flint and to use Haiku where it helps. This cloud session has the repo but
not the staged PDFs or the SecondBrain vault, so it took the work that runs on staging and
Drive alone. Haiku did the mechanical work. The coordinator checked every row.

## Done
- `scripts/vault_path.py`; the four vault scripts read the vault path from config (STATUS has the details).
- 31 Evans entries: the stray `</content>` line removed. Balance-board pointer fixed. Staging only.
- `staging/reciprocal_links_2026-10-09-ch6-7-backlinks.md` (290 rows, ready) and `..._held.md` (16, Eric's call).
- `docs/wave1-source-check-2026-10-09.md` (W1-W32).

## Next actions (Mac)
1. `git pull`, check out or merge `haiku-sweep-2026-10-09` (PR #6).
2. `python scripts/promote_to_vault.py strength-and-conditioning/elite-sports-performance--evans strength-and-conditioning/supertraining--verkhoshansky` (dry run: expect 32 changed, 0 new), then `--apply` on Eric's approval.
3. `python scripts/apply_reciprocal_links.py staging/reciprocal_links_2026-10-09-ch6-7-backlinks.md`, then `--apply`; sync back; memsearch re-index.
4. The 48 vault-only back-links (Bompa, research-papers, Moyer): build the rows with the vault present.
5. *Supertraining* Chapter 8, then Chapter 9 Addendum.
6. Wave 1: start with the 23 OK decks. Settle the 5 check-by-hand rows and W14 with Eric first.

## Open
- Eric: decide on the 16 held back-links; locate W14 (Stone, Explosive Exercise); confirm the W16 year.
- The vault key name in `_shared/config.*.json` was not visible from the cloud. The resolver scans for any value naming SecondBrain; set `FLINT_VAULT` if that misfires.

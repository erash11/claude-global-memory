# Hawkin Dynamics API Integration

**Status:** Implemented, verified, and **cut over** on 2026-07-22. The pipeline now runs off the API.
**Script:** `scripts/fetch_hawkin.py` · **Config:** `config.yaml` → `hawkin:` · **Credentials:** `.env` (gitignored)

Everything below was confirmed against live account data, not inferred from documentation.

---

## 1. What this replaces

`fetch_hawkin.py` is the API-based replacement for `import_data.py`. It writes the same
`master_data.csv` schema, so the analysis layer is untouched:

```
  (old)  ForceDecks CSV → import_data.py ──┐
                                           ├→ master_data.csv → generate_report.py
  (new)  Hawkin API → fetch_hawkin.py ─────┘                  → generate_recovery_report.py
```

`utils.py`, both report generators, and both HTML templates required **no changes**.

### Commands

```bash
python scripts/fetch_hawkin.py                      # last 14 days
python scripts/fetch_hawkin.py --date 2026-07-06    # one session date
python scripts/fetch_hawkin.py --from 2026-01-01 --to 2026-07-31
python scripts/fetch_hawkin.py --all                # entire account history
python scripts/fetch_hawkin.py --probe              # print raw API fields, write nothing
python scripts/fetch_hawkin.py --dry-run            # show what would be written
```

No new Python dependencies — it uses the stdlib plus the `pandas`/`pyyaml` already required.

---

## 2. API mechanics (verified)

- **Token exchange:** `GET https://cloud.hawkindynamics.com/api/token` with `Authorization: Bearer <refresh token>`. Returns `access_token`, `token_type`, `expires_at`. **Access tokens last 60 minutes**; the refresh token is long-lived.
- **Tests endpoint is the API root itself** — `GET https://cloud.hawkindynamics.com/api/v1?from=<epoch>&to=<epoch>`. There is **no `/tests` path**; requesting one returns 404. This is the single easiest thing to get wrong.
- Sub-resources that *do* exist: `/athletes`, `/tags`, `/teams`, `/groups`. (`/testTypes` returns 404 on v1.)
- Response envelope: `{ data: [...], count, lastSyncTime, lastTestTime }`.
- Each trial carries a unique `id`, a UNIX `timestamp`, a nested `athlete` object, a `testType` object (`id`, `name`, `canonicalId`, `tags`), and ~83 flat metric fields.
- CMJ `canonicalId` = `7nNduHeM5zETPjHxvm7s`. Match on this, not on `name` — the display name absorbs applied tags (e.g. `Countermovement Jump-Post Practice`).

Credentials live in `.env` as `HD_REFRESH_TOKEN`. Both `.env` and `HawkinDynamic_Key.txt` are gitignored.

---

## 3. Metric mapping (verified against live responses)

Raw API keys are **display-style with units in parentheses** — not the snake_case names the R/Python
client libraries produce after flattening. All six resolve `[OK]` under `--probe`.

| `master_data.csv` field | Hawkin API key | Unit | Conversion |
|---|---|---|---|
| `jump_height_cm` | `Jump Height(m)` | m | × 100 |
| `rsi_modified` | `mRSI` | ratio | — |
| `mean_propulsive_force_n` | `Avg. Propulsive Force(N)` | N | — |
| `ecc_braking_rfd_ns` | `Braking RFD(N/s)` | N/s | — |
| `time_to_takeoff_ms` | `Time To Takeoff(s)` | s | × 1000 |
| `cm_depth_cm` | `Countermovement Depth(m)` | m | × 100, **absolute value** |

**Countermovement depth is returned negative** (e.g. `-0.3352`), because Hawkin defines it as peak
*negative* displacement. Without `absolute: true` the `increase_bad` direction logic reads backwards
and a deeper dip registers as improvement. This is handled in config.

Percent-change thresholds are unit-invariant, so the conversions above do not require any change to
`thresholds:`. They exist so displayed values read as cm and ms.

---

## 4. Pre/post pairing — tags and clock windows both fail

The original design assumed `pairing.method: "tag"` would carry over. It does not.

- **Tags are effectively unused.** Of 1,728 CMJ trials in the account, only 34 carry any tag, all on a single date (2026-04-24). The account has a `Post Practice` tag but **no pre-practice tag at all**.
- **Fixed clock windows misclassify everything.** Practices alternate between morning and afternoon. Morning sessions run ~07:30 pre / ~10:00 post; afternoon sessions run ~14:15 pre / ~16:35 post. The configured windows (pre 06:00–12:00, post 14:00–22:00) would label a 10:00 post as *pre*, and a 14:15 pre as *post* — wrong on both session types.

**Solution implemented: split at the largest time gap within each athlete-date.**

Trials inside one testing bout are seconds to minutes apart; a genuine pre/post split shows a median
gap of **131 minutes**. Measured across 371 athlete-sessions: 313 have a gap ≥ 45 min (clean split),
and the dominant shape is 2 pre + 2 post (289 of 371). Where no gap exceeds
`min_split_gap_minutes` (default 45), the session was a single bout and all trials are labelled
`pre` — which is exactly what the recovery report consumes.

This is tag-independent and session-time-independent, so it keeps working if staff change practice
times or never adopt tags. Verified: 2026-04-23 paired 12 of 12 athletes, 0 unpaired.

Athletes jump ~2 trials per phase, reduced to one reported value by
`trial_aggregation` (default `mean`; `best` and `latest` also available).

---

## 5. Data reconciliation findings

### The Hawkin account already contains the ForceDecks history

The March–April sessions in `master_data.csv` are present in Hawkin with **identical timestamps to
the minute** (e.g. Julianna Hernandez 2026-03-23, CSV `4:39 PM` ↔ Hawkin `16:39`). The raw trials
were imported into Hawkin and recomputed with Hawkin's own algorithms — several tags carry the
description "Imported from third-party data".

So this is not a clean vendor cutover: it is the same jumps, with different numbers.

### The API unlocks substantially more history

| | dates | span |
|---|---|---|
| `master_data.csv` today | 22 | 2026-03-02 → 2026-04-24 |
| Hawkin API (`--all`) | 57 | **2024-08-12** → 2026-07-06 |

That includes June and July sessions never exported to CSV, and nearly a full extra season of
baseline.

### Roster mismatches (now handled via `athlete_aliases`)

| Hawkin name | Config roster name | Note |
|---|---|---|
| `Isabela Haggard` | `Isabella Haggard` | **Duplicate profile in Hawkin** — both spellings exist, splitting her history |
| `Ksusha Rahkmanchyk` | `Kseniya Rakhmanchyk` | Nickname profile |

`Anastasiia Nikolnikova` is on the config roster but has **no CMJ trials in Hawkin**.

Four non-roster people have trials in the account and are excluded via `exclude_athletes`:
Michael Wenger (21 trials), Jorge Penate, Joshua Walker, Sam Compton.

**Recommendation:** merge the duplicate Haggard profile in the Hawkin cloud UI. The alias mapping
papers over it, but the split profile will keep causing problems in Hawkin's own reporting.

---

## 6. ⚠ Threshold calibration does not transfer cleanly

This is the one finding that should gate clinical use.

The traffic-light thresholds in `config.yaml` were tuned on **ForceDecks-computed** metrics. Because
Hawkin recomputes the same jumps with different algorithms, the percent changes differ. Measured
across **162 athlete-sessions present in both sources**:

| Metric | median abs. difference in % change | p90 | traffic-light colour agreement |
|---|---|---|---|
| `mean_propulsive_force_n` | 0.2% | 0.6% | **98%** |
| `time_to_takeoff_ms` | 1.3% | 5.3% | 86% |
| `jump_height_cm` | 1.7% | 6.6% | 80% |
| `rsi_modified` | 2.3% | 9.3% | 80% |
| `ecc_braking_rfd_ns` | 7.1% | 14.5% | 70% |
| `cm_depth_cm` | 9.4% | 30.7% | **52%** |

Reading this:

- **Mean propulsive force, time to takeoff, jump height, RSI-mod** transfer well. Thresholds can stand.
- **Eccentric braking RFD** (70%) and especially **countermovement depth** (52%) do not. CM depth colour agreement is barely better than a coin flip — its thresholds (`yellow_min: 5.0`, `red_min: 12.0`) are *smaller than the median inter-system disagreement of 9.4%*. The threshold is finer than the measurement's reproducibility across systems.

Net effect on a real session (2026-04-23, same 12 athletes, same jumps):

| Source | Green | Yellow | Red |
|---|---|---|---|
| ForceDecks | 4 | 5 | 4 |
| Hawkin | 6 | 0 | 6 |

Same athletes, same practice — materially different guidance to coaches.

### Resolved — thresholds recalibrated 2026-07-22

Two metrics were recalibrated. The other four were left alone.

The noise floor was measured directly from the account: the trial-to-trial coefficient of variation
within a single testing bout, across 791 bouts. Because each reported value is the mean of ~2 trials,
the noise on a pre→post % change is roughly √2 × that CV.

| Metric | measured noise on % change | old yellow | verdict |
|---|---|---|---|
| Mean propulsive force | 2.3% | 5.0% | fine |
| Jump height | 3.4% | 5.0% | fine |
| Time to takeoff | 4.6% | 5.0% | fine |
| RSI-modified | 6.0% | 7.0% | fine |
| **Countermovement depth** | **6.7%** | **5.0%** | **below noise floor** |
| **Eccentric braking RFD** | **11.5%** | **8.0%** | **below noise floor** |

Both failing thresholds sat *below* their own measurement noise, so they were flagging measurement
error as fatigue. New values keep the same signal-to-noise ratio as the four metrics that transferred
cleanly (~1.4 × noise for yellow, ~2.8 × for red):

| Metric | old | new |
|---|---|---|
| `ecc_braking_rfd` | 8.0 / 20.0 | **15.0 / 30.0** |
| `countermovement_depth` | 5.0 / 12.0 | **10.0 / 20.0** |

**Three independent lines of evidence agree on this change:**

1. **Measured noise floor** (above) — both old thresholds were inside their own error band.
2. **Published literature.** Merrigan et al. (2024), *J Strength Cond Res* 38(1):30–37 — the one paper that directly compares Vald ForceDecks, Hawkin Dynamics, and Sparta Science on the same subjects — reports "poor test-retest reliability for modified reactive strength index (mRSI) and rate of force development (RFD)", and finds that although FD and HD agree acceptably on braking RFD, "systematic and proportionate bias existed for RFD". Their within-session FD reliability (jump height CV 4.14%, mRSI CV 6.70%) is the same order as measured here (3.4%, 6.0%), which is a useful check that these local estimates are sane. Their closing warning is precisely this situation: practitioners must account for "differences in metric definitions and units of measurement" before comparing across systems. DOI [10.1519/JSC.0000000000004586](https://doi.org/10.1519/JSC.0000000000004586).
3. **Distribution match.** The recalibrated thresholds independently reproduce the operating point the system has always produced, which was not something they were fitted to:

| | green | yellow | red |
|---|---|---|---|
| ForceDecks + original thresholds (*what staff were seeing*, 177 sessions) | 49% | 20% | 32% |
| Hawkin + original thresholds (312 sessions) | 42% | 19% | 39% |
| **Hawkin + recalibrated thresholds** (312 sessions) | **48%** | **20%** | **32%** |

Note the literature does *not* cover countermovement depth agreement between systems; the 52% figure
above is a local empirical finding only.

---

## 7. Idempotency — fixed

`import_data.py` had no deduplication, so re-running it appended duplicate rows (visible in
`master_data.csv` today as mixed date formats and a blank row). That is far more dangerous over an
API, where re-pulling a range is routine.

`fetch_hawkin.py` records the Hawkin trial ids behind every row in `hawkin_test_ids` and skips rows
whose ids are already present. Verified: a second `--all` run added **0 rows and skipped 830**.

Two provenance columns are appended to the schema: `source` (`hawkin`) and `hawkin_test_ids`, plus
`n_trials`. They are additive, so existing ForceDecks rows and the report scripts are unaffected.

---

## 8. Cutover completed 2026-07-22

- [x] **Fresh master built** from `--all`: 830 Hawkin-only rows, 57 dates, 2024-08-12 → 2026-07-06.
- [x] **Old ForceDecks master archived** to `data/archive/master_data_forcedecks_2026-07-22.csv` (plus its `.bak`). `data/archive/` is gitignored — it holds athlete data.
- [x] **Thresholds recalibrated** for CM depth and braking RFD (§6). The other four left untouched.
- [x] **`report.data_source`** changed to `"Hawkin Dynamics"`.
- [x] **`run_pipeline.py` cut over** to the API. `run_report.bat` needs no edit — it calls `run_pipeline.py`, which now fetches from Hawkin instead of scanning `data/imports/`.
- [x] **Test suite green:** 87 passed. (`tests/test_import.py` had been erroring since the `config/` reorg because it still pointed at the pre-reorg `config.yaml` path; fixed in passing.)

`import_data.py` is retained and still works for hand-importing a ForceDecks CSV if ever needed.

### Behaviour changes in `run_pipeline.py`

- Fetching zero new rows is no longer an error. The old importer exited if no CSVs were waiting; the API path may legitimately add nothing because the window is already synced, and the report should still render.
- The session date now defaults to **the most recent date with an actual pre/post pair**, rather than today. The old default failed on any day without testing.
- If no session in the window has both pre and post, it exits cleanly with an explanation instead of erroring out.

---

## 9. Open items

### ⚠ The recovery report's badge thresholds are miscalibrated (pre-existing)

Discovered while verifying the cutover; **not caused by it**. The recovery report classifies almost
every athlete "At Risk" regardless of data source:

| Data source + thresholds | At Risk | Watch | Recovered |
|---|---|---|---|
| ForceDecks + original thresholds (*what staff saw*) | 13 | 0 | 2 |
| Hawkin + recalibrated thresholds | 10 | 1 | 2 |

The recalibration slightly *improved* it, but the underlying problem is the badge rule itself. A
badge is assigned over a grid of 6 metrics × 6 sessions = 36 cells, and fires "At Risk" at 2 red or
3 yellow-plus-red cells. With 36 cells, that threshold is nearly certain to trip by chance, so the
badge carries almost no information — a report that flags 13 of 15 athletes as At Risk will be
ignored by coaches.

Shrinking the window helps (a 3-session window gives At Risk 3 / Watch 1 / Recovered 6), which is
consistent with the cell-count diagnosis. **This needs a decision from you**, because changing the
rule changes what coaches are told. I have deliberately not altered it. Options worth considering:
scale the badge thresholds with window size, express them as a *proportion* of non-green cells, or
weight recent sessions more heavily.

### Smaller items

- [ ] **Merge the duplicate `Isabela` / `Isabella Haggard` profile** in the Hawkin cloud. Aliasing handles it here, but the split profile will distort Hawkin's own reporting.
- [ ] `Anastasiia Nikolnikova` is on the config roster but has no CMJ trials in Hawkin — confirm whether she should be removed or is simply untested.
- [ ] Optionally create `Pre Practice` / `Post Practice` tags in Hawkin. Not required, since gap-splitting works without them, but tags would make intent explicit.
- [ ] The recovery report's default 6-session window currently spans the April→June offseason gap. Contiguous-block windows are more meaningful; consider a guard that warns when a window straddles a long break.

---

## References

- [How to create an API token](https://learning.hawkindynamics.com/knowledge/how-to-create-an-api-token) — Hawkin Help Center
- [hawkinR](https://hawkindynamics.github.io/hawkinR/) — official R client
- [hawkinPy / `hdforce`](https://github.com/HawkinDynamics/hawkinPy) — official Python client (not used here; stdlib was sufficient)

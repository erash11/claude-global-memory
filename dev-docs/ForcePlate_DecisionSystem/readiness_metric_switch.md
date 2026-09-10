# Readiness moved from RSI-modified to Peak Power / BM

**Decision date:** 2026-07-22

The readiness flag (green / yellow / orange / red) is now computed from
**Peak Power / BM** instead of **RSI-modified**. The gold / purple / white
performance tier is unchanged and still comes from RSI-modified percentiles.

---

## Why

RSI-modified is the noisiest of the metrics we lead with. Measured over the same
5,930 stable retest pairs (consecutive same-weekday tests <= 10 days apart,
2023-25, tails trimmed at 1/99pct):

| Metric | Typical error | Change-score SD |
|---|---|---|
| Peak Power / BM | **3.8%** | **5.40%** |
| RSI-modified | 8.8% | 13.09% |

Peak Power / BM carries less than half the measurement noise. A real drop of a
given size is correspondingly easier to separate from noise. Of the ten CMJ
metrics, Peak Power / BM also has the best signal-to-noise ratio against the
smallest worthwhile change (SWC/TE 0.78 vs 0.48).

## Why the thresholds had to change with it

**This is the part that matters.** Applying the existing RSI-modified ladder
(single-test 30 / 25 / 15) to Peak Power / BM unchanged fires on **0.00% of
noise-only comparisons** — a classifier that never flags anyone. The thresholds
are not a stylistic choice; each one is positioned against the noise of a
specific metric.

Every threshold below is calibrated to a **false-positive rate** — the share of
noise-only comparisons that would trip it — and the rates are held identical
across both metrics. A "red" therefore means the same thing whichever metric
produced it.

| Tier | Target false-positive rate | RSI-modified | Peak Power / BM |
|---|---|---|---|
| Single-test red | 1.30% | >30% | **>12%** |
| Single-test orange | 2.50% | >25% | **>11%** |
| Single-test yellow | 9.80% | >15% | **>7%** |
| Consecutive red | 0.96% | >15% both | **>7% both** |
| Consecutive orange | 3.32% | >10% both | **>5% both** |
| Consecutive yellow | 10.49% | >5% both | **>2.5% both** |

The Peak Power values are the empirical percentiles (11.7 / 10.6 / 6.7 and
6.7 / 4.6 / 2.3) rounded outward, which is how the RSI-modified ladder was
rounded. They land at roughly 40% of the RSI-modified numbers, exactly what the
5.40% vs 13.09% change-score SD predicts.

Confidence check: re-deriving the RSI-modified ladder with the same method
recovers 27.7 / 24.0 / 14.7 and 14.7 / 9.8 / 4.9, which is the shipped
30 / 25 / 15 and 15 / 10 / 5 after rounding.

## Effect on the stored history

All 10,730 classified rows were reclassified on 2026-07-22.

| Flag | Before | After | Change |
|---|---|---|---|
| green | 6,924 | 8,576 | +1,652 |
| yellow | 1,232 | 831 | −401 |
| orange | 954 | 490 | −464 |
| red | 1,620 | 833 | −787 |
| **non-green total** | **3,806** | **2,154** | **−43%** |

Reds roughly halve. This is the intended direction — the old single-test rule
(">10% -> red") fired on 18.2% of noise-only comparisons, so roughly one red in
five was measurement noise — but the size of the shift should be understood
before the flags are used operationally. **Fewer flags is not the same as fewer
athletes needing attention**; it means the flags that remain are the ones that
outrun the measurement error.

Baselines were rebuilt from each athlete's earliest test so the RSI-modified and
Peak Power baselines share a baseline date. A backup of the pre-switch database
is at `data/forceplate_backup_2026-07-22_pre_peak_power.db`.

## Fallback behaviour

Readiness falls back to RSI-modified when an athlete has no Peak Power baseline.
After the reclassification this applies to 236 rows — each athlete's first ever
test, which has no baseline of any kind and is green by definition.

## Two bugs found while doing this

1. **`classify_existing_raw_tests` silently skipped 300 tests.** `raw_tests`
   stores the position as VALD reports it (`Safety`, `Cornerback`,
   `Outside Linebacker`, `Running back`, `SPEC`) while the thresholds config
   uses canonical names. The function compared the raw value directly instead of
   calling `resolve_position`, so those tests were dropped without warning. The
   function now resolves the position and reports any position it still cannot
   place.

2. **A fresh database and a migrated one would have had different column
   orders.** The new columns were added mid-table in `CREATE TABLE` but
   `ALTER TABLE` appends at the end. They are now declared last so both paths
   produce an identical schema.

## Still open

- **20,049 rows in `raw_tests` have a blank position** and have always been
  skipped by classification. This predates the switch and is unchanged by it,
  but it is now reported rather than silent. Whether these are legitimately
  excluded needs a look.
- The **gold / purple / white tier still uses RSI-modified.** Ranking athletes on
  a different quality is a strength-and-conditioning judgment, not a measurement
  one, so it was deliberately left alone.

## Reproducing the calibration

```
python -m src.research.measurement          # CMJ typical error table
```

Threshold constants live in `src/classify/engine.py`
(`PEAK_POWER_SINGLE_TEST_THRESHOLDS`, `PEAK_POWER_CONSECUTIVE_THRESHOLDS`).

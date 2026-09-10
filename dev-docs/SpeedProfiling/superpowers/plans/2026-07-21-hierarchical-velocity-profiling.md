# Hierarchical Velocity Profiling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estimate every athlete's velocity profile jointly with a nonlinear mixed-effects model so short-run athletes (linemen, tight ends) borrow structure from long-run ones, and prove with held-out cross-validation whether that actually predicts better than v1's independent per-athlete fits.

**Architecture:** Two new pure-function files sit alongside the existing `R/functions.R`: `R/crossval.R` (a model-agnostic evaluation harness that takes a fitting function as an argument) and `R/fit_hierarchical.R` (an `nlme` model with a defined convergence-fallback ladder). A third, `R/synthetic.R`, generates synthetic athlete *populations* with known ground truth so the central claim is testable without player data. v1's `fit_velocity_profile()` stays as the shipped baseline and is reported side by side.

**Tech Stack:** R 4.5.3, `nlme` 3.1.168 (an R recommended package — already installed and already in `renv.lock`), `stats::nls`, dplyr/tibble/purrr, testthat, renv.

## Global Constraints

- **Zero new dependencies.** `nlme` is already in `renv.lock`. Do not add `lme4`, `brms`, `rstan`, or any package requiring a compiler toolchain. If you believe a new package is needed, stop and raise it rather than adding it.
- **Every constant lives in `R/config.R`.** Per `AGENTS.md`: "every analysis constant …; scripts contain none inline." This applies to the new files too. `tests/testthat/test-config.R` enforces part of this and will fail if violated.
- **FERPA:** repo private; `data/` and `output/` stay gitignored; never commit real player data, names, or jersey numbers. All test fixtures are synthetic.
- **v1's output must stay reproducible.** `fit_velocity_profile()` keeps its current behaviour under default arguments. The only permitted change is an *additive, defaulted* parameter (Task 1, Step 6) that preserves existing results exactly.
- **Pure functions stay pure.** `R/crossval.R`, `R/fit_hierarchical.R`, and `R/synthetic.R` must contain no API calls and no file I/O — same rule `R/functions.R` follows, which is what makes them testable.
- **Test suite baseline is 184 passing, 0 failing.** Run `Rscript tests/run-tests.R` from the project root. It must never go red at a commit boundary.
- **R on this machine:** invoke as `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe"` from Git Bash, or `Rscript` from PowerShell.

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `R/config.R` | modify | All new constants (CV, nlme control, synthetic-population defaults) |
| `R/crossval.R` | create | Fold construction and out-of-sample scoring. Knows nothing about any model. |
| `R/fit_hierarchical.R` | create | The `nlme` model, the fallback ladder, athlete-level coefficient extraction |
| `R/synthetic.R` | create | Synthetic athlete populations with known truth; public demo data |
| `R/functions.R` | modify | One additive `ci` parameter on `fit_velocity_profile()` (Task 1) |
| `R/03_velocity_profiling.R` | modify | Side-by-side reporting; CV decides which fit leads (Task 4) |
| `tests/testthat/helper-setup.R` | modify | Source the three new files |
| `tests/testthat/test-crossval.R` | create | Harness behaviour, including that it scores a wrong model worse |
| `tests/testthat/test-synthetic-population.R` | create | Generator structure + that short runs genuinely defeat independent NLS |
| `tests/testthat/test-fit-hierarchical.R` | create | Parameter recovery vs independent NLS; every ladder rung |

`generate_synthetic_sprint()` stays in `R/functions.R`. It is depended on by existing tests and moving it would churn them for no gain; `R/synthetic.R` calls it.

---

### Task 1: Cross-validation harness and v1 baseline

Builds the yardstick before the thing it measures. Ends with a recorded out-of-sample RMSE for v1's current fit.

**Files:**
- Create: `R/crossval.R`
- Create: `tests/testthat/test-crossval.R`
- Modify: `R/config.R` (append a CV constants block)
- Modify: `R/functions.R` (`fit_velocity_profile()` gains a defaulted `ci` parameter)
- Modify: `tests/testthat/helper-setup.R` (source `R/crossval.R`)

**Interfaces:**
- Consumes: `interpolate_sprint()`, `pool_qualifying_sprints()`, `fit_velocity_profile()`, `ATHLETE_COLS`, `MPH_PER_MS` — all from `R/functions.R` / `R/config.R`.
- Produces, relied on by Tasks 3 and 4:
  - `make_cv_folds(sprint_index, k, min_sprints, seed)` → `tibble(athlete_id, sprint_id, fold)`
  - `cv_evaluate(interp_all, fit_fn, folds)` → `list(per_sprint = tibble(athlete_id, sprint_id, fold, rmse_mph, n_points), summary = tibble(mean_rmse_mph, median_rmse_mph, n_sprints, n_athletes))`
  - **The `fit_fn` contract**, which Task 3's model must satisfy: a function taking one argument, a tibble of interpolated training rows (columns `athlete_id`, `position`, `sprint_id`, `dist_yd`, `V_ms`), and returning `tibble(athlete_id, VHmax_ms, K_yd)` with exactly one row per athlete it could fit.
  - `fit_fn_nls(train_interp)` — the v1 baseline adapter, conforming to that contract.

- [ ] **Step 1: Add CV constants to `R/config.R`**

Append at the end of the file:

```r
# -----------------------------------------------------------------------------
# Cross-validation (crossval.R)
# Held-out scoring is how this project decides whether a modelling change helps.
# K-fold rather than leave-one-out because a refit here is a whole-population
# mixed model, not one cheap NLS curve: 246 sprints would mean 246 refits.
# -----------------------------------------------------------------------------
CV_N_FOLDS     <- 5    # folds at the sprint level
CV_MIN_SPRINTS <- 2    # an athlete needs this many sprints to be scoreable
CV_SEED        <- 20260721  # fold assignment is deterministic across runs
```

- [ ] **Step 2: Write the failing test for fold construction**

Create `tests/testthat/test-crossval.R`:

```r
make_sprint_index <- function() {
  tibble::tibble(
    athlete_id = c(rep("A", 4), rep("B", 3), "C"),
    sprint_id  = c(paste0("A", 1:4), paste0("B", 1:3), "C1")
  )
}

test_that("make_cv_folds covers every scoreable sprint exactly once", {
  folds <- make_cv_folds(make_sprint_index(), k = 3, min_sprints = 2, seed = 1)

  # C has one sprint, so it is not scoreable and must be absent
  expect_false("C" %in% folds$athlete_id)
  expect_equal(nrow(folds), 7)
  expect_equal(sort(folds$sprint_id), sort(c(paste0("A", 1:4), paste0("B", 1:3))))
  expect_true(all(folds$fold %in% 1:3))
})

test_that("make_cv_folds never holds out all of an athlete's sprints at once", {
  folds <- make_cv_folds(make_sprint_index(), k = 3, min_sprints = 2, seed = 1)

  per_fold <- folds %>%
    dplyr::group_by(athlete_id) %>%
    dplyr::summarise(n_folds = dplyr::n_distinct(fold),
                     n_sprints = dplyr::n(), .groups = "drop")
  # every athlete's sprints are spread over more than one fold
  expect_true(all(per_fold$n_folds > 1))
})

test_that("make_cv_folds is deterministic for a given seed", {
  a <- make_cv_folds(make_sprint_index(), k = 3, min_sprints = 2, seed = 42)
  b <- make_cv_folds(make_sprint_index(), k = 3, min_sprints = 2, seed = 42)
  expect_equal(a, b)
})
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" -e 'testthat::test_file("tests/testthat/test-crossval.R")'`
Expected: FAIL, `could not find function "make_cv_folds"`.

- [ ] **Step 4: Implement `make_cv_folds` in `R/crossval.R`**

Create `R/crossval.R`:

```r
# =============================================================================
# crossval.R
# Held-out evaluation for velocity-profile fitting. Deliberately knows nothing
# about any particular model: cv_evaluate() takes the fitting function as an
# argument, so competing methods are scored on identical folds with identical
# arithmetic rather than by careful bookkeeping.
#
# Source order:
#   source(here::here("R", "config.R"))
#   source(here::here("R", "functions.R"))
#   source(here::here("R", "crossval.R"))
# =============================================================================

# -----------------------------------------------------------------------------
# Assign sprints to cross-validation folds
#
# Folds are struck within each athlete, so an athlete's sprints spread across
# folds and no athlete ever loses all of theirs at once — otherwise a fold
# would ask the model to predict an athlete it never saw, which measures
# something else entirely.
#
# sprint_index: tibble with athlete_id and sprint_id, one row per sprint.
# Returns tibble(athlete_id, sprint_id, fold); athletes with fewer than
# min_sprints sprints are dropped (they cannot be scored out-of-sample).
# -----------------------------------------------------------------------------
make_cv_folds <- function(sprint_index,
                          k           = CV_N_FOLDS,
                          min_sprints = CV_MIN_SPRINTS,
                          seed        = CV_SEED) {
  idx <- sprint_index %>%
    distinct(athlete_id, sprint_id) %>%
    group_by(athlete_id) %>%
    filter(n() >= min_sprints) %>%
    ungroup()

  if (nrow(idx) == 0) {
    return(tibble(athlete_id = character(), sprint_id = character(),
                  fold = integer()))
  }

  set.seed(seed)

  idx %>%
    arrange(athlete_id, sprint_id) %>%
    group_by(athlete_id) %>%
    # Shuffle within the athlete, then deal fold labels round-robin. Dealing
    # rather than drawing guarantees an athlete's sprints land in as many
    # distinct folds as they have sprints (capped at k), so no athlete is ever
    # wholly held out.
    mutate(fold = ((sample.int(n()) - 1L) %% min(k, n())) + 1L) %>%
    ungroup()
}
```

`set.seed` mutates global RNG state. That is accepted deliberately: fold assignment must be reproducible across runs, and callers of a CV harness expect determinism more than they expect RNG hygiene.

- [ ] **Step 5: Run the fold tests to verify they pass**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" -e 'testthat::test_file("tests/testthat/test-crossval.R")'`
Expected: PASS, 3 tests.

If "never holds out all sprints at once" fails for an athlete with exactly 2 sprints and k=3, adjust the `mutate` so fold labels come from `((seq_len(n()) - 1L) %% min(k, n())) + 1L` after shuffling row order — the requirement is that an athlete's sprints land in at least two distinct folds.

- [ ] **Step 6: Add a defaulted `ci` parameter to `fit_velocity_profile()`**

Cross-validation refits many times and never uses confidence intervals, but v1's fit spends 1000 bootstrap draws per athlete computing them. Skipping that in CV is the difference between minutes and hours.

In `R/functions.R`, change the signature (around line 203):

```r
fit_velocity_profile <- function(athlete_interp_df,
                                 n_boot       = N_BOOTSTRAP,
                                 yard_grid    = INTERP_YARDS,
                                 min_points   = MIN_FIT_POINTS,
                                 athlete_cols = ATHLETE_COLS,
                                 ci           = TRUE) {
```

Replace the bootstrap block (currently `nls_boot <- tryCatch(...)` through the `else` branch that calls `confint`) with:

```r
  # Confidence intervals are skipped when ci = FALSE: cross-validation refits
  # this many times and never reads them, and the bootstrap dominates runtime.
  if (!ci) {
    VHmax_lo <- NA_real_; VHmax_hi <- NA_real_
    K_lo     <- NA_real_; K_hi     <- NA_real_
  } else {
    nls_boot <- tryCatch(
      nlsBoot(nls_fit, niter = n_boot),
      error = function(e) {
        warning("Bootstrap failed for athlete ", df$athlete_id[1], ": ", conditionMessage(e))
        NULL
      }
    )
    if (!is.null(nls_boot)) {
      probs    <- c((1 - BOOT_CI_LEVEL) / 2, 1 - (1 - BOOT_CI_LEVEL) / 2)
      boot_par <- nls_boot$coefboot
      VHmax_lo <- quantile(boot_par[, "VHmax"], probs[1], names = FALSE)
      VHmax_hi <- quantile(boot_par[, "VHmax"], probs[2], names = FALSE)
      K_lo     <- quantile(boot_par[, "K"],     probs[1], names = FALSE)
      K_hi     <- quantile(boot_par[, "K"],     probs[2], names = FALSE)
    } else {
      ci_mat   <- suppressMessages(confint(nls_fit, level = BOOT_CI_LEVEL))
      VHmax_lo <- ci_mat["VHmax", 1]; VHmax_hi <- ci_mat["VHmax", 2]
      K_lo     <- ci_mat["K",     1]; K_hi     <- ci_mat["K",     2]
    }
  }
```

Note the local `ci` matrix was renamed to `ci_mat` to avoid shadowing the new parameter.

- [ ] **Step 7: Add a test that the `ci` parameter changes nothing else**

Append to `tests/testthat/test-crossval.R`:

```r
test_that("fit_velocity_profile(ci = FALSE) matches ci = TRUE on point estimates", {
  trace  <- generate_synthetic_sprint(TRUE_VHMAX_MS, TRUE_K_YD, n_seconds = 8)
  interp <- interpolate_sprint(as_sprint_df(trace))

  with_ci    <- fit_velocity_profile(interp, n_boot = 50, ci = TRUE)
  without_ci <- fit_velocity_profile(interp, ci = FALSE)

  expect_equal(with_ci$summary$VHmax_ms, without_ci$summary$VHmax_ms, tolerance = 1e-8)
  expect_equal(with_ci$summary$K_yd,     without_ci$summary$K_yd,     tolerance = 1e-8)
  expect_true(is.na(without_ci$summary$VHmax_lo_mph))
  expect_false(is.na(with_ci$summary$VHmax_lo_mph))
})
```

- [ ] **Step 8: Run the full suite**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" tests/run-tests.R`
Expected: PASS, 188 or more, 0 failures. If any pre-existing test fails, the `ci` refactor broke v1 behaviour — revert Step 6 and redo it.

- [ ] **Step 9: Write the failing test for `cv_evaluate`**

Append to `tests/testthat/test-crossval.R`:

```r
# Two synthetic athletes, three sprints each, known parameters.
make_cv_interp <- function() {
  mk <- function(aid, k_yd, sid, secs) {
    tr <- generate_synthetic_sprint(8, k_yd, n_seconds = secs,
                                    athlete_id = aid, position = "SYN",
                                    play_id = sid)
    interpolate_sprint(as_sprint_df(tr, sprint_id = sid))
  }
  dplyr::bind_rows(
    mk("A", 4, "A1", 8), mk("A", 4, "A2", 8), mk("A", 4, "A3", 8),
    mk("B", 6, "B1", 8), mk("B", 6, "B2", 8), mk("B", 6, "B3", 8)
  )
}

test_that("cv_evaluate scores every held-out sprint and returns a summary", {
  interp <- make_cv_interp()
  folds  <- make_cv_folds(dplyr::distinct(interp, athlete_id, sprint_id),
                          k = 3, min_sprints = 2, seed = 7)

  res <- cv_evaluate(interp, fit_fn_nls, folds)

  expect_equal(nrow(res$per_sprint), 6)
  expect_true(all(res$per_sprint$rmse_mph >= 0))
  expect_equal(res$summary$n_athletes, 2)
  expect_equal(res$summary$n_sprints, 6)
})

test_that("cv_evaluate scores a deliberately wrong model worse than the real one", {
  interp <- make_cv_interp()
  folds  <- make_cv_folds(dplyr::distinct(interp, athlete_id, sprint_id),
                          k = 3, min_sprints = 2, seed = 7)

  # A model that claims everyone tops out at walking pace with instant accel
  fit_fn_wrong <- function(train_interp) {
    train_interp %>%
      dplyr::distinct(athlete_id) %>%
      dplyr::mutate(VHmax_ms = 1, K_yd = 0.5)
  }

  good <- cv_evaluate(interp, fit_fn_nls,   folds)$summary$mean_rmse_mph
  bad  <- cv_evaluate(interp, fit_fn_wrong, folds)$summary$mean_rmse_mph

  expect_gt(bad, good)
})
```

- [ ] **Step 10: Run to verify it fails**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" -e 'testthat::test_file("tests/testthat/test-crossval.R")'`
Expected: FAIL, `could not find function "cv_evaluate"`.

- [ ] **Step 11: Implement `cv_evaluate` and `fit_fn_nls`**

Append to `R/crossval.R`:

```r
# -----------------------------------------------------------------------------
# Score a fitting function by held-out prediction error
#
# For each fold: fit on every sprint NOT in the fold, then for each held-out
# sprint predict velocity at that sprint's own observed distances and score
# RMSE in mph. The fitting function is an argument, so any model that satisfies
# the contract below is scored identically.
#
# fit_fn contract: function(train_interp) -> tibble(athlete_id, VHmax_ms, K_yd),
#   one row per athlete it managed to fit. Athletes it omits are skipped in
#   scoring and counted in the returned summary.
#
# interp_all: interpolated rows for every sprint (athlete_id, sprint_id,
#   dist_yd, V_ms, position).
# Returns list(per_sprint = ..., summary = ...).
# -----------------------------------------------------------------------------
cv_evaluate <- function(interp_all, fit_fn, folds) {
  scored <- list()

  for (f in sort(unique(folds$fold))) {
    held_ids  <- folds$sprint_id[folds$fold == f]
    train     <- interp_all %>% filter(!sprint_id %in% held_ids)
    test      <- interp_all %>% filter(sprint_id %in% held_ids)

    params <- fit_fn(train)
    if (is.null(params) || nrow(params) == 0) next

    joined <- test %>%
      inner_join(params, by = "athlete_id") %>%
      filter(!is.na(VHmax_ms), !is.na(K_yd), K_yd > 0)

    if (nrow(joined) == 0) next

    scored[[length(scored) + 1]] <- joined %>%
      mutate(V_ms_pred = VHmax_ms * (1 - exp(-dist_yd / K_yd))) %>%
      group_by(athlete_id, sprint_id) %>%
      summarise(
        rmse_mph = sqrt(mean((V_ms - V_ms_pred)^2, na.rm = TRUE)) * MPH_PER_MS,
        n_points = n(),
        .groups  = "drop"
      ) %>%
      mutate(fold = f)
  }

  per_sprint <- if (length(scored) == 0) {
    tibble(athlete_id = character(), sprint_id = character(),
           rmse_mph = numeric(), n_points = integer(), fold = integer())
  } else {
    bind_rows(scored)
  }

  summary_row <- tibble(
    mean_rmse_mph   = if (nrow(per_sprint)) mean(per_sprint$rmse_mph)   else NA_real_,
    median_rmse_mph = if (nrow(per_sprint)) median(per_sprint$rmse_mph) else NA_real_,
    n_sprints       = nrow(per_sprint),
    n_athletes      = n_distinct(per_sprint$athlete_id),
    n_sprints_asked = nrow(distinct(folds, sprint_id))
  )

  list(per_sprint = per_sprint, summary = summary_row)
}

# -----------------------------------------------------------------------------
# v1 baseline adapter: independent per-athlete NLS, one fit per athlete over
# whatever training sprints that athlete has. CIs are skipped (ci = FALSE) —
# cross-validation never reads them and the bootstrap dominates runtime.
# -----------------------------------------------------------------------------
fit_fn_nls <- function(train_interp) {
  train_interp %>%
    group_split(athlete_id) %>%
    map(function(df) {
      res <- tryCatch(fit_velocity_profile(df, ci = FALSE),
                      error = function(e) NULL, warning = function(w) NULL)
      if (is.null(res)) return(NULL)
      tibble(athlete_id = df$athlete_id[1],
             VHmax_ms   = res$summary$VHmax_ms,
             K_yd       = res$summary$K_yd)
    }) %>%
    compact() %>%
    bind_rows()
}
```

- [ ] **Step 12: Source the new file in the test helper**

In `tests/testthat/helper-setup.R`, after the `source(here::here("R", "functions.R"))` line, add:

```r
source(here::here("R", "crossval.R"))
```

- [ ] **Step 13: Run the full suite**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" tests/run-tests.R`
Expected: PASS, 0 failures.

- [ ] **Step 14: Record the v1 baseline on real data**

Create a scratch script (do **not** commit it; `data/` and `output/` are gitignored) and run it:

```r
suppressPackageStartupMessages({library(dplyr);library(tibble);library(purrr);library(nlstools)})
source(here::here("R","config.R")); source(here::here("R","functions.R"))
source(here::here("R","crossval.R"))
tagged <- readRDS(file.path(DATA_DIR,"data_tagged.rds"))
part   <- readRDS(file.path(DATA_DIR,"participation.rds"))
sprints <- pool_qualifying_sprints(tagged, part)
interp  <- sprints %>% group_split(sprint_id) %>% map(interpolate_sprint) %>%
  compact() %>% bind_rows()
folds <- make_cv_folds(distinct(interp, athlete_id, sprint_id))
res   <- cv_evaluate(interp, fit_fn_nls, folds)
print(res$summary)
```

Record the printed `mean_rmse_mph` and `median_rmse_mph` in the Task 4 comparison table and in the ticket. This is the number the hierarchical fit has to beat.

- [ ] **Step 15: Commit**

```bash
git add R/crossval.R R/config.R R/functions.R tests/testthat/test-crossval.R tests/testthat/helper-setup.R
git commit -m "feat: held-out cross-validation harness with v1 NLS baseline"
```

---

### Task 2: Synthetic population generator

Builds ground truth for the central claim. Ends with a fixture that provably exhibits the problem the milestone exists to solve.

**Files:**
- Create: `R/synthetic.R`
- Create: `tests/testthat/test-synthetic-population.R`
- Modify: `R/config.R` (population defaults)
- Modify: `tests/testthat/helper-setup.R` (source `R/synthetic.R`)

**Interfaces:**
- Consumes: `generate_synthetic_sprint()`, `interpolate_sprint()`, `MPH_PER_MS`, `M_TO_YD` from `R/functions.R` / `R/config.R`; `fit_fn_nls()` from Task 1.
- Produces, relied on by Task 3:
  - `generate_synthetic_population(spec, n_sprints_per_athlete, noise_sd_ms, seed)` → `list(truth = tibble(athlete_id, position, VHmax_ms_true, K_yd_true), sprints = tibble of 10 Hz rows with sprint_id, interp = tibble of interpolated rows)`
  - `SYN_POP_DEFAULT` — the default population spec tibble.

- [ ] **Step 1: Add population defaults to `R/config.R`**

Append:

```r
# -----------------------------------------------------------------------------
# Synthetic population defaults (synthetic.R)
# Mirrors the real roster's shape: a few long-run skill athletes and a larger
# set of short-run big men, which is the regime where independent per-athlete
# fitting fails. sprint_seconds drives run length, which drives whether K is
# identifiable at all.
# -----------------------------------------------------------------------------
SYN_POP_DEFAULT <- tibble::tribble(
  ~position, ~n_athletes, ~K_mean_yd, ~K_sd_yd, ~VHmax_mean_ms, ~VHmax_sd_ms, ~sprint_seconds,
  "SKILL",             6,          5,      0.8,            9.0,          0.6,             8,
  "MID",               4,          6,      0.8,            8.0,          0.5,             5,
  "BIG",               6,          7,      1.0,            7.0,          0.5,             3
)
SYN_POP_NOISE_SD_MS <- 0.15   # measurement noise on synthetic velocity
SYN_POP_SEED        <- 20260721
```

- [ ] **Step 2: Write the failing test**

Create `tests/testthat/test-synthetic-population.R`:

```r
test_that("generate_synthetic_population returns truth, sprints, and interp that agree", {
  pop <- generate_synthetic_population(n_sprints_per_athlete = 3, seed = 1)

  expect_equal(nrow(pop$truth), 16)                       # 6 + 4 + 6
  expect_setequal(unique(pop$truth$position), c("SKILL", "MID", "BIG"))
  expect_equal(dplyr::n_distinct(pop$sprints$sprint_id), 16 * 3)
  expect_setequal(unique(pop$interp$athlete_id), pop$truth$athlete_id)
  expect_true(all(pop$truth$K_yd_true > 0))
})

test_that("BIG athletes produce genuinely shorter runs than SKILL athletes", {
  pop <- generate_synthetic_population(seed = 1)

  reach <- pop$interp %>%
    dplyr::left_join(dplyr::select(pop$truth, athlete_id, position), by = "athlete_id") %>%
    dplyr::group_by(position) %>%
    dplyr::summarise(max_dist = max(dist_yd), .groups = "drop")

  big   <- reach$max_dist[reach$position == "BIG"]
  skill <- reach$max_dist[reach$position == "SKILL"]
  expect_lt(big, skill)
  expect_lt(big, 20)     # short enough that K is poorly identified
})

test_that("independent NLS recovers K poorly for the short-run group", {
  # This is the premise of the whole milestone. If it does not hold on data
  # built from the model itself, the fixture is wrong.
  pop <- generate_synthetic_population(seed = 1)
  est <- fit_fn_nls(pop$interp)

  cmp <- est %>%
    dplyr::inner_join(pop$truth, by = "athlete_id") %>%
    dplyr::mutate(k_abs_err = abs(K_yd - K_yd_true)) %>%
    dplyr::group_by(position) %>%
    dplyr::summarise(mean_k_err = mean(k_abs_err), .groups = "drop")

  big   <- cmp$mean_k_err[cmp$position == "BIG"]
  skill <- cmp$mean_k_err[cmp$position == "SKILL"]
  expect_gt(big, skill)
})
```

- [ ] **Step 3: Run to verify it fails**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" -e 'testthat::test_file("tests/testthat/test-synthetic-population.R")'`
Expected: FAIL, `could not find function "generate_synthetic_population"`.

- [ ] **Step 4: Implement `R/synthetic.R`**

```r
# =============================================================================
# synthetic.R
# Synthetic athlete populations with known ground truth. Every parameter is
# chosen, not measured, so tests can assert that an estimator recovers it.
# FERPA-safe by construction — no player data is involved anywhere — which is
# what makes these traces usable as public demo data.
#
# Source order:
#   source(here::here("R", "config.R"))
#   source(here::here("R", "functions.R"))
#   source(here::here("R", "synthetic.R"))
# =============================================================================

# -----------------------------------------------------------------------------
# Build a population of synthetic athletes and their sprints
#
# Per-athlete VHmax and K are drawn from their position group's mean and sd, so
# the data genuinely has the nested structure a hierarchical model assumes:
# athletes vary within positions, positions vary around a global mean.
# sprint_seconds controls run length per group, which is the lever that makes
# K identifiable (long runs) or not (short runs).
#
# spec: tibble with position, n_athletes, K_mean_yd, K_sd_yd, VHmax_mean_ms,
#   VHmax_sd_ms, sprint_seconds.
# Returns list(truth, sprints, interp).
# -----------------------------------------------------------------------------
generate_synthetic_population <- function(spec                  = SYN_POP_DEFAULT,
                                          n_sprints_per_athlete = 3,
                                          noise_sd_ms           = SYN_POP_NOISE_SD_MS,
                                          seed                  = SYN_POP_SEED) {
  set.seed(seed)

  truth <- spec %>%
    rowwise() %>%
    do({
      row <- .
      tibble(
        position       = row$position,
        athlete_id     = sprintf("%s-%02d", row$position, seq_len(row$n_athletes)),
        VHmax_ms_true  = rnorm(row$n_athletes, row$VHmax_mean_ms, row$VHmax_sd_ms),
        K_yd_true      = pmax(rnorm(row$n_athletes, row$K_mean_yd, row$K_sd_yd), 1),
        sprint_seconds = row$sprint_seconds
      )
    }) %>%
    ungroup()

  sprints <- truth %>%
    rowwise() %>%
    do({
      a <- .
      map_dfr(seq_len(n_sprints_per_athlete), function(j) {
        sid <- sprintf("%s-S%d", a$athlete_id, j)
        generate_synthetic_sprint(
          VHmax_ms      = a$VHmax_ms_true,
          K_yd          = a$K_yd_true,
          n_seconds     = a$sprint_seconds,
          noise_sd_ms   = noise_sd_ms,
          athlete_id    = a$athlete_id,
          athlete_name  = a$athlete_id,
          position      = a$position,
          jersey_number = 0,
          play_id       = sid
        ) %>% mutate(sprint_id = sid)
      })
    }) %>%
    ungroup()

  interp <- sprints %>%
    group_split(sprint_id) %>%
    map(function(df) {
      d <- df %>% mutate(sprint_dist_m  = O - O[1],
                         sprint_dist_yd = sprint_dist_m * M_TO_YD)
      interpolate_sprint(d)
    }) %>%
    compact() %>%
    bind_rows()

  list(
    truth   = truth %>% select(athlete_id, position, VHmax_ms_true, K_yd_true),
    sprints = sprints,
    interp  = interp
  )
}
```

- [ ] **Step 5: Source it in the test helper**

In `tests/testthat/helper-setup.R`, after the `crossval.R` line, add:

```r
source(here::here("R", "synthetic.R"))
```

- [ ] **Step 6: Run the tests**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" -e 'testthat::test_file("tests/testthat/test-synthetic-population.R")'`
Expected: PASS, 3 tests.

If the third test fails because independent NLS recovers BIG athletes' K *well*, the fixture is not short enough — reduce `sprint_seconds` for `BIG` in `SYN_POP_DEFAULT` to 2.5 and re-run. Do not weaken the assertion; the point is to build a fixture that exhibits the real problem.

- [ ] **Step 7: Run the full suite and commit**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" tests/run-tests.R`
Expected: PASS, 0 failures.

```bash
git add R/synthetic.R R/config.R tests/testthat/test-synthetic-population.R tests/testthat/helper-setup.R
git commit -m "feat: synthetic athlete population generator with known ground truth"
```

---

### Task 3: Hierarchical fit and fallback ladder

The model itself. Ends with a fit that provably beats independent NLS on short runs, and degrades visibly rather than silently.

**Files:**
- Create: `R/fit_hierarchical.R`
- Create: `tests/testthat/test-fit-hierarchical.R`
- Modify: `R/config.R` (nlme control constants)
- Modify: `tests/testthat/helper-setup.R` (source `R/fit_hierarchical.R`)

**Interfaces:**
- Consumes: `generate_synthetic_population()` (Task 2), `fit_fn_nls()` and the `fit_fn` contract (Task 1), `fit_velocity_profile()`, `ATHLETE_COLS`, `MPH_PER_MS`.
- Produces, relied on by Task 4:
  - `fit_velocity_profiles_hier(interp_all, athlete_cols)` → `tibble(athlete_id, VHmax_ms, VHmax_mph, VHmax_lo_mph, VHmax_hi_mph, K_yd, K_lo_yd, K_hi_yd, K3_yd, fit_method)` — one row per athlete. `fit_method` is one of `"hier_position"`, `"hier_athlete"`, `"hier_athlete_only"`, `"nls_fallback"`.
  - `fit_fn_hier(train_interp)` → `tibble(athlete_id, VHmax_ms, K_yd)`, satisfying Task 1's `fit_fn` contract so `cv_evaluate` can score it.

- [ ] **Step 1: Add nlme control constants to `R/config.R`**

Append:

```r
# -----------------------------------------------------------------------------
# Hierarchical fit (fit_hierarchical.R)
# Nonlinear mixed models on sparse groups routinely fail to converge, so the
# ladder in fit_velocity_profiles_hier() is an expected path, not an error path.
# -----------------------------------------------------------------------------
HIER_MAX_ITER     <- 100   # nlme outer iterations
HIER_MS_MAX_ITER  <- 200   # inner optimiser iterations
HIER_TOL          <- 1e-5
HIER_CI_LEVEL     <- BOOT_CI_LEVEL   # match v1's interval level exactly
```

- [ ] **Step 2: Write the failing test for parameter recovery**

Create `tests/testthat/test-fit-hierarchical.R`:

```r
test_that("hierarchical fitting recovers K better than independent NLS for short runs", {
  # The milestone's central claim, tested against known truth.
  pop <- generate_synthetic_population(seed = 1)

  nls_est  <- fit_fn_nls(pop$interp)
  hier_est <- fit_fn_hier(pop$interp)

  err <- function(est) {
    est %>%
      dplyr::inner_join(pop$truth, by = "athlete_id") %>%
      dplyr::filter(position == "BIG") %>%
      dplyr::summarise(m = mean(abs(K_yd - K_yd_true))) %>%
      dplyr::pull(m)
  }

  expect_lt(err(hier_est), err(nls_est))
})

test_that("fit_velocity_profiles_hier returns one row per athlete with interval columns", {
  pop <- generate_synthetic_population(seed = 2)
  out <- fit_velocity_profiles_hier(pop$interp)

  expect_equal(nrow(out), dplyr::n_distinct(pop$interp$athlete_id))
  expect_true(all(c("VHmax_ms", "VHmax_mph", "VHmax_lo_mph", "VHmax_hi_mph",
                    "K_yd", "K_lo_yd", "K_hi_yd", "K3_yd", "fit_method")
                  %in% names(out)))
  expect_true(all(out$fit_method %in% c("hier_position", "hier_athlete",
                                        "hier_athlete_only", "nls_fallback")))
})

test_that("the ladder drops the position rung when position does not vary", {
  # One position group: there is nothing for the position level to explain, so
  # rung 1 is skipped and rung 2 must win.
  one_pos <- SYN_POP_DEFAULT[SYN_POP_DEFAULT$position == "SKILL", ]
  pop <- generate_synthetic_population(spec = one_pos, seed = 5)

  out <- fit_velocity_profiles_hier(pop$interp)
  expect_true(all(out$fit_method %in% c("hier_athlete", "hier_athlete_only",
                                        "nls_fallback")))
  expect_false(any(out$fit_method == "hier_position"))
})

test_that("the ladder drops the sprint rung when each athlete has one sprint", {
  # With one sprint per athlete the sprint level is degenerate (each group has
  # a single observation set), so the athlete-only rung is the deepest that can
  # carry information.
  pop <- generate_synthetic_population(n_sprints_per_athlete = 1, seed = 6)

  out <- fit_velocity_profiles_hier(pop$interp)
  expect_equal(nrow(out), dplyr::n_distinct(pop$interp$athlete_id))
  expect_true(all(out$fit_method %in% c("hier_position", "hier_athlete",
                                        "hier_athlete_only", "nls_fallback")))
})

test_that("the ladder falls back to NLS when the mixed model cannot be fit", {
  # One athlete, one sprint: no grouping structure exists to pool over.
  tr <- generate_synthetic_sprint(8, 4, n_seconds = 8, athlete_id = "SOLO",
                                  position = "SYN", play_id = "SOLO-S1")
  interp <- interpolate_sprint(as_sprint_df(tr, sprint_id = "SOLO-S1"))

  out <- fit_velocity_profiles_hier(interp)

  expect_equal(nrow(out), 1)
  expect_equal(out$fit_method, "nls_fallback")
  expect_true(is.finite(out$K_yd))
})
```

- [ ] **Step 3: Run to verify it fails**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" -e 'testthat::test_file("tests/testthat/test-fit-hierarchical.R")'`
Expected: FAIL, `could not find function "fit_fn_hier"`.

- [ ] **Step 4: Implement `R/fit_hierarchical.R`**

```r
# =============================================================================
# fit_hierarchical.R
# Nonlinear mixed-effects velocity profiling. Athletes with short runs borrow
# structure from athletes with long ones, which is the only way K becomes
# identifiable for linemen: their own sprints do not contain the information.
#
# Model: V(d) = VHmax * (1 - exp(-d / K)), with VHmax and K varying by
# sprint nested in athlete nested in position. A position group of one athlete
# shrinks essentially to the global mean by construction; a group of seven
# keeps more of its own signal. Shrinkage is a property of the model, not a
# tuning decision.
#
# Source order:
#   source(here::here("R", "config.R"))
#   source(here::here("R", "functions.R"))
#   source(here::here("R", "fit_hierarchical.R"))
# =============================================================================

# The ladder, most-pooled first. Each entry is a random-effects formula tried
# in order; the first that converges wins and its label is recorded.
HIER_LADDER <- list(
  list(method = "hier_position",     random = ~ VHmax + K ~ 1 | position/athlete_id/sprint_id),
  list(method = "hier_athlete",      random = ~ VHmax + K ~ 1 | athlete_id/sprint_id),
  list(method = "hier_athlete_only", random = ~ VHmax + K ~ 1 | athlete_id)
)

# -----------------------------------------------------------------------------
# Try one rung of the ladder. Returns the fitted nlme object or NULL.
# -----------------------------------------------------------------------------
hier_try_fit <- function(df, random_formula, start_vals) {
  tryCatch(
    suppressWarnings(nlme::nlme(
      model   = V_ms ~ VHmax * (1 - exp(-dist_yd / K)),
      data    = df,
      fixed   = VHmax + K ~ 1,
      random  = random_formula[[2]],
      start   = start_vals,
      control = nlme::nlmeControl(maxIter   = HIER_MAX_ITER,
                                  msMaxIter = HIER_MS_MAX_ITER,
                                  tolerance = HIER_TOL,
                                  returnObject = FALSE)
    )),
    error = function(e) NULL
  )
}

# -----------------------------------------------------------------------------
# Pull athlete-level coefficients out of a fitted nlme object.
#
# coef() returns one row per group at the requested nesting level, with row
# names carrying the group path. The athlete level differs per ladder rung, so
# the caller passes which level to read.
# -----------------------------------------------------------------------------
hier_athlete_coefs <- function(fit, level) {
  cf <- nlme::coef(fit, level = level)
  ids <- rownames(cf)
  # Nested row names look like "SKILL/SKILL-01"; the athlete id is the last part
  tibble(
    athlete_id = sub(".*/", "", ids),
    VHmax_ms   = cf[["VHmax"]],
    K_yd       = cf[["K"]]
  )
}

# -----------------------------------------------------------------------------
# Fit every athlete's profile jointly, walking the ladder until something
# converges, and falling back to v1's independent NLS for whatever is left.
#
# interp_all: interpolated rows for every sprint (athlete_id, position,
#   sprint_id, dist_yd, V_ms).
# Returns one row per athlete with point estimates, intervals, and the
# fit_method that produced them.
# -----------------------------------------------------------------------------
fit_velocity_profiles_hier <- function(interp_all, athlete_cols = ATHLETE_COLS) {
  df <- interp_all %>%
    filter(!is.na(V_ms), V_ms > 0, !is.na(dist_yd)) %>%
    mutate(across(any_of(c("position", "athlete_id", "sprint_id")), as.factor))

  start_vals <- c(VHmax = max(df$V_ms, na.rm = TRUE) * VHMAX_START_FACTOR,
                  K     = K_START_YD)

  fit <- NULL; method <- NA_character_; level <- NA_integer_
  for (i in seq_along(HIER_LADDER)) {
    rung <- HIER_LADDER[[i]]
    # A rung is only attempted when its grouping actually varies
    if (rung$method == "hier_position" && n_distinct(df$position) < 2) next
    if (n_distinct(df$athlete_id) < 2) next

    candidate <- hier_try_fit(df, rung$random, start_vals)
    if (!is.null(candidate)) {
      fit    <- candidate
      method <- rung$method
      # athlete level: 2 when nested under position, 1 otherwise
      level  <- if (rung$method == "hier_position") 2L else 1L
      break
    }
  }

  hier_part <- tibble()
  if (!is.null(fit)) {
    pts  <- hier_athlete_coefs(fit, level)
    ints <- hier_intervals(fit)   # exactly one row — model-level, not per athlete
    hier_part <- pts %>%
      mutate(
        VHmax_lo_mph = ints$VHmax_lo_mph[1],
        VHmax_hi_mph = ints$VHmax_hi_mph[1],
        K_lo_yd      = ints$K_lo_yd[1],
        K_hi_yd      = ints$K_hi_yd[1],
        fit_method   = method
      )
  }

  fitted_ids <- hier_part$athlete_id %||% character()
  missing_ids <- setdiff(as.character(unique(df$athlete_id)), fitted_ids)

  nls_part <- tibble()
  if (length(missing_ids) > 0) {
    nls_part <- df %>%
      filter(athlete_id %in% missing_ids) %>%
      group_split(athlete_id) %>%
      map(function(d) {
        res <- tryCatch(fit_velocity_profile(d), error = function(e) NULL,
                        warning = function(w) NULL)
        if (is.null(res)) return(NULL)
        res$summary %>%
          transmute(athlete_id = as.character(athlete_id),
                    VHmax_ms, K_yd,
                    VHmax_lo_mph, VHmax_hi_mph, K_lo_yd, K_hi_yd) %>%
          mutate(fit_method = "nls_fallback")
      }) %>%
      compact() %>%
      bind_rows()
  }

  bind_rows(hier_part, nls_part) %>%
    mutate(
      VHmax_mph = VHmax_ms * MPH_PER_MS,
      K3_yd     = 3 * K_yd
    ) %>%
    select(athlete_id, VHmax_ms, VHmax_mph, VHmax_lo_mph, VHmax_hi_mph,
           K_yd, K_lo_yd, K_hi_yd, K3_yd, fit_method) %>%
    arrange(athlete_id)
}

# -----------------------------------------------------------------------------
# Population-level intervals from the fitted model.
#
# IMPORTANT — these are FIXED-EFFECT intervals: one interval for the whole
# model, identical for every athlete. They are NOT per-athlete uncertainty.
# A mixed model's per-athlete uncertainty lives in the conditional variance of
# the random effects, which nlme does not expose directly and which would need
# simulation to obtain honestly.
#
# The consequence is deliberate and must not be worked around: because the
# width is the same for every athlete, `flag_wide_ci` on these columns would be
# all-or-nothing and therefore meaningless as a per-athlete flag. Task 4 keeps
# flag_profile_quality() running on v1's bootstrap columns only, and reports
# the hierarchical interval once as a model-level diagnostic. Producing genuine
# per-athlete intervals is future work, not a gap to paper over with a number
# that looks per-athlete but is not.
#
# When intervals() fails — a normal outcome on near-singular fits — the bounds
# are NA rather than a falsely narrow default.
# -----------------------------------------------------------------------------
hier_intervals <- function(fit) {
  iv <- tryCatch(nlme::intervals(fit, level = HIER_CI_LEVEL, which = "fixed"),
                 error = function(e) NULL)
  if (is.null(iv)) {
    return(tibble(VHmax_lo_mph = NA_real_, VHmax_hi_mph = NA_real_,
                  K_lo_yd = NA_real_, K_hi_yd = NA_real_))
  }
  fx <- iv$fixed
  tibble(
    VHmax_lo_mph = fx["VHmax", "lower"] * MPH_PER_MS,
    VHmax_hi_mph = fx["VHmax", "upper"] * MPH_PER_MS,
    K_lo_yd      = fx["K", "lower"],
    K_hi_yd      = fx["K", "upper"]
  )
}

# -----------------------------------------------------------------------------
# fit_fn contract adapter (see crossval.R) so cv_evaluate can score this model
# on exactly the folds and arithmetic it uses for the NLS baseline.
# -----------------------------------------------------------------------------
fit_fn_hier <- function(train_interp) {
  fit_velocity_profiles_hier(train_interp) %>%
    select(athlete_id, VHmax_ms, K_yd)
}
```

- [ ] **Step 5: Verify the `coef(fit, level = ...)` assumption empirically**

This is the one place the plan asserts `nlme` API behaviour that must be confirmed rather than trusted. Run:

```r
source(here::here("R","config.R")); source(here::here("R","functions.R"))
source(here::here("R","synthetic.R")); source(here::here("R","fit_hierarchical.R"))
suppressPackageStartupMessages({library(dplyr);library(purrr);library(tibble)})
pop <- generate_synthetic_population(seed = 1)
df  <- pop$interp %>% mutate(across(c(position, athlete_id, sprint_id), as.factor))
f   <- hier_try_fit(df, ~ VHmax + K ~ 1 | position/athlete_id/sprint_id,
                    c(VHmax = 9, K = 5))
str(rownames(nlme::coef(f, level = 1)))
str(rownames(nlme::coef(f, level = 2)))
str(rownames(nlme::coef(f, level = 3)))
```

Expected: level 1 row names are positions (`SKILL`, `MID`, `BIG`); level 2 are `position/athlete` paths; level 3 are `position/athlete/sprint`. If the levels differ from this, correct the `level` assignment in `fit_velocity_profiles_hier` and the `sub(".*/", "", ids)` parsing in `hier_athlete_coefs` to match what `nlme` actually returns. Do not proceed until the athlete ids parsed out of `hier_athlete_coefs` exactly match `unique(pop$truth$athlete_id)`.

- [ ] **Step 6: Source it in the test helper**

In `tests/testthat/helper-setup.R`, add after the `synthetic.R` line:

```r
source(here::here("R", "fit_hierarchical.R"))
```

- [ ] **Step 7: Run the hierarchical tests**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" -e 'testthat::test_file("tests/testthat/test-fit-hierarchical.R")'`
Expected: PASS, 3 tests.

If the recovery test fails — hierarchical no better than NLS on `BIG` — do **not** weaken the assertion. Investigate in this order: (a) confirm Step 5's coefficient extraction really returns per-athlete values and not repeated fixed effects; (b) check that `BIG` runs are short enough that NLS is genuinely struggling (Task 2's third test); (c) if hierarchical genuinely does not help on clean synthetic data, that is the milestone's answer and it should be reported, not engineered around.

- [ ] **Step 8: Run the full suite and commit**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" tests/run-tests.R`
Expected: PASS, 0 failures.

```bash
git add R/fit_hierarchical.R R/config.R tests/testthat/test-fit-hierarchical.R tests/testthat/helper-setup.R
git commit -m "feat: hierarchical nlme velocity fit with convergence fallback ladder"
```

---

### Task 4: Side-by-side reporting, CV decides which fit leads

Ends with a report a human can act on and a recorded verdict on whether pooling helped.

**Files:**
- Modify: `R/03_velocity_profiling.R`
- Create: `tests/testthat/test-hier-reporting.R`

**Interfaces:**
- Consumes: `fit_velocity_profiles_hier()`, `fit_fn_hier()` (Task 3); `cv_evaluate()`, `make_cv_folds()`, `fit_fn_nls()` (Task 1); `flag_profile_quality()` from `R/functions.R`.
- Produces: `output/velocity_profiles.html` gaining hierarchical columns; new `output/cv_comparison.csv`.

- [ ] **Step 1: Write the failing test for the joined report shape**

Create `tests/testthat/test-hier-reporting.R`:

```r
test_that("hierarchical results join onto v1 profiles without dropping athletes", {
  pop <- generate_synthetic_population(seed = 3)

  v1 <- pop$interp %>%
    dplyr::group_split(athlete_id) %>%
    purrr::map(function(d) {
      r <- tryCatch(fit_velocity_profile(d, ci = FALSE), error = function(e) NULL,
                    warning = function(w) NULL)
      if (is.null(r)) NULL else r$summary
    }) %>%
    purrr::compact() %>% dplyr::bind_rows()

  hier <- fit_velocity_profiles_hier(pop$interp)

  joined <- v1 %>%
    dplyr::mutate(athlete_id = as.character(athlete_id)) %>%
    dplyr::left_join(hier, by = "athlete_id", suffix = c("", "_hier"))

  expect_equal(nrow(joined), nrow(v1))
  expect_true(all(c("VHmax_mph", "VHmax_mph_hier", "fit_method") %in% names(joined)))
  expect_false(any(is.na(joined$fit_method)))
})

test_that("hierarchical intervals are population-level, so flag_wide_ci is not per-athlete", {
  # Guards the documented limitation in hier_intervals(): fixed-effect
  # intervals are identical for every athlete. This test exists so that if a
  # future change makes them genuinely per-athlete, it fails loudly and the
  # reporting decision in script 03 gets revisited on purpose.
  pop  <- generate_synthetic_population(seed = 3)
  hier <- fit_velocity_profiles_hier(pop$interp)

  hier_rows <- hier[hier$fit_method != "nls_fallback", ]
  # If nothing converged there is no limitation to pin and the fixture is not
  # exercising the model at all — that is a failure, not a pass.
  expect_gt(nrow(hier_rows), 1)

  widths <- hier_rows$VHmax_hi_mph - hier_rows$VHmax_lo_mph
  expect_equal(length(unique(round(widths, 8))), 1L)
})

test_that("flag_profile_quality runs unchanged on v1 columns", {
  # flag_profile_quality needs exactly: VHmax_mph, obs_max_mph,
  # obs_game_max_mph, VHmax_lo_mph, VHmax_hi_mph, max_obs_dist, rmse_mph.
  fixture <- tibble::tibble(
    athlete_id       = c("A", "B"),
    position         = "SYN",
    VHmax_mph        = c(20, 15),
    obs_max_mph      = c(19.5, 15.2),
    obs_game_max_mph = c(20.1, 22.0),   # B ran 7 mph faster elsewhere
    VHmax_lo_mph     = c(19, 14),
    VHmax_hi_mph     = c(21, 16),
    max_obs_dist     = c(28, 12),
    rmse_mph         = c(0.2, 0.3)
  )

  flagged <- flag_profile_quality(fixture)
  expect_equal(nrow(flagged), 2)
  expect_false(flagged$needs_review[1])
  expect_true(flagged$needs_review[2])                       # short run + understated
  expect_match(flagged$review_flags[2], "understates-top-speed")
})
```

- [ ] **Step 2: Run to verify it fails**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" -e 'testthat::test_file("tests/testthat/test-hier-reporting.R")'`
Expected: FAIL on the first test with `could not find function "fit_velocity_profiles_hier"` if Task 3 is not yet merged, or with a row-count mismatch once it is. The second and third tests should pass immediately — they exercise code that already exists and are there to pin current behaviour before Step 3 changes the report.

- [ ] **Step 3: Add the hierarchical fit to script 03**

In `R/03_velocity_profiling.R`, insert immediately after the `message("Profiles fit: ...")` line (around line 135) — i.e. after `profile_summary` has been built and flagged. The variable is `profile_summary`; there is no variable named `profiles`. Placing the insert *after* `flag_profile_quality()` is deliberate: the review flags are computed on v1's bootstrap columns only, which is what keeps `flag_wide_ci` meaningful (see `hier_intervals`).

```r
# -----------------------------------------------------------------------------
# STEP 4b: Hierarchical fit over ALL sprints (fit_hierarchical.R)
# v1's fit above uses one sprint per athlete. This one pools every qualifying
# sprint so short-run athletes borrow structure from long-run ones. Both are
# reported; cross-validation below decides which leads.
# -----------------------------------------------------------------------------
message("Fitting hierarchical profiles over all ", n_distinct(sprints_all$sprint_id),
        " sprints...")

interp_all <- sprints_all %>%
  group_split(sprint_id) %>%
  map(interpolate_sprint) %>%
  compact() %>%
  bind_rows()

hier_profiles <- fit_velocity_profiles_hier(interp_all)

message("Hierarchical fit methods: ",
        paste(names(table(hier_profiles$fit_method)),
              table(hier_profiles$fit_method), sep = "=", collapse = ", "))

# The hierarchical interval is population-level (see hier_intervals) — one
# number for the model, not per athlete — so it is reported once here rather
# than as a per-athlete column that would invite a misreading.
hier_only <- hier_profiles %>% filter(fit_method != "nls_fallback")
if (nrow(hier_only) > 0 && !all(is.na(hier_only$VHmax_lo_mph))) {
  message("Hierarchical VHmax fixed-effect interval (model-level, not per athlete): [",
          round(hier_only$VHmax_lo_mph[1], 2), ", ",
          round(hier_only$VHmax_hi_mph[1], 2), "] mph")
}

profile_summary <- profile_summary %>%
  mutate(athlete_id = as.character(athlete_id)) %>%
  left_join(
    hier_profiles %>%
      select(athlete_id, VHmax_mph, K_yd, fit_method) %>%
      rename(VHmax_mph_hier = VHmax_mph, K_yd_hier = K_yd),
    by = "athlete_id"
  )
```

- [ ] **Step 4: Add the cross-validation comparison to script 03**

Immediately after the block from Step 3, insert:

```r
# -----------------------------------------------------------------------------
# STEP 4c: Which fit actually predicts better? (crossval.R)
# Held-out scoring on identical folds. This is what decides which number leads
# the report — not flag counts, which are our own thresholds.
# -----------------------------------------------------------------------------
cv_folds <- make_cv_folds(distinct(interp_all, athlete_id, sprint_id))

cv_results <- bind_rows(
  cv_evaluate(interp_all, fit_fn_nls,  cv_folds)$summary %>% mutate(method = "v1_nls"),
  cv_evaluate(interp_all, fit_fn_hier, cv_folds)$summary %>% mutate(method = "hierarchical")
) %>% select(method, everything())

write.csv(cv_results, file.path(OUTPUT_DIR, "cv_comparison.csv"), row.names = FALSE)
print(cv_results)

cv_winner <- cv_results$method[which.min(cv_results$mean_rmse_mph)]
message("Lower held-out RMSE: ", cv_winner,
        " (v1 ", round(cv_results$mean_rmse_mph[cv_results$method == "v1_nls"], 3),
        " vs hierarchical ",
        round(cv_results$mean_rmse_mph[cv_results$method == "hierarchical"], 3), " mph)")
```

- [ ] **Step 5: Add the hierarchical columns to the report table**

Two edits — the column must be carried through `profile_display` *and* declared in `reactable`, or it silently never reaches the page.

First, in the `profile_display <- profile_summary %>% ... transmute(...)` block (around line 409), add the three new columns after `K3_yd`:

```r
    K_yd, K_lo_yd, K_hi_yd, K3_yd,
    VHmax_mph_hier, K_yd_hier, fit_method,
    rmse_mph, fit_dist_yd = max_obs_dist,
```

Then in the `reactable(` call that builds `rt_profiles` (around line 421), add matching entries to `columns = list(...)`, after the `K3_yd` line:

```r
    VHmax_mph_hier   = colDef(name = "VHmax (hier)"),
    K_yd_hier        = colDef(name = "K (hier)"),
    fit_method       = colDef(name = "Fit method", minWidth = 120),
```

Note `profile_display` ends with `mutate(across(where(is.numeric), ~ round(.x, 2)))`, which rounds the two new numeric columns automatically — do not add a separate `format = colFormat(...)`, as the existing columns do not use one either.

- [ ] **Step 6: Run the reporting tests**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" -e 'testthat::test_file("tests/testthat/test-hier-reporting.R")'`
Expected: PASS, 2 tests.

- [ ] **Step 7: Run script 03 end-to-end on the cached game**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" R/03_velocity_profiling.R`
Expected: completes without error; prints the `fit_method` breakdown and the CV comparison; writes `output/cv_comparison.csv` and `output/velocity_profiles.html`.

Record in the ticket: the CV table, the `fit_method` counts, and the `understates-top-speed` flag count before and after. If the hierarchical fit loses on held-out RMSE, that is a legitimate result — record it, leave v1's fit as the leading column, and say so plainly in the ticket rather than tuning until it wins.

- [ ] **Step 8: Run the full suite and commit**

Run: `"/c/Progra~1/R/R-4.5.3/bin/Rscript.exe" tests/run-tests.R`
Expected: PASS, 0 failures.

```bash
git add R/03_velocity_profiling.R tests/testthat/test-hier-reporting.R
git commit -m "feat: report hierarchical fit beside v1 NLS, CV decides which leads"
```

- [ ] **Step 9: Open the PR**

```bash
git push -u origin hierarchical-fit
gh pr create --draft --title "feat: hierarchical velocity profiling with held-out CV" --body "Implements .scratch/speedprofiling-hierarchical/spec.md. Include the CV comparison table and fit_method breakdown from Task 4 Step 7 in this description."
```

---

## Notes for the implementer

- **`%||%`** is used once in Task 3. If it is not already available, `rlang::%||%` comes with the tidyverse; otherwise define `` `%||%` <- function(a, b) if (is.null(a)) b else a `` at the top of `R/fit_hierarchical.R`.
- **`nlme` is not attached by the numbered scripts.** All calls are namespaced (`nlme::nlme`, `nlme::coef`, `nlme::intervals`) so no `library(nlme)` is needed. Keep it that way — `nlme::coef` and `stats::coef` differ.
- **Convergence failure is normal here.** If the full rung never converges on real data and everything lands on `hier_athlete` or lower, that is information about the data, not a bug. Record which rung won.
- **Do not tune thresholds to make flags disappear.** The `REVIEW_*` constants stay untouched this milestone precisely so flag counts remain comparable before and after.

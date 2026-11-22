# Experimental Design, Statistics & Parameter Search

Load during **Phase 4 (Parameter Search & Paired Statistics)** and **Phase 5 (Stopping)**.

---

## 1. Noise Floor & Paired Decision Rules
1. **Measure the noise floor first:** run the baseline `k ≥ 5` times on the dev set (varying only uncontrolled randomness if stochastic, or bootstrap across examples). Define:
   - `MDE ≈ 2 · std(mean)` (minimum detectable effect).
   - If the expected gain of an experiment is `< MDE`, **enlarge `n` before running** (`std(mean) ∝ 1/√n`) or skip the experiment.
2. **Always pair comparisons:** evaluate baseline and candidate on the exact same examples, splits, and RNG seeds (common random numbers). Compute per-example deltas `d_i = score_cand(i) - score_base(i)`.
3. **Look beyond the mean:** inspect median, 95% paired bootstrap CI, hard-constraint violations, and worst-K tail shift (a gain in mean that breaks 1% of tail cases can be a net regression).
4. **Canonical decision rule** (automated by `scripts/ledger.py compare`):
   - **KEEP** iff `paired_mean_delta > max(MDE, min_effect_of_interest)` AND `ci95_low > 0` AND zero hard-constraint regressions AND no unacceptable tail degradation.
   - **REJECT** if delta ≤ 0 or hard constraint violated.
   - **INCONCLUSIVE** if `0 < delta ≤ MDE` (either drop or increase sample size if hypothesis is high-leverage).

---

## 2. Guarding Against Multiple Comparisons & Dev Overfitting
- Screen many candidates on cheap tiers; promote only a small pre-registered shortlist to full dev and holdout.
- **Never select on the holdout set.** If many rounds risk overfitting dev, rotate or expand dev with fresh seeds/splits.
- Confirm finalists across **≥ 2 independent data/seed draws**. Prefer lower-variance winners over spiky dev-specific winners.
- Inspect per-example delta distributions to verify gains are broad rather than driven by 1–2 outlier examples.
- **Freeze winners** before starting a new structural round so causality never blurs; re-sweep sensitive knobs *after* structural changes.

---

## 3. Search Space & Strategy Selection
Classify knobs first: **sensitive vs. inert** (fix inert knobs), **coupled vs. independent**, **static vs. schedule** (prefer parameterized schedules over dozens of fixed constants).

| Strategy | Best When | Avoid When |
|---|---|---|
| **OFAT (One-Factor-At-a-Time)** | Fast sensitivity screening & diagnosis | Strongly coupled parameters |
| **Small Factorial** | Top 3–5 sensitive knobs with suspected interactions | >5 parameters |
| **Random / Latin Hypercube** | Low effective dimensionality; weak prior | Very expensive evaluations |
| **Bayesian Opt (GP/TPE)** | Expensive evals, ≤20 smooth knobs | Heavy noise or high dimensions |
| **CMA-ES / Evolution** | Noisy, multimodal, coupled continuous knobs | Tiny evaluation budget |
| **Successive Halving / Hyperband** | Validated multi-fidelity cheap tiers exist | Cheap tier doesn't rank-correlate |

---

## 4. Practical Optimum Stopping Rule
Stop optimizing and move to final verification when **either**:
1. `expected_gain_of_next_round < max(MDE, round_cost_in_budget_terms)`, **or**
2. Remaining score gap is explained by irreducible floors (`practical_optimum = theoretical_ceiling − irreducible_floors`), **or**
3. Pre-registered kill criterion fires (phase exceeds budget without beating MDE).

Never chase noise below MDE.

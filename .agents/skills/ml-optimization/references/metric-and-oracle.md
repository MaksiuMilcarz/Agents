# Metric Archaeology & Replay Oracle Engineering

Load during **Phase 0 (Metric Archaeology)** and **Phase 1 (Build the Oracle)**.

---

## 1. Metric Archaeology Protocol
Do this before writing any model or sweep code:
1. **Locate exact scoring code.** If the evaluator is opaque/hidden, reconstruct its behavior via controlled one-variable perturbations on deterministic inputs.
2. **Decompose into additive terms:** separate reward terms, hard/soft penalties, indicators, thresholds, clipping, and tie-breakers.
3. **Classify every term:**
   - **Saturated:** already near its ceiling (stop investing here).
   - **Floor-bound:** irreducible penalty/noise you cannot avoid.
   - **Has headroom:** realistic achievable gain > MDE (attack first).
4. **Compute ceilings:**
   - `theoretical_ceiling` = mathematical max.
   - `practical_optimum` = `theoretical_ceiling − irreducible_penalties − reachability_floor − safety_floor`.
5. **Identify asymmetric trade-offs:** e.g., a fixed indicator penalty vs. continuous regret determines the optimal *decision rule* (often more valuable than a better predictor).
6. Record the decomposition table in `METRIC.md`.

---

## 2. Building the Replay Oracle (Highest-ROI Asset)
A 10× faster, deterministic, per-example replay harness compounds into every subsequent hypothesis.

### Requirements Checklist
- **Protocol fidelity:** identical call order, horizon, defaults, timeouts, edge checks.
- **RNG & data fidelity:** reproduce exact seeds, draw order, preprocessing, and evaluation distribution.
- **Metric fidelity:** differential-test against the real grader on a fixed suite; verify `max |Δ score| ≤ 1e-6` (or document exact tolerance).
- **Determinism:** repeated runs identical (pin `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1`, fixed seeds, deterministic ops).
- **Per-example observability:** output JSON with per-example scores, decomposed metric terms, constraint flags, and worst-K traces.
- **Immutability & versioning:** freeze the harness once verified; record harness hash + dataset hash in `LEDGER.jsonl`. Any harness edit requires re-running the differential test.
- **Zero leakage:** diagnostic introspection stays in the harness; the deliverable artifact may only consume permitted inference inputs.

---

## 3. Multi-Fidelity Evaluation Ladder
Use **successive halving / racing**: eliminate weak variants cheaply, promote only survivors.

| Tier | Size | Purpose | Promotion Gate |
|---|---|---|---|
| **Smoke** | 1–5 examples | Shape, NaN, domain, crash validation | Zero interface/runtime errors |
| **Pilot** | 5–10% | Signal direction & catastrophic-tail screen | Beats baseline beyond pilot noise |
| **Dev** | 20–100% | Paired selection & statistical CI | Paired Δ > MDE, no constraint regression |
| **Holdout** | Fresh untouched split | Overfitting guard (finalists only) | Confirms dev gain on unseen draw |
| **Final** | Exact grading environment | Ship gate | Verbatim grading command passes |

> **Proxy rule:** Before trusting any cheaper tier or proxy metric for decisions, run a one-off rank-correlation check (Spearman ρ) against the true metric across ≥5 diverse candidates. If correlation is weak or negative, ban that proxy for selection.

---

## 4. Parallel Execution & Environment Hygiene
- Worker pool = `min(#variants, cores - 1)`; never oversubscribe CPU/BLAS threads.
- Cache immutable prep work (tokenization, feature matrices, compiled kernels, dataset loads).
- Avoid per-run container startup overhead in hot sweeps (use bind-mounts or persistent workers).
- Compute round cost *before* launching: `cost ≈ #variants × (setup + #tasks × per_task) / parallelism`. If one round exceeds ~5% of budget, add a cheaper tier or shrink the batch.
- Fail fast at the interface boundary (shape/NaN/domain validator) so broken variants never waste grader quota.

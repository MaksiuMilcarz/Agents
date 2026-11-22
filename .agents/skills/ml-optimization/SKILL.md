---
name: ml-optimization
description: Closed-loop, metric-driven ML, prompt, RL, and hyperparameter optimization workflow combining fast deterministic oracle harnesses, metric archaeology, dual structure/parameter search loops, paired statistics, and holdout verification. Use for any task optimizing a quantitative model or algorithmic metric under constraints and compute budget.
---

# ML & Hyperparameter Optimization (`ml-optimization`)

A domain-agnostic scientific optimizer for ML, LLM/prompt tuning, RL, tabular, vision, recsys, time series, and scientific computing. **Not a grid-search wrapper**: parameter sweeps are the *bottom* lever of a much higher-ROI structural search stack.

Inherits all invariants from root `AGENTS.md` (verifier-first, one source of truth, evidence or silence, files as truth). Uses `scripts/ledger.py` for deterministic experiment logging, hashing, paired statistics, and `RUNS.md` generation.

---

## Dual Nested Loop Architecture

```text
OUTER LOOP (Structure / Ideas) — high variance, highest leverage (reserve 20–40% budget)
  frame -> metric archaeology -> replay oracle -> baseline -> loss/oracle-gap diagnosis
        -> mechanism hypothesis -> cheapest discriminating probe -> re-architect
                                       │
INNER LOOP (Parameters / Schedules) — cheap, fast, saturating
  paired batch sweep -> paired CI vs MDE -> keep winner -> refine -> freeze
                                       │
VERIFICATION LOOP (Load verify-and-ship)
  rebuild canonical artifact -> exact grader on fresh holdout -> residual risk -> ship
```

**Economic rule:** Always pick the next experiment maximizing `(expected_gain × confidence) / cost` (wall-clock + compute + tokens).

---

## Workspace Layout (Initialize Once)

Run `python3 .agents/skills/ml-optimization/scripts/ledger.py init <project_dir>` to scaffold:
- `BRIEF.md` — objective, exact metric command, hard/soft constraints, allowed/forbidden data policy, budget, kill criteria.
- `METRIC.md` — exact formula decomposition, ceiling vs. practical optimum, irreducible floors.
- `IDEAS.md` — prioritized structural hypothesis backlog (`expected_gain × confidence / cost`).
- `LEDGER.jsonl` — append-only, hashed experiment log (never hand-edit; write via `scripts/ledger.py log`).
- `RUNS.md` — auto-generated leaderboard table (`scripts/ledger.py summary`).
- `work/{harness,variants,logs,artifacts}` — frozen replay oracle, programmatically generated variants, raw logs (on disk only).

---

## Six-Phase Execution Flow

### Phase 0 — Frame & Metric Archaeology
1. Write `BRIEF.md` including the **legitimacy & data policy** (what is dev vs. holdout; what structural exploitation is allowed vs. forbidden) *before* touching data.
2. Read or probe the exact scoring function. Decompose it into additive terms (rewards, penalties, indicators) and record in `METRIC.md`: theoretical ceiling, irreducible floors, and **which term has real headroom**.
   - Deep guide: [references/metric-and-oracle.md](references/metric-and-oracle.md)

### Phase 1 — Build & Freeze the Replay Oracle
1. Build a fast, deterministic local replay harness that matches the real grader (protocol, RNG seeds, preprocessing, metric formula) and emits **per-example scores and failure terms**.
2. Differential-test against the real grader on a fixed suite (target `max |Δ| ≤ 1e-6` or documented tolerance). Record the verification certificate and harness hash.
3. Set up a **multi-fidelity ladder** (`smoke` 1–5 examples → `pilot` 5–10% → `dev` paired selection → `holdout` untouched finalists → `final` exact grader). Validate proxy rank-correlation once; ban unvalidated proxies.
   - Deep guide: [references/metric-and-oracle.md](references/metric-and-oracle.md)

### Phase 2 — Baseline & Diagnosis (Before Any Tuning)
1. Ship a working end-to-end baseline first (even if weak) to prove the harness and interface.
2. Measure the **noise floor** (`k ≥ 5` baseline reruns) to establish `MDE ≈ 2 · std(mean)`.
3. Decompose total loss by metric contribution (not frequency): crashes/validity → hard constraints → reachability/oracle-gap → decision rule/post-processing → model estimation error → irreducible floor.
4. Route based on dominant loss:
   - Systematic mechanism / scale bug / decision mismatch → **Structure Loop**
   - Smooth sensitivity to knobs → **Parameter Loop**
   - Floor/noise-bound → stop tuning; improve estimator or ship.

### Phase 3 — Structural Search Loop (Protect 20–40% of Budget)
Attack the **Leverage Ladder** top-down before grinding knobs:
1. Metric archaeology & objective reformulation
2. Generative-process invariants & cross-signal denoising
3. Oracle-gap & worst-K tail analysis
4. Problem decomposition & feature/target transform
5. Model class / inductive bias
6. Metric-aware decision rule / calibration / post-processing
7. Algorithm / schedule / curriculum
8. Parameters (inner loop)

Maintain `IDEAS.md`. Test each idea with the **cheapest single-variable discriminating probe**, pre-registering the expected effect before running. Re-express any diagnostic insight using *only* permitted inference inputs.
- Deep guide: [references/structural-search.md](references/structural-search.md)

### Phase 4 — Batched Parameter Search & Paired Statistics
1. Generate variants **programmatically** from one canonical base + override dict (never manual deliverable forks). Hash base and variant in `LEDGER.jsonl`.
2. Run **paired batches** (common random numbers: identical tasks, splits, seeds) in one parallel program; write raw logs to `work/logs/<id>.txt`, digest results via `scripts/ledger.py`.
3. Decide statistically using `scripts/ledger.py compare`:
   - **Accept** iff `paired_mean_delta > max(MDE, min_effect)` AND zero hard-constraint regressions AND tail risk does not worsen.
   - Confirm finalists on ≥2 independent draws / untouched holdout before adopting.
   - Freeze winner before starting a new structural round (re-tune knobs after major structural changes).
- Deep guide: [references/experimental-stats.md](references/experimental-stats.md)

### Phase 5 — Practical Optimum Stopping & Final Ship
- **Stop** when `expected_gain_of_next_round < max(MDE, round_cost)` or remaining gap equals irreducible floors (`practical_optimum = ceiling − irreducible_floors`).
- **Verify & Ship:** Rebuild final artifact cleanly from canonical base + winning config, then load `.agents/skills/verify-and-ship/SKILL.md` to verify with the exact grading command on fresh holdout data and write the residual-risk report.

---

## Reference Modules & Scripts (Load Only When Needed)
- Metric archaeology, oracle harness & multi-fidelity setup: [references/metric-and-oracle.md](references/metric-and-oracle.md)
- Structural insight-hunt playbook & legitimacy filter: [references/structural-search.md](references/structural-search.md)
- Paired stats, MDE, search strategies & stopping rules: [references/experimental-stats.md](references/experimental-stats.md)
- Domain transfer matrix (CV, LLM, prompt, tabular, RL, TS, recsys) & templates: [references/domain-matrix.md](references/domain-matrix.md)
- Deterministic ledger, paired bootstrap & `RUNS.md` CLI: `scripts/ledger.py` (`python3 .agents/skills/ml-optimization/scripts/ledger.py --help`)

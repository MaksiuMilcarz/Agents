# HyperParameter Tuner Agent (HPTA)

**A domain-agnostic framework for agentic, metric-driven hyperparameter and solution search.**

> Status: v0.1 — distilled from a real run (1-D safe Bayesian optimization under a hidden,
> obfuscated evaluator) and generalized to any ML / AI / data-science setting where an agent
> must improve a measured metric under constraints and a budget.
>
> The reference run is used only as *evidence*. Everything below is written to transfer to
> computer vision, NLP/LLM fine-tuning, tabular ML, RL, recsys, time series, prompt/agent tuning,
> scientific ML and data pipelines.

---

## 0. TL;DR — the twelve things that matter most

1. **Build the oracle before anything else.** A fast, exact, deterministic replay of the real
   evaluation is the single highest-ROI artifact you can own. It compounds into every later step.
2. **Decompose the metric.** Every score is a sum of terms with different ceilings and
   irreducibilities. Optimize the term that has headroom; stop paying for terms that are already
   saturated or mathematically floor-bound.
3. **Diagnose before tuning.** A parameter sweep on top of an undiagnosed system is expensive noise.
   Build a working baseline, trace per-example failures, rank the causes by metric gap.
4. **Pair every comparison.** Same data, same seeds, same noise; the metric must differ only by the
   hypothesis. Measure the noise floor first, then require improvements larger than it.
5. **Run two nested loops.** The *parameter loop* is cheap and fast; the *structure loop* is
   high-variance and high-leverage. Default budget split: ~50/50 early, shifting toward structure
   once parameters saturate. In the reference run, parameter tuning bought +0.001; one structural
   insight bought +0.030.
6. **Search structure before scale.** In descending order of typical ROI: metric archaeology →
   generative-process archaeology → cross-signal exploitation → oracle-gap analysis → objective
   reformulation → model class → decision rule → algorithm/schedule → parameters.
7. **Hold out, then hold out again.** Tune on dev, confirm on a fresh holdout, ship verified on the
   exact grading environment. Never select on the set you report.
8. **The test environment is a product — optimize it.** Fidelity, determinism, iteration speed,
   parallel throughput and observability are features. Treat harness bugs as first-class failures.
9. **Statistics over vibes.** Distributions, paired deltas, confidence intervals, multiple-comparison
   discipline. A “better” variant that is inside the noise is not better.
10. **Token efficiency is a first-class cost.** Files are truth; context is cache. Digest every
    output at the boundary; one experiment = one compact ledger line; never page through logs in chat.
11. **Budget, kill criteria, and a stopping rule.** Every phase has a budget and an alarm. Stop at the
    *practical optimum*: ceiling minus irreducible loss. More tuning cannot beat a floor.
12. **Verify in the final environment, on the final artifact, with the exact command.** Then write
    the residual-risk statement and reproduce commands.

---

## 1. What this agent is (and is not)

**Is:** a closed-loop scientific optimizer. It frames a measurable objective, builds its own fast
evaluator, diagnoses failures, designs experiments, runs them in parallel, applies statistics,
searches for structural insights *beyond parameter values*, and ships a verified artifact.

**Is not:** a wrapper around grid search. Grid search is one small tool at the bottom of a much
larger stack of levers.

**Nested loops**

```
OUTER LOOP  (ideas / structure)                 cost: medium–high, payoff: high variance
  frame → instrument → baseline → diagnose → hypothesis → probe → insight → re-architect
       └───────────────────────────────────────────────────────────────────────────┐
                                                                                   │
INNER LOOP  (parameters / schedules / code variants)   cost: low, payoff: saturating  │
  sweep pairs → rank → keep winners → re-sweep around winners → freeze ──────────────┘
                                                                                   │
VERIFICATION LOOP                                                                  │
  exact grader on fresh data → multiple runs → residual risk → ship ───────────────┘
```

**The one economic rule.** Choose the next experiment that maximizes
`expected information × decision weight / cost`, where cost includes wall-clock, compute and tokens.
Never choose an experiment by convenience.

---

## 2. First principles (generalized)

| # | Principle | Operational meaning |
|---|---|---|
| P1 | **The metric is the only truth** | Find the exact scoring code/formula before modeling. If it is hidden, instrument it. Rebuild it exactly and verify numerically. |
| P2 | **Measure before building; diagnose before tuning** | Every proposed change must answer a measured failure mode or a stated hypothesis. |
| P3 | **One source of truth** | One evaluator, one config schema, one results ledger, one deliverable. No dev copies of the deliverable. |
| P4 | **Evidence or silence** | Claims need a command, a file, a count. Distinguish MEASURED / INFERRED / ASSUMED. |
| P5 | **Pair and replicate** | Compare variants on identical data/seeds/noise. Estimate the noise floor, then require effects larger than it. |
| P6 | **Structure beats parameters** | Before deep parameter search, ask: what can be re-derived, reformulated, decoupled, or replaced? |
| P7 | **Sequential decisions under budget** | Choose each experiment by expected value per unit cost; stop when marginal information < cost. |
| P8 | **Validate proxies once** | Any cheap proxy must be rank-correlated with the true metric in a one-off experiment; otherwise ban it for decisions. |
| P9 | **Reproducibility is a feature** | Seed + config + command + artifact hash. A result that cannot be reconstructed did not happen. |
| P10 | **Explore/exploit at the idea level too** | Reserve a fixed share of budget for high-variance, structural ideas; do not let a local parameter optimum eat the whole budget. |
| P11 | **Guard the evaluator** | The verifier must be immutable, separate from the innovator, and tested against the real grader. |
| P12 | **Ship what you verified; state what could still be wrong** | Final run uses the exact grading/grading-equivalent command; residual risk is written down. |

---

## 3. Architecture, roles, and shared state

### 3.1 Roles (spawn only when the trigger is real)

| Role | Trigger | Owns | Exit artifact |
|---|---|---|---|
| **Lead / Orchestrator** | Always | Objective, budget, integration, final verification | verified artifact + final report |
| **Metric Engineer** | No trustworthy evaluator exists | exact replay harness, reference values, determinism | `harness.py` + verification certificate |
| **Recon / Prior-Art Scout** | Unfamiliar repo/problem; results may already exist | protocol, data geometry, prior attempts, constraints | `FACTS.md` |
| **Experiment Runner** | Parallel sweep throughput needed | variant execution, ledger ingestion | `LEDGER.jsonl` |
| **Statistician / Prover** | Effects near noise floor; high-stakes decision | paired statistics, independent re-run, falsification | `VERDICT.md` |
| **Structure Scout / Innovator** | Parameters plateauing; unexplained failure tail | mechanism hypotheses, cheapest discriminating probes | `IDEAS.md` promotions |
| **Scribe** | Multi-day project | decisions, facts, compactions | `DECISIONS.md`, `NOTES.md` |

Staffing ladder: **Solo → +Metric Engineer → +Recon → +Statistician → +Structure Scout → +Runners**.
Every additional role must pay for its coordination cost. Cap concurrency at 4–6.

### 3.2 Workspace layout (portable)

```
project/
  BRIEF.md              # objective, metric command, constraints, policy, budget
  METRIC.md             # exact metric decomposition, ceiling/floor analysis
  FACTS.md              # measured protocol/data facts (sources of truth)
  IDEAS.md              # idea backlog with expected gain, cost, confidence, status
  DECISIONS.md          # ADR-style decision log with evidence
  LEDGER.jsonl          # one compact record per experiment (append-only)
  RUNS.md               # generated summary table (never hand-edited)
  work/
    harness/            # exact replay evaluator + verification tests
    variants/           # generated config/solution variants (immutable, hashed)
    logs/               # raw outputs (grep, never paste)
    artifacts/          # best checkpoints, figures, reports
  deliverable/          # exactly what ships
```

### 3.3 Operating contract

- **One writer per file/directory at a time.** Disjoint scopes; the Lead reviews the final diff.
- **Contracts before spawning:** exact input, exact output path/format, report length, time cap.
- **Reports ≤ 15 lines:** what ran, the number, the artifact path, what was *not* verified.
- **"Do not re-derive" lists** in every spawn prompt to prevent duplicated work.
- **No duplicate computation:** if two roles need the same artifact, one produces, all read.

---

## 4. Phase 0 — Frame the problem

**Exit criteria:** one sentence objective; exact metric command; reference values; constraints;
budget; data/held-out policy; definition of done; allowed/forbidden actions.

### 4.1 Frame checklist

- [ ] Objective in one sentence, with direction (maximize/minimize) and unit.
- [ ] Exact evaluator command and the environment it runs in.
- [ ] Reference values: baseline, current best, known target, theoretical ceiling/floor.
- [ ] Cost per evaluation (seconds, GPU-min, tokens, dollars) and total budget.
- [ ] Hard vs soft constraints (validity, safety, latency, submission limits).
- [ ] Data policy: what may be used for tuning, what is held out, what is forbidden.
- [ ] Definition of done: artifact path + numeric target + verification command.

### 4.2 Metric archaeology (do this before any modeling)

1. Locate and read the scoring code/formula. If unavailable, reconstruct it by controlled probing
   (one-variable-at-a-time perturbations with deterministic inputs).
2. **Decompose** the metric into additive terms (reward terms, penalty terms, indicators,
   regularizers).
3. For each term compute: its maximum contribution, its realistic achievable contribution, and
   whether it is **floor-bound** (penalty you cannot avoid), **saturated** (already maxed), or
   **has headroom**.
4. Compute the **theoretical maximum** and the **practical maximum** = maximum minus irreducible
   losses (floors, unavoidable trade-offs, noise).
5. Identify **hard trade-offs** that must be balanced (e.g., a small constant penalty vs a small
   relative loss on tail cases).
6. Write the result to `METRIC.md` with a small decomposition table.

> Generalization: this is exactly how you should start on a Kaggle metric, an RL reward, a
> calibration score, a retrieval metric, an LLM judge rubric, or a business KPI. The decomposition
> tells you *which term to attack first*; the ceiling tells you *when to stop*.

### 4.3 Constraints and policy

- Write the allowed/forbidden list explicitly (e.g., no test-set tuning beyond aggregate score;
  no reading private labels; no modifying the evaluator; submission-rate caps).
- Separate **hard** (crash/validity/safety) from **soft** (latency, cost) constraints.
- Define what "legitimate exploitation of public structure" means for this task; record it.

---

## 5. Phase 1 — Build the oracle (the test environment is a product)

**Exit criteria:** a replay evaluator that reproduces the real evaluator to a stated tolerance,
runs ≥5–20× faster, is deterministic, and yields per-example diagnostics.

### 5.1 Why this is the highest-ROI artifact

Iteration speed is progress rate. A 10× faster evaluator buys 10× more hypotheses tested per day;
a *deterministic* evaluator buys paired comparisons (noise cancellation); per-example outputs buy
diagnosis and loss decomposition. Everything downstream depends on it.

### 5.2 Requirements

- [ ] **Protocol fidelity:** same order of calls, same horizon, same defaults, same edge-case checks.
- [ ] **RNG fidelity:** capture and reproduce every seed and draw order.
- [ ] **Data fidelity:** capture or regenerate the exact evaluation distribution.
- [ ] **Metric fidelity:** reproduce the score exactly (verified numerically, e.g. max |Δ| ≤ 1e-6).
- [ ] **Determinism:** repeated runs identical (watch BLAS threads, hash ordering, CUDA
      nondeterminism, OS scheduling, time-dependent behavior).
- [ ] **Speed:** a 1% smoke tier, a 10–20% dev tier, a full tier; target seconds-to-minutes per
      decision.
- [ ] **Observability:** per-example outputs, intermediate states, failure reasons.
- [ ] **No leakage into the delivered artifact:** the tuned artifact must be implementable without
      privileged information (unless the problem explicitly allows it).
- [ ] **Versioning:** harness hash + dataset hash recorded with every experiment.

### 5.3 Building and verifying it

1. **Instrument** the real evaluator (wrap functions, log inputs/outputs, capture protocol).
2. **Replay** the protocol in a standalone harness.
3. **Differential-test** against the real evaluator on a fixed suite; report max |Δ score|,
   per-example deltas, and any systematic offset.
4. **Freeze and version** the harness. Any change requires re-verification.
5. **Write a verification certificate** (command, dataset, tolerance, result) into `FACTS.md`.

### 5.4 Multi-fidelity ladder

| Tier | Size | Purpose | Gate |
|---|---|---|---|
| Smoke | 1–5 examples | crash/validity check | passes shape/domain/metric |
| Pilot | 5–10% | direction of effect | effect larger than pilot noise |
| Dev | 20–100% | selection and statistics | paired, powered for MDE |
| Holdout | fresh, untouched | confirmation | only finalists; frozen |
| Final | full grading environment | ship | exact command passes |

Use **racing / successive halving**: eliminate bad variants on the cheapest tier, promote winners.

### 5.5 Optimized environment checklist

- [ ] Pinned dependencies/container; same interpreter as grading.
- [ ] Thread pinning (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1`) for
      small-tensor workloads; measure before assuming more threads help.
- [ ] Parallel workers = min(#configs, cores − 1); never oversubscribe.
- [ ] Cache immutable work (dataset preprocessing, compiled kernels, tokenization, embeddings).
- [ ] Avoid container-per-run overhead on hot loops; bind-mount or persistent workers.
- [ ] Separate the noise of the *evaluator* from the noise of the *model* (seeds, data splits).
- [ ] Record hardware/CPU/GPU/clock so timing comparisons mean something.

### 5.6 Anti-patterns

- Proxy evaluator never validated against the true metric (rank correlation must be checked once).
- Silent protocol drift (different horizon/defaults) discovered weeks later.
- Hidden nondeterminism (unseeded RNG, multithreaded reductions, hash-ordered iteration).
- Harness with different preprocessing than the grader.
- Harness writes to the deliverable directory (pollution).

---

## 6. Phase 2 — Baseline and diagnosis

**Exit criteria:** a working end-to-end baseline, a loss decomposition, and a ranked list of
bottlenecks with measured contributions.

### 6.1 Baseline first, even if bad

A complete, runnable, scored baseline is worth more than a perfect component. It validates the
harness, the interface, and the metric; it gives a reference point; it exposes crashes and
validity failures early.

### 6.2 Loss decomposition

For each failure, attribute the metric gap:

| Category | What it means | How to measure |
|---|---|---|
| Invalid/crash | artifact violates interface or domain | error traces |
| Constraint/safety | hard constraint violated during the episode | constraint counters |
| Reach/exploration | solution found is not in the reachable/best region | per-example gap to oracle |
| Selection/post-processing | right information, wrong final decision | compare chosen vs oracle-best feasible |
| Model/estimation error | predictions noisy or biased | calibration/error plots |
| Irreducible | metric floor, noise, luck | ceiling analysis, repeated runs |

**Rank by metric contribution, not by frequency.** A single catastrophic failure mode can outweigh
hundreds of small ones.

### 6.3 What to instrument (analysis only)

- Per-example: input, prediction, score, all metric terms.
- Decision points: chosen action, alternatives considered, uncertainty.
- Oracle gap: what the score would be with privileged information (closed-form best feasible).
- Tails: the worst K examples with their full trace, not just counts.

> The oracle gap is the most under-used diagnostic in ML tuning: it separates “the model is weak”
> from “the reachable/feasible set is the bottleneck”, and it gives a hard upper bound on what
> tuning can ever achieve.

### 6.4 Decide: parameters or structure?

- If the loss is dominated by a *systematic mechanism* (a wrong scale, a violated invariant, an
  exploitable coupling, a decision rule mismatch) → **structure loop**.
- If the loss is dominated by *smooth sensitivity* to a small number of knobs → **parameter loop**.
- If the loss is dominated by *noise/floor* → stop tuning; improve the estimator or accept.

---

## 7. Phase 3 — Parameter search that is actually informative

### 7.1 Design the search space

- Classify parameters: sensitive vs inert, monotone vs multimodal, coupled vs independent,
  continuous vs discrete vs categorical, static vs schedule/functional.
- Fix inert parameters; focus on sensitive ones; explicitly model interactions among coupled ones.
- Prefer **parameterized schedules** (functions of progress/budget) over dozens of static constants.
- Bound the search using domain priors, but keep one or two "long-shot" tails to detect non-monotonic
  optima.

### 7.2 Strategy selection

| Strategy | Use when | Avoid when |
|---|---|---|
| One-factor-at-a-time (OFAT) | diagnosis, sensitivity screening | strong interactions |
| Factorial / fractional factorial | few parameters, suspected interactions | many parameters |
| Random / Latin hypercube | low effective dimensionality; no strong prior | very expensive evals |
| Bayesian optimization (GP/EI) | expensive evals, ≤ ~20 params, smooth | high dims, heavy noise |
| CMA-ES / evolution | noisy, multimodal, parameter interactions | very expensive evals |
| Successive halving / Hyperband / BOHB | multi-fidelity budget available | fidelity does not rank-correlate |
| Population-based training | schedules/hyperparameters co-adapted | small compute budget |
| Racing with statistical elimination | noisy comparisons, many variants | nonstationary evaluators |

### 7.3 Experiment design rules

- **Pair everything:** same data split, same seeds, same evaluator noise. Common random numbers.
- **Estimate the noise floor** by re-running the baseline k≥5 times; define the minimum detectable
  effect `MDE ≈ 2·std(mean)`. Only accept effects > MDE.
- **Limit simultaneous hypotheses**; use multiple-comparison control (or pre-register a handful).
- **Sweep in batches**, not one-turn-per-experiment; one program → all variants → one table.
- **Coarse-to-fine:** screen broadly with cheap tiers, refine only winners on the full tier.
- **Interactions:** after OFAT winners, run a small factorial over the top 3–5 knobs.
- **Robustness:** evaluate winners across ≥2 independent data/noise draws before adopting.
- **Freeze** a winning configuration before entering a new structural round (avoid mixed causality).

### 7.4 Parameter-loop pseudo-algorithm

```
freeze harness + dev set + baseline
noise = std of k baseline reruns
candidates = prior-informed grid / random sample of promising region
loop until budget or saturation:
    run batch (paired, same tasks/seeds) -> ledger
    rank by mean metric with CI; drop candidates whose upper CI < best lower CI
    if winner improvement < MDE: break
    recenter resampling around winner ± step
freeze winner; re-verify on holdout; record in DECISIONS.md
```

---

## 8. Phase 4 — The parallel execution engine

**Exit criteria:** a reproducible way to launch N variants in parallel, ingest their metrics without
reading raw logs, and reproduce any ledger entry from its config.

### 8.1 Variant management

- Generate variants **programmatically** from a base artifact by overriding declared parameters
  (regex/structured config), never by manual copy-paste forks.
- Every variant is **immutable and hashed**; the ledger stores base hash + override dict + variant hash.
- Keep one canonical base; the delivered artifact is the base with the winning overrides applied at
  the end (no "dev copy" of the deliverable).

### 8.2 Ledger schema (append-only JSONL)

```json
{"ts":"2026-01-01T12:00:00Z","id":"E-0042","phase":"param|structure|verify",
 "base_hash":"ab12…","variant_hash":"cd34…","name":"eta03_firstprobes",
 "overrides":{"ETA":0.03,"FIRST_PROBES":true},
 "dataset":"dev-v3(seed=0,n=1000)","command":"python harness.py variants/… --tasks 1000",
 "metrics":{"mean":0.9745,"median":0.9776,"std":0.0102,"ci95":[0.9737,0.9753],
            "regret_mean":0.0045,"unsafe_tasks":1,"constraint_floor":0.0011},
 "cost":{"wall_s":152,"cpu_s":900,"tokens":0,"gpu_min":0},
 "verdict":"keep|reject|inconclusive","notes":"why"}
```

- `RUNS.md` is **generated** from the ledger (never hand-edited).
- Add a `--tag` per round so results can be re-aggregated by phase.
- Store raw logs under `logs/<id>.txt`; grep/head when needed; never paste them into chat.

### 8.3 Parallelism and resource accounting

- Worker pool = min(#variants, cores − 1); pin threads per worker.
- Account for setup cost (container start, imports, dataset load). Batch small tasks into one worker.
- Monitor load and wall-clock; kill long tails; retry transient errors once with a logged signature.
- Prefer persistent workers/containers for >20 sequential experiments.

### 8.4 Failure handling

- Timeouts with structured error signatures (`TypeError: shape …`), not full tracebacks in context.
- Validators at the interface boundary (shape, domain, NaN) so bad variants fail fast and cheaply.
- Any “invalid output” that crashes the real evaluator is a **hard bug**, not a bad result.

### 8.5 Scaling math (do it before each round)

`round_cost ≈ #variants × (setup + #tasks × per_task × passes) / parallelism`.
If a single full-tier evaluation costs more than ~5% of the total budget, add a cheaper tier or
reduce #variants. If the expected effect is below the MDE at the planned sample size, enlarge the
evaluation set *before* running, not after.

---

## 9. Phase 5 — Statistical discipline

### 9.1 Estimate the noise floor first

- Re-run the baseline k≥5 times on the dev set; report mean, std of the mean, 95% CI.
- `MDE ≈ 2 · std(mean)`. If the expected gain is below the MDE, the experiment is not decision-grade.
- The noise floor depends on sample size: report `std(mean) ∝ 1/√n`; choose n to resolve the
  smallest effect that matters.

### 9.2 Paired comparisons

- Same tasks/seeds/noise for every candidate → compare paired deltas per example, not aggregate means.
- Use paired bootstrap CIs, sign tests, or Wilcoxon. Means hide tail behavior; report quantiles too.
- For heavy-tailed metrics (occasional catastrophic examples), report tail counts and the worst-K.

### 9.3 Multiple comparisons

- Screen many variants cheaply; confirm few. Pre-register the confirmation set.
- Apply family-wise control for claims, or simply require a large margin above the noise floor.

### 9.4 Overfitting the dev set

- Never select on the holdout. Rotate/expand the dev set if many rounds are needed.
- Evaluate finalists on ≥2 independent draws (fresh seeds/datasets) and report the distribution.
- Prefer configurations with lower variance and similar mean over high-variance winners.
- Watch for “dev-specific” wins driven by a few examples; check the per-example delta distribution.

### 9.5 Decision rule template

```
accept variant  if  paired_mean_delta > max(MDE, min_effect_of_interest)
                and no regression on any hard constraint
                and tail_count_unsafe does not increase
reject          otherwise (inconclusive if within MDE and hypothesis matters)
```

---

## 10. Phase 6 — Structural / novel solution search (the high-leverage loop)

> **Core lesson:** parameter tuning performs local search on a point; structural insight changes the
> manifold. In the reference run, all knob tuning together moved the score ~+0.001, while one
> discovered identity between the observation channels moved it ~+0.030 — and the remaining gap was
> mathematically irreducible, not a tuning failure.

### 10.1 The leverage ladder (usual ROI order)

1. **Metric archaeology** — reformulate the objective using the exact scoring structure
   (weights, normalization, indicators, clipping, tie-breaking). Optimize the metric, not a proxy.
2. **Generative-process archaeology** — understand how data/observations are produced. Look for
   exogenous randomness, invariants, physics, symmetries, hidden parameters, or deterministic
   couplings between signals.
3. **Cross-signal exploitation** — use a *low-noise or cheap* channel to infer/supervise a
   high-noise or expensive channel. (Reference example: an almost noiseless constraint signal
   determines the noisy objective up to a constant.)
4. **Oracle-gap analysis** — compute the best possible score with privileged information. If the gap
   is large, the problem is reachable; if small, stop optimizing and improve the estimator/decision.
5. **Reformulation / decomposition** — closed-form subproblems, normalization, transformation of the
   target, constraint elimination, symmetry reduction, dimensionality reduction.
6. **Model class** — linear → tree/ensemble → kernel → neural → probabilistic → hybrid; right
   inductive bias beats more capacity.
7. **Decision rule / post-processing** — thresholds, calibration, abstention, selection rules,
   metric-aware final choice, ensembles, ranking vs regression.
8. **Algorithm / schedule** — optimization algorithm, curriculum, data order, annealing,
   exploration schedule.
9. **Environment / measurement** — better proxies, stratified/active evaluation, better diagnostics.

### 10.2 The insight-hunt playbook (how to find wins that are not parameters)

Run these as short, cheap probes; each is a *hypothesis generator*:

- **Read the grader.** Differentiate each term; ask what behavior it rewards and punishes; compute
  the ceiling.
- **Question the documentation.** Verify every stated prior empirically (neural nets, reward
  functions, thresholds and defaults are often misdescribed). Maintain a “facts vs claims” table.
- **Look for conservation laws / identities.** “Signal A = const + c·Signal B” relationships can
  let one measurement supervise another. Fit/testing such relations on a small sample is cheap.
- **Compare noise levels.** Which channels are reliable? Can a reliable channel denoise an
  unreliable one? (Common in calibration, weak supervision, physics-informed ML, sensor fusion.)
- **Find asymmetry.** Asymmetric costs/penalties mean the optimal *decision rule* differs from the
  optimal *prediction*; thresholds and abstention are often worth more than model tuning.
- **Compute the oracle.** If you knew the hidden truth, what would the score be? The gap is your
  maximum headroom and tells you which stage (estimation vs decision vs reach) is weak.
- **Study the tails.** The worst 1% often dominate the mean; a mechanism fix for the tail can beat
  weeks of average-case tuning.
- **Probe mechanisms.** Instrument internal state at decision points; test one mechanism per probe.
- **Borrow analogues.** Search literature/other domains for the same mathematical object
  (e.g., safe exploration, constrained bandits, calibration, retrieval reranking).
- **Adversarial red-team.** Ask: how could a rational competitor maximize this metric? What would
  “too good to be true” look like? Then check whether that mechanism is legitimate.

### 10.3 Idea funnel

```
IDEAS.md entry: {claim, mechanism, expected_gain, p(success), cost, cheapest_test, status}
            ↓ expected value per cost
cheapest discriminating experiment (one variable, pre-registered outcome)
            ↓ accept / reject / inconclusive
promote to implementation plan → robust artifact → verification
```

- Keep an explicit **idea backlog**. Score ideas by `expected_gain × confidence / cost`.
- Reserve **20–40% of budget** for structural ideas; protect it from parameter-loop drift.
- Re-read the backlog every round; an idea rejected early may become viable after new facts.
- Record negative results: “tried X, effect was Y, mechanism rejected” is first-class knowledge.

### 10.4 Oracle-gap and ceiling analysis template

```
For each example:
  score_actual      = metric(model output)
  score_oracle      = metric(best feasible output with privileged information)
  gap_estimation    = score_oracle − score(model with oracle decision)
  gap_decision      = score(model with oracle decision) − score_actual
Aggregate: mean/median of each gap, tail counts, decomposition by failure category.
Decision: attack estimation (gap_estimation) or decision/reach (gap_decision) or stop (small).
```

### 10.5 From insight to robust artifact

- An insight found via instrumentation must be re-expressed as an algorithm that uses **only the
  permitted inputs**; verify it on the harness *without* privileged access.
- Prefer identities/invariants that are structural (true for the whole problem family) over
  per-example constants that may not generalize.
- Write the mechanism into `DECISIONS.md` with evidence and expected effect; pre-register the test.
- Re-run a parameter sweep *after* a structural change — the optimal knobs move.

### 10.6 Legitimacy filter (write it before you need it)

- Allowed: exploiting public structure, documented distributions, metric algebra, symmetry,
  available auxiliary signals, domain knowledge.
- Usually forbidden: modifying the evaluator, extracting private labels, hard-coding test answers,
  reverse-engineering RNGs to memorize tasks, leaking held-out data into training.
- If an insight requires privileged introspection, use it for **analysis only** and rebuild an
  honest equivalent before shipping. State this explicitly in the final report.

### 10.7 Track leverage (learn where to invest next)

Keep a simple table per round:

| Change type | Example | Gain | Cost | Note |
|---|---|---|---|---|
| bug fix | unit/scale mismatch | +0.54 | low | diagnostic-driven |
| constraint handling | conservative envelope | +0.02 | low | safety |
| structural insight | cross-signal identity | +0.03 | medium | biggest win |
| schedule tuning | exploration weight | +0.001 | low | saturates |
| model bank | kernel family | +0.000 | low | no effect |

After a few rounds, allocate budget to the columns that historically paid off in **this** domain.

---

## 11. Phase 7 — Token and context efficiency

### 11.1 Principles

- **Files are truth; context is cache.** Everything decision-relevant is written to a file and
  reloaded by search, never re-derived or re-read wholesale.
- **Compress at every boundary.** Tool output → digest; experiment → one ledger line; log → error
  signature; paper → 5 bullets.
- **The cheapest token is the one you never emit.** Never paste raw logs, never `cat` large files,
  never re-read a file you just wrote.

### 11.2 Concrete budget rules

| Artifact | Budget | Implementation |
|---|---|---|
| Single tool output | ≤ ~2 KB | grep/head/tail/count/aggregate in the command |
| Experiment record | 1 JSONL line | schema in §8.2 |
| Subagent report | ≤ 15 lines | what / number / path / not verified |
| Round summary | ≤ 30 lines | generated table + decision |
| “Facts” file | append-only bullets | `FACTS.md`, reloaded by grep |
| Raw logs | on disk only | `logs/<id>.txt`, inspect only on failure |

### 11.3 Execution patterns

- **One program, many experiments**, print one table — not one turn per experiment.
- **Batch shell/Python calls**: generate variants, run, parse, write ledger in one command.
- **Background jobs + one long wait**: start expensive work, do independent work, collect once.
  Never poll in a loop.
- **Subagents for noise**: delegate exploration/recon/red-team to fresh-context subagents that return
  digests. Fork only when the child needs this conversation.
- **Stable prefix, append-only ledger, periodic compaction**: summary files keep context small as
  the project grows.
- **Failure logging**: one line with error type + first frame + repro command; keep the traceback on
  disk. If a failure repeats, fix the harness, don’t re-read the traceback.

### 11.4 Context layout

```
STABLE (rarely changes)         APPEND-ONLY                PERIODIC
brief + metric + facts  |  ledger, decisions, results  |  NOTES.md compaction
skills/playbooks        |  idea backlog updates        |  "what we know" summary
```

### 11.5 Token budget accounting

Estimate tokens per phase at plan time; log actuals in `LEDGER`/`NOTES`; alarm at 150% of the phase
budget without a metric improvement. Token efficiency is measured as *score gain per 1k tokens*, not
tokens per se.

---

## 12. Phase 8 — Budgets, risk, and stopping

### 12.1 Budget dimensions

wall-clock, compute (CPU/GPU-min), tokens, money, number of graded submissions, human interruptions.
Write the budget in `BRIEF.md`; allocate per phase; alarm at 150% of a phase without progress.

### 12.2 Kill criteria (pre-registered)

For each approach, before running: “if metric gain < X after Y experiments / Z cost, stop this
approach and re-plan.” An agent that never kills an approach is not efficient.

### 12.3 Practical optimum and stopping rule

```
practical_optimum = theoretical_ceiling − irreducible_penalties − reachability_floor − safety_floor
stop when  expected_gain_of_next_round < max(MDE, cost_of_round_in_budget_terms)
```

- Compute the irreducible components from the metric decomposition and oracle gap (§10.4).
- When the remaining gap is dominated by floors, more tuning **cannot** help; shift to verification
  or documentation.
- If the metric is noisy at the chosen sample size, enlarge the evaluation set or accept the noise;
  do not chase noise.

### 12.4 Risk register (default)

| Risk | Detection | Mitigation |
|---|---|---|
| Overfitting dev | holdout score drops | rotate/expand dev, confirm on fresh draw |
| Harness drift | replay vs real Δ grows | differential test each version, freeze harness |
| Nondeterminism | identical reruns differ | seeds, thread pinning, deterministic ops |
| Evaluator change | sudden metric shift | version-pin evaluator; record hashes |
| Submission limits | count near cap | track in ledger; reserve final runs |
| Resource contention | wall-clock inflation | thread pinning, worker caps |
| Leakage / illegitimate shortcut | privileged info in artifact | policy check, independent audit |
| Silent metric miscomputation | ledger math bug | unit-test the reporting code itself |

---

## 13. Phase 9 — Verification and shipping

**Exit criteria:** the exact grading command passes in the final environment on the final artifact;
a residual-risk statement and reproduction commands are written.

Checklist:

- [ ] Rebuild the artifact from the canonical base + winning config (no manual forks).
- [ ] Run the **exact** grading command, not a close approximation.
- [ ] Fresh environment / clean checkout / pinned deps.
- [ ] Fresh holdout or fresh random evaluation set (not the tuning set).
- [ ] Multiple runs for stochastic graders; report mean + interval + worst case.
- [ ] Artifact hash and provenance in the report.
- [ ] Interface/validity tests: shape, range, NaNs, edge inputs, zero-data cases.
- [ ] No forbidden dependencies, files, secrets, or test-set leakage in the artifact.
- [ ] Residual risk: what could still be wrong, and its expected cost.
- [ ] Reproduction: three commands from clean → verified number.
- [ ] Cleanup: stop background jobs, remove scratch, keep ledger + verification evidence.
- [ ] Final report: result/was, verified-by, change, rejected ideas, residual risk, reproduce, next.

---

## 14. Anti-patterns catalog (generalized)

| Symptom | Root cause | Fix |
|---|---|---|
| Score stuck after many knob sweeps | wrong scale/unit bug or wrong objective term | decompose metric; unit-test predictions vs observations |
| Great dev score, worse holdout | overfitting the tuning set | holdout, rotation, paired fresh draws |
| Tuning “improvements” vanish | effects inside noise floor | measure MDE first; paired tests |
| Optimizer chases a saturated term | no ceiling/floor analysis | `METRIC.md` with headroom per term |
| Local optimum trap | expansion/exploration schedule too short | schedule exploration budget explicitly |
| Safety/constraint violations during search | overconfident model / missing margin | worst-case envelope, conservative early model |
| Bad variants crash the grader | no interface validator | fail fast at boundary; domain/shape/NaN checks |
| Two versions of the truth | dev copy of deliverable | one base + overrides; generated variants only |
| Long agent runs with little signal | one experiment per turn, raw logs in context | batch + digest + ledger |
| Duplicate work across agents | no shared brief / no “do not re-derive” list | brief + disjoint scopes + contracts |
| Expensive full runs on unpromising ideas | no multi-fidelity ladder | racing/successive halving |
| Analysis paralysis | no budget/alarm/kill criteria | phase budgets + andon cord + stop rule |
| Metric looks too good | leakage/proxy artifact | red-team; oracle-gap; holdout audit |
| Lost knowledge between sessions | context-only state | files: FACTS/IDEAS/DECISIONS/LEDGER |
| Spent all budget on knobs | no idea-level explore/exploit | reserve 20–40% for structure |

---

## 15. Domain transfer matrix

What stays constant: the loop (frame → instrument → baseline → diagnose → experiment → verify),
paired comparisons, ceiling/floor analysis, holdouts, ledger + digests, budget/stop rules.
What changes: the metric, the evaluation cost, the leverage points, the noise model, the failure modes.

| Domain | Typical metric | Eval cost / noise | Highest-leverage structural moves | Special risks |
|---|---|---|---|---|
| **Vision (classification/detection/segmentation)** | accuracy, mAP, IoU, F1 | minutes–hours; seed noise | loss/preprocessing/threshold calibration; test-time augmentation; label noise handling; class balance | leakage via near-duplicate images; augmentation/test mismatch |
| **NLP / LLM fine-tuning** | accuracy, F1, ROUGE/BLEU, win rate, judge score | expensive; high variance | data curation/ordering, prompt/format, decoding, LoRA rank/targets, calibration, distillation, rubric exploitation (legit) | judge instability; contamination; overfitting benchmark style |
| **Prompt / agent tuning** | task success, judge score, cost/latency | cheap–medium; high variance | instruction structure, tool schema, few-shot selection, decomposition, self-consistency, stopping rules | evaluator drift; reward hacking of judge; non-reproducible sampling |
| **Tabular ML** | AUC/PR, RMSE, calibration | fast; low noise | feature engineering, leakage removal, categorical encoding, monotone constraints, calibrated ensembles, metric-aware thresholds | target leakage; train/serve skew; distribution shift |
| **RL** | return, success rate, safety cost | expensive; very noisy | reward shaping (careful), exploration schedule, safety shield, action space, horizon, curriculum, model-based rollouts | reward hacking; seed variance; simulation-to-real gap |
| **Time series** | MAE/sMAPE/MASE, coverage | fast–medium | leakage-free CV, horizon stationarity, decomposition, hierarchical reconciliation, quantile calibration | temporal leakage; nonstationarity; evaluation window mismatch |
| **Recommender / retrieval** | NDCG, recall@k, CTR | medium; noisy | candidate generation, reranking, negative sampling, position bias correction, diversity/calibration | feedback loops; position bias; metric gaming |
| **Scientific ML / AutoML** | R², MAE, physical consistency | expensive; low noise | generative/physics invariants, symmetry constraints, uncertainty calibration, surrogate modeling, active learning | unphysical extrapolation; hidden data coupling |
| **Data pipelines / ETL** | freshness, correctness, cost | cheap, deterministic | schema/invariant checks, idempotency, query rewriting, partitioning, caching | silent schema drift; partial failures |

**Asset mapping:** the Metric Engineer is universal; the Recon role scales with domain unfamiliarity;
the Structure Scout is most valuable where the metric is complex and the data-generating process is
learnable; the Statistician is essential wherever evaluation is noisy or expensive.

---

## 16. Improving the framework (roadmap)

### 16.1 Maturity stages

| Version | Capability | Deliverables |
|---|---|---|
| **v0.1 (this doc)** | Manual phases, exact harness, parallel parameter sweeps, ledger | templates, checklists |
| **v0.2** | Standard interfaces + auto statistics + runner | `Evaluator` protocol, paired stats module, `sweep` CLI, generated `RUNS.md` |
| **v0.3** | Cost-aware scheduler + multi-fidelity racing + BO | scheduler with expected-value-per-cost; early elimination; search-space priors |
| **v0.4** | Insight agents | metric archaeologist, data archaeologist, oracle-gap analyst, tail analyst; idea backlog with EV/cost; automatic mechanism probes |
| **v0.5** | Code-mutation loop | LLM-generated structural variants + automatic test/verification gating; novelty search |
| **v1.0** | Meta-learning | per-domain playbooks; transfer priors across projects; self-post-mortem that updates the playbook; shared facts base |

### 16.2 Concrete enhancements to design next

1. **Standard `Evaluator` protocol** (the most important interface):
   ```python
   class Evaluator(Protocol):
       def run(self, artifact, examples, seeds) -> Result: ...
       # Result: per-example scores + metric terms + failures + cost + artifact hash
   ```
   Everything (sweep, racing, stats, dashboard) is built on this, so domains plug in by implementing
   one adapter.
2. **Automatic paired statistics**: the runner returns paired deltas vs a reference from the ledger;
   the framework decides keep/reject/inconclusive by default, with the decision rule configurable.
3. **Cost-aware scheduler**: maintain a queue of experiments with `(expected_gain, p_success, cost)`;
   allocate workers to maximize expected improvement; kill jobs whose upper bound is below the
   current incumbent (racing).
4. **Automatic ceiling/floor analysis**: from per-term metric outputs, compute headroom and
   irreducible components; warn when the expected remaining gain is below the MDE.
5. **Idea backlog with EV scoring**: every idea carries `expected_gain, confidence, cost, cheapest
   test, status`; the orchestrator schedules ideas and parameters together.
6. **Insight agents**: specialized probes (cross-channel relation fitting, oracle-gap, tail clustering,
   assumption verification) that return mechanism hypotheses with evidence and a cheapest test.
7. **Code-mutation loop**: an LLM proposes structural mutations to a base artifact; each mutation is
   compiled, unit-tested, and evaluated on a pilot tier; only survivors enter the sweep. Guard with
   the legitimacy filter and a frozen harness.
8. **Harness CI**: a tiny differential test runs on every harness change and blocks if
   replay↔real divergence exceeds tolerance.
9. **Ledger query tooling**: `hpt status`, `hpt best --metric`, `hpt compare A B`, plus a generated
   Markdown table with CIs — no reading logs.
10. **Reproducibility manifests**: every ledger line carries base hash, dataset hash, environment
    hash, and the exact command; any line can be replayed with one command.
11. **Submission/quota accounting**: track graded runs against limits; reserve the final verification
    runs; never burn quota on exploratory sweeps.
12. **Self-post-mortem**: after each project, record which change types paid, which diagnostics
    caught bugs, which harness decisions saved time — append to this playbook.

### 16.3 Meta-metrics for the tuner itself

- **Time-to-first-signal**: time until a valid metric with the exact harness.
- **Evaluations-to-MDE**: experiments needed to resolve the smallest meaningful effect.
- **Score gain per compute-hour / per 1k tokens.**
- **Rework rate**: fraction of experiments invalidated by harness/interface bugs.
- **Human interventions per project.**
- **Claim-at-ship accuracy**: fraction of shipped claims that reproduced.
- **Leverage ratio**: gain from structural vs parameter changes (tracked over projects).

### 16.4 Guardrails

- Frozen evaluator; all changes versioned and differential-tested.
- Explicit legitimacy policy in `BRIEF.md`; independent check that the artifact uses only allowed
  inputs.
- Audit trail: every shipped number traceable to a ledger record + artifact hash.
- Never trade correctness/validity for score; hard constraints are vetoes, not weights.

---

## 17. Templates

### 17.1 `BRIEF.md`

```markdown
# Brief
Objective (one sentence, direction, units):
Metric command: <exact command>   Reference: <baseline/current/target>
Metric decomposition file: METRIC.md
Environment: <container/deps/hardware>
Hard constraints: <validity, safety, latency, submission limits…>
Soft constraints: <cost, style…>
Allowed: <files, data, actions>
Forbidden: <test leakage, evaluator edits, privileged inputs…>
Data policy: <dev/holdout/oracle rules>
Budget: <wall-clock | compute | tokens | graded runs | human interruptions>
Definition of done: <artifact path + number + verification command>
Kill criteria: <numeric conditions that end an approach>
```

### 17.2 `METRIC.md` skeleton

```markdown
# Metric
Formula / code path: <link or excerpt>
Terms: | term | weight | achievable max | floor | headroom | notes |
Ceiling: <theoretical max>   Practical optimum: <ceiling − irreducible>
Irreducible losses: <list with evidence>
Hard trade-offs: <e.g., penalty A vs relative loss B>
Decision rule implications: <what the optimum action looks like>
```

### 17.3 Idea backlog (`IDEAS.md`)

```markdown
| id | claim / mechanism | expected gain | confidence | cost | cheapest test | status |
|----|-------------------|---------------|------------|------|---------------|--------|
| I-01 | observation A determines B up to a constant → denoise B | +0.02 | 0.5 | 2h | fit relation on 50 samples | promoted |
| I-02 | calibrated threshold beats argmax under asymmetric costs | +0.005 | 0.6 | 1h | replay per-example outputs | rejected |
```

### 17.4 Variant spec

```json
{"name": "w_quad02",
 "base": "artifact.sha256:ab12…",
 "overrides": {"ETA_SAFE": 0.03, "FIRST_PROBES": true, "QUAD_WINDOW": 0.2},
 "notes": "winner of round 3"}
```

### 17.5 Sweep runner skeleton

```python
def sweep(base, configs, evaluator, dev_set, seeds, workers, ledger):
    variants = [make_variant(base, c) for c in configs]        # immutable, hashed
    with WorkerPool(workers) as pool:
        results = pool.map(lambda v: evaluator.run(v, dev_set, seeds), variants)
    summarize(results, ledger, reference=ledger.best("dev"))
    # default decision: paired delta vs reference, require > MDE, no constraint regression
    return decide(results, mde=ledger.noise_floor())
```

### 17.6 Report templates

**Experiment report (≤15 lines):** what changed · metric delta (paired, CI) · cost · artifact path ·
not verified · next recommendation.

**Final report:**
```markdown
Result: <number> (was <number>); verified by <exact command> in <environment>
Change: <files/params, ~lines, one-line rationale>
Structural insights: <mechanism + evidence>
Tried and rejected: <experiment: number>
Remaining loss: <decomposition; floors vs reachable>
Residual risk: <what could still be wrong>
Reproduce: <3 commands>
Open items: <next steps>
```

### 17.7 Agent spawn prompt contract

1. Role, one-sentence mission, shared brief.
2. Facts already established — **do not re-derive**.
3. Exact metric command and how to read it.
4. Write scope and forbidden paths.
5. Resource cap (threads/model/time/turns).
6. Deliverable: exact path, format, ≤15-line report.
7. Join protocol: when to report, what to do if blocked.

---

## 18. Reference micro-case (evidence, not the point)

**Setting:** hidden, obfuscated evaluator; 100 stochastic tasks × 21 sequential decisions; score =
1 − 0.4·normalized regret − 0.6·sigmoid(3·unsafe − 3.25) − 0.15·deadzone indicator; ceiling 0.978.

**What generalized, in order of impact:**

1. **Metric archaeology** revealed the penalty structure and the exact additivity, and that the
   deadzone was a fixed penalty worth trading against small regret → the final decision rule was
   reformulated as a two-term metric maximization, not “pick the best prediction”.
2. **Instrumentation + exact replay** turned a ~4 s/100-task black box into a deterministic,
   per-example-diagnosable harness, verified to ~1e-8 against the grader. This enabled all later
   paired experiments and tail diagnosis.
3. **Diagnosis beat tuning:** a unit/scale bug and an overconfident model dominated the early loss;
   fixing them moved the score far more than any knob.
4. **Generative-process archaeology** found a deterministic identity between the two observation
   channels, letting the cheap/noiseless channel supervise the noisy one (+~0.03).
5. **Parameter tuning** (single-factor sweeps + holdout) then added ~+0.001; a two-probe safe
   start-up and a metric-aware final refinement added small but repeatable gains.
6. **Stopping rule:** ceiling-minus-irreducible analysis showed the remaining gap was a deadzone
   floor + reachability limit, i.e. not tunable. Final verified score ~0.975–0.977 across runs.

**Transferable takeaways:** build the oracle; decompose the metric; diagnose before tuning; use
paired, noise-aware comparisons; hunt for cross-signal identities and metric-aware decision rules;
keep a holdout; stop at the practical optimum; verify with the exact grader.

---

## 19. Quick reference card

**Before any work**
- [ ] Objective sentence, metric command, reference numbers, ceiling/floor analysis started.
- [ ] Constraints + data policy + allowed/forbidden written.
- [ ] Budget + phase alarms + kill criteria.
- [ ] Prior art inventoried; shared brief written; scopes assigned.

**Every experiment**
- [ ] One hypothesis, one variable (or a pre-registered small factorial).
- [ ] Paired with reference on identical data/seeds; noise floor known.
- [ ] Predicted outcome written *before* running.
- [ ] Cost recorded; result ingested as one ledger line; raw log on disk only.
- [ ] Decision: keep / reject / inconclusive (with rule).

**Every round**
- [ ] Idea backlog reviewed; structural share of budget protected.
- [ ] Leverage table updated (what type of change is paying?).
- [ ] Facts/decisions files updated; stale assumptions removed.
- [ ] Andon if 150% of phase budget without metric improvement.

**Before shipping**
- [ ] Rebuilt from canonical base + winning config; artifact hashed.
- [ ] Exact grading command in the final environment on the final artifact.
- [ ] Fresh holdout; multiple runs if stochastic; distribution reported.
- [ ] Validity/interface/edge-case tests passed.
- [ ] Residual risk + reproduce commands + final report written.
- [ ] Background jobs stopped; scratch cleaned; evidence retained.

**Post-mortem (every project)**
1. What was the decisive fact, and when did we learn it?
2. Where did we spend the most cost for the least information?
3. Which rule would have prevented the biggest waste?
4. Which structural insight paid off, and what probe found it?
5. Add 1–3 generalized lessons to this document; delete rules that never fired.

---

## 20. Glossary

- **Oracle / harness:** fast, exact replay of the real evaluator used for iteration.
- **Metric term:** an additive component of the score (reward, penalty, indicator).
- **Ceiling / practical optimum:** theoretical max / max minus irreducible losses.
- **Floor:** a penalty/shortfall you cannot avoid; tuning beyond it is wasted.
- **Oracle gap:** difference between the achievable score with privileged information and the current
  score; bounds headroom and localizes the weak stage.
- **MDE:** minimum detectable effect at a given sample size and noise level.
- **Paired comparison:** comparing variants on identical examples/seeds/noise.
- **Multi-fidelity:** evaluating candidates on cheaper, smaller, rank-correlated tiers first.
- **Racing / successive halving:** eliminate weak candidates on cheap tiers; promote survivors.
- **Leverage ladder:** ordered list of structural change types by typical return.
- **Idea backlog:** explicit queue of structural hypotheses scored by expected gain × confidence / cost.
- **Practical stopping rule:** stop when expected gain of the next round < max(MDE, round cost).
- **Andon cord:** stop-and-re-plan signal when a phase exceeds its budget without improvement.
- **Ledger:** append-only JSONL record of every experiment (the project’s memory of truth).

---

*This document is meant to evolve. After each project, add one generalized lesson and one concrete
framework improvement — never a project-specific anecdote without a transferable rule.*

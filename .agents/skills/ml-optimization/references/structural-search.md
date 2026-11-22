# Structural Solution Search (High-Leverage Outer Loop)

Load during **Phase 2 (Diagnosis)** and **Phase 3 (Structural Search)**.

> Parameter tuning moves a point along a fixed manifold; structural insight changes the manifold. Reserve **20–40% of total budget** for structural hypotheses and protect it from parameter-sweep drift.

---

## 1. The Leverage Ladder (Typical ROI, Highest First)
1. **Metric archaeology:** reformulate loss/objective to match exact scoring algebra.
2. **Generative-process archaeology:** uncover exogenous noise, invariants, symmetries, physics, or hidden couplings.
3. **Cross-signal exploitation:** use a low-noise/cheap signal to denoise or supervise a high-noise/expensive channel.
4. **Oracle-gap analysis:** measure best feasible score with privileged truth to pinpoint *which stage* is weak.
5. **Reformulation & decomposition:** closed-form subproblems, target transforms, constraint elimination, normalization.
6. **Model class / inductive bias:** linear, GBDT, kernel, neural, probabilistic, or hybrid suited to data geometry.
7. **Decision rule & post-processing:** metric-aware thresholds, calibration, abstention, reranking, ensembling.
8. **Algorithm / schedule:** curriculum, annealing, exploration schedule, active sampling.
9. **Parameters:** local knob sweeps (inner loop — run *after* structural moves stabilize).

---

## 2. Oracle-Gap & Loss Decomposition Template
Compute per example on the dev harness (for analysis only):
```text
score_actual   = metric(model_output)
score_oracle   = metric(best_feasible_output_with_privileged_truth)
gap_estimation = score_oracle - metric(model_prediction + oracle_decision_rule)
gap_decision   = metric(model_prediction + oracle_decision_rule) - score_actual
```
- **Large `gap_estimation`:** improve features, model class, denoising, or cross-signal supervision.
- **Large `gap_decision`:** fix thresholds, calibration, constraint margins, or post-processing.
- **Small total gap:** near practical optimum — stop tuning and verify/ship.

Rank failure modes by **total metric contribution**, not occurrence count (one tail catastrophe often outweighs hundreds of small errors).

---

## 3. Insight-Hunt Playbook (Cheap Hypothesis Generators)
Run targeted, single-variable probes:
- **Verify documentation empirically:** maintain a *Claims vs. Measured Facts* list; stated priors, defaults, and reward terms are often wrong or subtle.
- **Test conservation laws / identities:** check whether `signal_A ≈ f(signal_B)` on 50 samples; deterministic couplings yield massive denoising wins.
- **Compare signal-to-noise across channels:** let clean channels guide or bound noisy ones.
- **Inspect the worst-K tails:** dump full decision traces for the worst 1% examples; a targeted mechanism fix beats weeks of average-case tuning.
- **Exploit cost asymmetry:** whenever false positives and false negatives (or safety vs. regret) have unequal penalties, Bayes-optimal action ≠ argmax prediction.
- **Adversarial red-team:** ask *"how could a rational competitor get an unreasonably high score?"* Check whether that mechanism is legitimate or exposes a metric quirk.

---

## 4. Idea Funnel & Leverage Tracking
Score every structural hypothesis in `IDEAS.md` by `EV/cost = (expected_gain × confidence) / cost`:
```markdown
| ID | Hypothesis / Mechanism | Est. Gain | Conf | Cost | Cheapest Probe | Status |
|---|---|---|---|---|---|---|
| I-01 | Low-noise channel B predicts noisy A up to offset | +0.020 | 0.5 | 1h | Fit linear relation on 50 samples | promoted |
| I-02 | Metric-aware threshold beats argmax | +0.005 | 0.6 | 30m | Replay saved dev logits | rejected |
```
- Pre-register expected effect *before* running the probe.
- Log rejected ideas explicitly — negative results prevent future loops from re-testing dead ends.
- Track a **Leverage Table** (change type → measured gain → cost) and shift future budget toward categories actually paying off in this domain.

---

## 5. Legitimacy Filter (Write in `BRIEF.md` at Phase 0)
- **Allowed:** exploiting public structure, metric algebra, documented distributions, symmetries, available auxiliary signals, domain physics.
- **Forbidden:** modifying the evaluator, extracting private test labels, hard-coding test answers, leaking held-out data into training, or using privileged harness state inside the shipped artifact.
- **Rule:** Any insight found via privileged analysis must be re-expressed as an honest algorithm using *only* permitted inputs, then verified on the clean harness.

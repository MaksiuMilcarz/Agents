# Domain Transfer Matrix & ML Templates

Load when adapting `ml-optimization` to a specific ML/data domain or creating `METRIC.md`.

---

## 1. Domain Transfer Matrix

| Domain | Typical Metric | Eval Cost / Noise | Highest-Leverage Structural Moves | Special Risks |
|---|---|---|---|---|
| **Vision** | Accuracy, mAP, IoU, F1 | High / seed noise | Loss & threshold calibration, TTA (validate!), label-noise cleanup, resolution/crop parity | Near-duplicate leakage; train/test augment skew |
| **NLP / LLM Fine-Tuning** | Accuracy, F1, win rate, rubric | High / high variance | Data curation & ordering, format/prompt alignment, decoding strategy, LoRA targets, distillation | Judge instability, contamination, style overfitting |
| **Prompt / Agent Tuning** | Task success, rubric, cost/latency | Low–med / high variance | Decomposition, tool schema clarity, few-shot selection, verifier loops, stopping rules | Evaluator drift, judge reward-hacking, sampling variance |
| **Tabular ML** | AUC/PR, RMSE, log-loss | Fast / low noise | Feature engineering, leakage removal, target encoding, monotone constraints, calibrated ensembles, threshold tuning | Target leakage, train/serve skew, distribution shift |
| **RL** | Return, success, safety cost | High / very noisy | Safety shield, action-space design, exploration schedule, curriculum, model-based rollouts | Reward hacking, seed variance, sim-to-real gap |
| **Time Series** | MAE, sMAPE, MASE, coverage | Fast–med | Leakage-free rolling CV, decomposition, stationarity transforms, quantile calibration, hierarchical reconciliation | Temporal leakage, nonstationarity, horizon mismatch |
| **RecSys / Retrieval** | NDCG, Recall@k, CTR | Med / noisy | Candidate recall, negative sampling, reranking features, position-bias debiasing, diversity calibration | Feedback loops, position bias, metric gaming |
| **Scientific ML / BO** | R², MAE, regret, physics loss | Med–high / low–med | Physics/symmetry invariants, cross-signal identities, uncertainty calibration, surrogate class | Unphysical extrapolation, hidden channel coupling |
| **Data Pipelines / ETL** | Correctness, latency, cost | Cheap / deterministic | Schema invariants, query rewriting, partitioning, idempotency, caching | Silent schema drift, partial writes |

---

## 2. `METRIC.md` Template
```markdown
# Metric Decomposition
- **Exact formula / code path:** `<path or equation>`
- **Direction:** maximize | minimize
- **Theoretical ceiling:** `<val>` | **Practical optimum:** `<val>`

## Term Breakdown
| Term | Weight | Max Contribution | Irreducible Floor | Headroom | Status |
|---|---|---|---|---|---|
| <term_1> | <w> | <max> | <floor> | <headroom> | headroom / saturated / floor-bound |

## Hard Trade-Offs & Decision-Rule Implications
- <e.g. fixed penalty A vs continuous regret B -> optimal threshold/abstention rule>
```

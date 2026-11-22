---
name: verify-and-ship
description: Independently verify changes in the exact target environment, run adversarial edge-case checks, clean scratch artifacts, and produce a concise evidence-backed final report. Use before declaring any non-trivial software or ML task complete.
---

# Verify and Ship

**Verification is the product.** Never declare a task done because code compiles or "looks right."

---

## Five-Step Verification Protocol

### 1. Environment & Command Parity
- Run the **exact** CI, test, or grading command verbatim in the target environment (same container, pinned dependencies, same interpreter/flags).
- A local approximation is a pilot, never a ship gate.

### 2. Reference Comparison
- Compare the verified output against the recorded baseline, spec target, or prior commit.
- A number or green test without a baseline comparison is incomplete evidence.

### 3. Adversarial Pass (Try to Falsify)
Ask *"what would make this fail?"* before *"does this look right?"*:
- **Boundary & edge cases:** empty inputs, nulls, NaNs, zero-length collections, large inputs, invalid shapes/schemas.
- **Determinism & clean start:** re-run from a clean state or multiple seeds (if stochastic) to rule out flaky passes or stale caches.
- **Fresh-context check (high-stakes changes):** For security, data integrity, money, irreversible actions, or gameable metrics, run an isolated read-only Verifier subagent that did *not* author the code to counter confirmation bias.

### 4. Artifact Integrity & Cleanup
- Review the full diff (`git diff --stat` and targeted inspection): confirm one clear reason per change, zero unintended edits, zero dev forks, zero secrets/credentials.
- Confirm the shipped artifact is the exact version that was verified (commit SHA or content hash) and that the revert path is clear.
- Stop orphaned background processes and remove temporary scratch directories while retaining durable evidence (tests, ledger, reports).

### 5. Calibrated Final Report
Present a compact, evidence-first summary (≤ 15 lines for routine work; structured template for major work):
- **Result:** exact verified outcome vs. baseline + exact command & environment.
- **Changes:** modified files + concise rationale.
- **Tried & rejected** (if applicable): negative results worth preserving.
- **Residual risk:** explicitly state what was *not* tested or could still fail.
- **Reproduce:** 1–3 exact commands from clean state to verified result.

Load [references/checklists.md](references/checklists.md) for the full pre-ship checklist and final report template.

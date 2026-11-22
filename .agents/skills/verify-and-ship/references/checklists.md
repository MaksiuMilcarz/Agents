# Pre-Ship Checklists & Report Template

## Pre-Ship Checklist
- [ ] **Canonical artifact:** Built from one source of truth (no manual dev copies).
- [ ] **Exact command:** Verbatim CI/test/grading command executed in the final environment.
- [ ] **Baseline delta:** Before/after numbers or test counts recorded with evidence.
- [ ] **Edge & validity checks:** Empty, malformed, boundary, and error paths tested.
- [ ] **Determinism / variance:** Re-run verified (or mean + CI + worst case reported if stochastic).
- [ ] **Diff & hygiene:** Clean `git status`; no debug prints, secrets, temp files, or stray edits.
- [ ] **Runtime cleanup:** Background jobs/servers stopped unless explicitly requested to persist.
- [ ] **Revertability:** Clear rollback path (commit hash or backup).

## Final Report Template
```markdown
**Result:** <verified outcome / metric> (baseline: <before>); verified via `<exact command>` in `<environment>`
**Changes:** `<file1>`, `<file2>` (~N lines) — <one-line rationale>
**Tried & Rejected:** <approach: measured outcome> (omit if none)
**Residual Risk:** <what remains untested, assumptions, or failure modes>
**Reproduce:**
1. `<setup / checkout command>`
2. `<exact verification command>`
```

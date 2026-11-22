---
name: spec-and-plan
description: Extract unambiguous requirements, acceptance tests, task graphs, write scopes, and kill criteria before implementing medium/large or ambiguous tasks. Use when requirements are vague ("make it better/faster"), multi-stakeholder, architectural, or high-risk. Skip for crisp single-file fixes.
---

# Spec and Plan

Turn ambiguous intent into executable acceptance tests (`SPEC.md`) and a minimal, bounded execution plan (`PLAN.md`) before writing production code.

## When to Use / Skip
- **Use:** Ambiguous goals, new subsystems, risky refactors, or tasks where wrong assumptions waste >15 minutes.
- **Skip:** Crisp tickets with an existing spec or single-file bug fixes (just reproduce and fix).

---

## Phase 1: Prior-Art & Environment Recon (5-Minute Cap)
Before proposing designs, inspect what already exists:
1. Check repo layout, existing tests, CI/build configs, recent git commits, branches, caches, or archived attempts.
2. Identify the **2–3 decisive unknowns** whose answers would change the plan.
3. Run the cheapest read-only probes to resolve them and record verified facts in `FACTS.md` (with paths/counts, never guesses).

---

## Phase 2: Requirements Grilling (Only When Ambiguous)
Follow strict low-friction interview rules:
1. **One decision at a time** — never dump a 10-question form on the user.
2. **Lead with a recommendation** — state Option A (recommended) + rationale, then Option B + tradeoff.
3. **Challenge assumptions** — ask whether bottlenecks or constraints are measured or assumed.
4. **Convert every answer into an executable acceptance test** (`AT1..ATn`). Anything that cannot be tested is a preference, not a requirement.
5. **Do not block on minor unknowns** — pick a sensible default, tag it `ASSUMED` with a revisit trigger, and proceed.
6. **Stop condition:** Stop as soon as every core requirement has a test and further questions will not change the plan. Summarize the spec in ≤10 lines and confirm before building.

Write agreed requirements to `SPEC.md` using [references/templates.md](references/templates.md).

---

## Phase 3: Execution Planning (`PLAN.md`)
Produce a concise `PLAN.md` containing:
1. **Critical path:** Shortest sequence of steps to reach the verified Definition of Done. Cut or defer everything else.
2. **First decisive test:** The cheapest experiment or failing test that could invalidate the chosen approach early.
3. **Task graph:** Small incremental tasks (`T1..Tn`), each with:
   - Concrete deliverable & disjoint file write scope
   - Exact verification command (how to prove `T_i` is done)
   - Dependencies
4. **Kill criteria:** Explicit numeric or behavioral condition that forces stopping and switching approaches instead of grinding.
5. **Risks & mitigations:** Top 3–5 failure modes and how you will detect them early.

> **Decision heuristic:** Prioritize steps by `(expected information × decision weight) / cost`. Build the smallest change that satisfies the acceptance tests (YAGNI).

Load [references/templates.md](references/templates.md) only when creating `BRIEF.md`, `SPEC.md`, or `PLAN.md`.

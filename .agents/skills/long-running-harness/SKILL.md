---
name: long-running-harness
description: Manage multi-session ("shift-work") agentic coding across multiple context windows without state loss, context rot, or premature victory. Use when a project spans multiple sessions, hours, or features that cannot safely finish in one clean context window.
---

# Long-Running Harness (Cross-Session Continuity)

Solves the **shift-work problem**: when tasks outlive a single context window, agents lose track of global state, duplicate work, or declare victory early. Persist state in clean filesystem artifacts and atomic git commits so any fresh session can resume in <60 seconds.

---

## Architecture: Initializer vs. Worker Sessions

### Session 0 — Initializer (Run Once)
1. **Verify workspace & VCS:** Ensure git is initialized with a clean baseline commit and the repo's smoke-test/setup command works.
2. **Create `features.json` (Default-Fail Contract):** Break the project into granular, independently testable requirements. Every item starts `"passes": false`. Never mark an item `"passes": true` without executing its verification command.
3. **Create `PROGRESS.md`:** Record the baseline command, environment setup, current architecture map, and the ordered backlog pointer.
4. **Commit the harness state:** Make a clean initial commit so future sessions can always diff or roll back to a known-good state.

### Sessions 1..N — Incremental Worker Loop
Every new session follows this exact startup-work-handoff cycle:

#### 1. Cold-Start Re-Orientation (First Turn Only)
Run **one** batched read/shell step to recover state:
- Read `PROGRESS.md` (tail/current status) and `features.json` (filter `"passes": false`).
- Run `git status --short && git log --oneline -n 5`.
- Run the fast baseline smoke test to confirm the repo is healthy before editing. If broken, **fix the regression first** before starting new features.

#### 2. Pick Exactly ONE Increment
- Select the highest-priority incomplete item from `features.json` whose dependencies pass.
- Do **not** attempt to build the entire remaining backlog in one session; small verified increments beat big broken diffs.

#### 3. Implement & Verify End-to-End
- Write or update the automated test / real runtime check first (unit, integration, or UI/browser verification where applicable).
- Implement the minimal change to pass.
- Run both the feature's exact verification command **and** the regression suite.

#### 4. Clean Checkpoint & Handoff (Before Ending Session)
- Update `features.json`: flip `"passes": true` **only** after observing a passing run, and record the exact verification command + commit hash. Never delete or silently weaken acceptance criteria.
- Append a concise handoff entry (≤15 lines) to `PROGRESS.md`: what shipped, verification evidence, decisions made, known blockers, and the exact next task ID.
- Leave a **clean git commit** with a clear message referencing the feature/decision ID (`feat(F03): ...`). Never leave half-broken uncommitted changes at handoff.

---

## Anti-Patterns Prevented
- **Premature victory:** `features.json` is the ground truth; the project is not done while any required item is `"passes": false`.
- **Context-compaction amnesia:** `PROGRESS.md` + `git log` replace relying on lossy chat summaries.
- **Snowballing broken builds:** Smoke-testing at session start + atomic commits per feature guarantees instant rollback.

Load [references/handoff-templates.md](references/handoff-templates.md) when initializing `features.json` or `PROGRESS.md`.

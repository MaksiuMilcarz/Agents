# Planning & Specification Templates

Use only the templates warranted by task size. Keep every artifact concise and grounded in verifiable commands.

## `BRIEF.md` (Phase 0 — 10–15 lines)
```markdown
# Brief: <task>
- **Objective (1 sentence):** <what changes + direction/outcome>
- **Verifier command:** `<exact command>` | **Baseline:** `<value/status>`
- **Definition of Done:** <deliverable path + verified condition>
- **Environment:** <OS / container / interpreter / runtime constraints>
- **Allowed:** <files, tools, data>
- **Forbidden:** <paths, actions, data leakage rules>
- **Known prior art:** <paths, commits, docs>
- **Kill criteria:** <condition that triggers stop & re-plan>
```

## `SPEC.md` (Requirements & Decisions)
```markdown
# Spec: <feature or project>

## Problem & Outcome
<2–4 lines: who needs this, what fails today, what success looks like.>

## Acceptance Tests (Executable)
- **AT1:** <exact input/action -> exact observable output / command>
- **AT2:** ...

## Constraints & Non-Goals
- **Hard constraints:** <security, latency, compatibility, schema invariants>
- **Non-goals:** <explicitly out of scope>

## Decisions (ADRs)
- **D1:** <decision> — *Rationale:* <why>. *Rejected:* <alternatives>.

## Assumptions & Open Questions
- **A1 (ASSUMED):** <assumption> — *Revisit if:* <trigger>
- **Q1:** <question> — *Owner:* <person/role>
```

## `PLAN.md` (Task Graph & Risk Register)
```markdown
# Plan: <task>

## Critical Path & First Decisive Check
- **First decisive check:** <cheapest test that validates or falsifies the approach>
- **Critical path:** T1 -> T2 -> T3

## Tasks
| ID | Task | Write Scope | Depends On | Verification Command | Kill Criterion |
|---|---|---|---|---|---|
| T1 | <verb phrase> | `path/a` | — | `<cmd>` | <condition> |
| T2 | <verb phrase> | `path/b` | T1 | `<cmd>` | <condition> |

## Top Risks
| Risk | Early Signal | Mitigation |
|---|---|---|
| <risk> | <observable symptom> | <preventive action> |
```

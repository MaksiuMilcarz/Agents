---
name: multi-agent-orchestration
description: Coordinate subagents or parallel agent teams safely with disjoint write scopes, strict spawn contracts, and zero duplicated compute. Use only when a task genuinely parallelizes across independent files/investigations or requires fresh-context adversarial verification. Default is a single agent.
---

# Multi-Agent Orchestration

**Default staff is ONE agent (Lead).** Every spawned worker adds coordination and token overhead. Spawn another agent only when it clearly pays for itself.

---

## Pre-Spawn Gate (All 3 Must Be Crisp)
Before spawning any subagent or teammate, answer:
1. **Unique value:** What information, parallel throughput, or fresh-context independence does it provide that I cannot get cleanly in 1–2 turns myself?
2. **Disjoint write scope:** Which exact paths may it edit (or is it strictly read-only)? Overlapping write scopes are a planning bug—use isolated git worktrees/branches if parallel writers touch the same repo.
3. **Contracted exit artifact:** What exact file path, format, and report length (≤15 lines) must it return?

If any answer is vague, **do not spawn**—do the work directly.

---

## Role Archetypes & Capabilities (Model-Agnostic)

Cap active concurrency at **≤ 4** workers (unless running pure parallel eval harnesses).

| Role | Trigger | Access Level | Exit Artifact |
|---|---|---|---|
| **Recon Scout** | Unfamiliar codebase/prior art; broad search that would pollute main context | Read-only | `FACTS.md` or ≤15-line digest with exact paths/counts |
| **Metric / Harness Builder** | No trustworthy verifier/evaluator exists yet | Scoped write (`tests/`, `harness/`) | Runnable verifier command + reference check |
| **Implementer** | Large change cleanly splits into disjoint modules/files | Scoped write (exclusive fileset or isolated branch) | Minimal diff + unit tests |
| **Independent Verifier / Red-Team** | High correctness risk, gameable metric, or "too good to be true" result | Read-only + command execution (fresh context!) | `PASS/FAIL` verdict + repro evidence + residual risks |

> **Routing principle (capability-based, not vendor-locked):** Route architecture, planning, and adversarial verification to your strongest reasoning tier (read-only); route well-specified scoped edits to a fast coder tier; route log/data extraction to the lightest tier.

---

## Operating Rules

1. **Brief once, pass verbatim:** Write a 10–15 line shared brief (objective, exact verifier command, forbidden actions, resource caps) plus a **"Facts already established — DO NOT re-derive"** list.
2. **Fresh context by default:** Spawn fresh-context subagents to absorb exploration noise and eliminate confirmation bias. Fork conversation history only when deep prior dialogue is strictly necessary.
3. **One writer per file/directory:** Lead owns integration and final delivery; workers never edit the final deliverable unless explicitly and exclusively assigned.
4. **No duplicate heavy compute:** If two workers need the same expensive build, index, or dataset run, one produces the artifact on disk and the rest read it.
5. **No polling loops:** Wait for worker completion notifications or join at phase gates; cancel workers immediately if their line of inquiry is superseded.
6. **Verify worker claims:** Treat subagent summaries as untrusted until checked against command outputs, diffs, or file artifacts.

Load [references/spawn-contract.md](references/spawn-contract.md) for the copy-paste spawn prompt template.

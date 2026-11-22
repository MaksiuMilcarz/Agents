# Model-Agnostic Agentic Engineering Workflow (v2.0)



# USAGE: init-agents



A progressive-disclosure, harness-agnostic workflow built on open standards (**`AGENTS.md`** + **`agentskills.io` `SKILL.md`**) with deterministic Python guardrails.

Designed to work unchanged across **Deepseek Harness, Claude Code, Antigravity, Cursor, Gemini CLI, GitHub Copilot**.

---

## Why v2.0 Exists (Key Shifts from Legacy Monoliths)

| Legacy v1 (`archive/`) | v2.0 Progressive Disclosure | Why It Matters |
|---|---|---|
| `AGENTS.md` = 604 lines / 36 KB (~9K tokens), silently truncated by harnesses | `AGENTS.md` = ~75 lines / ~4 KB (~950 tokens) | Prevents context rot, truncation, and 20–34% token tax on every turn |
| `HyperParameterTunnerAGENTS.md` = 961 lines / 54 KB manually pasted into chat | `.agents/skills/ml-optimization/` (auto-discovered on demand) | Loads ~40 tokens at startup; deep guides load only per phase |
| Duplicated roles, templates, and conflicting limits across 2 files | Single source of truth (`AGENTS.md` invariants + modular skills) | Zero rule drift |
| Prose-only instructions ("log JSONL", "run paired stats", "keep it short") | Executable stdlib Python scripts (`ledger.py`, `validate_workflow.py`) | Deterministic enforcement > asking an LLM to remember |
| DeepSeek Harness-specific appendix | Capability-based instructions + thin shims via `install.sh` | Truly model- and harness-agnostic |

---

## Repository Layout

```text
.
├── AGENTS.md                           # Tier 1: Always-on invariants, task routing & skill catalog (<=100 lines / <=5 KB)
├── .agents/skills/                     # Tier 2 & 3: Open Agent Skills standard (loaded on demand)
│   ├── spec-and-plan/                  # Requirements grilling, SPEC.md, PLAN.md, kill criteria
│   ├── long-running-harness/           # Multi-session continuity (features.json, PROGRESS.md, git checkpoints)
│   ├── multi-agent-orchestration/      # Disjoint write scopes, spawn contracts, fresh-context verifiers
│   ├── verify-and-ship/                # Environment parity, adversarial checks, calibrated final report
│   └── ml-optimization/                # Dual-loop ML optimizer (oracle -> diagnosis -> structure vs params -> stats)
│       ├── SKILL.md
│       ├── references/                 # Phase-specific deep guides (metric/oracle, structure, stats, domain matrix)
│       └── scripts/ledger.py           # Deterministic JSONL ledger, sha256 hashing, paired bootstrap CI & RUNS.md
├── scripts/
│   ├── validate_workflow.py            # Enforces AGENTS.md token/line budget, SKILL.md spec & link integrity
│   └── install.sh                      # Drops workflow into any project (+ optional Claude/Cursor/Gemini shims)
└── archive/                            # Original v1 files preserved for reference
```

---

## Quickstart

### 1. Validate this repository
```bash
python3 scripts/validate_workflow.py
```

### 2. Install into any project repository
```bash
# Copy into a target repo (add --claude, --cursor, --gemini as needed, or --symlink to stay synced):
./scripts/install.sh /path/to/your-project --claude --cursor --gemini
```
Then edit **Section 5 (Project Commands)** in the target repo's `AGENTS.md` with its exact test/lint/build commands.

### 3. Global (all-repos) installation
- **Codex / Antigravity / OpenCode / Copilot:** Copy or symlink `AGENTS.md` and `.agents/skills/` into your tool's global config directory (e.g., `~/.agents/skills/` or `~/.codex/AGENTS.md`).
- **Claude Code:** Symlink `~/.agents/skills` → `~/.claude/skills` and point `~/.claude/CLAUDE.md` to `@/path/to/Agents/AGENTS.md`.

### 4. Using the ML Optimization Ledger CLI
```bash
LEDGER=.agents/skills/ml-optimization/scripts/ledger.py

# Initialize workspace
python3 "$LEDGER" init ./my-ml-project

# Log a run (auto-hashes base & variant files)
python3 "$LEDGER" log --ledger ./my-ml-project/LEDGER.jsonl \
  --phase baseline --name baseline_v1 --metrics '{"val_auc": 0.842}' --verdict baseline

# Estimate noise floor (MDE) from k>=2 baseline score JSON files
python3 "$LEDGER" compare --noise-floor base_r1.json base_r2.json base_r3.json

# Paired bootstrap comparison (95% CI, worst-5% tail check, keep/reject/inconclusive verdict)
python3 "$LEDGER" compare --baseline base_scores.json --candidate cand_scores.json \
  --direction maximize --mde 0.002

# Auto-generate RUNS.md leaderboard
python3 "$LEDGER" summary --ledger ./my-ml-project/LEDGER.jsonl \
  --output ./my-ml-project/RUNS.md --metric val_auc --direction maximize
```

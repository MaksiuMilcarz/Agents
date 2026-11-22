# Spawn Prompt Contract & Handoff Format

Pass this compact structure to every spawned subagent or teammate to prevent scope creep, duplicated work, and verbose report dumps.

## Spawn Prompt Template
```markdown
## Role & Mission
- **Role:** <Recon Scout | Harness Builder | Implementer | Independent Verifier>
- **Mission (1 sentence):** <exact objective>

## Shared Brief
<paste 10–15 line BRIEF.md or core objective + constraints>

## Facts Already Established (DO NOT RE-DERIVE)
- <verified fact + file path>
- <verified fact + command output>

## Verifier Command
- Run: `<exact command>`
- Expected / Reference: `<baseline or pass condition>`

## Scope & Limits
- **Write scope:** <NONE (read-only) | exact directory/file list>
- **Forbidden:** <paths, network/data rules, deliverable protection>
- **Resource cap:** <threads/concurrency/time guidance>

## Deliverable Contract
- **Artifact:** <exact file path + format, or "digest only — no files">
- **Final message (≤ 15 lines):**
  1. What ran / changed
  2. Exact metric or test output (with command)
  3. Artifact path(s) or commit hash
  4. What was NOT verified (known gaps / blockers)
```

## Join Checklist (For Lead)
- [ ] Check worker respected write scope (`git status` / diff check).
- [ ] Verify claimed numbers/tests directly if high-stakes.
- [ ] Record durable facts/decisions in repo files before closing or continuing.

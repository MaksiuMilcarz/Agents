# Handoff & State Templates

## `features.json` (Default-Fail Requirement Tracker)
Never delete items or loosen checks without explicit user approval.

```json
{
  "project": "<name>",
  "smoke_command": "<fast command verifying baseline health>",
  "features": [
    {
      "id": "F01",
      "category": "core|ui|api|infra|ml",
      "description": "Concrete user-observable capability",
      "depends_on": [],
      "verify_command": "<exact command or e2e check>",
      "passes": false,
      "verified_commit": null,
      "notes": ""
    }
  ]
}
```

## `PROGRESS.md` (Append-Only Session Handoff Log)
Keep each session entry ≤15 lines so cold-start reads stay fast.

```markdown
# Progress Log

## Environment & Commands
- Setup: `<cmd>`
- Smoke test: `<cmd>`
- Full verification: `<cmd>`

---

## Session 2026-XX-XX — [F01] <short title>
- **Completed:** <1–2 bullets with file paths>
- **Verified by:** `<exact command>` -> PASS (<key metric/count>)
- **Commit:** `<short-sha>`
- **Decisions / Gotchas:** <non-obvious facts next session must not re-derive>
- **Next task:** `F02` (<1-line starting hint>)
```

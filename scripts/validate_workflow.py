#!/usr/bin/env python3
"""Deterministic harness validator for AGENTS.md + .agents/skills/ (agentskills.io spec).

Enforces:
  1. AGENTS.md context budget (<= 100 lines, <= 5120 bytes) to prevent context rot & truncation.
  2. agentskills.io YAML frontmatter validity for every `.agents/skills/*/SKILL.md`.
  3. Zero broken local markdown file links across AGENTS.md and all SKILL.md files.

Zero external dependencies (Python 3.9+ stdlib only).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]*)?\)")
BACKTICK_PATH_RE = re.compile(r"`(\.agents/skills/[a-z0-9\-/._]+)`")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Missing opening YAML frontmatter delimiter '---'")
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError("Missing closing YAML frontmatter delimiter '---'")

    meta: dict[str, str] = {}
    for line in lines[1:end_idx]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ValueError(f"Malformed frontmatter line: {line!r}")
        key, val = stripped.split(":", 1)
        meta[key.strip()] = val.strip().strip('"').strip("'")
    body = "\n".join(lines[end_idx + 1 :])
    return meta, body


def check_links(file_path: Path, text: str, repo_root: Path, errors: list[str]) -> None:
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (file_path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"{file_path.relative_to(repo_root)}: broken link -> {target}")
    for match in BACKTICK_PATH_RE.finditer(text):
        rel = match.group(1).strip()
        if not (repo_root / rel).exists():
            errors.append(f"{file_path.relative_to(repo_root)}: missing referenced path -> {rel}")


def validate(repo_root: Path, max_lines: int, max_bytes: int, max_skill_lines: int) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    agents_md = repo_root / "AGENTS.md"
    if not agents_md.is_file():
        errors.append("Missing root AGENTS.md")
    else:
        raw = agents_md.read_bytes()
        text = raw.decode("utf-8")
        n_lines = len(text.splitlines())
        n_bytes = len(raw)
        if n_lines > max_lines:
            errors.append(f"AGENTS.md exceeds line budget: {n_lines} > {max_lines}")
        if n_bytes > max_bytes:
            errors.append(f"AGENTS.md exceeds byte budget: {n_bytes} > {max_bytes}")
        check_links(agents_md, text, repo_root, errors)
        print(f"AGENTS.md: {n_lines}/{max_lines} lines, {n_bytes}/{max_bytes} bytes")

    skills_dir = repo_root / ".agents" / "skills"
    if not skills_dir.is_dir():
        errors.append("Missing .agents/skills/ directory")
    else:
        skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
        if not skill_dirs:
            errors.append("No skills found in .agents/skills/")
        for sdir in skill_dirs:
            skill_md = sdir / "SKILL.md"
            if not skill_md.is_file():
                errors.append(f"{sdir.relative_to(repo_root)}: missing SKILL.md")
                continue
            text = skill_md.read_text(encoding="utf-8")
            n_lines = len(text.splitlines())
            try:
                meta, _ = parse_frontmatter(text)
            except ValueError as exc:
                errors.append(f"{skill_md.relative_to(repo_root)}: {exc}")
                continue

            name = meta.get("name", "")
            desc = meta.get("description", "")
            if not name:
                errors.append(f"{skill_md.relative_to(repo_root)}: missing frontmatter 'name'")
            else:
                if name != sdir.name:
                    errors.append(
                        f"{skill_md.relative_to(repo_root)}: frontmatter name {name!r} != dir {sdir.name!r}"
                    )
                if len(name) > 64 or not NAME_RE.match(name):
                    errors.append(
                        f"{skill_md.relative_to(repo_root)}: invalid skill name {name!r} (lowercase alphanumeric/hyphens, <=64)"
                    )
            if not desc:
                errors.append(f"{skill_md.relative_to(repo_root)}: missing frontmatter 'description'")
            elif len(desc) > 1024:
                errors.append(
                    f"{skill_md.relative_to(repo_root)}: description length {len(desc)} > 1024"
                )
            if n_lines > max_skill_lines:
                warnings.append(
                    f"{skill_md.relative_to(repo_root)}: {n_lines} lines (recommended <= {max_skill_lines}; move detail to references/)"
                )

            check_links(skill_md, text, repo_root, errors)
            print(f"  skill {sdir.name}: {n_lines} lines, desc={len(desc)} chars")

    for w in warnings:
        print(f"WARN: {w}", file=sys.stderr)
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)

    if errors:
        print(f"\nValidation FAILED ({len(errors)} error(s)).", file=sys.stderr)
        return 1
    print("\nValidation PASSED.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AGENTS.md budget and Agent Skills spec")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--max-lines", type=int, default=100)
    parser.add_argument("--max-bytes", type=int, default=5120)
    parser.add_argument("--max-skill-lines", type=int, default=160)
    args = parser.parse_args()
    return validate(Path(args.root).resolve(), args.max_lines, args.max_bytes, args.max_skill_lines)


if __name__ == "__main__":
    raise SystemExit(main())

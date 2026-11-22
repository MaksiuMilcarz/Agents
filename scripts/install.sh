#!/usr/bin/env bash
# Install this model-agnostic AGENTS.md + .agents/skills/ workflow into a target directory.
# Works both locally and remotely via `curl -fsSL ... | bash -s -- [target] [flags]`.
#
# Usage:
#   ./scripts/install.sh [target-dir (default: .)] [--symlink] [--all] [--claude] [--cursor] [--gemini] [--aider] [--cline]
set -euo pipefail

REPO_URL="${AGENTS_REPO_URL:-https://github.com/MaksiuMilcarz/Agents.git}"
REPO_BRANCH="${AGENTS_REPO_BRANCH:-main}"

TARGET="."
MODE="copy"
ADD_CLAUDE=0
ADD_CURSOR=0
ADD_GEMINI=0
ADD_AIDER=0
ADD_CLINE=0
TARGET_SET=0

for arg in "$@"; do
  case "$arg" in
    --symlink) MODE="symlink" ;;
    --all)     ADD_CLAUDE=1; ADD_CURSOR=1; ADD_GEMINI=1; ADD_AIDER=1; ADD_CLINE=1 ;;
    --claude)  ADD_CLAUDE=1 ;;
    --cursor)  ADD_CURSOR=1 ;;
    --gemini)  ADD_GEMINI=1 ;;
    --aider)   ADD_AIDER=1 ;;
    --cline)   ADD_CLINE=1 ;;
    -h|--help)
      echo "Usage: $0 [target-dir (default: .)] [--symlink] [--all] [--claude] [--cursor] [--gemini] [--aider] [--cline]"
      exit 0
      ;;
    --*)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
    *)
      if [[ "$TARGET_SET" -eq 0 ]]; then
        TARGET="$arg"
        TARGET_SET=1
      else
        echo "Unexpected extra argument: $arg" >&2
        exit 1
      fi
      ;;
  esac
done

TMP_CLONE=""
cleanup() {
  if [[ -n "$TMP_CLONE" && -d "$TMP_CLONE" ]]; then
    rm -rf "$TMP_CLONE"
  fi
}
trap cleanup EXIT

# Detect whether running locally inside the repo or remotely (e.g. piped via curl | bash).
SRC_ROOT=""
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  CANDIDATE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
  if [[ -f "${CANDIDATE_ROOT}/AGENTS.md" && -d "${CANDIDATE_ROOT}/.agents/skills" ]]; then
    SRC_ROOT="$CANDIDATE_ROOT"
  fi
fi

if [[ -z "$SRC_ROOT" ]]; then
  if [[ "$MODE" == "symlink" ]]; then
    echo "ERROR: --symlink requires a local clone, not remote curl execution." >&2
    exit 1
  fi
  TMP_CLONE="$(mktemp -d)"
  echo "Downloading workflow from ${REPO_URL} (${REPO_BRANCH})..."
  git clone --depth 1 --branch "$REPO_BRANCH" --quiet "$REPO_URL" "$TMP_CLONE"
  SRC_ROOT="$TMP_CLONE"
fi

mkdir -p "$TARGET/.agents" "$TARGET/scripts"
TARGET_ABS="$(cd "$TARGET" && pwd)"

install_item() {
  local src="$1"
  local dst="$2"
  if [[ -e "$dst" || -L "$dst" ]]; then
    echo "SKIP (already exists): $dst"
    return 0
  fi
  if [[ "$MODE" == "symlink" ]]; then
    ln -s "$src" "$dst"
    echo "LINKED: $dst -> $src"
  else
    cp -R "$src" "$dst"
    echo "COPIED: $dst"
  fi
}

install_item "${SRC_ROOT}/AGENTS.md" "${TARGET_ABS}/AGENTS.md"
install_item "${SRC_ROOT}/.agents/skills" "${TARGET_ABS}/.agents/skills"
install_item "${SRC_ROOT}/scripts/validate_workflow.py" "${TARGET_ABS}/scripts/validate_workflow.py"

if [[ "$ADD_CLAUDE" -eq 1 ]]; then
  if [[ ! -e "${TARGET_ABS}/CLAUDE.md" ]]; then
    printf '@AGENTS.md\n' > "${TARGET_ABS}/CLAUDE.md"
    echo "CREATED: ${TARGET_ABS}/CLAUDE.md (thin @AGENTS.md shim)"
  else
    echo "SKIP (already exists): ${TARGET_ABS}/CLAUDE.md"
  fi
  mkdir -p "${TARGET_ABS}/.claude"
  if [[ ! -e "${TARGET_ABS}/.claude/skills" && ! -L "${TARGET_ABS}/.claude/skills" ]]; then
    ln -s ../.agents/skills "${TARGET_ABS}/.claude/skills"
    echo "LINKED: ${TARGET_ABS}/.claude/skills -> ../.agents/skills"
  fi
fi

if [[ "$ADD_CURSOR" -eq 1 ]]; then
  mkdir -p "${TARGET_ABS}/.cursor/rules"
  if [[ ! -e "${TARGET_ABS}/.cursor/rules/agents.mdc" ]]; then
    cat > "${TARGET_ABS}/.cursor/rules/agents.mdc" <<'EOF'
---
description: Core repository agent operating protocol (delegates to AGENTS.md)
alwaysApply: true
---
Follow the repository contract in `AGENTS.md` and load relevant skills from `.agents/skills/*/SKILL.md` on demand.
EOF
    echo "CREATED: ${TARGET_ABS}/.cursor/rules/agents.mdc"
  fi
fi

if [[ "$ADD_GEMINI" -eq 1 ]]; then
  if [[ ! -e "${TARGET_ABS}/GEMINI.md" ]]; then
    printf 'Read and follow `AGENTS.md` as the primary repository operating contract, and load `.agents/skills/*/SKILL.md` on demand.\n' > "${TARGET_ABS}/GEMINI.md"
    echo "CREATED: ${TARGET_ABS}/GEMINI.md (thin shim)"
  fi
fi

if [[ "$ADD_AIDER" -eq 1 ]]; then
  if [[ ! -e "${TARGET_ABS}/.aider.conf.yml" ]]; then
    cat > "${TARGET_ABS}/.aider.conf.yml" <<'EOF'
# Thin shim so Aider (including with DeepSeek models) auto-loads AGENTS.md
read:
  - AGENTS.md
EOF
    echo "CREATED: ${TARGET_ABS}/.aider.conf.yml (thin shim)"
  else
    echo "SKIP (already exists): ${TARGET_ABS}/.aider.conf.yml"
  fi
fi

if [[ "$ADD_CLINE" -eq 1 ]]; then
  mkdir -p "${TARGET_ABS}/.clinerules"
  if [[ ! -e "${TARGET_ABS}/.clinerules/agents.md" ]]; then
    printf 'Follow `AGENTS.md` as the primary repository operating contract, and load `.agents/skills/*/SKILL.md` on demand.\n' > "${TARGET_ABS}/.clinerules/agents.md"
    echo "CREATED: ${TARGET_ABS}/.clinerules/agents.md (thin shim)"
  else
    echo "SKIP (already exists): ${TARGET_ABS}/.clinerules/agents.md"
  fi
fi

echo "Done. Next: customize section 5 (Project Commands) in ${TARGET_ABS}/AGENTS.md and run:"
echo "  python3 ${TARGET_ABS}/scripts/validate_workflow.py --root ${TARGET_ABS}"

#!/usr/bin/env bash
# Install the skills in this repo into the agent skill directories.
#
# Skill loaders expect one flat directory per skill, named exactly as the
# `name:` field in its frontmatter. This repo groups skills under
# `engineering/` for readability, so installing is a flatten + symlink:
#
#   engineering/orchestrator/  (name: engineering-orchestrator)
#       → ~/.claude/skills/engineering-orchestrator
#       → ~/.agents/skills/engineering-orchestrator
#
# Symlinks, not copies: `git pull` updates every install at once.
#
#   ./install.sh              install into every target that exists
#   ./install.sh --list       show what would be linked, change nothing
#   ./install.sh --uninstall  remove only the links pointing at this repo
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")
MODE="${1:-install}"

# name: field of a SKILL.md — the directory name the loader expects
skill_name() { sed -n 's/^name:[[:space:]]*//p' "$1/SKILL.md" | head -1; }

# Plain glob, not mapfile — macOS ships bash 3.2.
DIRS=()
for d in "$REPO"/engineering/*/; do [[ -f "${d}SKILL.md" ]] && DIRS+=("${d%/}"); done
[[ ${#DIRS[@]} -gt 0 ]] || { echo "no skills found under $REPO/engineering" >&2; exit 1; }

if [[ "$MODE" == "--list" ]]; then
  printf '%-28s %s\n' "NAME" "SOURCE"
  for d in "${DIRS[@]}"; do printf '%-28s %s\n' "$(skill_name "$d")" "engineering/$(basename "$d")"; done
  echo; echo "targets:"
  for t in "${TARGETS[@]}"; do [[ -d "$t" ]] && echo "  $t" || echo "  $t   (absent — would be skipped)"; done
  exit 0
fi

n=0
for t in "${TARGETS[@]}"; do
  [[ -d "$t" ]] || { echo "skip $t (does not exist)"; continue; }
  for d in "${DIRS[@]}"; do
    name="$(skill_name "$d")"
    [[ -n "$name" ]] || { echo "✗ $(basename "$d"): no name: field" >&2; exit 1; }
    link="$t/$name"

    # Never clobber a real directory — that would be somebody's own skill.
    if [[ -e "$link" && ! -L "$link" ]]; then
      echo "✗ $link exists and is not a symlink — left alone" >&2
      continue
    fi

    if [[ "$MODE" == "--uninstall" ]]; then
      # Only remove links that point into this repo.
      if [[ -L "$link" && "$(readlink "$link")" == "$REPO"/* ]]; then
        rm "$link"; echo "removed $link"; n=$((n+1))
      fi
    else
      ln -sfn "$d" "$link"; echo "linked  $link"; n=$((n+1))
    fi
  done
done

echo
if [[ "$MODE" == "--uninstall" ]]; then
  echo "$n link(s) removed."
else
  echo "$n link(s) installed. Restart the agent to pick them up."
fi

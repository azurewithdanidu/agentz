#!/usr/bin/env bash
# Set up this machine to contribute to the agentz marketplace.
#
#   scripts/init.sh                 # full setup
#   scripts/init.sh --skip-hve      # without HVE Core
#   scripts/init.sh --hve-ref <ref> # pin HVE Core to a tag or commit (default: main)
#   scripts/init.sh --dry-run       # show what would run
#
# Safe to re-run. Steps whose tool isn't installed are skipped and reported.
set -uo pipefail

MARKETPLACE_REPO="azurewithdanidu/agentz"
MARKETPLACE_NAME="agentz"
HVE_REPO="microsoft/hve-core"
HVE_EXTENSION="ise-hve-essentials.hve-core"
VALLY_VERSION="0.20.0"
SKIP_HVE=0
HVE_REF=""
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --skip-hve) SKIP_HVE=1 ;;
    --hve-ref) HVE_REF="${2:?--hve-ref needs a value}"; shift ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

cd "$(dirname "$0")/.." || exit 1
DONE=(); SKIPPED=(); FAILED=()

run() {
  echo "  \$ $*"
  [ "$DRY_RUN" -eq 1 ] && return 0
  "$@"
}
have() { command -v "$1" >/dev/null 2>&1; }
step() { echo; echo "== $1"; }

hve_spec="$HVE_REPO"; [ -n "$HVE_REF" ] && hve_spec="$HVE_REPO#$HVE_REF"

step "Python and PyYAML (marketplace scripts)"
if have python3; then
  if python3 -c 'import yaml' 2>/dev/null; then DONE+=("PyYAML already installed")
  elif run python3 -m pip install --user --quiet pyyaml; then DONE+=("PyYAML installed")
  else FAILED+=("PyYAML: run 'python3 -m pip install pyyaml'"); fi
else FAILED+=("Python 3.10+ not found"); fi

step "Node.js and Vally (evals)"
if have npx; then
  if run npx -y "@microsoft/vally-cli@$VALLY_VERSION" --version >/dev/null; then DONE+=("Vally $VALLY_VERSION ready")
  else FAILED+=("Vally: run 'npx -y @microsoft/vally-cli@$VALLY_VERSION --version'"); fi
else SKIPPED+=("Node.js 20+ not found: evals can't be linted or run locally"); fi

step "VS Code"
if have code; then
  run code --install-extension github.copilot-chat >/dev/null && DONE+=("VS Code: GitHub Copilot Chat")
  if [ "$SKIP_HVE" -eq 0 ]; then
    run code --install-extension "$HVE_EXTENSION" >/dev/null && DONE+=("VS Code: HVE Core extension")
  fi
  DONE+=("VS Code: workspace settings add the $MARKETPLACE_NAME marketplace (.vscode/settings.json)")
else SKIPPED+=("VS Code CLI 'code' not on PATH: open the repo in VS Code and accept the recommended extensions"); fi

step "GitHub Copilot CLI"
if have copilot; then
  run copilot plugin marketplace add "$MARKETPLACE_REPO" || true
  if run copilot plugin install "agentz-publisher@$MARKETPLACE_NAME"; then DONE+=("Copilot CLI: agentz-publisher")
  else FAILED+=("Copilot CLI: agentz-publisher install"); fi
  if [ "$SKIP_HVE" -eq 0 ]; then
    run copilot plugin marketplace add "$hve_spec" || true
    if run copilot plugin install "hve-core@hve-core"; then DONE+=("Copilot CLI: hve-core (${HVE_REF:-main})")
    else FAILED+=("Copilot CLI: hve-core install"); fi
  fi
else SKIPPED+=("Copilot CLI not found"); fi

step "Claude Code"
if have claude; then
  run claude plugin marketplace add "$MARKETPLACE_REPO" || true
  if run claude plugin install "agentz-publisher@$MARKETPLACE_NAME"; then DONE+=("Claude Code: agentz-publisher")
  else FAILED+=("Claude Code: agentz-publisher install"); fi
  [ "$SKIP_HVE" -eq 0 ] && SKIPPED+=("Claude Code: HVE Core isn't available for Claude Code; use VS Code or Copilot CLI for hve-builder and vally-tests")
else SKIPPED+=("Claude Code not found"); fi

step "Working folder for publishing notes"
if [ "$DRY_RUN" -eq 0 ]; then
  mkdir -p .agentz
  grep -qxF '.agentz/' .gitignore 2>/dev/null || echo '.agentz/' >> .gitignore
fi
DONE+=(".agentz/ ready (git-ignored)")

step "Checking the repository"
if have python3 && python3 -c 'import yaml' 2>/dev/null; then
  if run python3 scripts/validate_repo.py >/dev/null; then DONE+=("Marketplace gate passes")
  else FAILED+=("Marketplace gate: run 'python3 scripts/validate_repo.py' to see errors"); fi
fi

echo; echo "================ Summary"
[ "$DRY_RUN" -eq 1 ] && echo "  (dry run: nothing was changed; results show what would happen)"
for i in "${DONE[@]}"; do echo "  done     $i"; done
for i in "${SKIPPED[@]}"; do echo "  skipped  $i"; done
for i in "${FAILED[@]}"; do echo "  FAILED   $i"; done
echo; echo "Next: run /new-plugin in Copilot Chat, or select the 'publisher' agent."
[ "${#FAILED[@]}" -eq 0 ]

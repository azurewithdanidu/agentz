#!/usr/bin/env bash
# Set up this machine for the agentz marketplace (macOS, Linux, WSL).
#
#   setup.sh                          # user: add the marketplace to every installed client
#   setup.sh --plugins a,b            # user: also install these plugins
#   setup.sh --role contributor       # contributor: also publisher, Python, Vally, HVE Core
#   setup.sh --skip-hve               # contributor without HVE Core
#   setup.sh --hve-ref <ref>          # pin HVE Core to a tag or commit (default: main)
#   setup.sh --dry-run                # show what would run, change nothing
#
# Safe to re-run. Steps whose tool isn't installed are skipped and reported.
# Run it from the agentz repository clone when contributing; users can run it anywhere.
set -uo pipefail

MARKETPLACE_REPO="azurewithdanidu/agentz"
MARKETPLACE_NAME="agentz"
HVE_REPO="microsoft/hve-core"
HVE_EXTENSION="ise-hve-essentials.hve-core"
VALLY_VERSION="0.20.0"
ROLE="user"; PLUGINS=""; SKIP_HVE=0; HVE_REF=""; DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --role) ROLE="${2:?--role needs user or contributor}"; shift ;;
    --plugins) PLUGINS="${2:?--plugins needs a comma-separated list}"; shift ;;
    --skip-hve) SKIP_HVE=1 ;;
    --hve-ref) HVE_REF="${2:?--hve-ref needs a value}"; shift ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done
case "$ROLE" in user|contributor) ;; *) echo "--role must be user or contributor" >&2; exit 2 ;; esac

DONE=(); SKIPPED=(); FAILED=()
run() { echo "  \$ $*"; [ "$DRY_RUN" -eq 1 ] && return 0; "$@"; }
have() { command -v "$1" >/dev/null 2>&1; }
step() { echo; echo "== $1"; }

# Plugins to install in each CLI client.
plugin_list=()
IFS=',' read -r -a requested <<< "$PLUGINS"
for p in "${requested[@]}"; do [ -n "$p" ] && plugin_list+=("$p"); done
[ "$ROLE" = "contributor" ] && plugin_list+=("agentz-publisher")

hve_spec="$HVE_REPO"; [ -n "$HVE_REF" ] && hve_spec="$HVE_REPO#$HVE_REF"

install_plugins() {  # $1 = client CLI name
  local cli="$1" p
  run "$cli" plugin marketplace add "$MARKETPLACE_REPO" || true
  DONE+=("$cli: marketplace $MARKETPLACE_NAME added")
  for p in "${plugin_list[@]:-}"; do
    [ -z "$p" ] && continue
    if run "$cli" plugin install "$p@$MARKETPLACE_NAME"; then DONE+=("$cli: $p")
    else FAILED+=("$cli: $p install"); fi
  done
}

step "GitHub Copilot CLI"
if have copilot; then
  install_plugins copilot
  if [ "$ROLE" = "contributor" ] && [ "$SKIP_HVE" -eq 0 ]; then
    run copilot plugin marketplace add "$hve_spec" || true
    if run copilot plugin install "hve-core@hve-core"; then DONE+=("copilot: hve-core (${HVE_REF:-main})")
    else FAILED+=("copilot: hve-core install"); fi
  fi
else SKIPPED+=("Copilot CLI not found"); fi

step "Claude Code"
if have claude; then
  install_plugins claude
  [ "$ROLE" = "contributor" ] && [ "$SKIP_HVE" -eq 0 ] && SKIPPED+=("Claude Code: HVE Core isn't available for Claude Code; use VS Code or Copilot CLI for hve-builder and vally-tests")
else SKIPPED+=("Claude Code not found"); fi

step "VS Code"
if have code; then
  run code --install-extension github.copilot-chat >/dev/null && DONE+=("VS Code: GitHub Copilot Chat")
  if [ "$ROLE" = "contributor" ] && [ "$SKIP_HVE" -eq 0 ]; then
    run code --install-extension "$HVE_EXTENSION" >/dev/null && DONE+=("VS Code: HVE Core extension")
  fi
else SKIPPED+=("VS Code CLI 'code' not on PATH"); fi
# Editing the user's settings.json automatically is risky (comments, merges), so this stays manual.
SKIPPED+=("VS Code (manual): add \"$MARKETPLACE_REPO\" to chat.plugins.marketplaces, then install from the Plugins view")

if [ "$ROLE" = "contributor" ]; then
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

  step "Repository clone"
  if [ -f scripts/validate_repo.py ]; then
    if [ "$DRY_RUN" -eq 0 ]; then
      mkdir -p .agentz
      grep -qxF '.agentz/' .gitignore 2>/dev/null || echo '.agentz/' >> .gitignore
    fi
    DONE+=(".agentz/ ready (git-ignored)")
    if have python3 && python3 -c 'import yaml' 2>/dev/null; then
      if run python3 scripts/validate_repo.py >/dev/null; then DONE+=("Marketplace gate passes")
      else FAILED+=("Marketplace gate: run 'python3 scripts/validate_repo.py' to see errors"); fi
    fi
  else SKIPPED+=("Not in an agentz clone: clone $MARKETPLACE_REPO and re-run from its root to prepare .agentz/ and check the gate"); fi
fi

echo; echo "================ Summary ($ROLE)"
[ "$DRY_RUN" -eq 1 ] && echo "  (dry run: nothing was changed; results show what would happen)"
for i in "${DONE[@]:-}"; do [ -n "$i" ] && echo "  done     $i"; done
for i in "${SKIPPED[@]:-}"; do [ -n "$i" ] && echo "  skipped  $i"; done
for i in "${FAILED[@]:-}"; do [ -n "$i" ] && echo "  FAILED   $i"; done
if [ "$ROLE" = "contributor" ]; then echo; echo "Next: run /new-plugin in Copilot Chat, or select the 'publisher' agent."
else echo; echo "Next: browse plugins with 'copilot plugin marketplace browse $MARKETPLACE_NAME' or '/plugin' in Claude Code."; fi
[ "${#FAILED[@]}" -eq 0 ]

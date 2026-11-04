<#
.SYNOPSIS
  Set up this machine to contribute plugins to the agentz marketplace (Windows).
  Installs agentz-publisher, HVE Core, Python with PyYAML and Vally (the eval tooling).
.EXAMPLE
  .\setup.ps1                  # full setup
  .\setup.ps1 -SkipHve         # without HVE Core
  .\setup.ps1 -HveRef <ref>    # pin HVE Core to a tag or commit (default: main)
  .\setup.ps1 -DryRun          # show what would run, change nothing
.NOTES
  Safe to re-run. Steps whose tool isn't installed are skipped and reported.
  Run it from a clone of the agentz repository.
  Works in Windows PowerShell 5.1 and PowerShell 7+.
#>
[CmdletBinding()]
param(
  [switch]$SkipHve,
  [string]$HveRef = "",
  [switch]$DryRun
)

$MarketplaceRepo = "azurewithdanidu/agentz"
$MarketplaceName = "agentz"
$HveRepo         = "microsoft/hve-core"
$HveExtension    = "ise-hve-essentials.hve-core"
$VallyVersion    = "0.20.0"

$done = @(); $skipped = @(); $failed = @()

function Invoke-Step([string]$Exe, [string[]]$ArgList) {
  Write-Host "  `$ $Exe $($ArgList -join ' ')"
  if ($DryRun) { return $true }
  & $Exe @ArgList *> $null
  return ($LASTEXITCODE -eq 0)
}
function Test-Tool([string]$Name) { [bool](Get-Command $Name -ErrorAction SilentlyContinue) }
function Write-Step([string]$Title) { Write-Host ""; Write-Host "== $Title" }

$hveSpec = if ($HveRef) { "$HveRepo#$HveRef" } else { $HveRepo }
$python = if (Test-Tool "python") { "python" } elseif (Test-Tool "py") { "py" } elseif (Test-Tool "python3") { "python3" } else { $null }

Write-Step "Python and PyYAML (marketplace scripts)"
if ($python) {
  & $python -c "import yaml" *> $null
  if ($LASTEXITCODE -eq 0) { $done += "PyYAML already installed" }
  elseif (Invoke-Step $python @("-m", "pip", "install", "--user", "--quiet", "pyyaml")) { $done += "PyYAML installed" }
  else { $failed += "PyYAML: run '$python -m pip install pyyaml'" }
} else { $failed += "Python 3.10+ not found" }

Write-Step "Node.js and Vally (evals)"
if (Test-Tool "npx") {
  if (Invoke-Step "npx" @("-y", "@microsoft/vally-cli@$VallyVersion", "--version")) { $done += "Vally $VallyVersion ready" }
  else { $failed += "Vally: run 'npx -y @microsoft/vally-cli@$VallyVersion --version'" }
} else { $skipped += "Node.js 20+ not found: evals can't be linted or run locally" }

Write-Step "VS Code"
if (Test-Tool "code") {
  if (Invoke-Step "code" @("--install-extension", "github.copilot-chat")) { $done += "VS Code: GitHub Copilot Chat" }
  if (-not $SkipHve) {
    if (Invoke-Step "code" @("--install-extension", $HveExtension)) { $done += "VS Code: HVE Core extension" }
    else { $failed += "VS Code: HVE Core extension install" }
  }
} else { $skipped += "VS Code CLI 'code' not on PATH: install the HVE Core extension ($HveExtension) from the Extensions view" }
# Editing the user's settings.json automatically is risky (comments, merges), so this stays manual.
$skipped += "VS Code (manual): add `"$MarketplaceRepo`" to chat.plugins.marketplaces, then install agentz-publisher from the Plugins view"

Write-Step "GitHub Copilot CLI"
if (Test-Tool "copilot") {
  [void](Invoke-Step "copilot" @("plugin", "marketplace", "add", $MarketplaceRepo))
  if (Invoke-Step "copilot" @("plugin", "install", "agentz-publisher@$MarketplaceName")) { $done += "Copilot CLI: agentz-publisher" }
  else { $failed += "Copilot CLI: agentz-publisher install" }
  if (-not $SkipHve) {
    [void](Invoke-Step "copilot" @("plugin", "marketplace", "add", $hveSpec))
    $label = if ($HveRef) { $HveRef } else { "main" }
    if (Invoke-Step "copilot" @("plugin", "install", "hve-core@hve-core")) { $done += "Copilot CLI: hve-core ($label)" }
    else { $failed += "Copilot CLI: hve-core install" }
  }
} else { $skipped += "Copilot CLI not found" }

Write-Step "Claude Code"
if (Test-Tool "claude") {
  [void](Invoke-Step "claude" @("plugin", "marketplace", "add", $MarketplaceRepo))
  if (Invoke-Step "claude" @("plugin", "install", "agentz-publisher@$MarketplaceName")) { $done += "Claude Code: agentz-publisher" }
  else { $failed += "Claude Code: agentz-publisher install" }
  if (-not $SkipHve) { $skipped += "Claude Code: HVE Core isn't available for Claude Code; use VS Code or Copilot CLI for hve-builder and vally-tests" }
} else { $skipped += "Claude Code not found" }

Write-Step "Repository clone"
if (Test-Path "scripts/validate_repo.py") {
  if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path ".agentz" | Out-Null
    if (-not (Select-String -Path ".gitignore" -Pattern '^\.agentz/$' -Quiet -ErrorAction SilentlyContinue)) {
      Add-Content -Path ".gitignore" -Value ".agentz/"
    }
  }
  $done += ".agentz/ ready (git-ignored)"
  if ($python) {
    & $python -c "import yaml" *> $null
    if ($LASTEXITCODE -eq 0) {
      if (Invoke-Step $python @("scripts/validate_repo.py")) { $done += "Marketplace gate passes" }
      else { $failed += "Marketplace gate: run '$python scripts/validate_repo.py' to see errors" }
    }
  }
} else { $skipped += "Not in an agentz clone: clone $MarketplaceRepo and re-run from its root to prepare .agentz/ and check the gate" }

Write-Host ""; Write-Host "================ Summary"
if ($DryRun) { Write-Host "  (dry run: nothing was changed; results show what would happen)" }
$done    | ForEach-Object { Write-Host "  done     $_" }
$skipped | ForEach-Object { Write-Host "  skipped  $_" }
$failed  | ForEach-Object { Write-Host "  FAILED   $_" -ForegroundColor Red }
Write-Host ""; Write-Host "Next: run /new-plugin in Copilot Chat, or select the 'publisher' agent."
if ($failed.Count -gt 0) { exit 1 }

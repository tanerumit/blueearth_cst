# Exclude tracked board snapshots in one explicitly selected session worktree.
# Navigation is provided by setup-worktree-navigation.ps1's Explorer shortcuts.
param(
    [string]$WorktreeRoot = (Join-Path $PSScriptRoot '../..'),
    [switch]$ExcludeSnapshots,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
if (-not $ExcludeSnapshots) { throw 'Use -ExcludeSnapshots to exclude session board snapshots.' }

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$targetRoot = (Resolve-Path -LiteralPath $WorktreeRoot).Path
$lines = @(git -C $repoRoot worktree list --porcelain)
if ($LASTEXITCODE -ne 0) { throw 'Cannot list Git worktrees.' }
$registered = $false
$isMain = $false
$path = $null
foreach ($line in $lines) {
    if ($line.StartsWith('worktree ')) {
        $path = [IO.Path]::GetFullPath($line.Substring(9))
        if ($path -eq $targetRoot) { $registered = $true }
    } elseif ($line -eq 'branch refs/heads/main' -and $path -eq $targetRoot) {
        $isMain = $true
    }
}
if (-not $registered -or $isMain) { throw 'Snapshot exclusion requires a registered session worktree.' }
$changes = @(git -C $targetRoot status --porcelain)
if ($LASTEXITCODE -ne 0 -or $changes.Count) {
    throw "The target worktree must be clean before excluding board snapshots: $targetRoot"
}
$sparse = git -C $targetRoot config --bool core.sparseCheckout
if ($LASTEXITCODE -notin @(0, 1)) { throw "Cannot read sparse configuration: $targetRoot" }
if ($sparse -eq 'true') {
    $patterns = @(git -C $targetRoot sparse-checkout list)
    if ($LASTEXITCODE -ne 0 -or ($patterns -join "`n") -ne "/*`n!/dev/TODO.md`n!/dev/tasks/") {
        throw "Refusing to replace a custom sparse layout: $targetRoot"
    }
    Write-Host "Board snapshots already excluded: $targetRoot"
    return
}
if ($CheckOnly) { return }
git -C $targetRoot sparse-checkout set --no-cone '/*' '!/dev/TODO.md' '!/dev/tasks/'
if ($LASTEXITCODE -ne 0) { throw "Cannot exclude board snapshots: $targetRoot" }
Write-Host "Board snapshots excluded: $targetRoot"

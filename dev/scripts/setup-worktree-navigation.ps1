# Preview or create ignored Explorer shortcuts; never copy worktree contents.
param(
    [switch]$Apply,
    [switch]$ExcludeSnapshots
)
$ErrorActionPreference = 'Stop'
if (-not $IsWindows) { throw 'Explorer navigation requires Windows.' }
if ($ExcludeSnapshots -and -not $Apply) { throw '-ExcludeSnapshots requires -Apply.' }

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$lines = git -C $repoRoot worktree list --porcelain
if ($LASTEXITCODE -ne 0) { throw 'Cannot list worktrees.' }
$roots = @()
$mainRoot = $null
$root = $null
foreach ($line in $lines) {
    if ($line.StartsWith('worktree ')) {
        $root = $line.Substring(9)
        $roots += $root
    } elseif ($line -eq 'branch refs/heads/main') {
        $mainRoot = $root
    }
}
if (-not $mainRoot) { throw 'Expected a registered main worktree.' }

# Use Explorer shortcuts rather than junctions: cleanup cannot recurse into another tree.
$shell = if ($Apply) { New-Object -ComObject WScript.Shell } else { $null }
foreach ($root in $roots) {
    $navigationPath = Join-Path $root '.tmp/navigation'
    Write-Host "Navigation: $navigationPath"
    foreach ($relative in @('.tmp', '.tmp/navigation', '.tmp/scratchpad')) {
        $existing = Get-Item -LiteralPath (Join-Path $root $relative) -Force -ErrorAction SilentlyContinue
        if ($existing -and (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
                -not $existing.PSIsContainer)) {
            throw "Refusing linked or non-directory navigation parent: $($existing.FullName)"
        }
    }
    git -C $root check-ignore -q .tmp/navigation/
    if ($LASTEXITCODE -ne 0) { throw "Navigation must be ignored before setup: $root" }

    $targets = [ordered]@{ 'main-dev' = (Join-Path $mainRoot 'dev') }
    foreach ($targetRoot in $roots) {
        $label = if ($targetRoot -eq $mainRoot) { 'main' } else { Split-Path $targetRoot -Leaf }
        if ($targets.Contains($label)) { throw "Duplicate navigation label: $label" }
        $targets[$label] = $targetRoot
    }
    $targets['local-scratch'] = Join-Path $root '.tmp/scratchpad'
    if ($Apply) {
        New-Item -ItemType Directory -Path $navigationPath -Force | Out-Null
        New-Item -ItemType Directory -Path $targets['local-scratch'] -Force | Out-Null
    }
    foreach ($label in $targets.Keys) {
        $shortcutPath = Join-Path $navigationPath "$label.lnk"
        $existing = Get-Item -LiteralPath $shortcutPath -Force -ErrorAction SilentlyContinue
        if ($existing -and (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
                $existing.PSIsContainer)) {
            throw "Refusing unrelated shortcut path: $shortcutPath"
        }
        if ($Apply) {
            $shortcut = $shell.CreateShortcut($shortcutPath)
            if ($existing -and (-not $shortcut.TargetPath -or
                    [IO.Path]::GetFullPath($shortcut.TargetPath) -ne
                    [IO.Path]::GetFullPath($targets[$label]))) {
                throw "Refusing to replace a different shortcut: $shortcutPath"
            }
            $shortcut.TargetPath = $targets[$label]
            $shortcut.Description = 'Worktree navigation; files remain in their owning checkout.'
            $shortcut.Save()
        }
        Write-Host "  $label -> $($targets[$label])"
    }
    if ($ExcludeSnapshots -and $root -ne $mainRoot) {
        # Preserve custom sparse layouts rather than silently replacing them.
        $sparse = git -C $root config --bool core.sparseCheckout
        if ($sparse -eq 'true') {
            $patterns = @(git -C $root sparse-checkout list)
            if ($LASTEXITCODE -ne 0 -or ($patterns -join "`n") -ne "/*`n!/dev/TODO.md`n!/dev/tasks/") {
                throw "Refusing to replace a custom sparse layout: $root"
            }
            Write-Host "  Board snapshots already excluded: $root"
        } else {
            & (Join-Path $PSScriptRoot 'setup-board-view.ps1') -WorktreeRoot $root -ExcludeSnapshots
        }
    }
}
if (-not $Apply) { Write-Host 'Preview only. Use -Apply to create shortcuts.' }

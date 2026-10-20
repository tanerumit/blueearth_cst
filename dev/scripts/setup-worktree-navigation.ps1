# Preview or create ignored Explorer shortcuts; never copy worktree contents.
param(
    [switch]$Apply,
    [switch]$ExcludeSnapshots,
    [string[]]$Worktree
)
$ErrorActionPreference = 'Stop'
if (-not $IsWindows) { throw 'Explorer navigation requires Windows.' }
if ($ExcludeSnapshots -and -not $Worktree) {
    throw '-ExcludeSnapshots requires explicitly named targets: -Worktree session-N.'
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$lines = @(git -C $repoRoot worktree list --porcelain)
if ($LASTEXITCODE -ne 0) { throw 'Cannot list worktrees.' }
$roots = @()
$mainRoot = $null
$root = $null
foreach ($line in $lines) {
    if ($line.StartsWith('worktree ')) {
        $root = [IO.Path]::GetFullPath($line.Substring(9))
        $roots += $root
    } elseif ($line -eq 'branch refs/heads/main') {
        if ($mainRoot) { throw 'Expected exactly one registered main worktree.' }
        $mainRoot = $root
    }
}
if (-not $mainRoot) { throw 'Expected a registered main worktree; nothing changed.' }

$destinations = [ordered]@{ 'main-dev' = (Join-Path $mainRoot 'dev') }
foreach ($root in $roots) {
    $label = if ($root -eq $mainRoot) { 'main' } else { Split-Path $root -Leaf }
    if ($destinations.Contains($label)) { throw "Duplicate navigation label: $label" }
    $destinations[$label] = $root
}
$selected = if ($Worktree) {
    foreach ($name in $Worktree) {
        if ($name -eq 'main-dev' -or -not $destinations.Contains($name)) {
            throw "Unknown worktree: $name; nothing changed."
        }
        $destinations[$name]
    }
} else { $roots }
$selected = @($selected | Select-Object -Unique)

# Read existing shortcuts even in preview; CreateShortcut does not write until Save.
$shell = New-Object -ComObject WScript.Shell
$plans = @()
$failures = @()
foreach ($root in $selected) {
    try {
        $navigationPath = Join-Path $root '.tmp/navigation'
        foreach ($relative in @('', '.tmp', '.tmp/navigation', '.tmp/tasks', 'dev')) {
            $parentPath = if ($relative) { Join-Path $root $relative } else { $root }
            $existing = Get-Item -LiteralPath $parentPath -Force -ErrorAction SilentlyContinue
            if (($relative -eq '' -and -not $existing) -or ($existing -and
                    (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
                    -not $existing.PSIsContainer))) {
                throw "Refusing missing, linked or non-directory navigation parent: $parentPath"
            }
        }
        git -C $root check-ignore -q .tmp/navigation/
        if ($LASTEXITCODE -ne 0) { throw "Navigation must be ignored before setup: $root" }
        $targets = [ordered]@{}
        foreach ($label in $destinations.Keys) {
            if (-not (Test-Path -LiteralPath $destinations[$label] -PathType Container)) {
                throw "Missing navigation target: $($destinations[$label])"
            }
            $targets[$label] = $destinations[$label]
        }
        $targets['local-tasks'] = Join-Path $root 'dev/tasks'
        $targets['local-scratch'] = Join-Path $root '.tmp/tasks'
        $existingShortcuts = @(Get-ChildItem -LiteralPath $navigationPath -Filter '*.lnk' -Force -ErrorAction SilentlyContinue)
        foreach ($existing in $existingShortcuts) {
            if (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $existing.PSIsContainer) {
                throw "Refusing unrelated shortcut path: $($existing.FullName)"
            }
            $shortcut = $shell.CreateShortcut($existing.FullName)
            if (-not $shortcut.TargetPath -or -not (Test-Path -LiteralPath $shortcut.TargetPath)) {
                Write-Warning "Stale shortcut retained: $($existing.FullName) -> $($shortcut.TargetPath)"
            }
        }
        foreach ($label in $targets.Keys) {
            $shortcutPath = Join-Path $navigationPath "$label.lnk"
            $existing = Get-Item -LiteralPath $shortcutPath -Force -ErrorAction SilentlyContinue
            if ($existing) {
                if (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $existing.PSIsContainer) {
                    throw "Refusing unrelated shortcut path: $shortcutPath"
                }
                $shortcut = $shell.CreateShortcut($shortcutPath)
                $legacyScratch = $label -eq 'local-scratch' -and $shortcut.TargetPath -and
                    [IO.Path]::GetFullPath($shortcut.TargetPath) -eq (Join-Path $root '.tmp/scratchpad')
                if (-not $shortcut.TargetPath -or [IO.Path]::GetFullPath($shortcut.TargetPath) -ne
                        [IO.Path]::GetFullPath($targets[$label]) -and -not $legacyScratch) {
                    throw "Refusing to replace a different shortcut: $shortcutPath"
                }
            }
        }
        if ($ExcludeSnapshots) {
            & (Join-Path $PSScriptRoot 'setup-board-view.ps1') -WorktreeRoot $root -ExcludeSnapshots -CheckOnly
        }
        $plans += [pscustomobject]@{ Root = $root; Navigation = $navigationPath; Targets = $targets }
    } catch {
        $failures += "$root : $($_.Exception.Message)"
        Write-Warning $failures[-1]
    }
}

# All selected worktrees have been checked before the first mutation.
foreach ($plan in $plans) {
    try {
        Write-Host "Navigation: $($plan.Navigation)"
        if ($Apply) {
            New-Item -ItemType Directory -Path $plan.Navigation -Force | Out-Null
            New-Item -ItemType Directory -Path $plan.Targets['local-scratch'] -Force | Out-Null
        }
        foreach ($label in $plan.Targets.Keys) {
            if ($Apply) {
                $shortcut = $shell.CreateShortcut((Join-Path $plan.Navigation "$label.lnk"))
                $shortcut.TargetPath = $plan.Targets[$label]
                $shortcut.Description = 'Worktree navigation; files remain in their owning checkout.'
                $shortcut.Save()
            }
            Write-Host "  $label -> $($plan.Targets[$label])"
        }
        if ($Apply -and $ExcludeSnapshots) {
            & (Join-Path $PSScriptRoot 'setup-board-view.ps1') -WorktreeRoot $plan.Root -ExcludeSnapshots
        }
    } catch {
        $failures += "$($plan.Root) : $($_.Exception.Message)"
        Write-Warning $failures[-1]
    }
}
if (-not $Apply) { Write-Host 'Preview only. Use -Apply to create shortcuts.' }
if ($failures.Count) {
    Write-Warning "Navigation failed for $($failures.Count) of $($selected.Count) worktrees; valid targets continued."
    exit 1
}
Write-Host "Navigation checked for $($selected.Count) worktrees."

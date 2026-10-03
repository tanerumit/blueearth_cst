# Give session worktrees a visible Explorer path to the canonical board on main.
# The tracked board snapshots stay intact for Git; Explorer hides them locally.
param([string]$WorktreeRoot = (Join-Path $PSScriptRoot '../..'))
$ErrorActionPreference = 'Stop'
if (-not $IsWindows) { return }

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$targetRoot = (Resolve-Path -LiteralPath $WorktreeRoot).Path
$worktrees = git -C $repoRoot worktree list --porcelain
if ($LASTEXITCODE -ne 0) { throw 'Cannot list Git worktrees.' }

$mainRoot = $null
$currentRoot = $null
$path = $null
foreach ($line in @($worktrees) + '') {
    if ($line.StartsWith('worktree ')) {
        $path = $line.Substring(9)
    } elseif ($line -eq 'branch refs/heads/main') {
        $mainRoot = $path
    } elseif ($line -eq '' -and $path) {
        if ([IO.Path]::GetFullPath($path) -eq [IO.Path]::GetFullPath($targetRoot)) {
            $currentRoot = $path
        }
        $path = $null
    }
}
if (-not $mainRoot -or -not $currentRoot) { throw 'Expected this checkout and one main worktree.' }
if ([IO.Path]::GetFullPath($mainRoot) -eq [IO.Path]::GetFullPath($targetRoot)) { return }

$sessionDev = Join-Path $targetRoot 'dev'
$mainDev = Join-Path $mainRoot 'dev'
$link = Join-Path $sessionDev '00-current-board-main'
$todo = Join-Path $sessionDev 'TODO.md'
$tasks = Join-Path $sessionDev 'tasks'
if (-not (Test-Path -LiteralPath (Join-Path $mainDev 'TODO.md')) -or
    -not (Test-Path -LiteralPath (Join-Path $mainDev 'tasks')) -or
    -not (Test-Path -LiteralPath $todo) -or
    -not (Test-Path -LiteralPath $tasks)) {
    throw 'The main or session board is missing.'
}

$existing = Get-Item -LiteralPath $link -Force -ErrorAction SilentlyContinue
if ($existing) {
    if ($existing.LinkType -ne 'Junction' -or
        [IO.Path]::GetFullPath($existing.Target) -ne [IO.Path]::GetFullPath($mainDev)) {
        throw "Refusing to replace an unrelated path: $link"
    }
} else {
    New-Item -ItemType Junction -Path $link -Target $mainDev | Out-Null
}

attrib.exe +h $todo
if ($LASTEXITCODE -ne 0) { throw "Cannot hide $todo" }
attrib.exe +h $tasks
if ($LASTEXITCODE -ne 0) { throw "Cannot hide $tasks" }
Write-Host "Current board: $link"

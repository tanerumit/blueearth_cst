# Exclude branch snapshots or expose main's canonical board in a session.
param(
    [string]$WorktreeRoot = (Join-Path $PSScriptRoot '../..'),
    [switch]$ExcludeSnapshots,
    [switch]$LinkCanonicalBoard,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
if ($ExcludeSnapshots -eq $LinkCanonicalBoard) {
    throw 'Choose -ExcludeSnapshots or -LinkCanonicalBoard.'
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$targetRoot = (Resolve-Path -LiteralPath $WorktreeRoot).Path
$lines = @(git -C $repoRoot worktree list --porcelain)
if ($LASTEXITCODE -ne 0) { throw 'Cannot list Git worktrees.' }
$registered = $false
$isMain = $false
$mainRoot = $null
$path = $null
foreach ($line in $lines) {
    if ($line.StartsWith('worktree ')) {
        $path = [IO.Path]::GetFullPath($line.Substring(9))
        if ($path -eq $targetRoot) { $registered = $true }
    } elseif ($line -eq 'branch refs/heads/main') {
        if ($mainRoot) { throw 'Expected exactly one main checkout.' }
        $mainRoot = $path
        if ($path -eq $targetRoot) { $isMain = $true }
    }
}
if (-not $registered -or $isMain) { throw 'Snapshot exclusion requires a registered session worktree.' }
$sparse = git -C $targetRoot config --bool core.sparseCheckout
if ($LASTEXITCODE -notin @(0, 1)) { throw "Cannot read sparse configuration: $targetRoot" }
if ($sparse -eq 'true') {
    $patterns = @(git -C $targetRoot sparse-checkout list)
    if ($LASTEXITCODE -ne 0 -or ($patterns -join "`n") -ne "/*`n!/dev/TODO.md`n!/dev/tasks/") {
        throw "Refusing to replace a custom sparse layout: $targetRoot"
    }
}
if ($LinkCanonicalBoard) {
    if (-not $IsWindows -or -not $mainRoot -or $sparse -ne 'true') {
        throw 'Canonical links require Windows, a main checkout and prior -ExcludeSnapshots setup.'
    }
    # Never traverse an unexpected parent or relocate linked scratch.
    foreach ($relative in @('', 'dev', '.tmp')) {
        $parent = if ($relative) { Join-Path $targetRoot $relative } else { $targetRoot }
        $item = Get-Item -LiteralPath $parent -Force -ErrorAction SilentlyContinue
        if ($item -and (-not $item.PSIsContainer -or
                ($item.Attributes -band [IO.FileAttributes]::ReparsePoint))) {
            throw "Refusing linked or non-directory parent: $parent"
        }
    }
    $boardChanges = @(git -C $targetRoot diff HEAD --name-only -- dev/TODO.md dev/tasks)
    if ($LASTEXITCODE -ne 0 -or $boardChanges.Count) { throw 'Session board changes must be resolved first.' }
    $untracked = @(git -C $targetRoot ls-files --others --exclude-standard -- dev/tasks)
    if ($LASTEXITCODE -ne 0 -or $untracked.Count) { throw 'Session tasks contain unignored files.' }
    $scratch = Join-Path $targetRoot '.tmp/tasks'
    git -C $targetRoot check-ignore -q .tmp/tasks/
    if ($LASTEXITCODE -ne 0) { throw 'Local .tmp/tasks must be ignored before setup.' }
    $ignorePath = Join-Path $targetRoot 'dev/.gitignore'
    $ignoreText = "# Managed by setup-board-view.ps1; canonical board aliases only.`n/.gitignore`n/tasks/`n/TODO.md`n"
    $trackedIgnore = @(git -C $targetRoot ls-files -- dev/.gitignore)
    if ($LASTEXITCODE -ne 0 -or $trackedIgnore.Count) { throw 'dev/.gitignore must be local and untracked.' }
    $existingIgnore = Get-Item -LiteralPath $ignorePath -Force -ErrorAction SilentlyContinue
    if ($existingIgnore -and ($existingIgnore.LinkType -or $existingIgnore.PSIsContainer -or
            [IO.File]::ReadAllText($ignorePath) -ne $ignoreText)) {
        throw 'Refusing to replace an unrelated dev/.gitignore.'
    }
    $links = @(
        @{ Name = 'TODO.md'; Type = 'SymbolicLink'; Container = $false },
        @{ Name = 'tasks'; Type = 'Junction'; Container = $true }
    )
    foreach ($link in $links) {
        $link.Source = Join-Path $targetRoot "dev/$($link.Name)"
        $link.Target = Join-Path $mainRoot "dev/$($link.Name)"
        $canonical = Get-Item -LiteralPath $link.Target -Force
        if ($canonical.LinkType -or $canonical.PSIsContainer -ne $link.Container) {
            throw "Unexpected canonical board target: $($link.Target)"
        }
        $item = Get-Item -LiteralPath $link.Source -Force -ErrorAction SilentlyContinue
        $link.Exists = $false
        if (-not $item) { continue }
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            if ($item.LinkType -ne $link.Type -or
                    [IO.Path]::GetFullPath($item.Target) -ne $link.Target) {
                throw "Refusing unrelated board link: $($link.Source)"
            }
            $link.Exists = $true
        } elseif ($link.Name -eq 'tasks' -and $item.PSIsContainer) {
            if (Test-Path -LiteralPath $scratch) { throw "Scratch destination already exists: $scratch" }
            $children = @(Get-ChildItem -LiteralPath $link.Source -Recurse -Force)
            if ($children | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) {
                throw 'Refusing to relocate scratch containing links.'
            }
            # Sparse index entries must never be mistaken for local scratch.
            $tracked = @(git -C $targetRoot ls-files -- dev/tasks)
            if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect tracked task paths.' }
            foreach ($file in $tracked) {
                if (Test-Path -LiteralPath (Join-Path $targetRoot $file)) {
                    throw "Tracked snapshot still present: $file"
                }
            }
            $link.MoveScratch = $true
        } else { throw "Refusing to replace board path: $($link.Source)" }
    }
    if ($CheckOnly) {
        Write-Host "Canonical board preflight passed: $targetRoot"
        return
    }
    git -C $targetRoot config --worktree sparse.expectFilesOutsideOfPatterns true
    if ($LASTEXITCODE -ne 0) { throw 'Cannot configure sparse board aliases.' }
    [IO.File]::WriteAllText($ignorePath, $ignoreText)
    foreach ($link in $links) {
        if ($link.Exists) { continue }
        if ($link.MoveScratch) {
            New-Item -ItemType Directory -Path (Join-Path $targetRoot '.tmp') -Force | Out-Null
            Move-Item -LiteralPath $link.Source -Destination $scratch
        }
        New-Item -ItemType $link.Type -Path $link.Source -Target $link.Target | Out-Null
    }
    Write-Host "Canonical board linked: $targetRoot -> $mainRoot"
    return
}
if ($sparse -eq 'true') {
    Write-Host "Board snapshots already excluded: $targetRoot"
    return
}
$changes = @(git -C $targetRoot status --porcelain)
if ($LASTEXITCODE -ne 0 -or $changes.Count) {
    throw "The target worktree must be clean before excluding board snapshots: $targetRoot"
}
if ($CheckOnly) { return }
git -C $targetRoot sparse-checkout set --no-cone '/*' '!/dev/TODO.md' '!/dev/tasks/'
if ($LASTEXITCODE -ne 0) { throw "Cannot exclude board snapshots: $targetRoot" }
Write-Host "Board snapshots excluded: $targetRoot"

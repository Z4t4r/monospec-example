#requires -Version 7.0
# Deploy reviewed templates only; never enumerate the source repository.
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$Target
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-NoReparsePoint([string]$Path) {
    $cursor = [System.IO.Path]::GetFullPath($Path)
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
                throw "Reparse point is not allowed: $cursor"
            }
        }
        $parent = Split-Path -Parent $cursor
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
}

function Resolve-PackagePath([string]$Root, [string]$Relative) {
    if ([string]::IsNullOrWhiteSpace($Relative) -or
        $Relative -match '(^[/\\]|:|(^|[/\\])\.\.?([/\\]|$))') {
        throw "Unsafe manifest path: $Relative"
    }
    $path = [System.IO.Path]::GetFullPath((Join-Path $Root $Relative))
    $prefix = $Root.TrimEnd([char[]]@('/', '\')) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $path.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes root: $Relative"
    }
    Assert-NoReparsePoint $path
    return $path
}

try {
    $packageRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
    $targetRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Target)
    $targetRoot = [System.IO.Path]::GetFullPath($targetRoot)
    Assert-NoReparsePoint $targetRoot
    if ((Test-Path -LiteralPath $targetRoot) -and
        -not (Test-Path -LiteralPath $targetRoot -PathType Container)) {
        throw 'Target must be a directory.'
    }
    $manifest = Get-Content -LiteralPath (Join-Path $packageRoot 'manifest.json') -Raw -Encoding utf8 | ConvertFrom-Json
    if ($manifest.schema_version -ne 1 -or $manifest.files.Count -eq 0) {
        throw 'Unsupported or empty manifest.'
    }
    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $plan = @()
    $conflicts = @()
    foreach ($entry in $manifest.files) {
        if (-not $seen.Add($entry.target)) { throw "Duplicate destination: $($entry.target)" }
        $source = Resolve-PackagePath $packageRoot $entry.source
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing template: $($entry.source)" }
        $destination = Resolve-PackagePath $targetRoot $entry.target
        # A file in a required parent path must fail before any writes.
        $parent = Split-Path -Parent $destination
        while ($parent -and $parent.Length -ge $targetRoot.Length) {
            if ((Test-Path -LiteralPath $parent) -and
                -not (Test-Path -LiteralPath $parent -PathType Container)) {
                throw "Destination parent is a file: $parent"
            }
            $parent = Split-Path -Parent $parent
        }
        $content = [System.IO.File]::ReadAllText($source).Replace("`r`n", "`n")
        if (Test-Path -LiteralPath $destination) {
            if (-not (Test-Path -LiteralPath $destination -PathType Leaf) -or
                [System.IO.File]::ReadAllText($destination).Replace("`r`n", "`n") -cne $content) {
                $conflicts += $entry.target
            }
        } else {
            $plan += @{ Destination = $destination; Content = $content; Relative = $entry.target }
        }
    }
    if ($conflicts.Count) { throw ("CONFLICT: " + ($conflicts -join ', ')) }
    foreach ($item in $plan) {
        if ($PSCmdlet.ShouldProcess($item.Destination, 'Install template')) {
            Assert-NoReparsePoint $item.Destination
            [System.IO.Directory]::CreateDirectory((Split-Path -Parent $item.Destination)) | Out-Null
            # CreateNew also refuses a file created by another process after preflight.
            $stream = [System.IO.File]::Open($item.Destination, [System.IO.FileMode]::CreateNew)
            try {
                $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($item.Content)
                $stream.Write($bytes, 0, $bytes.Length)
            } finally { $stream.Dispose() }
        }
    }
    if ($WhatIfPreference) { Write-Output "PLAN: $($plan.Count) new files" }
    elseif ($plan.Count) { Write-Output "INSTALLED: $($plan.Count) files; package $($manifest.version)" }
    else { Write-Output "UNCHANGED: package $($manifest.version)" }
} catch {
    Write-Error -Message $_.Exception.Message -ErrorAction Continue
    exit 1
}

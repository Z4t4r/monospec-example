#requires -Version 7.0
# Integration tests use disposable targets outside the source repository.
[CmdletBinding()]
param(
    [string]$SourceRoot,
    [string]$PythonExecutable
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$package = Split-Path -Parent $PSScriptRoot
$installer = Join-Path $package 'install.ps1'
$manifest = Get-Content -LiteralPath (Join-Path $package 'manifest.json') -Raw -Encoding utf8 | ConvertFrom-Json
$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('portable-bootstrap-' + [guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($testRoot) | Out-Null
$checks = 0

function Assert([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "FAIL: $Message" }
    $script:checks++
}

function Invoke-Installer([string]$Destination, [string]$Script = $installer, [switch]$Preview) {
    $arguments = @('-NoProfile', '-File', $Script, '-Target', $Destination)
    if ($Preview) { $arguments += '-WhatIf' }
    $output = & (Join-Path $PSHOME 'pwsh') @arguments 2>&1 | Out-String
    return @{ Code = $LASTEXITCODE; Output = $output }
}

try {
    $allowedPackageFiles = @('AGENTS.md', 'install.ps1', 'manifest.json', 'source-map.json', 'tests/run-tests.ps1') + @($manifest.files.source)
    $actualPackageFiles = @(Get-ChildItem -LiteralPath $package -Force -Recurse -File)
    Assert ($actualPackageFiles.Count -eq $allowedPackageFiles.Count) 'Package contains only reviewed files'
    foreach ($file in $actualPackageFiles) {
        $relative = [System.IO.Path]::GetRelativePath($package, $file.FullName).Replace('\', '/')
        Assert ($allowedPackageFiles -ccontains $relative) "Reviewed package file: $relative"
    }
    $sourceMap = Get-Content -LiteralPath (Join-Path $package 'source-map.json') -Raw -Encoding utf8 | ConvertFrom-Json
    $traitOrigins = @($sourceMap.files | Where-Object {$_.source -match '^traits/.+-trait\.md$'})
    Assert ($traitOrigins.Count -eq 17) 'All 17 current non-excluded Traits are shipped'
    foreach ($origin in $sourceMap.files) {
        $text = [System.IO.File]::ReadAllText((Join-Path $package $origin.template)).Replace("`r`n", "`n")
        $hash = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($text))).ToLowerInvariant()
        Assert ($hash -ceq $origin.template_sha256) "Source-map checksum matches full template: $($origin.target)"
        if ($SourceRoot) {
            $sourceText = [System.IO.File]::ReadAllText((Join-Path $SourceRoot $origin.source)).Replace("`r`n", "`n")
            $sourceHash = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($sourceText))).ToLowerInvariant()
            Assert ($sourceHash -ceq $origin.source_sha256) "Original source has not drifted: $($origin.source)"
        }
    }
    foreach ($origin in $traitOrigins) {
        Assert ($origin.unexpected_missing_heading_count -eq 0) "No unapproved section loss: $($origin.source)"
        Assert (($origin.retained_heading_count + $origin.excluded_section_numbers.Count) -eq $origin.source_heading_count) "Only explicitly excluded sections removed: $($origin.source)"
        Assert ($origin.template_lines -ge (0.9 * $origin.source_lines)) "Full Trait has not been replaced by summary: $($origin.source)"
        if ($origin.source -match '/(bmad|ced|docs|standard-words|technology-first)-trait\.md$') {
            Assert ($origin.identical -and $origin.source_sha256 -ceq $origin.template_sha256) "Domain-independent Trait is unchanged: $($origin.source)"
        }
    }
    $fevEntry = $manifest.files | Where-Object {$_.target -eq 'traits/fev-trait.md'}
    $icdEntry = $manifest.files | Where-Object {$_.target -eq 'traits/icd-trait.md'}
    $fevText = [System.IO.File]::ReadAllText((Join-Path $package $fevEntry.source)).Replace("`r`n", "`n")
    $icdText = [System.IO.File]::ReadAllText((Join-Path $package $icdEntry.source)).Replace("`r`n", "`n")
    Assert (@([regex]::Matches($fevText,'(?m)^# \d+\. ')).Count -eq 35) 'FEV retains all 35 numbered sections'
    Assert (@([regex]::Matches($icdText,'(?m)^# \d+\. ')).Count -eq 19) 'ICD retains all 19 numbered sections'
    foreach ($level in 1..4) { Assert ($icdText -match "(?m)^## L$level — ") "ICD L$level remains defined" }
    if ($SourceRoot) {
        $originalFev = [System.IO.File]::ReadAllText((Join-Path $SourceRoot 'traits/fev-trait.md')).Replace("`r`n", "`n")
        Assert ($originalFev.Substring($originalFev.IndexOf('# 1. Purpose')) -ceq $fevText.Substring($fevText.IndexOf('# 1. Purpose'))) 'Entire FEV mechanism body is unchanged from original'
        $originalIcd = [System.IO.File]::ReadAllText((Join-Path $SourceRoot 'traits/icd-trait.md')).Replace("`r`n", "`n")
        $expectedIcd = $originalIcd.Replace('Implement VMD parser.','Implement animation parser.').Replace('a supported VMD file','a supported animation file')
        Assert ($expectedIcd -ceq $icdText) 'ICD differs only in the excluded-domain example'
    }
    $archive = Join-Path $testRoot 'project-template.zip'
    Compress-Archive -LiteralPath $package -DestinationPath $archive
    $extracted = Join-Path $testRoot 'distribution'
    Expand-Archive -LiteralPath $archive -DestinationPath $extracted
    $result = Invoke-Installer (Join-Path $testRoot 'standalone') (Join-Path $extracted 'project-template/install.ps1')
    Assert ($result.Code -eq 0 -and $result.Output -match 'INSTALLED:') 'ZIP installs independently of source repository'
    $target = Join-Path $testRoot 'new project'
    $result = Invoke-Installer $target -Preview
    Assert ($result.Code -eq 0 -and $result.Output -match 'PLAN:') 'WhatIf succeeds'
    Assert (-not (Test-Path -LiteralPath $target)) 'WhatIf creates nothing'

    $result = Invoke-Installer $target
    Assert ($result.Code -eq 0 -and $result.Output -match 'INSTALLED:') 'Empty target installation succeeds'
    $installed = @(Get-ChildItem -LiteralPath $target -Force -Recurse -File)
    Assert ($installed.Count -eq $manifest.files.Count) 'Only manifest files are installed'
    $timestamps = @{}
    foreach ($file in $installed) { $timestamps[$file.FullName] = $file.LastWriteTimeUtc.Ticks }
    $result = Invoke-Installer $target
    Assert ($result.Code -eq 0 -and $result.Output -match 'UNCHANGED:') 'Repeat installation is idempotent'
    foreach ($file in Get-ChildItem -LiteralPath $target -Force -Recurse -File) {
        Assert ($timestamps[$file.FullName] -eq $file.LastWriteTimeUtc.Ticks) 'Existing files are not rewritten'
    }

    # Git autocrlf must not turn a matching destination into a conflict.
    $rootEntry = Join-Path $target 'AGENTS.md'
    $rootContent = [System.IO.File]::ReadAllText($rootEntry)
    [System.IO.File]::WriteAllText($rootEntry, $rootContent.Replace("`n", "`r`n"))
    $result = Invoke-Installer $target
    Assert ($result.Code -eq 0 -and $result.Output -match 'UNCHANGED:') 'CRLF checkout remains idempotent'

    # A conflict in the final destination must prevent earlier new files too.
    $conflictTarget = Join-Path $testRoot 'conflict'
    $conflictFile = Join-Path $conflictTarget 'bootstrap/AGENTS.md'
    [System.IO.Directory]::CreateDirectory((Split-Path -Parent $conflictFile)) | Out-Null
    [System.IO.File]::WriteAllText($conflictFile, 'Existing project policy')
    $result = Invoke-Installer $conflictTarget
    Assert ($result.Code -ne 0 -and $result.Output -match 'CONFLICT:') 'Conflict returns failure'
    Assert (-not (Test-Path -LiteralPath (Join-Path $conflictTarget 'AGENTS.md'))) 'Conflict preflight prevents partial installation'
    Assert ([System.IO.File]::ReadAllText($conflictFile) -ceq 'Existing project policy') 'Conflict preserves user content'

    $blockedTarget = Join-Path $testRoot 'blocked'
    [System.IO.Directory]::CreateDirectory($blockedTarget) | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $blockedTarget 'traits'), 'Existing file')
    $result = Invoke-Installer $blockedTarget
    Assert ($result.Code -ne 0) 'File in required parent path fails'
    Assert (-not (Test-Path -LiteralPath (Join-Path $blockedTarget 'AGENTS.md'))) 'Blocked parent prevents partial installation'

    # Simulate a modified package in a disposable copy, never change the source.
    $badPackage = Join-Path $testRoot 'bad-package'
    Copy-Item -LiteralPath $package -Destination $badPackage -Recurse
    $badManifestPath = Join-Path $badPackage 'manifest.json'
    $originalManifest = [System.IO.File]::ReadAllText($badManifestPath)
    foreach ($attack in @('../escape.md', '/absolute.md', 'C:\escape.md', 'nested/../../escape.md')) {
        $badManifest = $originalManifest | ConvertFrom-Json
        $badManifest.files[-1].target = $attack
        $badManifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $badManifestPath -Encoding utf8
        $badTarget = Join-Path $testRoot 'unsafe-target'
        $result = Invoke-Installer $badTarget (Join-Path $badPackage 'install.ps1')
        Assert ($result.Code -ne 0) "Reject manifest traversal: $attack"
        Assert (-not (Test-Path -LiteralPath $badTarget)) 'Unsafe manifest writes nothing'
    }
    $badManifest = $originalManifest | ConvertFrom-Json
    $badManifest.files[-1].source = '../outside.template'
    $badManifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $badManifestPath -Encoding utf8
    $result = Invoke-Installer (Join-Path $testRoot 'unsafe-source') (Join-Path $badPackage 'install.ps1')
    Assert ($result.Code -ne 0) 'Reject source traversal'

    $badManifest = $originalManifest | ConvertFrom-Json
    $badManifest.files[-1].target = 'agents.md'
    $badManifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $badManifestPath -Encoding utf8
    $result = Invoke-Installer (Join-Path $testRoot 'duplicate') (Join-Path $badPackage 'install.ps1')
    Assert ($result.Code -ne 0 -and $result.Output -match 'Duplicate destination') 'Reject case-insensitive duplicate'

    $outside = Join-Path $testRoot 'outside'
    [System.IO.Directory]::CreateDirectory($outside) | Out-Null
    $linkedTarget = Join-Path $testRoot 'linked-target'
    [System.IO.Directory]::CreateDirectory($linkedTarget) | Out-Null
    $link = Join-Path $linkedTarget 'traits'
    $linkType = if ($IsWindows) { 'Junction' } else { 'SymbolicLink' }
    New-Item -ItemType $linkType -Path $link -Target $outside | Out-Null
    try {
        $result = Invoke-Installer $linkedTarget
        Assert ($result.Code -ne 0 -and $result.Output -match 'Reparse point') 'Reject target junction / symlink'
        Assert (@(Get-ChildItem -LiteralPath $outside -Force).Count -eq 0) 'No write through junction / symlink'
        Assert (-not (Test-Path -LiteralPath (Join-Path $linkedTarget 'AGENTS.md'))) 'Link preflight prevents partial installation'
    } finally {
        # Delete only the link itself, never recurse into the external target.
        Remove-Item -LiteralPath $link -Force
    }

    # The allowlist and privacy checks cover every deployed text file.
    $templateFiles = @(Get-ChildItem -LiteralPath (Join-Path $package 'templates') -File -Force)
    Assert ($templateFiles.Count -eq $manifest.files.Count) 'No unlisted templates'
    foreach ($entry in $manifest.files) {
        $source = Join-Path $package $entry.source
        $deployed = Join-Path $target $entry.target
        Assert (Test-Path -LiteralPath $source -PathType Leaf) "Template exists: $($entry.source)"
        $content = [System.IO.File]::ReadAllText($deployed)
        Assert ($content -notmatch '(?i)MMD|PMX|PMD|VMD|VRM4U|mmd_tools|mmd_core|Velina|Parvati|CharacterSamples|BlenderTools-MonoSpecs') "No excluded domain / source business identity: $($entry.target)"
        Assert ($content -notmatch '(?i)(?<![a-z])[A-Z]:[\\/]|/Users/|/home/|file://|localhost:\d|127\.0\.0\.1:\d|77162') "No machine path / endpoint / account: $($entry.target)"
        Assert ($content -notmatch '(?i)-----BEGIN .*PRIVATE KEY|sk-[A-Za-z0-9]{16}|gh[pousr]_[A-Za-z0-9]{16}') "No recognized credential pattern: $($entry.target)"
        Assert ($entry.target -notmatch '(?i)(^|/)README\.md$|\.(blend|uasset|umap|fbx|glb)$') 'No directory README or assets'
        if ($entry.target -notmatch '\.md$') { continue }
        # Examples inside fenced code are not real Markdown navigation links.
        $markdown = [regex]::Replace($content, '(?ms)^```.*?^```[^\n]*', '')
        foreach ($match in [regex]::Matches($markdown, '\[[^\]]+\]\(([^)]+)\)')) {
            $reference = $match.Groups[1].Value.Split('#')[0]
            if (-not $reference) { continue }
            $resolved = [System.IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $deployed) $reference))
            Assert (Test-Path -LiteralPath $resolved) "Installed Markdown link resolves: $($entry.target) -> $reference"
        }
    }
    $registry = [System.IO.File]::ReadAllText((Join-Path $target '.hagicode/monospecs.yaml'))
    Assert ($registry -match '(?m)^version: "1.0"') 'MonoSpec schema version preserved'
    Assert ($registry -match '(?m)^repo_dir: repos') 'Business projects sideload under repos'
    Assert ($registry -match '(?m)^commit_when_archive: true') 'MonoSpec archive behavior preserved'
    Assert ($registry -match '(?m)^repositories: \[\]') 'Source business registry is empty'
    foreach ($field in @('path','url','displayName','description','optional','tags')) {
        Assert ($registry -match "(?m)^#\s+(?:- )?${field}:") "MonoSpec entry example preserves $field"
    }
    if ($PythonExecutable) {
        Push-Location (Join-Path $target 'pipelines/_shared')
        try {
            & $PythonExecutable -m fev_parallel self-test
            Assert ($LASTEXITCODE -eq 0) 'Installed FEV P0-P8 self-tests pass'
            & $PythonExecutable -m unittest cook_runtime.test_evidence
            Assert ($LASTEXITCODE -eq 0) 'Installed Evidence helper regression tests pass'
        } finally { Pop-Location }
        & $PythonExecutable (Join-Path $target '.github/scripts/validate_docs_topics.py') --strict-existing-links
        Assert ($LASTEXITCODE -eq 0) 'Installed DOCS policy validator passes without source baseline debt'
    }
    # A root-level symlink is also rejected by ancestor traversal.
    $rootLink = Join-Path $testRoot 'root-link'
    New-Item -ItemType $linkType -Path $rootLink -Target $outside | Out-Null
    try {
        $result = Invoke-Installer (Join-Path $rootLink 'child')
        Assert ($result.Code -ne 0) 'Reject symlink / junction ancestor of target root'
    } finally { Remove-Item -LiteralPath $rootLink -Force }

    Write-Output "PASS: $checks checks; PowerShell $($PSVersionTable.PSVersion)"
} finally {
    # Verify the exact disposable root before recursive cleanup.
    $resolvedTestRoot = [System.IO.Path]::GetFullPath($testRoot)
    $tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd([char[]]@('/', '\')) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $resolvedTestRoot.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
        (Split-Path -Leaf $resolvedTestRoot) -notmatch '^portable-bootstrap-[a-f0-9]{32}$') {
        throw "Refusing cleanup outside disposable test root: $resolvedTestRoot"
    }
    Remove-Item -LiteralPath $resolvedTestRoot -Recurse -Force
}

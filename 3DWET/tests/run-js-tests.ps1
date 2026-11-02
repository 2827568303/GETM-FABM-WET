$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$testFiles = @(
    Get-ChildItem -LiteralPath $PSScriptRoot -Filter 'test_*.js' -File
    Get-ChildItem -LiteralPath (Join-Path $repoRoot 'tests') -Recurse -File |
        Where-Object {
            $_.Extension -in @('.js', '.cjs', '.mjs') -and
            $_.FullName -notmatch '[\\/](build|CMakeFiles|node_modules)[\\/]'
        }
) | Sort-Object FullName
$nodeTestFiles = @()
$standaloneFiles = @()

foreach ($testFile in $testFiles) {
    $source = Get-Content -LiteralPath $testFile.FullName -Raw
    if ($source -match 'node:test') {
        $nodeTestFiles += $testFile.FullName
    } else {
        $standaloneFiles += $testFile.FullName
    }
}

$failed = @()
Push-Location $repoRoot
try {
    if ($nodeTestFiles.Count -gt 0) {
        Write-Host "Running $($nodeTestFiles.Count) node:test files"
        & node --test --test-concurrency=1 --test-timeout=10000 @nodeTestFiles
        if ($LASTEXITCODE -ne 0) { $failed += 'node:test files' }
    }

    foreach ($standaloneFile in $standaloneFiles) {
        Write-Host "Running $([IO.Path]::GetFileName($standaloneFile))"
        & node $standaloneFile
        if ($LASTEXITCODE -ne 0) { $failed += [IO.Path]::GetFileName($standaloneFile) }
    }
} finally {
    Pop-Location
}

if ($failed.Count -gt 0) {
    Write-Error "JavaScript test failures: $($failed -join ', ')"
    exit 1
}

Write-Host "All $($testFiles.Count) JavaScript test files passed (3DWET/tests + repository tests/)."

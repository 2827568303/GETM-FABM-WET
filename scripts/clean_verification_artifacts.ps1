param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$outputRoot = $env:WET_OUTPUT_ROOT
if ([string]::IsNullOrWhiteSpace($outputRoot)) { $outputRoot = 'D:\GETM-FABM-WET-outputs' }
$outputRoot = [IO.Path]::GetFullPath($outputRoot)
function Assert-OutsideSystemDrive {
    param([string]$Path, [string]$Label)
    $fullPath = [IO.Path]::GetFullPath($Path)
    if ([IO.Path]::GetPathRoot($fullPath).Equals('C:\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label must be outside C:. Refusing to write to $fullPath"
    }
    return $fullPath
}
$outputRoot = Assert-OutsideSystemDrive -Path $outputRoot -Label 'WET_OUTPUT_ROOT'
$buildRoot = [IO.Path]::GetFullPath((Join-Path $outputRoot '_migrated_from_c_20261027\build'))
$releaseRoot = [IO.Path]::GetFullPath((Join-Path $outputRoot '_migrated_from_c_20261027\release'))
$audit = Join-Path $outputRoot 'audit\2026-10-11-evidence'
$manifestPath = Assert-OutsideSystemDrive -Path (Join-Path $outputRoot 'build\cleanup-manifests\2026-10-11-cleanup.json') -Label 'Cleanup manifest'
foreach ($name in @('final-packaged-all6-20261011','final-packaged-external-20261011','final-packaged-features-20261011','final-installed-standalone-20261011-retry')) {
    $report = Get-Content -LiteralPath (Join-Path $audit ($name+'\verification.json')) -Encoding UTF8 -Raw | ConvertFrom-Json
    if (-not $report.passed) { throw "Final verification incomplete: $name" }
}
# Exact names from the inspected build inventory; unrelated new directories are preserved.
$names = @(
 'category-output-probe','current-case-native-smoke','direct-package-luoma-20261009',
 'external-alternative-inputs-20261010','external-random-20261010','external-random-all-engines-20261010','external-random-doy-all-engines-20261010',
 'feature-matrix-20261010','feature-matrix-20261010-complete','feature-matrix-20261010-final','feature-matrix-20261010-final2','feature-matrix-20261010b',
 'final-packaged-all6-20261011','final-packaged-external-20261011','final-packaged-features-20261011','final-preview-20261011',
 'final-installed-standalone-20261011','final-installed-standalone-20261011-retry','final-installer-upgrade-20261011',
 'installed-coupled-verified','installer-fixture','installer-fixture-output','installer-preservation-test',
 'native-pressure-regression-20261010','native-pressure-regression-20261010-2','native-pressure-regression-20261010-3','native-smoke',
 'packaged-coupled-final','packaged-coupled-test','packaged-coupled-verified','performance-benchmark','performance-benchmark-v2','pyinstaller',
 'root-cause-probe-20261010','source-all-five-20261010','source-final-defaults-all5-20261010','theoretical-relative-datum-20261010','usability-ui-root',
 'verify-all-builtin-cases-20261009','verify-all-builtin-cases-20261009-2','verify-packaged-all-cases-20261009','verify-packaged-all-cases-20261009-2','verify-packaged-all-cases-20261009-3',
 'verify-packaged-luoma-20261009','verify-packaged-luoma-20261009-3','verify-packaged-luoma-20261009-4','verify-packaged-luoma-20261009-5',
 'verify-packaged-luoma-no-lock-20261009','verify-packaged-luoma-no3d-20261009','verify-packaged-luoma-poll2-20261009','verify-packaged-luoma-poll4-20261009',
 'verify-packaged-luoma-slowpoll-20261009','verify-packaged-luoma-true-lock-20261009','verify-packaged-nativetest-20261009','verify-packaged-studiodemo-20261009',
 'verify-source-launcher-packaged-model-luoma-20261009','verify-source-luoma-20261009'
)
$targets = @($names | ForEach-Object {Join-Path $buildRoot $_})
$targets += Join-Path $releaseRoot 'stage'
$targets += Join-Path $releaseRoot 'verification'
$targets += @(Get-ChildItem -LiteralPath $buildRoot -File | Where-Object {$_.Extension -eq '.log' -or $_.Name -eq '3DWETStudio.spec'} | Select-Object -ExpandProperty FullName)
$manifest = @()
foreach ($target in $targets) {
    if (-not (Test-Path -LiteralPath $target)) { continue }
    $resolved = (Resolve-Path -LiteralPath $target).Path
    $allowed = $resolved.StartsWith($buildRoot+'\',[StringComparison]::OrdinalIgnoreCase) -or
               $resolved -eq (Join-Path $releaseRoot 'stage') -or $resolved.StartsWith((Join-Path $releaseRoot 'stage')+'\',[StringComparison]::OrdinalIgnoreCase) -or
               $resolved -eq (Join-Path $releaseRoot 'verification') -or $resolved.StartsWith((Join-Path $releaseRoot 'verification')+'\',[StringComparison]::OrdinalIgnoreCase)
    if (-not $allowed) { throw "Refused path outside generated directories: $resolved" }
    $item = Get-Item -LiteralPath $resolved
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refused linked target: $resolved" }
    if ($item.PSIsContainer) {
        $children = @(Get-ChildItem -LiteralPath $resolved -Recurse -Force)
        if (@($children | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count) { throw "Refused directory containing links: $resolved" }
        $bytes = ($children | Where-Object {-not $_.PSIsContainer} | Measure-Object Length -Sum).Sum
    } else { $bytes = $item.Length }
    $manifest += [pscustomobject][ordered]@{path=$resolved; bytes=$bytes}
}
$summary = [ordered]@{applied=[bool]$Apply; targets=$manifest; bytes=($manifest | Measure-Object bytes -Sum).Sum;
    retained='Source, original case inputs/user data, installed application, installer, synthetic input archive, evidence, build toolchains and native rollback snapshot.'}
$manifestParent = Split-Path -Parent $manifestPath
New-Item -ItemType Directory -Path $manifestParent -Force | Out-Null
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
if ($Apply) {
    foreach ($entry in $manifest) { Remove-Item -LiteralPath $entry.path -Recurse -Force }
}
Write-Output ("Targets={0}; GiB={1:N2}; Applied={2}" -f $manifest.Count,($summary.bytes/1GB),[bool]$Apply)

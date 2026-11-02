param([string]$Version = '1.3.0')
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
if ($Version -notmatch '^\d+\.\d+\.\d+(\.\d+)?$') { throw 'Version must be a numeric version such as 1.3.0.' }
$outputRoot = $env:WET_OUTPUT_ROOT
if ([string]::IsNullOrWhiteSpace($outputRoot)) { $outputRoot = 'D:\GETM-FABM-WET-outputs' }
$outputRoot = [IO.Path]::GetFullPath($outputRoot)
if ([IO.Path]::GetPathRoot($outputRoot).Equals('C:\', [StringComparison]::OrdinalIgnoreCase)) {
    throw "WET_OUTPUT_ROOT must be outside C:. Refusing to write to $outputRoot"
}
$buildRoot = [IO.Path]::GetFullPath((Join-Path $outputRoot 'build')) + '\'
$fixture = [IO.Path]::GetFullPath((Join-Path $buildRoot "installer-upgrade-fixtures\$Version"))
if (-not $fixture.StartsWith($buildRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Fixture outside build directory.' }
if (Test-Path -LiteralPath $fixture) { throw 'Use a fresh installer fixture.' }
$oldDir = Join-Path $fixture '3DWET\case\Lake Dianchi'
$customDir = Join-Path $fixture '3DWET\case\Lake Luoma'
New-Item -ItemType Directory -Path $oldDir,$customDir -Force | Out-Null
$oldSource = Join-Path $repo 'docs\audit\2026-10-10-original-defaults\Lake Dianchi\getm.inp'
$oldTarget = Join-Path $oldDir 'getm.inp'
$customTarget = Join-Path $customDir 'getm.inp'
Copy-Item -LiteralPath $oldSource -Destination $oldTarget
[IO.File]::WriteAllText($customTarget, "! User custom fixture: must be preserved`r`n&time`r`n timestep = 3`r`n/`r`n")
$customHash = (Get-FileHash -LiteralPath $customTarget -Algorithm SHA256).Hash
$releaseBuild = Join-Path $outputRoot 'release\build'
$setup = Join-Path $releaseBuild '3DWETStudio-Setup.exe'
$args = @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/NOICONS','/TASKS=""',('/DIR="'+$fixture+'"'),('/LOG="'+(Join-Path $fixture 'installation.log')+'"'))
$process = Start-Process -FilePath $setup -ArgumentList $args -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0) { throw "Installer fixture failed: $($process.ExitCode)" }
$stageSource = Join-Path $releaseBuild 'stage\3DWETStudio\3DWET\case\Lake Dianchi\getm.inp'
$backup = $oldTarget + '.before-' + $Version + '.bak'
$checks = [ordered]@{
    installer_exit = $process.ExitCode
    factory_updated = (Get-FileHash -LiteralPath $oldTarget).Hash -eq (Get-FileHash -LiteralPath $stageSource).Hash
    factory_backup_matches_original = (Test-Path -LiteralPath $backup) -and ((Get-FileHash -LiteralPath $backup).Hash -eq (Get-FileHash -LiteralPath $oldSource).Hash)
    custom_preserved = (Get-FileHash -LiteralPath $customTarget).Hash -eq $customHash
    glossary_present = Test-Path -LiteralPath (Join-Path $fixture '_internal\fabm_glossary.json')
    icon_matches = (Get-FileHash -LiteralPath (Join-Path $fixture '3DWETStudio.ico')).Hash -eq (Get-FileHash -LiteralPath (Join-Path $repo '3DWET\app\static\brand\3dwet.ico')).Hash
}
$checks['passed'] = $checks.factory_updated -and $checks.factory_backup_matches_original -and $checks.custom_preserved -and $checks.glossary_present -and $checks.icon_matches
$reportDir = Join-Path $buildRoot 'installer-upgrade-reports'
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
$checks | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $reportDir "installer-upgrade-$Version.json") -Encoding UTF8
$checks | ConvertTo-Json
if (-not $checks.passed) { throw 'Installer preservation/upgrade checks failed.' }

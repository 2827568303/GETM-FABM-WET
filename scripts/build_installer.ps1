[CmdletBinding()]
param(
    [string]$StageDir,
    [string]$OutputDir,
    [string]$AppVersion = '1.0.0',
    [switch]$PrepareToolsOnly
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$installerDir = Join-Path $PSScriptRoot 'installer'
$configuredOutputRoot = $env:WET_OUTPUT_ROOT
if ([string]::IsNullOrWhiteSpace($configuredOutputRoot)) { $configuredOutputRoot = 'D:\GETM-FABM-WET-outputs' }
$outputRoot = [IO.Path]::GetFullPath($configuredOutputRoot)

function Assert-OutsideSystemDrive {
    param([string]$Path, [string]$Label)
    $fullPath = [IO.Path]::GetFullPath($Path)
    if ([IO.Path]::GetPathRoot($fullPath).Equals('C:\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label must be outside C:. Refusing to write to $fullPath"
    }
}

Assert-OutsideSystemDrive -Path $outputRoot -Label 'WET_OUTPUT_ROOT'
if (-not $StageDir) { $StageDir = Join-Path $outputRoot 'release\build\stage\3DWETStudio' }
if (-not $OutputDir) { $OutputDir = Join-Path $outputRoot 'release\build' }
$StageDir = [IO.Path]::GetFullPath($StageDir)
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
Assert-OutsideSystemDrive -Path $StageDir -Label 'StageDir'
Assert-OutsideSystemDrive -Path $OutputDir -Label 'OutputDir'
$toolsDir = Join-Path $outputRoot 'build\installer-tools'
$compilerDir = Join-Path $toolsDir 'InnoSetup'
$manifest = Get-Content -LiteralPath (Join-Path $installerDir 'downloads.json') -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null

function Assert-VerifiedDownload {
    param([string]$Path, [string]$Sha256, [string]$Signer)
    $actualHash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    if ($actualHash -ne $Sha256) { throw "SHA256 verification failed: $Path. Delete the cached file and retry; do not use it." }
    $signature = Get-AuthenticodeSignature -LiteralPath $Path
    $expectedCommonName = 'CN=' + $Signer + ','
    if ($signature.Status -ne 'Valid' -or -not $signature.SignerCertificate.Subject.Contains($expectedCommonName)) {
        throw "Authenticode verification failed: $Path; expected publisher $Signer; status $($signature.Status)."
    }
    Write-Host "Verified $([IO.Path]::GetFileName($Path)): SHA256 $actualHash; publisher $Signer"
}

foreach ($download in $manifest.files) {
    $target = Join-Path $toolsDir $download.filename
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        $partial = $target + '.download'
        Write-Host "Downloading official prerequisite: $($download.filename)"
        Invoke-WebRequest -Uri $download.url -OutFile $partial -UseBasicParsing
        Assert-VerifiedDownload $partial $download.sha256 $download.signer
        Move-Item -LiteralPath $partial -Destination $target
    }
    Assert-VerifiedDownload $target $download.sha256 $download.signer
}

$compiler = Join-Path $compilerDir 'ISCC.exe'
if (-not (Test-Path -LiteralPath $compiler -PathType Leaf)) {
    $innoInstaller = Join-Path $toolsDir 'innosetup-6.7.3.exe'
    $arguments = @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/CURRENTUSER', '/NOICONS', ('/DIR="' + $compilerDir + '"'), '/TASKS=""')
    $process = Start-Process -FilePath $innoInstaller -ArgumentList $arguments -WindowStyle Hidden -PassThru -Wait
    if ($process.ExitCode -ne 0) { throw "Task-local Inno Setup installation failed: exit $($process.ExitCode)" }
}
$compilerSignature = Get-AuthenticodeSignature -LiteralPath $compiler
if ($compilerSignature.Status -ne 'Valid' -or -not $compilerSignature.SignerCertificate.Subject.Contains('CN=Pyrsys B.V.,')) {
    throw 'Task-local Inno Setup compiler signature verification failed.'
}
if ($PrepareToolsOnly) { Write-Host "Verified installer tools ready: $toolsDir"; return }

foreach ($relative in @('3DWETStudio.exe', '_internal', '3DWET\bin\getm_cartesian.exe', '3DWET\bin\getm_cartesian_parallel.exe', '3DWET\bin\runtime', '3DWET\bin\mpi\mpiexec.exe', '3DWET\bin\mpi\msmpi.dll', '3DWET\bin\mpi\MS-MPI-LICENSE.txt', '3DWET\scripts\merge_getm_rank_outputs.py', '3DWET\case', 'DEPENDENCIES.txt', 'THIRD_PARTY_LICENSES')) {
    if (-not (Test-Path -LiteralPath (Join-Path $StageDir $relative))) { throw "Staged application is incomplete: missing $relative in $StageDir" }
}
$licenses = @(Get-ChildItem -LiteralPath (Join-Path $StageDir 'THIRD_PARTY_LICENSES') -File -Recurse)
if ($licenses.Count -eq 0) { throw 'THIRD_PARTY_LICENSES must contain actual bundled-component license files.' }
if ($AppVersion -notmatch '^\d+\.\d+\.\d+(\.\d+)?$') { throw 'AppVersion must be a numeric Windows version, e.g. 1.0.0.' }
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$compilerArgs = @('/Qp', ('/DStageDir=' + $StageDir), ('/DToolsDir=' + $toolsDir), ('/DOutputDir=' + $OutputDir), ('/DAppVersion=' + $AppVersion), (Join-Path $installerDir '3DWETStudio.iss'))
& $compiler @compilerArgs
if ($LASTEXITCODE -ne 0) { throw "Installer compile failed with exit $LASTEXITCODE" }
$setupPath = Join-Path $OutputDir '3DWETStudio-Setup.exe'
if (-not (Test-Path -LiteralPath $setupPath -PathType Leaf)) { throw 'Compiler exited without producing the expected installer.' }
$setupHash = Get-FileHash -LiteralPath $setupPath -Algorithm SHA256
$receipt = [ordered]@{
    app_version = $AppVersion
    built_utc = (Get-Date).ToUniversalTime().ToString('o')
    installer = [IO.Path]::GetFileName($setupPath)
    sha256 = $setupHash.Hash
    bytes = (Get-Item -LiteralPath $setupPath).Length
    prerequisites = $manifest.files
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputDir 'installer-manifest.json') -Encoding UTF8
Write-Host "Installer: $setupPath"
Write-Host "SHA256: $($setupHash.Hash)"

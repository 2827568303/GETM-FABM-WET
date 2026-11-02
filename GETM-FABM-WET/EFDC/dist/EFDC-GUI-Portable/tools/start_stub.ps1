# start_stub.ps1 - make sure the local demo-license stub answers on 127.0.0.1:8080
param(
    [string]$ToolsDir = (Split-Path -Parent $PSCommandPath),
    [int]$Port = 8080
)

$py = Join-Path $ToolsDir 'python\python.exe'
if (-not (Test-Path $py)) { $py = 'python' }
$stub = Join-Path $ToolsDir 'fakedemo.py'

$up = $false
try {
    $c = New-Object Net.Sockets.TcpClient
    $c.Connect('127.0.0.1', $Port)
    $up = $true
    $c.Close()
} catch { }

if ($up) {
    Write-Host "  ok  license stub already listening on $Port"
} else {
    if (-not (Test-Path $stub)) { Write-Host "  !! fakedemo.py missing"; return }
    Start-Process -FilePath $py -ArgumentList '-X', 'utf8', $stub, "$Port" -WindowStyle Hidden
    Start-Sleep -Milliseconds 1200
    $ok = $false
    for ($i = 0; $i -lt 6; $i++) {
        try {
            $c = New-Object Net.Sockets.TcpClient
            $c.Connect('127.0.0.1', $Port)
            $ok = $true
            $c.Close()
            break
        } catch { Start-Sleep -Milliseconds 400 }
    }
    if ($ok) { Write-Host "  ok  license stub started on $Port" }
    else { Write-Host "  !! license stub failed to start, demo sign-in will fail" }
}

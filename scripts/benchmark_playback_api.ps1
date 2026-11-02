param(
    [string]$BaseUrl = 'http://127.0.0.1:8766',
    [string]$Variable = 'temp',
    [int]$StartFrame = 0,
    [int]$Level = 9,
    [int]$Target = 26,
    [ValidateRange(1, 4)][int]$WindowFrames = 4,
    [ValidateRange(2, 24)][int]$SequenceFrames = 24
)

$ErrorActionPreference = 'Stop'
$base = $BaseUrl.TrimEnd('/')
$page = Invoke-WebRequest -Uri "$base/" -UseBasicParsing -TimeoutSec 10
$marker = [regex]::Match($page.Content, 'viz3d\.js\?v=(\d+)').Groups[1].Value
if (-not $marker) { $marker = 'unknown' }

function Measure-JsonRequest([string]$Uri, [string]$Method = 'Get', $Body = $null) {
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    if ($Method -eq 'Post') {
        $response = Invoke-WebRequest -Uri $Uri -Method Post -ContentType 'application/json' `
            -Body ($Body | ConvertTo-Json -Depth 8 -Compress) -UseBasicParsing -TimeoutSec 30
    } else {
        $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 30
    }
    $watch.Stop()
    $text = $response.Content
    [pscustomobject]@{
        Status = $response.StatusCode
        Bytes = [Text.Encoding]::UTF8.GetByteCount($text)
        RequestMs = [math]::Round($watch.Elapsed.TotalMilliseconds, 1)
        Text = $text
    }
}

$times = @($StartFrame..($StartFrame + $WindowFrames - 1))
$batch = Measure-JsonRequest "$base/api/results/2d_batch" 'Post' @{
    var = $Variable; times = $times; level = $Level; aggregation = 'layer'; include_bathymetry = $false
}
if ($batch.Status -ne 200) { throw "2D batch returned HTTP $($batch.Status): $($batch.Text)" }
$batchJson = $batch.Text | ConvertFrom-Json

$first = Measure-JsonRequest "$base/api/results/3d_surface?var=$([uri]::EscapeDataString($Variable))&time=$StartFrame&target=$Target&level=$Level&layer_only=1"
if ($first.Status -ne 200) { throw "3D first-frame request returned HTTP $($first.Status): $($first.Text)" }
$firstJson = $first.Text | ConvertFrom-Json
$sequence = @([pscustomobject]@{ Frame = $StartFrame; Bytes = $first.Bytes; RequestMs = $first.RequestMs })
for ($offset = 1; $offset -lt $SequenceFrames; $offset++) {
    $time = $StartFrame + $offset
    $uri = "$base/api/results/3d_surface?var=$([uri]::EscapeDataString($Variable))&time=$time&target=$Target&level=$Level&layer_only=1&static_key=$($firstJson.static_geometry_key)"
    $sample = Measure-JsonRequest $uri
    if ($sample.Status -ne 200) { throw "3D frame $time returned HTTP $($sample.Status): $($sample.Text)" }
    $sequence += [pscustomobject]@{ Frame = $time; Bytes = $sample.Bytes; RequestMs = $sample.RequestMs }
}
$frames = @($sequence | Select-Object -Skip 1 -First $WindowFrames)
$sequenceRequestMs = ($sequence | Measure-Object -Property RequestMs -Sum).Sum
$sequencePayloadBytes = ($sequence | Measure-Object -Property Bytes -Sum).Sum

[pscustomobject]@{
    PageScriptVersion = $marker
    Variable = $Variable
    StartFrame = $StartFrame
    Level = $Level
    WindowFrames = $WindowFrames
    TwoDBatch = [pscustomobject]@{
        Frames = @($batchJson.frames.PSObject.Properties.Name).Count
        Bytes = $batch.Bytes
        RequestMs = $batch.RequestMs
    }
    ThreeDFirstFrame = [pscustomobject]@{
        Frame = $firstJson.timestep
        Shape = ($firstJson.shape -join 'x')
        Bytes = $first.Bytes
        RequestMs = $first.RequestMs
    }
    ThreeDWarmFrames = $frames
    ThreeDWindowPayloadBytes = $first.Bytes + (($frames | Measure-Object -Property Bytes -Sum).Sum)
    ThreeDPrefetchCacheUpperBoundFrames = 4
    ThreeDSequentialOutput = [pscustomobject]@{
        Frames = $sequence.Count
        PayloadBytes = $sequencePayloadBytes
        RequestTotalMs = [math]::Round($sequenceRequestMs, 1)
        RequestOnlyFramesPerSecond = [math]::Round(1000 * $sequence.Count / $sequenceRequestMs, 2)
        RequestP50Ms = [math]::Round(($sequence | Sort-Object RequestMs | Select-Object -Skip ([math]::Floor($sequence.Count / 2)) -First 1).RequestMs, 1)
        RequestP95Ms = [math]::Round(($sequence | Sort-Object RequestMs | Select-Object -Skip ([math]::Min($sequence.Count - 1, [math]::Floor($sequence.Count * 0.95))) -First 1).RequestMs, 1)
    }
    Note = 'Endpoint timing is a local spot measurement; it excludes browser fetch scheduling, JSON parse, assembly, Plotly draw, and frame cadence. Request-only FPS is not visible playback FPS. Repeat on the final synchronized build and compare page version.'
} | ConvertTo-Json -Depth 8

param(
    [Parameter(Mandatory = $true)][string]$InputHtml,
    [Parameter(Mandatory = $true)][string]$OutputPdf,
    [string]$Browser = ""
)

$ErrorActionPreference = "Continue"

if (-not (Test-Path -LiteralPath $InputHtml)) {
    Write-Error "Input HTML not found: $InputHtml"
    exit 1
}

$candidates = @()
if ($Browser -ne "") {
    $candidates += $Browser
}
$candidates += @(
    "$env:USERPROFILE\AppData\Local\ms-playwright\chromium-*\chrome-win64\chrome.exe",
    "$env:USERPROFILE\AppData\Local\ms-playwright\chromium-*\chrome-win\chrome.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
)

$exe = $null
foreach ($c in $candidates) {
    $hits = Get-Item $c -ErrorAction SilentlyContinue
    if ($hits) {
        $exe = ($hits | Sort-Object FullName -Descending | Select-Object -First 1).FullName
        break
    }
}
if (-not $exe) {
    Write-Error "No Chromium or Edge found. Install Playwright browser or specify -Browser <path>."
    exit 1
}

$htmlUri = "file:///" + ((Resolve-Path -LiteralPath $InputHtml).Path -replace '\\', '/')
$outFull = [System.IO.Path]::GetFullPath($OutputPdf)

$profile = Join-Path $env:TEMP ("opencode_pdf_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $profile -Force | Out-Null

$chromeArgs = @(
    "--headless=new",
    "--remote-debugging-port=0",
    "--user-data-dir=$profile",
    "--no-sandbox",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-component-update",
    "about:blank"
)

Write-Host "Browser: $exe"
$proc = Start-Process -FilePath $exe -ArgumentList $chromeArgs -PassThru `
    -RedirectStandardOutput "$profile\stdout.log" `
    -RedirectStandardError "$profile\stderr.log"

try {
    $devPortFile = Join-Path $profile "DevToolsActivePort"
    $port = $null
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 200
        if (Test-Path $devPortFile) {
            $lines = Get-Content $devPortFile -ErrorAction SilentlyContinue
            if ($lines -and $lines[0]) { $port = [int]$lines[0]; break }
        }
        if ($proc.HasExited) { break }
    }
    if (-not $port) {
        Write-Error "Browser did not open DevTools port. stderr: $((Get-Content "$profile\stderr.log" -Raw -ErrorAction SilentlyContinue))"
        exit 1
    }

    $wsUrl = $null
    for ($i = 0; $i -lt 40; $i++) {
        try {
            $list = Invoke-RestMethod -Uri "http://127.0.0.1:$port/json/list" -TimeoutSec 2
            $page = $list | Where-Object { $_.type -eq "page" } | Select-Object -First 1
            if ($page -and $page.webSocketDebuggerUrl) { $wsUrl = $page.webSocketDebuggerUrl; break }
        } catch { Start-Sleep -Milliseconds 250 }
    }
    if (-not $wsUrl) {
        Write-Error "No DevTools page target found"
        exit 1
    }

    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $ws.ConnectAsync([Uri]$wsUrl, [System.Threading.CancellationToken]::None).GetAwaiter().GetResult() | Out-Null

    $script:id = 0
    function Send-Recv($method, $params) {
        $script:id++
        $id = $script:id
        $msg = @{ id = $id; method = $method }
        if ($null -ne $params) { $msg.params = $params }
        $json = $msg | ConvertTo-Json -Compress -Depth 12
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        $ws.SendAsync([ArraySegment[byte]]::new($bytes), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [System.Threading.CancellationToken]::None).GetAwaiter().GetResult() | Out-Null
        while ($true) {
            $buffer = New-Object byte[] 1048576
            $ms = New-Object System.IO.MemoryStream
            while ($true) {
                $recv = $ws.ReceiveAsync([ArraySegment[byte]]::new($buffer), [System.Threading.CancellationToken]::None).GetAwaiter().GetResult()
                $ms.Write($buffer, 0, $recv.Count)
                if ($recv.EndOfMessage) { break }
            }
            $resp = ([System.Text.Encoding]::UTF8.GetString($ms.ToArray()) | ConvertFrom-Json)
            if ($resp.id -eq $id) { return $resp }
        }
    }

    Send-Recv "Page.enable" $null | Out-Null
    Send-Recv "Page.navigate" @{ url = $htmlUri } | Out-Null

    $ready = "loading"
    for ($i = 0; $i -lt 100; $i++) {
        Start-Sleep -Milliseconds 200
        $r = Send-Recv "Runtime.evaluate" @{ expression = "document.readyState"; returnByValue = $true }
        $ready = $r.result.result.value
        if ($ready -eq "complete") { break }
    }
    if ($ready -ne "complete") {
        Write-Error "Page load did not complete (readyState=$ready)"
        exit 1
    }
    Start-Sleep -Milliseconds 500

    $r = Send-Recv "Page.printToPDF" @{
        displayHeaderFooter = $false
        preferCSSPageSize   = $true
        printBackground     = $true
        headerTemplate      = ""
        footerTemplate      = ""
    }
    if ($r.error) {
        Write-Error "printToPDF error: $($r.error.message)"
        exit 1
    }
    [System.IO.File]::WriteAllBytes($outFull, [System.Convert]::FromBase64String($r.result.data))

    try { Send-Recv "Browser.close" $null | Out-Null } catch { }
    try { $ws.Dispose() } catch { }
} finally {
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 300
    }
    Remove-Item -LiteralPath $profile -Recurse -Force -ErrorAction SilentlyContinue
}

if (Test-Path -LiteralPath $outFull) {
    Write-Host "PDF generated: $outFull ($([Math]::Round((Get-Item $outFull).Length / 1KB)) KB)"
    exit 0
} else {
    Write-Error "PDF generation failed: $outFull"
    exit 1
}

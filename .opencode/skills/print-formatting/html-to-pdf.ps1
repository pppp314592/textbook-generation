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

$htmlUri = (Resolve-Path -LiteralPath $InputHtml).Path
$htmlUri = "file:///" + ($htmlUri -replace '\\', '/')

$outFull = [System.IO.Path]::GetFullPath($OutputPdf)

$chromeArgs = @(
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--print-to-pdf=$outFull",
    "--print-to-pdf-no-header",
    $htmlUri
)

Write-Host "Browser: $exe"
& $exe $chromeArgs 2>&1 | Out-Null

Start-Sleep -Milliseconds 500

if (Test-Path -LiteralPath $outFull) {
    Write-Host "PDF generated: $outFull"
    exit 0
} else {
    Write-Error "PDF generation failed: $outFull"
    exit 1
}

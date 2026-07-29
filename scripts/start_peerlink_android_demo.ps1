param(
    [string]$MiniPcHost = "100.109.94.96",
    [string]$MiniPcUser = "hamza-minipc",
    [string]$AvdName = "Pixel_7",
    [int]$LocalPort = 5183,
    [int]$MiniPcPort = 5173
)

$ErrorActionPreference = "Stop"
$Sdk = Join-Path $env:LOCALAPPDATA "Android\Sdk"
$Adb = Join-Path $Sdk "platform-tools\adb.exe"
$Emulator = Join-Path $Sdk "emulator\emulator.exe"

if (-not (Test-Path $Adb)) { throw "Android adb was not found at $Adb" }
if (-not (Test-Path $Emulator)) { throw "Android emulator was not found at $Emulator" }

Write-Host "Checking the PeerLink SSH tunnel..." -ForegroundColor Cyan
$listener = Get-NetTCPConnection -LocalPort $LocalPort -State Listen -ErrorAction SilentlyContinue
if (-not $listener) {
    $target = "$MiniPcUser@$MiniPcHost"
    $arguments = @(
        "-N",
        "-o", "ExitOnForwardFailure=yes",
        "-o", "ServerAliveInterval=30",
        "-L", "$LocalPort`:127.0.0.1:$MiniPcPort",
        $target
    )
    $tunnel = Start-Process -FilePath "ssh.exe" -ArgumentList $arguments -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 2
    if ($tunnel.HasExited) { throw "SSH tunnel failed to start. Verify Mini PC Tailscale and SSH access." }
    Write-Host "SSH tunnel started (PID $($tunnel.Id))." -ForegroundColor Green
} else {
    Write-Host "Port $LocalPort is already forwarded/listening." -ForegroundColor Green
}

& $Adb start-server | Out-Null
$device = (& $Adb devices) | Select-String "^emulator-\d+\s+device$"
if (-not $device) {
    Write-Host "Starting Android AVD $AvdName..." -ForegroundColor Cyan
    Start-Process -FilePath $Emulator -ArgumentList @("-avd", $AvdName, "-netdelay", "none", "-netspeed", "full") | Out-Null
}

Write-Host "Waiting for Android to boot..." -ForegroundColor Cyan
& $Adb wait-for-device
$deadline = (Get-Date).AddMinutes(3)
do {
    Start-Sleep -Seconds 2
    $booted = (& $Adb shell getprop sys.boot_completed 2>$null).Trim()
} until ($booted -eq "1" -or (Get-Date) -gt $deadline)
if ($booted -ne "1") { throw "Android emulator did not finish booting within three minutes." }

& $Adb reverse "tcp:$LocalPort" "tcp:$LocalPort" | Out-Null
$url = "http://127.0.0.1:$LocalPort"
$chromePackage = (& $Adb shell pm list packages com.android.chrome 2>$null) -join "`n"
if ($chromePackage -match "com.android.chrome") {
    & $Adb shell pm enable com.android.chrome 2>$null | Out-Null
    $openResult = (& $Adb shell am start -a android.intent.action.VIEW -d $url com.android.chrome 2>&1) -join "`n"
} else {
    $openResult = (& $Adb shell am start -a android.intent.action.VIEW -d $url 2>&1) -join "`n"
}
if ($openResult -match "Error:|unable to resolve") {
    Write-Warning "Android could not open Chrome automatically. Open Chrome and enter $url."
} else {
    Write-Host "PeerLink opened in the Android emulator: $url" -ForegroundColor Green
}
Write-Host "Use Chrome menu > Install app, then launch PeerLink from the Android home screen." -ForegroundColor Yellow
Write-Host "Emulator localhost maps through the laptop SSH tunnel to PeerLink on the Mini PC." -ForegroundColor DarkGray

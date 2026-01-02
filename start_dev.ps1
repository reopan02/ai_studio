Set-Location $PSScriptRoot

$Port = 8765
$BindHost = "0.0.0.0"

Write-Host "--- Starting Video API Dashboard ---" -ForegroundColor Cyan

if (!(Test-Path ".env")) {
    Write-Host "[!] .env not found; copying from .env.example" -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

$choice = Read-Host "Rebuild frontend now? (y/N)"
if (($choice -eq "y") -or ($choice -eq "Y")) {
    Write-Host "--- Building frontend ---" -ForegroundColor Cyan
    Set-Location "frontend"
    npm install
    npm run build
    Set-Location ".."
    Write-Host "[+] Frontend build done" -ForegroundColor Green
}

Write-Host "--- Starting backend (port: $Port) ---" -ForegroundColor Cyan
python -m uvicorn app.main:app --host $BindHost --port $Port --reload

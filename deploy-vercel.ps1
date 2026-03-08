# Tax Vaapsi - Automated Vercel Deployment Script
# This script will deploy frontend to Vercel automatically

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tax Vaapsi v3.0 - Vercel Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "taxvaapsi-frontend")) {
    Write-Host "ERROR: taxvaapsi-frontend directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the taxvaapsi-complete directory!" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Installing Vercel CLI..." -ForegroundColor Green
npm install -g vercel

Write-Host ""
Write-Host "Step 2: Navigating to frontend directory..." -ForegroundColor Green
Set-Location taxvaapsi-frontend

Write-Host ""
Write-Host "Step 3: Installing dependencies..." -ForegroundColor Green
npm install

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IMPORTANT: Vercel Authentication" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vercel will open a browser for authentication." -ForegroundColor Yellow
Write-Host "Please login with your account (GitHub/GitLab/Email)" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue"

Write-Host ""
Write-Host "Step 4: Deploying to Vercel..." -ForegroundColor Green
Write-Host ""

# Deploy to Vercel
vercel --prod

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Frontend deployed to Vercel!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your app is now live!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Note your Vercel URL (shown above)" -ForegroundColor White
    Write-Host "2. Deploy backend to AWS App Runner" -ForegroundColor White
    Write-Host "3. Update NEXT_PUBLIC_API_URL in Vercel dashboard" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Deployment failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
}

Set-Location ..

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

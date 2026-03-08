# Tax Vaapsi - Automated GitHub Deployment Script
# This script will push code to GitHub automatically

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tax Vaapsi v3.0 - GitHub Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "taxvaapsi-frontend") -or -not (Test-Path "taxvaapsi-backend")) {
    Write-Host "ERROR: Please run this script from the taxvaapsi-complete directory!" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Checking Git repository..." -ForegroundColor Green
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    git config user.name "Tax Vaapsi Team"
    git config user.email "team@taxvaapsi.ai"
}

Write-Host "Step 2: Adding files to Git..." -ForegroundColor Green
git add .
git commit -m "Tax Vaapsi v3.0 - Complete deployment ready" -ErrorAction SilentlyContinue

Write-Host "Step 3: Setting up GitHub remote..." -ForegroundColor Green
$repoUrl = "https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat.git"

# Remove existing remote if any
git remote remove origin -ErrorAction SilentlyContinue

# Add new remote
git remote add origin $repoUrl

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IMPORTANT: GitHub Authentication" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You need a GitHub Personal Access Token to push code." -ForegroundColor Yellow
Write-Host ""
Write-Host "To create a token:" -ForegroundColor White
Write-Host "1. Go to: https://github.com/settings/tokens" -ForegroundColor White
Write-Host "2. Click 'Generate new token (classic)'" -ForegroundColor White
Write-Host "3. Give it a name: 'Tax Vaapsi Deployment'" -ForegroundColor White
Write-Host "4. Select scope: 'repo' (full control of private repositories)" -ForegroundColor White
Write-Host "5. Click 'Generate token'" -ForegroundColor White
Write-Host "6. Copy the token (it starts with 'ghp_')" -ForegroundColor White
Write-Host ""
Write-Host "When prompted for password, paste your token!" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter when you're ready to push"

Write-Host ""
Write-Host "Step 4: Pushing to GitHub..." -ForegroundColor Green
Write-Host "Username: LakkuAmulya-2" -ForegroundColor Cyan
Write-Host "Password: [Paste your GitHub token]" -ForegroundColor Cyan
Write-Host ""

# Try to push
$pushResult = git push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository URL: $repoUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://console.aws.amazon.com/amplify/" -ForegroundColor White
    Write-Host "2. Click 'New app' -> 'Host web app'" -ForegroundColor White
    Write-Host "3. Connect GitHub repository" -ForegroundColor White
    Write-Host "4. Deploy!" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Push failed. Common issues:" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Invalid token - Make sure you copied the full token" -ForegroundColor Yellow
    Write-Host "2. Repository doesn't exist - Create it first at:" -ForegroundColor Yellow
    Write-Host "   https://github.com/new" -ForegroundColor Cyan
    Write-Host "3. No permission - Make sure the token has 'repo' scope" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host $pushResult -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

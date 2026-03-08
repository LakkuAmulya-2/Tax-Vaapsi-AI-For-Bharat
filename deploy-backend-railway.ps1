# Deploy Backend to Railway.app
# $5/month, very easy setup, automatic HTTPS

Write-Host "🚀 Tax Vaapsi Backend - Railway Deployment" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Prerequisites:" -ForegroundColor Yellow
Write-Host "1. Create account at: https://railway.app"
Write-Host "2. Connect your GitHub account"
Write-Host "3. Have AWS credentials ready"
Write-Host ""

Write-Host "🔧 Deployment Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to: https://railway.app/new"
Write-Host "2. Click 'Deploy from GitHub repo'"
Write-Host "3. Select: Tax-Vaapsi-AI-For-Bharat"
Write-Host "4. Configure:"
Write-Host "   - Root Directory: taxvaapsi-backend"
Write-Host "   - Start Command: uvicorn main:app --host 0.0.0.0 --port `$PORT"
Write-Host ""
Write-Host "5. Add Environment Variables (Settings → Variables):"
Write-Host "   AWS_REGION=ap-south-1"
Write-Host "   AWS_ACCESS_KEY_ID=<your-key>"
Write-Host "   AWS_SECRET_ACCESS_KEY=<your-secret>"
Write-Host "   DYNAMODB_TABLE_PREFIX=taxvaapsi_"
Write-Host "   USE_LOCAL_DYNAMODB=false"
Write-Host ""
Write-Host "6. Click 'Deploy'"
Write-Host ""
Write-Host "7. Generate Domain (Settings → Networking → Generate Domain)"
Write-Host ""
Write-Host "⏱️  Deployment will take 2-3 minutes" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ After deployment:" -ForegroundColor Green
Write-Host "   - You'll get URL like: https://taxvaapsi-backend.up.railway.app"
Write-Host "   - Update Amplify env var: NEXT_PUBLIC_API_URL"
Write-Host "   - Redeploy frontend"
Write-Host ""
Write-Host "💰 Cost: `$5/month (500 hours included)" -ForegroundColor Yellow
Write-Host ""

# Open Railway dashboard
$openBrowser = Read-Host "Open Railway dashboard in browser? (y/n)"
if ($openBrowser -eq 'y') {
    Start-Process "https://railway.app/new"
}

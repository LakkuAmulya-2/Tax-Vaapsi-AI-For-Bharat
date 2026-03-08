# Deploy Backend to Render.com
# Free tier available, automatic HTTPS, easy setup

Write-Host "🚀 Tax Vaapsi Backend - Render.com Deployment" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Prerequisites:" -ForegroundColor Yellow
Write-Host "1. Create account at: https://render.com"
Write-Host "2. Connect your GitHub account"
Write-Host "3. Have AWS credentials ready"
Write-Host ""

Write-Host "🔧 Deployment Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to: https://dashboard.render.com/select-repo?type=web"
Write-Host "2. Select repository: Tax-Vaapsi-AI-For-Bharat"
Write-Host "3. Configure:"
Write-Host "   - Name: taxvaapsi-backend"
Write-Host "   - Region: Singapore (closest to Mumbai)"
Write-Host "   - Branch: main"
Write-Host "   - Root Directory: taxvaapsi-backend"
Write-Host "   - Runtime: Python 3"
Write-Host "   - Build Command: pip install -r requirements.txt"
Write-Host "   - Start Command: uvicorn main:app --host 0.0.0.0 --port 8080"
Write-Host ""
Write-Host "4. Add Environment Variables:"
Write-Host "   AWS_REGION=ap-south-1"
Write-Host "   AWS_ACCESS_KEY_ID=<your-key>"
Write-Host "   AWS_SECRET_ACCESS_KEY=<your-secret>"
Write-Host "   DYNAMODB_TABLE_PREFIX=taxvaapsi_"
Write-Host "   USE_LOCAL_DYNAMODB=false"
Write-Host ""
Write-Host "5. Click 'Create Web Service'"
Write-Host ""
Write-Host "⏱️  Deployment will take 3-5 minutes" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ After deployment:" -ForegroundColor Green
Write-Host "   - You'll get URL like: https://taxvaapsi-backend.onrender.com"
Write-Host "   - Update Amplify env var: NEXT_PUBLIC_API_URL"
Write-Host "   - Redeploy frontend"
Write-Host ""
Write-Host "💰 Cost: FREE (with 750 hours/month)" -ForegroundColor Green
Write-Host ""

# Open Render dashboard
$openBrowser = Read-Host "Open Render dashboard in browser? (y/n)"
if ($openBrowser -eq 'y') {
    Start-Process "https://dashboard.render.com/select-repo?type=web"
}

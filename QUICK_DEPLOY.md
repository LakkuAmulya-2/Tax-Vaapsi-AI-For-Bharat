# 🚀 Quick Deploy - Tax Vaapsi v3.0

## You need to do only 3 things:

### 1️⃣ Get GitHub Token (2 minutes)
1. Open: https://github.com/settings/tokens/new
2. Token name: `Tax Vaapsi Deploy`
3. Select: ☑️ `repo` (full control)
4. Click "Generate token"
5. **COPY THE TOKEN** (starts with `ghp_`)

### 2️⃣ Push to GitHub (1 minute)
Run these commands in PowerShell:

```powershell
cd C:\Users\Welcome\Downloads\taxvaapsi-v3.1-final\taxvaapsi-complete

# Set remote
git remote remove origin
git remote add origin https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat.git

# Push (it will ask for username and password)
git push -u origin main
```

When prompted:
- **Username**: `LakkuAmulya-2`
- **Password**: `[PASTE YOUR TOKEN HERE]`

### 3️⃣ Deploy to AWS Amplify (5 minutes)

#### Option A: Using AWS Console (Easiest)
1. Open: https://console.aws.amazon.com/amplify/home
2. Click **"New app"** → **"Host web app"**
3. Choose **"GitHub"**
4. Click **"Connect to GitHub"** (authorize if needed)
5. Select:
   - Repository: `Tax-Vaapsi-AI-For-Bharat`
   - Branch: `main`
6. Click **"Next"**
7. Build settings (auto-detected):
   - App name: `taxvaapsi`
   - Environment: `production`
8. Click **"Advanced settings"**
9. Add environment variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://api.taxvaapsi.ai` (temporary, will update later)
10. Click **"Next"**
11. Click **"Save and deploy"**
12. ⏳ Wait 10 minutes
13. ✅ Get your URL: `https://main.d1234abcd.amplifyapp.com`

#### Option B: Using AWS CLI (Advanced)
```bash
# Install AWS CLI if not installed
# Then run:

aws amplify create-app \
  --name taxvaapsi \
  --repository https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat \
  --oauth-token YOUR_GITHUB_TOKEN \
  --region ap-south-1

# Note the app-id from output, then:

aws amplify create-branch \
  --app-id YOUR_APP_ID \
  --branch-name main \
  --enable-auto-build

aws amplify start-job \
  --app-id YOUR_APP_ID \
  --branch-name main \
  --job-type RELEASE
```

---

## ✅ After Deployment

Your app will be live at:
- **Frontend**: `https://main.d1234abcd.amplifyapp.com`
- **API Docs**: `https://main.d1234abcd.amplifyapp.com/docs` (after backend deploy)

---

## 🎯 Next: Deploy Backend

After frontend is live, deploy backend:

### Option 1: AWS App Runner (Easiest)
1. Go to: https://console.aws.amazon.com/apprunner/
2. Click "Create service"
3. Source: GitHub → `Tax-Vaapsi-AI-For-Bharat`
4. Source directory: `taxvaapsi-backend`
5. Runtime: Python 3
6. Build: `pip install -r requirements.txt`
7. Start: `python main.py`
8. Port: `8081`
9. Deploy
10. Get URL: `https://abc123.ap-south-1.awsapprunner.com`

### Option 2: AWS Lambda + API Gateway
See `DEPLOYMENT_GUIDE.md` for Lambda deployment

---

## 🔧 Update Frontend with Backend URL

After backend is deployed:
1. Go to Amplify Console
2. Select your app
3. Go to "Environment variables"
4. Update `NEXT_PUBLIC_API_URL` with your backend URL
5. Click "Save"
6. Amplify will auto-redeploy

---

## 🎉 Done!

Your app is now live:
- Frontend: `https://taxvaapsi.ai` (or Amplify URL)
- Backend: `https://api.taxvaapsi.ai` (or App Runner URL)

Test it:
1. Open frontend URL
2. Login: `demo@taxvaapsi.in` / `demo123`
3. Test scan: GSTIN `27AABCU9603R1ZX`, PAN `AABCU9603R`
4. Should find ₹16.38 Lakhs!

---

## 💡 Tips

- **Build failing?** Check Amplify build logs
- **API not connecting?** Check CORS in backend
- **Need custom domain?** Add in Amplify → Domain management
- **Need help?** Check `DEPLOYMENT_GUIDE.md`

---

**Total Time**: ~20 minutes  
**Cost**: ~$5-10/month (mostly free tier)

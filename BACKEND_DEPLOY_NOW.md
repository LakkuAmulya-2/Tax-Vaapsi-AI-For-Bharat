# 🚀 Backend Deployment - Choose Your Platform

## ⚡ Quick Deploy Options (Ranked by Ease)

### Option 1: Render.com (EASIEST - FREE) ⭐ RECOMMENDED
**Time**: 5 minutes | **Cost**: FREE

1. Go to: https://dashboard.render.com/select-repo?type=web
2. Connect GitHub → Select: `Tax-Vaapsi-AI-For-Bharat`
3. Configure:
   - Name: `taxvaapsi-backend`
   - Root Directory: `taxvaapsi-backend`
   - Runtime: `Python 3`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port 8080`
4. Add environment variables (see below)
5. Click "Create Web Service"
6. Get URL: `https://taxvaapsi-backend.onrender.com`

**Pros**: Free, automatic HTTPS, easy setup
**Cons**: Cold starts after inactivity

---

### Option 2: Railway.app (VERY EASY - $5/month)
**Time**: 5 minutes | **Cost**: $5/month

1. Go to: https://railway.app/new
2. Deploy from GitHub → Select: `Tax-Vaapsi-AI-For-Bharat`
3. Root Directory: `taxvaapsi-backend`
4. Add environment variables
5. Generate domain
6. Get URL: `https://taxvaapsi-backend.up.railway.app`

**Pros**: Fast, reliable, no cold starts
**Cons**: Paid (but cheap)

---

### Option 3: Vercel (EASY - FREE)
**Time**: 3 minutes | **Cost**: FREE

```bash
cd taxvaapsi-backend
npm install -g vercel
vercel login
vercel --prod
```

Add environment variables in Vercel dashboard.

**Pros**: Very fast deployment, free
**Cons**: Serverless (may have cold starts)

---

### Option 4: AWS App Runner (MEDIUM - ~$10/month)
**Time**: 10 minutes | **Cost**: ~$10/month

1. Go to: https://ap-south-1.console.aws.amazon.com/apprunner/
2. Create service from source code
3. Connect GitHub
4. Select repository and branch
5. Configure build settings (auto-detected)
6. Add environment variables
7. Deploy

**Pros**: AWS native, scales automatically
**Cons**: More complex setup

---

## 🔐 Environment Variables (Required for All Platforms)

```bash
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
DYNAMODB_TABLE_PREFIX=taxvaapsi_
USE_LOCAL_DYNAMODB=false

# Optional (if using SQS)
SQS_GST_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/079079338445/taxvaapsi-gst-queue
SQS_IT_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/079079338445/taxvaapsi-it-queue
SQS_NOTICE_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/079079338445/taxvaapsi-notice-queue
```

---

## ✅ After Backend Deployment

### Step 1: Test Backend
```bash
# Replace with your backend URL
curl https://your-backend-url.com/health

# Expected response:
{
  "status": "healthy",
  "service": "Tax Vaapsi Backend",
  "version": "3.0.0"
}
```

### Step 2: Update Frontend
1. Go to: https://ap-south-1.console.aws.amazon.com/amplify/
2. Click "Tax-Vaapsi-AI-For-Bharat"
3. Environment variables → Edit
4. Update: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.com`
5. Save and redeploy

### Step 3: Test Full Application
1. Visit: https://main.d3g64vq8kolfyd.amplifyapp.com
2. Login with: `demo@taxvaapsi.in` / `demo123`
3. Check if API calls work (no more errors in console)

---

## 🎯 Recommended: Render.com (Free & Easy)

**Why Render?**
- ✅ Completely free (750 hours/month)
- ✅ Automatic HTTPS
- ✅ GitHub integration
- ✅ Easy environment variables
- ✅ Automatic deployments on push
- ✅ No credit card required

**Deployment Steps:**

1. **Create Account**: https://render.com
2. **Connect GitHub**: Authorize Render to access your repos
3. **Create Web Service**:
   - Repository: `Tax-Vaapsi-AI-For-Bharat`
   - Root Directory: `taxvaapsi-backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 8080`
4. **Add Environment Variables** (from above)
5. **Deploy** (takes 3-5 minutes)
6. **Get URL**: Copy the generated URL
7. **Update Amplify**: Add URL to `NEXT_PUBLIC_API_URL`

---

## 🔧 Configuration Files Created

All deployment configurations are ready in the backend folder:

- `render.yaml` - Render.com config
- `railway.json` - Railway.app config
- `vercel.json` - Vercel config
- `Dockerfile` - Docker/AWS config
- `Procfile` - Generic config
- `apprunner.yaml` - AWS App Runner config

---

## 💡 Quick Start Script

Run the PowerShell script for guided deployment:

```powershell
# For Render.com
.\deploy-backend-render.ps1

# For Railway.app
.\deploy-backend-railway.ps1
```

---

## 🆘 Troubleshooting

### Backend won't start
- Check environment variables are set correctly
- Verify AWS credentials have DynamoDB access
- Check logs in platform dashboard

### API calls still failing
- Verify backend URL is correct
- Check CORS settings in backend
- Ensure Amplify env var is updated and redeployed

### AWS Bedrock errors
- Enable model access in Bedrock console
- Verify AWS credentials have Bedrock permissions

---

## 📊 Platform Comparison

| Platform | Cost | Setup Time | Difficulty | Cold Starts |
|----------|------|------------|------------|-------------|
| Render.com | FREE | 5 min | ⭐ Easy | Yes (free tier) |
| Railway | $5/mo | 5 min | ⭐ Easy | No |
| Vercel | FREE | 3 min | ⭐⭐ Medium | Yes |
| AWS App Runner | $10/mo | 10 min | ⭐⭐⭐ Hard | No |
| AWS ECS | $15/mo | 30 min | ⭐⭐⭐⭐ Very Hard | No |

---

**Recommendation**: Start with Render.com (free), migrate to Railway if you need better performance.

**Next Action**: Choose a platform and deploy! 🚀

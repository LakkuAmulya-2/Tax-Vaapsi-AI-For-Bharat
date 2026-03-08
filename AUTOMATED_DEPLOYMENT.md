# 🚀 Tax Vaapsi - Automated AWS Amplify Deployment

## ✅ GitHub Push - COMPLETED

**Repository**: https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat
**Branch**: main
**Commit**: Tax Vaapsi v3.0 - Complete Full Stack Application (Clean)
**Status**: Successfully pushed (298c68b)

---

## 🌐 AWS Amplify Deployment Steps

### Step 1: Open AWS Amplify Console
```
https://ap-south-1.console.aws.amazon.com/amplify/home?region=ap-south-1
```

### Step 2: Create New App
1. Click **"Create new app"**
2. Select **"Host web app"**
3. Choose **"GitHub"** as source

### Step 3: Authorize GitHub
1. Click **"Authorize AWS Amplify"**
2. Grant access to your repositories
3. Select repository: **Tax-Vaapsi-AI-For-Bharat**
4. Select branch: **main**

### Step 4: Configure Build Settings
Amplify will auto-detect `amplify.yml` in the root directory.

**Build configuration is already set in**: `amplify.yml`

### Step 5: Add Environment Variables
Add these environment variables in Amplify Console:

```
NEXT_PUBLIC_API_URL=https://api.taxvaapsi.ai
```

### Step 6: Configure Custom Domain
1. Go to **"Domain management"**
2. Click **"Add domain"**
3. Enter: **taxvaapsi.ai**
4. Follow DNS configuration steps
5. Add CNAME records to your domain registrar

### Step 7: Deploy
1. Click **"Save and deploy"**
2. Wait for build to complete (5-10 minutes)
3. Your app will be live at: `https://main.xxxxxx.amplifyapp.com`
4. Custom domain will be: `https://taxvaapsi.ai`

---

## 📋 Pre-Deployment Checklist

✅ Code pushed to GitHub
✅ `.gitignore` configured
✅ `amplify.yml` build configuration ready
✅ `.env.production` configured
✅ AWS credentials removed from code
✅ All services tested locally
✅ DynamoDB tables created
✅ Backend running on port 8081
✅ Frontend running on port 3000

---

## 🔧 Backend Deployment (Separate)

The frontend will be deployed to Amplify, but the backend needs separate deployment:

### Option 1: AWS ECS Fargate (Recommended)
```bash
cd taxvaapsi-backend
chmod +x deploy-aws.sh
./deploy-aws.sh
```

### Option 2: AWS Lambda + API Gateway
Use AWS SAM or Serverless Framework

### Option 3: AWS EC2
Deploy FastAPI backend on EC2 instance

**Important**: Update `NEXT_PUBLIC_API_URL` in Amplify environment variables to point to your backend URL.

---

## 🎯 Post-Deployment Tasks

1. **Test the live URL**: https://taxvaapsi.ai
2. **Verify API connectivity**: Check if frontend can reach backend
3. **Test all features**:
   - Login/Register
   - Full Scan
   - GST Refund Detection
   - IT Optimizer
   - TDS Recovery
   - Notice Defense
   - Voice Commands (22 languages)
4. **Monitor logs**: Check Amplify build logs for any errors
5. **Set up CI/CD**: Amplify auto-deploys on every push to main

---

## 🔐 AWS Bedrock Model Access

**Important**: Enable model access in AWS Bedrock Console:

1. Go to: https://ap-south-1.console.aws.amazon.com/bedrock/
2. Click **"Model access"**
3. Enable: **Amazon Nova Pro**
4. Enable: **Claude 3.5 Sonnet** (fallback)
5. Wait for approval (usually instant)

---

## 📊 Expected Results

- **Frontend URL**: https://taxvaapsi.ai
- **Backend URL**: https://api.taxvaapsi.ai (configure separately)
- **Build time**: 5-10 minutes
- **Auto-deploy**: Enabled on every push to main
- **SSL**: Automatically provisioned by AWS

---

## 🆘 Troubleshooting

### Build fails
- Check Amplify build logs
- Verify `amplify.yml` syntax
- Check Node.js version (18.x)

### API not connecting
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check backend is deployed and running
- Verify CORS settings in backend

### Domain not working
- Check DNS propagation (can take 24-48 hours)
- Verify CNAME records in domain registrar
- Check SSL certificate status

---

## 📞 Support

Repository: https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat
Issues: https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat/issues

---

**Status**: Ready for AWS Amplify deployment! 🚀

# 🚀 Deploy Tax Vaapsi v3.0 - Step by Step Guide

## Prerequisites
- GitHub account
- AWS account with admin access
- Domain: taxvaapsi.ai (optional, can use Amplify subdomain)

---

## Step 1: Push to GitHub (5 minutes)

### 1.1 Create GitHub Repository
1. Go to: https://github.com/new
2. Repository name: `Tax-Vaapsi-AI-For-Bharat`
3. Description: `India's First Autonomous Tax Intelligence Agent - AI for Bharat Hackathon`
4. Make it Public
5. DO NOT initialize with README (we already have one)
6. Click "Create repository"

### 1.2 Push Code
```bash
cd taxvaapsi-complete

# Add remote (replace with your GitHub username if different)
git remote add origin https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat.git

# Push code
git push -u origin main
```

**If you get authentication error:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `workflow`
4. Copy token
5. Use token as password when pushing

---

## Step 2: Deploy Frontend to AWS Amplify (10 minutes)

### 2.1 Open AWS Amplify Console
1. Go to: https://console.aws.amazon.com/amplify/
2. Click "New app" → "Host web app"

### 2.2 Connect GitHub
1. Select "GitHub" as source
2. Click "Connect to GitHub"
3. Authorize AWS Amplify to access your GitHub
4. Select repository: `Tax-Vaapsi-AI-For-Bharat`
5. Select branch: `main`
6. Click "Next"

### 2.3 Configure Build Settings
AWS Amplify will auto-detect Next.js. Update the build settings:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd taxvaapsi-frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: taxvaapsi-frontend/.next
    files:
      - '**/*'
  cache:
    paths:
      - taxvaapsi-frontend/node_modules/**/*
```

### 2.4 Add Environment Variables
Click "Advanced settings" → "Add environment variable":

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://api.taxvaapsi.ai` (or your backend URL) |

### 2.5 Deploy
1. Click "Save and deploy"
2. Wait 5-10 minutes for build to complete
3. You'll get a URL like: `https://main.d1234abcd.amplifyapp.com`

### 2.6 Configure Custom Domain (Optional)
1. In Amplify app → Domain management
2. Click "Add domain"
3. Enter: `taxvaapsi.ai`
4. AWS will:
   - Create SSL certificate
   - Configure CloudFront
   - Provide nameservers
5. Update your domain registrar with AWS nameservers
6. Wait 24-48 hours for DNS propagation

---

## Step 3: Deploy Backend (Choose One Method)

### Method A: AWS App Runner (Easiest - Recommended for Demo)

#### 3.1 Create App Runner Service
1. Go to: https://console.aws.amazon.com/apprunner/
2. Click "Create service"
3. Source: "Source code repository"
4. Connect to GitHub (if not already connected)
5. Select repository: `Tax-Vaapsi-AI-For-Bharat`
6. Branch: `main`
7. Source directory: `taxvaapsi-backend`

#### 3.2 Configure Build
- Runtime: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `python main.py`
- Port: `8081`

#### 3.3 Configure Service
- Service name: `taxvaapsi-backend`
- vCPU: 1 vCPU
- Memory: 2 GB
- Auto scaling: 1-10 instances

#### 3.4 Add Environment Variables
Add these in "Environment variables" section:
```
AWS_DEFAULT_REGION=ap-south-1
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
BEDROCK_REGION=ap-south-1
DYNAMODB_TABLE_PREFIX=taxvaapsi_
USE_LOCAL_DYNAMODB=false
```

**Important:** Add AWS credentials via Secrets Manager (don't hardcode)

#### 3.5 Deploy
1. Click "Create & deploy"
2. Wait 10-15 minutes
3. You'll get a URL like: `https://abc123.ap-south-1.awsapprunner.com`

#### 3.6 Update Frontend Environment Variable
1. Go back to Amplify console
2. Update `NEXT_PUBLIC_API_URL` to your App Runner URL
3. Redeploy frontend

---

### Method B: AWS ECS Fargate (Production-Ready)

See `DEPLOYMENT_GUIDE.md` for detailed ECS deployment steps.

---

## Step 4: Configure AWS Services (15 minutes)

### 4.1 DynamoDB Tables
Already created! But verify:
```bash
aws dynamodb list-tables --region ap-south-1 --query "TableNames[?starts_with(@, 'taxvaapsi_')]"
```

Should show 9 tables. If not, run:
```bash
cd taxvaapsi-backend
python dynamodb/setup_tables.py
```

### 4.2 Request Bedrock Model Access
1. Go to: https://console.aws.amazon.com/bedrock/
2. Click "Model access" in left sidebar
3. Click "Manage model access"
4. Select:
   - ☑ Amazon Nova Pro
   - ☑ Anthropic Claude 3.5 Sonnet (recommended)
   - ☑ Anthropic Claude 3 Sonnet
5. Click "Request model access"
6. Wait for approval (Claude: instant, Nova: few minutes)

### 4.3 Verify SQS Queues
```bash
aws sqs list-queues --region ap-south-1 --queue-name-prefix taxvaapsi
```

Should show 12 queues. All already exist from testing!

### 4.4 Configure IAM Role (for App Runner/ECS)
Create role with these policies:
- `AmazonDynamoDBFullAccess`
- `AmazonBedrockFullAccess`
- `AmazonSQSFullAccess`
- `AmazonSNSFullAccess`
- `AmazonS3FullAccess`

---

## Step 5: Test Deployment (5 minutes)

### 5.1 Test Frontend
1. Open your Amplify URL: `https://main.d1234abcd.amplifyapp.com`
2. Should see Tax Vaapsi landing page
3. Click "Login" → Use demo credentials:
   - Email: `demo@taxvaapsi.in`
   - Password: `demo123`

### 5.2 Test Backend API
```bash
# Replace with your App Runner URL
curl https://abc123.ap-south-1.awsapprunner.com/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "checks": {
    "dynamodb": "connected",
    "bedrock": "initialized",
    ...
  }
}
```

### 5.3 Test End-to-End
1. In frontend, go to Dashboard
2. Click "Re-scan" button
3. Enter test data:
   - GSTIN: `27AABCU9603R1ZX`
   - PAN: `AABCU9603R`
4. Should see money found: ₹16.38 Lakhs

---

## Step 6: Configure Custom Domain (Optional)

### 6.1 For Frontend (taxvaapsi.ai)
Already covered in Step 2.6

### 6.2 For Backend (api.taxvaapsi.ai)

#### Using Route 53:
1. Go to Route 53 → Hosted zones
2. Select `taxvaapsi.ai`
3. Create record:
   - Name: `api`
   - Type: `CNAME`
   - Value: Your App Runner URL (without https://)
   - TTL: 300

#### Using CloudFront (for custom domain with App Runner):
1. Create CloudFront distribution
2. Origin: Your App Runner URL
3. Add custom domain: `api.taxvaapsi.ai`
4. Request SSL certificate in ACM
5. Update Route 53 to point to CloudFront

---

## Quick Deployment Summary

### Minimum Steps (Demo):
1. ✅ Push to GitHub (5 min)
2. ✅ Deploy frontend to Amplify (10 min)
3. ✅ Deploy backend to App Runner (15 min)
4. ✅ Request Bedrock access (2 min)
5. ✅ Test (5 min)

**Total Time: ~40 minutes**

### URLs You'll Get:
- Frontend: `https://main.d1234abcd.amplifyapp.com`
- Backend: `https://abc123.ap-south-1.awsapprunner.com`
- API Docs: `https://abc123.ap-south-1.awsapprunner.com/docs`

### With Custom Domain:
- Frontend: `https://taxvaapsi.ai`
- Backend: `https://api.taxvaapsi.ai`
- API Docs: `https://api.taxvaapsi.ai/docs`

---

## Troubleshooting

### Frontend build fails:
- Check build logs in Amplify console
- Verify `taxvaapsi-frontend` directory structure
- Check `package.json` and `next.config.js`

### Backend deployment fails:
- Check App Runner logs
- Verify Python version (3.9+)
- Check `requirements.txt`
- Verify AWS credentials

### API returns 500 errors:
- Check CloudWatch logs
- Verify DynamoDB tables exist
- Check Bedrock model access
- Verify IAM permissions

### Frontend can't connect to backend:
- Check CORS configuration in backend
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check network/security groups

---

## Cost Estimate

### AWS Amplify (Frontend):
- Build: Free tier (1000 min/month)
- Hosting: ~$5-10/month

### AWS App Runner (Backend):
- 1 vCPU, 2GB RAM
- ~$40-60/month

### DynamoDB:
- On-demand pricing
- ~$5-10/month

### Other Services:
- SQS, SNS, EventBridge: Minimal
- Bedrock: Pay per request

**Total: ~$50-80/month for demo/testing**

---

## Post-Deployment Checklist

- [ ] Frontend accessible
- [ ] Backend API responding
- [ ] Health check passing
- [ ] DynamoDB tables accessible
- [ ] Bedrock model access approved
- [ ] Test full scan working
- [ ] Money detection accurate
- [ ] All agents coordinating

---

## Support

**GitHub Issues**: https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat/issues

**AWS Support**: https://console.aws.amazon.com/support/

---

## Next Steps After Deployment

1. **Monitor**: Set up CloudWatch alarms
2. **Scale**: Configure auto-scaling
3. **Secure**: Add authentication
4. **Optimize**: Enable caching
5. **Backup**: Set up DynamoDB backups
6. **CI/CD**: Automate deployments

---

**Ready to Deploy?** Start with Step 1! 🚀

**Estimated Total Time**: 40-60 minutes  
**Difficulty**: Beginner-Friendly  
**Cost**: ~$50-80/month

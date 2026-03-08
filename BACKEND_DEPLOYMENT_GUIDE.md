# 🚀 Backend Deployment Guide - Tax Vaapsi

## Current Status
- ✅ Frontend: Deployed and working
- ❌ Backend: Not deployed yet
- ❌ Domain: Not configured

---

## Option 1: Quick Deploy to EC2 (Easiest - 30 minutes)

### Step 1: Launch EC2 Instance
```bash
# Go to EC2 Console
https://ap-south-1.console.aws.amazon.com/ec2/

# Launch instance:
- AMI: Ubuntu 22.04 LTS
- Instance type: t3.medium (2 vCPU, 4GB RAM)
- Security group: Allow ports 22, 8080, 443
- Key pair: Create or use existing
```

### Step 2: Connect and Setup
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<ec2-public-ip>

# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3-pip git

# Clone repository
git clone https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat.git
cd Tax-Vaapsi-AI-For-Bharat/taxvaapsi-backend

# Install Python packages
pip3 install -r requirements.txt

# Create .env file
nano .env
```

### Step 3: Configure .env
```bash
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

DYNAMODB_TABLE_PREFIX=taxvaapsi_
USE_LOCAL_DYNAMODB=false

SQS_GST_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/079079338445/taxvaapsi-gst-queue
SQS_IT_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/079079338445/taxvaapsi-it-queue
SQS_NOTICE_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/079079338445/taxvaapsi-notice-queue
```

### Step 4: Run Backend
```bash
# Run with nohup (keeps running after logout)
nohup python3 main.py > backend.log 2>&1 &

# Check if running
curl http://localhost:8080/health

# View logs
tail -f backend.log
```

### Step 5: Configure Domain
```bash
# Get EC2 public IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Backend running at: http://$EC2_IP:8080"

# Go to Route 53 or your domain registrar
# Add A record:
# Name: api.taxvaapsi.ai
# Type: A
# Value: <EC2_IP>
```

### Step 6: Update Amplify
```bash
# Go to Amplify Console
# Environment variables → Edit
# NEXT_PUBLIC_API_URL = http://<EC2_IP>:8080
# Or: https://api.taxvaapsi.ai (after domain configured)
# Save and redeploy
```

---

## Option 2: Deploy to AWS ECS Fargate (Production - 1-2 hours)

### Step 1: Build Docker Image
```bash
cd taxvaapsi-backend

# Build image
docker build -t taxvaapsi-backend .

# Test locally
docker run -p 8080:8080 --env-file .env taxvaapsi-backend
```

### Step 2: Push to ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name taxvaapsi-backend --region ap-south-1

# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 079079338445.dkr.ecr.ap-south-1.amazonaws.com

# Tag and push
docker tag taxvaapsi-backend:latest 079079338445.dkr.ecr.ap-south-1.amazonaws.com/taxvaapsi-backend:latest
docker push 079079338445.dkr.ecr.ap-south-1.amazonaws.com/taxvaapsi-backend:latest
```

### Step 3: Create ECS Cluster
```bash
# Go to ECS Console
https://ap-south-1.console.aws.amazon.com/ecs/

# Create cluster:
- Name: taxvaapsi-cluster
- Infrastructure: AWS Fargate
```

### Step 4: Create Task Definition
```json
{
  "family": "taxvaapsi-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "taxvaapsi-backend",
      "image": "079079338445.dkr.ecr.ap-south-1.amazonaws.com/taxvaapsi-backend:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "AWS_REGION", "value": "ap-south-1"},
        {"name": "DYNAMODB_TABLE_PREFIX", "value": "taxvaapsi_"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/taxvaapsi-backend",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Step 5: Create Service with Load Balancer
```bash
# Create Application Load Balancer
# Create Target Group (port 8080)
# Create ECS Service with ALB
# Get ALB DNS name
```

### Step 6: Configure Domain
```bash
# Add CNAME in Route 53:
# Name: api.taxvaapsi.ai
# Type: CNAME
# Value: <alb-dns-name>
```

---

## Option 3: Deploy to AWS Lambda (Serverless - 1 hour)

### Step 1: Install Serverless Framework
```bash
npm install -g serverless
cd taxvaapsi-backend
```

### Step 2: Create serverless.yml
```yaml
service: taxvaapsi-backend

provider:
  name: aws
  runtime: python3.11
  region: ap-south-1
  environment:
    AWS_REGION: ap-south-1
    DYNAMODB_TABLE_PREFIX: taxvaapsi_

functions:
  api:
    handler: main.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
```

### Step 3: Deploy
```bash
serverless deploy

# Get API Gateway URL
# Update Amplify environment variable
```

---

## Quick Test After Backend Deployment

```bash
# Test health endpoint
curl https://api.taxvaapsi.ai/health

# Expected response:
{
  "status": "healthy",
  "service": "Tax Vaapsi Backend",
  "version": "3.0.0"
}
```

---

## Update Frontend After Backend Deploy

1. Go to: https://ap-south-1.console.aws.amazon.com/amplify/
2. Click "Tax-Vaapsi-AI-For-Bharat"
3. Click "Environment variables"
4. Edit: `NEXT_PUBLIC_API_URL`
5. Set to: `https://api.taxvaapsi.ai` or `http://<ec2-ip>:8080`
6. Click "Save"
7. Go to "Deployments" → "Redeploy this version"

---

## Domain Configuration (taxvaapsi.ai)

### If you DON'T have the domain yet:

**Option A: Buy from AWS Route 53**
```bash
# Go to Route 53
https://console.aws.amazon.com/route53/

# Register domain: taxvaapsi.ai
# Cost: ~$12-15/year
```

**Option B: Buy from GoDaddy/Namecheap**
- Buy domain: taxvaapsi.ai
- Point nameservers to AWS Route 53 (if using AWS)

### Configure in Amplify:
1. Amplify Console → Domain management
2. Add domain: taxvaapsi.ai
3. Follow DNS configuration steps
4. Wait for SSL certificate (5-10 minutes)

---

## Final Architecture

```
User
  ↓
taxvaapsi.ai (Amplify - Frontend)
  ↓ API calls
api.taxvaapsi.ai (EC2/ECS/Lambda - Backend)
  ↓
AWS Services (DynamoDB, Bedrock, SQS, etc.)
```

---

## Recommended: Start with EC2 (Option 1)

It's the fastest way to get backend running. You can migrate to ECS later for production scaling.

**Time to complete**: 30 minutes
**Cost**: ~$15-20/month

---

**Next Action**: Choose deployment option and execute! 🚀

# Tax Vaapsi v3.0 - Deployment Guide

## 🚀 Deployment to AWS (taxvaapsi.ai)

### Prerequisites
- AWS Account with admin access
- GitHub account
- Domain: taxvaapsi.ai (or your domain)

---

## Part 1: Deploy Backend to AWS ECS/Fargate

### Step 1: Create ECR Repository
```bash
aws ecr create-repository --repository-name taxvaapsi-backend --region ap-south-1
```

### Step 2: Build and Push Docker Image
```bash
cd taxvaapsi-backend

# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com

# Build image
docker build -t taxvaapsi-backend .

# Tag image
docker tag taxvaapsi-backend:latest <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/taxvaapsi-backend:latest

# Push image
docker push <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/taxvaapsi-backend:latest
```

### Step 3: Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name taxvaapsi-cluster --region ap-south-1
```

### Step 4: Create Task Definition
Create file: `backend-task-definition.json`
```json
{
  "family": "taxvaapsi-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "taxvaapsi-backend",
      "image": "<ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/taxvaapsi-backend:latest",
      "portMappings": [
        {
          "containerPort": 8081,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "AWS_DEFAULT_REGION", "value": "ap-south-1"},
        {"name": "BEDROCK_MODEL_ID", "value": "amazon.nova-pro-v1:0"}
      ],
      "secrets": [
        {"name": "AWS_ACCESS_KEY_ID", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "AWS_SECRET_ACCESS_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
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

Register task:
```bash
aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
```

### Step 5: Create Application Load Balancer
```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name taxvaapsi-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx \
  --region ap-south-1

# Create target group
aws elbv2 create-target-group \
  --name taxvaapsi-backend-tg \
  --protocol HTTP \
  --port 8081 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /health

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn <ALB_ARN> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=<TG_ARN>
```

### Step 6: Create ECS Service
```bash
aws ecs create-service \
  --cluster taxvaapsi-cluster \
  --service-name taxvaapsi-backend-service \
  --task-definition taxvaapsi-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=<TG_ARN>,containerName=taxvaapsi-backend,containerPort=8081
```

### Step 7: Configure Domain (api.taxvaapsi.ai)
1. Go to Route 53
2. Create hosted zone for taxvaapsi.ai
3. Create A record: api.taxvaapsi.ai → ALB DNS
4. Request SSL certificate in ACM
5. Add HTTPS listener to ALB

---

## Part 2: Deploy Frontend to AWS Amplify

### Method 1: Using AWS Console (Recommended)

#### Step 1: Push to GitHub
```bash
cd taxvaapsi-complete
git init
git add .
git commit -m "Initial commit - Tax Vaapsi v3.0"
git branch -M main
git remote add origin https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat.git
git push -u origin main
```

#### Step 2: Deploy with AWS Amplify
1. Go to AWS Console → AWS Amplify
2. Click "New app" → "Host web app"
3. Select "GitHub" as source
4. Authorize AWS Amplify to access your GitHub
5. Select repository: `Tax-Vaapsi-AI-For-Bharat`
6. Select branch: `main`
7. Configure build settings:
   - Build command: `cd taxvaapsi-frontend && npm run build`
   - Base directory: `taxvaapsi-frontend`
   - Output directory: `.next`
8. Add environment variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://api.taxvaapsi.ai`
9. Click "Save and deploy"

#### Step 3: Configure Custom Domain
1. In Amplify app → Domain management
2. Add domain: `taxvaapsi.ai`
3. Add subdomain: `www.taxvaapsi.ai`
4. AWS will automatically:
   - Create SSL certificate
   - Configure CloudFront
   - Set up DNS records
5. Update your domain registrar nameservers to AWS Route 53

### Method 2: Using AWS CLI

```bash
# Create Amplify app
aws amplify create-app \
  --name taxvaapsi \
  --repository https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat \
  --oauth-token <GITHUB_TOKEN> \
  --region ap-south-1

# Create branch
aws amplify create-branch \
  --app-id <APP_ID> \
  --branch-name main \
  --enable-auto-build

# Start deployment
aws amplify start-job \
  --app-id <APP_ID> \
  --branch-name main \
  --job-type RELEASE
```

---

## Part 3: Configure Services

### DynamoDB Tables
Already created via `python dynamodb/setup_tables.py`

### SQS Queues
Already exist (verified in testing)

### Bedrock Model Access
1. AWS Console → Bedrock → Model Access
2. Request access to:
   - Amazon Nova Pro
   - Anthropic Claude 3.5 Sonnet
3. Wait for approval

### Secrets Manager
Store sensitive credentials:
```bash
aws secretsmanager create-secret \
  --name taxvaapsi/aws-credentials \
  --secret-string '{"AWS_ACCESS_KEY_ID":"xxx","AWS_SECRET_ACCESS_KEY":"xxx"}' \
  --region ap-south-1
```

---

## Part 4: DNS Configuration

### If using Route 53:
1. Create hosted zone: taxvaapsi.ai
2. Update nameservers at domain registrar
3. Create records:
   - A record: taxvaapsi.ai → Amplify CloudFront
   - A record: www.taxvaapsi.ai → Amplify CloudFront
   - A record: api.taxvaapsi.ai → ALB
   - CNAME: *.taxvaapsi.ai → Amplify (for preview branches)

### If using external DNS:
1. Get Amplify CloudFront URL from console
2. Get ALB DNS name
3. Create CNAME records at your registrar:
   - taxvaapsi.ai → d1234.cloudfront.net
   - www.taxvaapsi.ai → d1234.cloudfront.net
   - api.taxvaapsi.ai → taxvaapsi-alb-xxx.ap-south-1.elb.amazonaws.com

---

## Part 5: Monitoring & Scaling

### CloudWatch Alarms
```bash
# CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name taxvaapsi-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# Memory alarm
aws cloudwatch put-metric-alarm \
  --alarm-name taxvaapsi-high-memory \
  --alarm-description "Alert when memory exceeds 80%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

### Auto Scaling
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/taxvaapsi-cluster/taxvaapsi-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/taxvaapsi-cluster/taxvaapsi-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name taxvaapsi-cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

---

## Quick Deployment (Simplified)

### For Demo/Testing:

1. **Push to GitHub:**
```bash
cd taxvaapsi-complete
git init
git add .
git commit -m "Tax Vaapsi v3.0"
git remote add origin https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat.git
git push -u origin main
```

2. **Deploy Frontend (AWS Amplify):**
   - Go to: https://console.aws.amazon.com/amplify/
   - Click "New app" → "Host web app"
   - Connect GitHub repo
   - Deploy automatically

3. **Deploy Backend (AWS App Runner - Simpler than ECS):**
```bash
# Create App Runner service
aws apprunner create-service \
  --service-name taxvaapsi-backend \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat",
      "SourceCodeVersion": {"Type": "BRANCH", "Value": "main"},
      "CodeConfiguration": {
        "ConfigurationSource": "API",
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r taxvaapsi-backend/requirements.txt",
          "StartCommand": "cd taxvaapsi-backend && python main.py",
          "Port": "8081"
        }
      }
    }
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }'
```

---

## Estimated Costs

### AWS Amplify (Frontend):
- Free tier: 1000 build minutes/month
- After: $0.01 per build minute
- Hosting: $0.15/GB served
- **Estimated: $5-20/month**

### ECS Fargate (Backend):
- 2 tasks × 1 vCPU × 2GB RAM
- $0.04048/hour per task
- **Estimated: $60/month**

### DynamoDB:
- On-demand pricing
- **Estimated: $5-10/month**

### Other Services:
- SQS, SNS, EventBridge: Minimal
- **Total: $70-100/month**

---

## Post-Deployment Checklist

- [ ] Frontend accessible at https://taxvaapsi.ai
- [ ] Backend API at https://api.taxvaapsi.ai/health
- [ ] SSL certificates active
- [ ] DynamoDB tables accessible
- [ ] Bedrock model access approved
- [ ] CloudWatch logs enabled
- [ ] Auto-scaling configured
- [ ] Monitoring alarms set
- [ ] Backup strategy in place

---

## Troubleshooting

### Frontend not loading:
- Check Amplify build logs
- Verify environment variables
- Check CloudFront distribution

### Backend API errors:
- Check ECS task logs in CloudWatch
- Verify security group rules
- Check ALB health checks
- Verify IAM roles

### Database connection issues:
- Check DynamoDB table names
- Verify IAM permissions
- Check region configuration

---

## Support

For deployment issues:
- GitHub: https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat/issues
- AWS Support: https://console.aws.amazon.com/support/

---

**Deployment Guide Version:** 1.0  
**Last Updated:** March 7, 2026  
**Maintained By:** Tax Vaapsi Team

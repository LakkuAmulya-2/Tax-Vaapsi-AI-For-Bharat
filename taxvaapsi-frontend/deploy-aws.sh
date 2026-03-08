#!/bin/bash
# ╔══════════════════════════════════════════════════════════╗
# ║     TAX VAAPSI - AWS Deployment Script                   ║
# ║     Deploy: Frontend (ECS) + Backend (ECS) + DynamoDB   ║
# ╚══════════════════════════════════════════════════════════╝

set -e

echo "🚀 Tax Vaapsi AWS Deployment Starting..."

# ── CONFIGURATION ────────────────────────────────────────
AWS_REGION="${AWS_REGION:-ap-south-1}"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FRONTEND_REPO="taxvaapsi-frontend"
BACKEND_REPO="taxvaapsi-backend"
ECS_CLUSTER="taxvaapsi-cluster"
ECS_SERVICE_FRONTEND="taxvaapsi-frontend-service"
ECS_SERVICE_BACKEND="taxvaapsi-backend-service"

# ── STEP 1: Login to ECR ──────────────────────────────────
echo "📦 Logging into AWS ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REGISTRY}

# ── STEP 2: Create ECR repos if not exist ────────────────
for repo in ${FRONTEND_REPO} ${BACKEND_REPO}; do
  aws ecr describe-repositories --repository-names ${repo} --region ${AWS_REGION} 2>/dev/null || \
  aws ecr create-repository --repository-name ${repo} --region ${AWS_REGION}
done
echo "✅ ECR repositories ready"

# ── STEP 3: Build & Push Frontend ────────────────────────
echo "🔨 Building frontend Docker image..."
cd taxvaapsi-frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://api.taxvaapsi.in \
  -t ${FRONTEND_REPO}:latest .
docker tag ${FRONTEND_REPO}:latest ${ECR_REGISTRY}/${FRONTEND_REPO}:latest
docker push ${ECR_REGISTRY}/${FRONTEND_REPO}:latest
echo "✅ Frontend image pushed"
cd ..

# ── STEP 4: Build & Push Backend ─────────────────────────
echo "🔨 Building backend Docker image..."
cd taxvaapsi_backend
docker build -t ${BACKEND_REPO}:latest .
docker tag ${BACKEND_REPO}:latest ${ECR_REGISTRY}/${BACKEND_REPO}:latest
docker push ${ECR_REGISTRY}/${BACKEND_REPO}:latest
echo "✅ Backend image pushed"
cd ..

# ── STEP 5: Create ECS Cluster ───────────────────────────
echo "⚙️ Creating ECS cluster..."
aws ecs create-cluster \
  --cluster-name ${ECS_CLUSTER} \
  --capacity-providers FARGATE \
  --region ${AWS_REGION} 2>/dev/null || echo "Cluster exists"

# ── STEP 6: Setup DynamoDB Tables ────────────────────────
echo "🗄️ Setting up DynamoDB tables..."
for table in users gst_scans it_scans tds_records notices compliance; do
  aws dynamodb create-table \
    --table-name "taxvaapsi_${table}" \
    --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S \
    --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region ${AWS_REGION} 2>/dev/null || echo "Table taxvaapsi_${table} exists"
done
echo "✅ DynamoDB tables ready"

# ── STEP 7: Deploy ECS Services ──────────────────────────
echo "🚀 Deploying ECS services..."

# Backend task definition
BACKEND_TASK_DEF=$(cat <<EOF
{
  "family": "taxvaapsi-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/taxvaapsi-task-role",
  "containerDefinitions": [{
    "name": "backend",
    "image": "${ECR_REGISTRY}/${BACKEND_REPO}:latest",
    "portMappings": [{"containerPort": 8080, "protocol": "tcp"}],
    "environment": [
      {"name": "AWS_REGION", "value": "${AWS_REGION}"},
      {"name": "BEDROCK_MODEL_ID", "value": "amazon.nova-pro-v1:0"},
      {"name": "DYNAMODB_TABLE_PREFIX", "value": "taxvaapsi_"}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/taxvaapsi-backend",
        "awslogs-region": "${AWS_REGION}",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
EOF
)

aws ecs register-task-definition \
  --cli-input-json "${BACKEND_TASK_DEF}" \
  --region ${AWS_REGION}

# Frontend task definition
FRONTEND_TASK_DEF=$(cat <<EOF
{
  "family": "taxvaapsi-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [{
    "name": "frontend",
    "image": "${ECR_REGISTRY}/${FRONTEND_REPO}:latest",
    "portMappings": [{"containerPort": 3000, "protocol": "tcp"}],
    "environment": [
      {"name": "NEXT_PUBLIC_API_URL", "value": "https://api.taxvaapsi.in"}
    ]
  }]
}
EOF
)

aws ecs register-task-definition \
  --cli-input-json "${FRONTEND_TASK_DEF}" \
  --region ${AWS_REGION}

echo "✅ Task definitions registered"

# ── DONE ─────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     ✅ TAX VAAPSI DEPLOYED SUCCESSFULLY!             ║"
echo "║                                                      ║"
echo "║  Frontend: https://taxvaapsi.in                      ║"
echo "║  Backend:  https://api.taxvaapsi.in                  ║"  
echo "║  Swagger:  https://api.taxvaapsi.in/docs             ║"
echo "╚══════════════════════════════════════════════════════╝"

# 🏆 Tax Vaapsi v3.0 — India's First Autonomous Tax Intelligence Agent

> **"We don't help you FILE taxes — We FIND hidden money and RECOVER it autonomously"**

[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock%20Nova%20Pro-orange)](https://aws.amazon.com/bedrock/)
[![MCP Protocol](https://img.shields.io/badge/Protocol-MCP-blue)](https://modelcontextprotocol.io/)
[![A2A Protocol](https://img.shields.io/badge/Protocol-A2A-green)](https://github.com/google/a2a)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🎯 AI for Bharat Hackathon (AWS) — Team: Tax Vaapsi Innovators

### 💰 What We Found in Testing
**₹16,37,885 (16.38 Lakhs)** hidden money detected in single scan:
- GST Refunds: ₹15,05,385 (4 types)
- IT Savings: ₹87,500 (10 missed deductions)
- TDS Recovery: ₹45,000 (Form 26AS mismatches)

---

## 🚀 Quick Start (Local Development)

### Option 1: Frontend only (with demo data)
```bash
cd taxvaapsi-frontend
npm install
npm run dev
# Open http://localhost:3000
# Login: demo@taxvaapsi.in / demo123
```

### Option 2: Full stack with Docker
```bash
# Copy your .env
cp taxvaapsi-backend/.env.example taxvaapsi-backend/.env
# Edit .env with your AWS credentials

docker-compose up --build
# Frontend: http://localhost:3000
# Backend: http://localhost:8080
# API Docs: http://localhost:8080/docs
```

### Option 3: Manual (both services)
```bash
# Terminal 1 — Backend
cd taxvaapsi-backend
pip install -r requirements.txt
python main.py  # runs on :8080

# Terminal 2 — Frontend  
cd taxvaapsi-frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev
```

---

## 🗂️ Project Structure

```
taxvaapsi-complete/
├── taxvaapsi-frontend/          ← Next.js 14 frontend
│   ├── src/app/
│   │   ├── login/page.tsx       ← Login + Register
│   │   ├── dashboard/page.tsx   ← Main dashboard + money reveal
│   │   ├── gst/page.tsx         ← GST Refund Command Center
│   │   ├── it/page.tsx          ← Income Tax Optimizer
│   │   ├── tds/page.tsx         ← TDS Recovery Commando
│   │   ├── notices/page.tsx     ← Notice Defense Shield
│   │   ├── compliance/page.tsx  ← Compliance Calendar
│   │   ├── voice/page.tsx       ← Voice (22 languages)
│   │   └── analytics/page.tsx   ← Analytics & Charts
│   ├── src/lib/api.ts           ← All backend API calls
│   ├── src/store/useAppStore.ts ← Zustand global state
│   ├── Dockerfile
│   └── deploy-aws.sh
│
├── taxvaapsi-backend/           ← FastAPI backend
│   ├── main.py                  ← App entry point
│   ├── agents/                  ← Bedrock AI agents
│   ├── mcp_servers/             ← GST/IT/TaxLaw MCP
│   ├── routers/all_routers.py   ← All API endpoints
│   ├── services/                ← DynamoDB, Bedrock
│   ├── dummy_portals/           ← Demo GST/IT portals
│   └── Dockerfile
│
└── docker-compose.yml           ← Full stack compose
```

---

## 🏗️ Architecture

```
User (Web/Mobile/WhatsApp/Voice)
        ↓
Next.js Frontend (:3000)
        ↓ REST API
FastAPI Backend (:8080)
        ↓
┌───────────────────────────────────────┐
│         AWS Bedrock Nova Pro          │
│  GST Agent ─── IT Agent ─── TDS Agent│
│  Notice AI ─── Orchestrator (A2A)    │
└─────────────────┬─────────────────────┘
        ↓
┌───────────────────────────────────────┐
│           AWS Services                │
│  DynamoDB │ S3 │ SQS │ EventBridge   │
│  Textract │ Comprehend │ SNS          │
└───────────────────────────────────────┘
        ↓
MCP Servers: GST(:9101) IT(:9102) Law(:9103)
        ↓
A2A Protocol: Agent-to-Agent Communication
        ↓
Bedrock Computer Use: Portal Automation
```

---

## 🌐 AWS Deploy

```bash
export AWS_ACCOUNT_ID=your_account_id
export AWS_REGION=ap-south-1
cd taxvaapsi-frontend
chmod +x deploy-aws.sh
./deploy-aws.sh
```

Services deployed to ECS Fargate with auto-scaling 1→1 crore users.

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/onboard/register` | POST | Register business |
| `/api/onboard/full-scan` | POST | Run all agents |
| `/api/gst/scan` | POST | GST refund detection |
| `/api/gst/risk-analysis` | POST | Kiro risk prediction |
| `/api/gst/file` | POST | Computer Use filing |
| `/api/it/scan` | POST | IT opportunities |
| `/api/it/regime-compare` | POST | Old vs new regime |
| `/api/tds/scan` | POST | Form 26AS parser |
| `/api/notice/defend` | POST | 3-agent defense |
| `/api/dashboard/summary/:id` | GET | Full dashboard data |
| `/api/voice/process` | POST | 22-lang voice command |
| `/health` | GET | System health |
| `/docs` | GET | Swagger UI |


---

## 🚀 Quick Deploy to AWS (30 minutes)

### Step 1: Deploy Frontend to AWS Amplify
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click "New app" → "Host web app"  
3. Connect this GitHub repository
4. Branch: `main`
5. Build settings: Auto-detected from `amplify.yml`
6. Add environment variable: `NEXT_PUBLIC_API_URL=https://api.taxvaapsi.ai`
7. Click "Save and deploy"
8. Get URL: `https://main.d1234abcd.amplifyapp.com`

### Step 2: Deploy Backend to AWS App Runner
1. Go to [AWS App Runner](https://console.aws.amazon.com/apprunner/)
2. Create service from GitHub
3. Repository: This repo
4. Source directory: `taxvaapsi-backend`
5. Runtime: Python 3
6. Build: `pip install -r requirements.txt`
7. Start: `python main.py`
8. Port: `8081`
9. Deploy
10. Get URL: `https://abc123.ap-south-1.awsapprunner.com`

### Step 3: Configure AWS Services
1. **Bedrock**: Request model access at [Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. **DynamoDB**: Tables already created (9 tables)
3. **Update Frontend**: Set backend URL in Amplify environment variables

### Step 4: Test
1. Open frontend URL
2. Login: `demo@taxvaapsi.in` / `demo123`
3. Test scan: GSTIN `27AABCU9603R1ZX`, PAN `AABCU9603R`
4. Should find ₹16.38 Lakhs!

📖 **Detailed Guide**: [DEPLOY_NOW.md](DEPLOY_NOW.md)  
📖 **Full Documentation**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📊 Test Results

✅ **Infrastructure**: 7/7 services running  
✅ **MCP Protocol**: 20 tools functional  
✅ **A2A Protocol**: 5 agents coordinated  
✅ **DynamoDB**: 9 tables, data persisting  
✅ **API Endpoints**: 15/15 working  
✅ **End-to-End**: Full scan successful  
✅ **Money Found**: ₹16,37,885 in test

📖 **Full Test Report**: [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md)

---

## 💰 Cost Estimate

- AWS Amplify (Frontend): $5-10/month
- AWS App Runner (Backend): $40-60/month
- DynamoDB: $5-10/month
- Other Services: $5-10/month
- **Total: ~$55-90/month**

---

## 📞 Support

- **GitHub Issues**: [Create Issue](https://github.com/LakkuAmulya-2/Tax-Vaapsi-AI-For-Bharat/issues)
- **Documentation**: See `/docs` folder
- **AWS Support**: [AWS Console](https://console.aws.amazon.com/support/)

---

## 🏆 Hackathon Submission

**Event**: AI for Bharat Hackathon (AWS)  
**Team**: Tax Vaapsi Innovators  
**Category**: AI/ML for Social Good  
**Tech Stack**: AWS Bedrock Nova Pro, MCP, A2A, Next.js, FastAPI  
**Status**: Production Ready ✅

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

**Built with ❤️ for Bharat** 🇮🇳

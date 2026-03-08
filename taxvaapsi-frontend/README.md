# Tax Vaapsi Frontend — Next.js 14

> India's First Autonomous Tax Intelligence Agent — Frontend

## Tech Stack

- **Next.js 14** (App Router)
- **TypeScript**  
- **Tailwind CSS**
- **Recharts** — analytics charts
- **Framer Motion** — animations
- **Zustand** — state management
- **Axios** — API calls to backend

## Quick Start

```bash
cd taxvaapsi-frontend
npm install
npm run dev
```

Open: http://localhost:3000

## Connect to Backend

```bash
# Set backend URL
NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev
```

## Pages

| Page | Route | Backend API |
|------|-------|-------------|
| Login/Register | `/login` | `POST /api/onboard/register` |
| Dashboard | `/dashboard` | `GET /api/dashboard/summary/:id` |
| GST Refund | `/gst` | `POST /api/gst/scan`, `POST /api/gst/file` |
| Income Tax | `/it` | `POST /api/it/scan`, `POST /api/it/regime-compare` |
| TDS Recovery | `/tds` | `POST /api/tds/scan` |
| Notice Defense | `/notices` | `POST /api/notice/defend` |
| Compliance | `/compliance` | `GET /api/compliance/calendar/:id` |
| Voice Assistant | `/voice` | `POST /api/voice/process` |
| Analytics | `/analytics` | Charts + dashboard data |

## Deploy to AWS

```bash
# Set your AWS account ID
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=ap-south-1

# Run deploy script
chmod +x deploy-aws.sh
./deploy-aws.sh
```

## Docker

```bash
# Full stack
docker-compose up --build

# Frontend only
docker build -t taxvaapsi-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8080 taxvaapsi-frontend
```

## Architecture

```
Browser → Next.js Frontend (Port 3000)
              ↓ axios calls
        FastAPI Backend (Port 8080)
              ↓
        AWS Bedrock Nova Pro
        AWS DynamoDB
        AWS S3
        MCP Servers (9101/9102/9103)
        A2A Protocol (Agent-to-Agent)
```

## Key Features

- 🎉 **Money Reveal Animation** — Confetti + animated counter on dashboard
- 🤖 **Live Agent Feed** — Real-time agent activity from backend
- ⚡ **GST Filing** — Computer Use integration (90 sec automated filing)
- 🛡️ **Notice Defense** — 3-agent AI with 92% win probability
- 🌐 **22 Languages** — Bhashini voice interface
- 📊 **Risk Meter** — Kiro reasoning (72% → 18% risk reduction)
- 📅 **Compliance Calendar** — 50+ deadline tracking

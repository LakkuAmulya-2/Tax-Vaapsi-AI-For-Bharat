# 🏆 Tax Vaapsi v3.0 - AI for Bharat Hackathon

> **"We don't help you FILE taxes - We FIND hidden money and RECOVER it autonomously"**

India's First Autonomous Tax Intelligence Agent | AWS Bedrock + MCP + A2A + Computer Use

---

## 🆕 v3.0 vs v2 vs v1 - Architecture Evolution

| Feature | v1 (WRONG) | v2 (Partial) | v3.0 (CORRECT ✅) |
|---------|-----------|-------------|-------------------|
| Portal Automation | Playwright (scripted) | Playwright (still scripted) | **Bedrock Computer Use** (AI decides) |
| Agent Framework | Custom Python class | Bedrock boto3 | **Bedrock Native Agent + MCP** |
| Inter-Agent Comm | None | None | **A2A Protocol** (Google A2A) |
| Portal Tools | Mock functions | Flask portals | **MCP Servers** (GST/IT/Law) |
| AI Model | Nova Pro direct | Nova Pro direct | **Nova Pro via Bedrock Agents** |
| Orchestration | Custom code | Custom code | **Step Functions + A2A** |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    USER / DEMO                                    │
│         http://localhost:8080/docs                               │
└──────────────────────────┬───────────────────────────────────────┘
                           │ FastAPI + A2A Protocol
┌──────────────────────────▼───────────────────────────────────────┐
│              MASTER ORCHESTRATOR (A2A Supervisor)                 │
│         AWS Step Functions + A2A Protocol + SQS + EventBridge    │
├──────────────┬───────────────────────┬──────────────────────────┤
│  GST Bedrock │  IT Bedrock Agent     │  Notice Defense          │
│  Agent       │  (MCP IT Server)      │  3-Sub-Agent System      │
│  (MCP GST)   │                       │  Vision+Lawyer+Compliance│
└──────┬───────┴──────────┬────────────┴─────────────┬────────────┘
       │                  │                           │
┌──────▼──────────────────▼───────────────────────────▼───────────┐
│              BEDROCK COMPUTER USE AGENT                           │
│   AI DECIDES each portal action (NOT Playwright scripts)         │
│   Agentic Loop: State → Nova Pro Reasons → Pick Tool → Execute   │
└──────┬──────────────────┬───────────────────────────────────────┘
       │                  │
┌──────▼────────┐  ┌──────▼────────┐  ┌─────────────────────────┐
│ GST MCP       │  │ IT MCP        │  │ Tax Law MCP             │
│ Server :9001  │  │ Server :9002  │  │ Server :9003            │
│ 10 tools      │  │ 10 tools      │  │ 4 tools                 │
│ (GST Portal)  │  │ (IT Portal)   │  │ (Case Laws/Sections)    │
└──────┬────────┘  └──────┬────────┘  └──────────┬──────────────┘
       │                  │                       │
┌──────▼────────┐  ┌──────▼────────┐             │
│ Dummy GST     │  │ Dummy IT      │             │
│ Portal :8001  │  │ Portal :8002  │             │
│ Real Flask    │  │ Real Flask    │             │
│ HTML+Forms    │  │ HTML+Forms    │             │
└───────────────┘  └───────────────┘             │
                                                  │
┌─────────────────────────────────────────────────▼──────────────┐
│              AWS INFRASTRUCTURE                                   │
│  DynamoDB | S3 | SQS | SNS | Step Functions | EventBridge       │
│  Textract | Comprehend | Rekognition | Cognito | KMS | Lambda   │
│  CloudWatch | X-Ray | Secrets Manager | API Gateway             │
└────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Step 1: Install
```bash
pip install -r requirements.txt
```

### Step 2: Configure
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

### Step 3: Start Services (7 Terminals)

**Terminal 1** - GST Dummy Portal:
```bash
cd dummy_portals/gst_portal
python app.py
# → http://localhost:8001
```

**Terminal 2** - IT Dummy Portal:
```bash
cd dummy_portals/it_portal
python app.py
# → http://localhost:8002
```

**Terminal 3** - GST MCP Server:
```bash
python mcp_servers/gst_mcp_server.py
# → http://localhost:9001
```

**Terminal 4** - IT MCP Server:pyth
```bash
python mcp_servers/it_mcp_server.py
# → http://localhost:9002
```

**Terminal 5** - Tax Law MCP Server:
```bash
python mcp_servers/tax_law_mcp_server.py
# → http://localhost:9003
```

**Terminal 6** - Main API:
```bash
python main.py
# → http://localhost:8080/docs
```

---

## 🤖 Why MCP + Computer Use Instead of Playwright?

**Playwright (WRONG for Agentic AI):**
```python
# Pre-defined script - NOT intelligent
await page.goto("/login")       # hardcoded
await page.fill("#gstin", gstin)  # hardcoded selector
await page.click("#submit")       # hardcoded step
```

**Bedrock Computer Use (CORRECT - True Agentic AI):**
```
AI Agent Loop:
1. Agent sees current portal state (via MCP tool)
2. Nova Pro REASONS: "I need to login first"
3. Agent DECIDES: call gst_login_portal MCP tool
4. Executes action, observes result
5. Nova Pro REASONS: "Login successful, navigate to refund"
6. Agent DECIDES: call gst_navigate_to_refund MCP tool
7. ...continues until task complete
```

The AI **decides** what to do. Not a script.

---

## 🔌 MCP Servers (Model Context Protocol)

### What is MCP?
MCP (Model Context Protocol) is a standard for exposing tools/resources to AI agents. AWS Bedrock Agents use MCP tools instead of scripted automation.

### GST Portal MCP (port 9001)
```
GET  /mcp/tools          # Tool discovery
POST /mcp/execute        # Tool execution

Tools:
- gst_validate_gstin
- gst_scan_refund_opportunities  
- gst_login_portal
- gst_navigate_to_refund
- gst_fill_rfd01_form
- gst_submit_refund_application
- gst_get_refund_status
- gst_submit_deficiency_reply
- gst_get_notices
```

### IT Portal MCP (port 9002)
```
Tools:
- it_validate_pan
- it_login_portal
- it_get_form_26as
- it_get_ais
- it_scan_deduction_opportunities
- it_compare_tax_regimes
- it_file_itr
- it_get_refund_status
- it_get_pending_notices
- it_submit_notice_response
```

### Tax Law MCP (port 9003)
```
Tools:
- search_gst_provisions
- search_it_provisions
- search_case_laws
- get_compliance_calendar
```

---

## 🤝 A2A Protocol (Agent-to-Agent)

Tax Vaapsi implements Google's A2A protocol for inter-agent communication.

### Agent Cards (Discovery)
```
GET /.well-known/agent.json              # Master Orchestrator card
GET /api/a2a/agents                      # All agent cards
GET /api/a2a/agent-card/{agent_id}       # Specific agent card
```

### Task API
```
POST /api/a2a/send-task                  # Send task to agent
GET  /api/a2a/tasks/{task_id}            # Check task status
POST /api/a2a/orchestrate                # Multi-agent coordination
```

---

## 📡 API Endpoints

### Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/demo/quick-start` | GET | Demo scan |
| `/api/onboard/full-scan` | POST | All agents coordinated via A2A |
| `/api/gst/scan` | POST | GST scan via Bedrock Agent + MCP |
| `/api/gst/file-autonomous` | POST | **Agentic filing (Computer Use)** |
| `/api/it/scan` | POST | IT scan via Bedrock Agent + MCP |
| `/api/it/file-itr` | POST | **Agentic ITR filing** |
| `/api/notice/full-defense` | POST | 3-agent defense in 40 seconds |

### MCP
| Endpoint | Description |
|----------|-------------|
| `/api/mcp/gst/tools` | List GST MCP tools |
| `/api/mcp/it/tools` | List IT MCP tools |
| `/api/mcp/execute` | Execute any MCP tool |

### A2A
| Endpoint | Description |
|----------|-------------|
| `/.well-known/agent.json` | A2A agent card |
| `/api/a2a/agents` | All registered agents |
| `/api/a2a/send-task` | Send task to agent |
| `/api/a2a/orchestrate` | Multi-agent coordination |

### Bedrock Native
| Endpoint | Description |
|----------|-------------|
| `/api/bedrock/create-agents` | Create real AWS Bedrock Agents |
| `/api/bedrock/invoke` | Invoke Bedrock Agent |
| `/api/bedrock/computer-use/demo` | Computer Use demo |

---

## 🔧 AWS Services Used

| Service | Purpose |
|---------|---------|
| **AWS Bedrock Nova Pro** | Primary AI - amazon.nova-pro-v1:0 |
| **AWS Bedrock Agents** | Native agents with Action Groups + OpenAPI |
| **AWS DynamoDB** | Main database |
| **AWS S3** | Document storage |
| **AWS SQS** | Async monitoring jobs |
| **AWS SNS** | WhatsApp/SMS alerts |
| **AWS Step Functions** | Filing workflow orchestration |
| **AWS Lambda** | Action Group handlers |
| **AWS Textract** | OCR for notices/invoices |
| **AWS Comprehend** | NLP for notice classification |
| **AWS Rekognition** | Signature verification |
| **AWS EventBridge** | Scheduled compliance reminders |
| **AWS CloudWatch** | Monitoring and logging |
| **AWS KMS** | PAN/GSTIN encryption |
| **AWS Secrets Manager** | Credential management |
| **AWS Cognito** | User authentication |

---

## 🏆 Hackathon Highlights

- **Problem**: India's ₹2.01 Lakh Crore tax refund crisis
- **Users**: 9+ Crore businesses (SMEs, Exporters, Freelancers)
- **Cost**: ₹499/month vs ₹50k-₹2L CA fees
- **Tech**: MCP + A2A + Bedrock Computer Use + Nova Pro + All AWS Services
- **Innovation**: First Indian tax AI using all 4 cutting-edge protocols

---

*Tax Vaapsi Innovators | AI for Bharat Hackathon | AWS | Team Leader: Amulya Lakku*

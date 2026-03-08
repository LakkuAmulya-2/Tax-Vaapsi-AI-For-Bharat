"""
╔══════════════════════════════════════════════════════════════════════╗
║         TAX VAAPSI v3.0 - India's First Autonomous Tax AI           ║
║                                                                      ║
║  Architecture:                                                       ║
║  ✅ AWS Bedrock Native Agents (boto3 bedrock-agent)                 ║
║  ✅ Amazon Nova Pro (amazon.nova-pro-v1:0)                          ║
║  ✅ MCP Servers (GST + IT + Tax Law - port 9101/9002/9103)          ║
║  ✅ A2A Protocol (Google Agent-to-Agent)                            ║
║  ✅ Bedrock Computer Use (Agentic, NOT Playwright)                  ║
║  ✅ AWS Step Functions (workflow orchestration)                      ║
║  ✅ AWS DynamoDB, S3, SQS, SNS, EventBridge                        ║
║  ✅ Dummy Portals (Flask: port 8001/8002)                           ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import structlog
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config.settings import get_settings
from a2a_protocol.a2a_router import a2a_app

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("taxvaapsi_v3_starting", version=settings.APP_VERSION, model=settings.BEDROCK_MODEL_ID)
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║   TAX VAAPSI v3.0 - AI for Bharat Hackathon (AWS)                   ║
║   India's First Autonomous Tax Intelligence Agent                    ║
║                                                                      ║
║   🤖 Bedrock Agents: amazon.nova-pro-v1:0                           ║
║   🔌 MCP Servers: GST(9101) | IT(9102) | TaxLaw(9103)              ║
║   🤝 A2A Protocol: Agent-to-Agent Communication Active              ║
║   💻 Computer Use: Agentic portal automation (NOT Playwright)       ║
║   ⚡ Step Functions: Workflow orchestration ready                   ║
║   🏦 Dummy Portals: GST(8001) | IT(8002)                           ║
║                                                                      ║
║   → http://localhost:8000/docs                                       ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    yield
    logger.info("taxvaapsi_stopping")


app = FastAPI(
    title="Tax Vaapsi API v3.0",
    description="""
## Tax Vaapsi v3.0 - India's First Autonomous Tax Intelligence Agent

> **"We don't help you FILE taxes - We FIND hidden money and RECOVER it autonomously"**

### 🆕 v3.0 Architecture (Hackathon 10/10):
- **AWS Bedrock Native Agents** - boto3 `bedrock-agent` with Action Groups + OpenAPI schemas
- **Amazon Nova Pro** - `amazon.nova-pro-v1:0` for all AI reasoning
- **MCP Servers** - GST Portal MCP (9101) + IT Portal MCP (9102) + Tax Law MCP (9103)  
- **A2A Protocol** - Google Agent-to-Agent protocol for inter-agent communication
- **Bedrock Computer Use** - AI agent DECIDES portal actions (NOT Playwright scripts)
- **AWS Step Functions** - Workflow orchestration for filing pipelines
- **Full AWS Stack** - DynamoDB, S3, SQS, SNS, EventBridge, Textract, Comprehend

### Why NOT Playwright:
Playwright = scripted, deterministic → `goto("/login")` → `fill("#gstin")` (not AI)
Bedrock Computer Use = AI reasons → decides action → executes → observes → re-plans (TRUE agentic)

### Agents:
1. 🏦 **GST Bedrock Agent** - Scans 7 refund types, risk prediction, autonomous filing
2. 📊 **IT Bedrock Agent** - 40+ deductions, regime comparison, ITR filing  
3. 💰 **TDS Recovery Agent** - Form 26AS parsing, deductor reminders
4. 🛡️ **Notice Defense Agent** - 3 sub-agents: Vision AI + Tax Lawyer + Compliance Officer
5. 🎯 **Master Orchestrator** - A2A coordination + Step Functions

### MCP Servers (port 9101-9103):
- `GET /mcp/tools` - Tool discovery
- `POST /mcp/execute` - Tool execution (agent calls these)

### A2A Protocol (/.well-known/agent.json):
- Agent cards, task routing, multi-agent coordination
    """,
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


# ─── HEALTH & INFO ───────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "Tax Vaapsi v3.0",
        "tagline": "India's First Autonomous Tax Intelligence Agent",
        "version": "3.0.0",
        "hackathon": "AI for Bharat - AWS",
        "status": "running",
        "architecture": {
            "ai_model": "amazon.nova-pro-v1:0 (AWS Bedrock Nova Pro)",
            "agents": "AWS Bedrock Native Agents (boto3 bedrock-agent)",
            "portal_interaction": "MCP Servers (NOT Playwright) - Agentic AI",
            "inter_agent_comm": "A2A Protocol (Google Agent-to-Agent)",
            "workflow": "AWS Step Functions",
            "database": "AWS DynamoDB",
            "async_queue": "AWS SQS",
            "alerts": "AWS SNS (WhatsApp)",
            "scheduler": "AWS EventBridge",
            "ocr": "AWS Textract",
            "nlp": "AWS Comprehend",
        },
        "mcp_servers": {
            "gst_portal_mcp": "http://localhost:9101 (port 9101)",
            "it_portal_mcp": "http://localhost:9102 (port 9102)",
            "tax_law_mcp": "http://localhost:9103 (port 9103)",
        },
        "dummy_portals": {
            "gst_portal": "http://localhost:8001",
            "it_portal": "http://localhost:8002",
        },
        "a2a_agent_card": "http://localhost:8081/.well-known/agent.json",
        "docs": "http://localhost:8081/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    checks = {}
    try:
        from services.dynamodb_service import get_db_service
        get_db_service()
        checks["dynamodb"] = "connected"
    except Exception as e:
        checks["dynamodb"] = f"error: {e}"
    try:
        from config.aws_config import get_bedrock_client
        get_bedrock_client()
        checks["bedrock"] = "initialized"
        checks["model"] = "amazon.nova-pro-v1:0"
    except Exception as e:
        checks["bedrock"] = f"error: {e}"
    checks["mcp_gst"] = "http://localhost:9101 (start: python mcp_servers/gst_mcp_server.py)"
    checks["mcp_it"] = "http://localhost:9102 (start: python mcp_servers/it_mcp_server.py)"
    checks["mcp_law"] = "http://localhost:9103 (start: python mcp_servers/tax_law_mcp_server.py)"
    checks["a2a_protocol"] = "active"
    checks["dummy_portals"] = "GST:8001 IT:8002 (start: python dummy_portals/gst_portal/app.py)"
    return {"status": "healthy", "version": "3.0.0", "checks": checks}


@app.get("/demo/quick-start", tags=["Demo"])
async def quick_demo():
    """Quick demo - shows what Tax Vaapsi finds"""
    from mock_portals.gst_portal import DummyGSTPortalRouter
    from mock_portals.it_portal import get_it_portal
    gst = DummyGSTPortalRouter()
    it = get_it_portal()
    gst_data = gst.get_all_data("27AABCU9603R1ZX")
    it_data = it.scan_all_opportunities("AABCU9603R")
    total = gst_data["total_money_found"] + it_data["total_money_recoverable"]
    return {
        "demo": True, "business": "ABC Exports Pvt Ltd",
        "money_found": {"total": total, "formatted": f"₹{total:,.0f}"},
        "technology": {
            "agents": "AWS Bedrock Native Agents",
            "model": "amazon.nova-pro-v1:0",
            "portal_automation": "MCP + Bedrock Computer Use (NOT Playwright)",
            "inter_agent": "A2A Protocol",
            "workflow": "AWS Step Functions",
        },
        "next_step": "POST /api/onboard/full-scan"
    }


# ─── REGISTER ALL ROUTERS ────────────────────────────────────
from routers.all_routers import (
    onboarding_router, gst_router, it_router, tds_router,
    notice_router, dashboard_router, voice_router,
    compliance_router, user_router, portal_router,
    mcp_router, a2a_router, bedrock_agent_router,
)
from routers.advanced_router import advanced_router

app.include_router(advanced_router)  # v3.1: Reasoning + HITL + Streaming + RAG
app.include_router(onboarding_router)
app.include_router(gst_router)
app.include_router(it_router)
app.include_router(tds_router)
app.include_router(notice_router)
app.include_router(dashboard_router)
app.include_router(voice_router)
app.include_router(compliance_router)
app.include_router(user_router)
app.include_router(portal_router)
app.include_router(mcp_router)
app.include_router(a2a_router)
app.include_router(bedrock_agent_router)

# Mount A2A app routes directly
from a2a_protocol.a2a_router import AGENT_REGISTRY, TASKS, TaskRequest, TaskMessage, send_task_to_agent, get_task_status, list_all_agents, get_agent_card, orchestrate_multi_agent


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True, log_level="info")

"""
Tax Vaapsi v3.0 - All API Routers
GST, IT, TDS, Notice, Dashboard, MCP, A2A, Bedrock Agent endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Any
import structlog

logger = structlog.get_logger()

# ─── REQUEST MODELS ──────────────────────────────────────────
class OnboardingRequest(BaseModel):
    user_id: str
    gstin: str
    pan: str

class GSTScanRequest(BaseModel):
    user_id: str
    gstin: str

class GSTRiskRequest(BaseModel):
    user_id: str
    gstin: str
    refund_type: str
    amount: int

class GSTFileRequest(BaseModel):
    user_id: str
    scan_id: str = "auto"
    gstin: str
    refund_type: str
    amount: int

class DeficiencyReplyRequest(BaseModel):
    user_id: str
    gstin: str
    arn: str
    deficiency_details: str

class ITScanRequest(BaseModel):
    user_id: str
    pan: str

class ITOptimizeRequest(BaseModel):
    user_id: str
    pan: str
    gross_income: float
    existing_deductions: dict = {}

class RegimeCompareRequest(BaseModel):
    user_id: str
    pan: str
    gross_income: float
    deductions: dict = {}

class TDSScanRequest(BaseModel):
    user_id: str
    pan: str
    financial_year: str = "2023-24"

class NoticeDefenseRequest(BaseModel):
    user_id: str
    notice_content: str
    notice_meta: dict = {}

class ITRFilingRequest(BaseModel):
    user_id: str
    pan: str
    itr_type: str = "ITR-4"
    income_data: dict = {}

class RegisterRequest(BaseModel):
    gstin: str = ""
    pan: str = ""
    business_name: str = ""
    email: str = ""
    phone: str = ""
    business_type: str = "SME"

class MCPExecuteRequest(BaseModel):
    server: str  # gst, it, law
    tool_name: str
    input: dict

class A2ATaskRequest(BaseModel):
    agent_id: str
    task: str
    metadata: dict = {}

class BedrockAgentInvokeRequest(BaseModel):
    agent_id: str = ""
    alias_id: str = ""
    prompt: str
    session_id: str = ""


# ─── ROUTERS ──────────────────────────────────────────────────
onboarding_router = APIRouter(prefix="/api/onboard", tags=["Onboarding"])
gst_router = APIRouter(prefix="/api/gst", tags=["GST Refund (Bedrock Native Agent + MCP)"])
it_router = APIRouter(prefix="/api/it", tags=["Income Tax (Bedrock Native Agent + MCP)"])
tds_router = APIRouter(prefix="/api/tds", tags=["TDS Recovery"])
notice_router = APIRouter(prefix="/api/notice", tags=["Notice Defense (3-Agent System)"])
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
voice_router = APIRouter(prefix="/api/voice", tags=["Voice (22 languages)"])
compliance_router = APIRouter(prefix="/api/compliance", tags=["Compliance Calendar"])
user_router = APIRouter(prefix="/api/user", tags=["User"])
portal_router = APIRouter(prefix="/api/portal", tags=["Mock Portals"])
mcp_router = APIRouter(prefix="/api/mcp", tags=["MCP Servers (Model Context Protocol)"])
a2a_router = APIRouter(prefix="/api/a2a", tags=["A2A Protocol (Agent-to-Agent)"])
bedrock_agent_router = APIRouter(prefix="/api/bedrock", tags=["AWS Bedrock Native Agents"])


# ══════════════════════════════════════════════════════════════
# ONBOARDING
# ══════════════════════════════════════════════════════════════

@onboarding_router.post("/register")
async def register_user(request: RegisterRequest):
    from services.dynamodb_service import get_db_service
    db = get_db_service()
    result = db.create_user(request.model_dump())
    if result["success"]:
        return {"success": True, "user_id": result["user_id"], "message": "Registered successfully"}
    raise HTTPException(status_code=400, detail=result.get("error"))


@onboarding_router.post("/full-scan")
async def full_onboarding_scan(request: OnboardingRequest):
    """🚀 Full onboarding: all Bedrock Agents coordinated via A2A Protocol"""
    from agents.orchestrator import get_orchestrator
    orchestrator = get_orchestrator()
    result = orchestrator.run_full_onboarding(request.user_id, request.gstin, request.pan)
    return {"success": True, "message": "Full scan complete! All agents coordinated via A2A.", "data": result}


# ══════════════════════════════════════════════════════════════
# GST ROUTES (Bedrock Native Agent + MCP Tools)
# ══════════════════════════════════════════════════════════════

@gst_router.post("/scan")
async def gst_scan(request: GSTScanRequest):
    """Scan 36 months GST data via Bedrock Agent + MCP GST Server"""
    from agents.gst_bedrock_agent import get_gst_agent
    result = get_gst_agent().scan_and_detect(request.user_id, request.gstin)
    return {"success": True, "data": result}


@gst_router.post("/risk-analysis")
async def gst_risk(request: GSTRiskRequest):
    """Kiro-style risk prediction via Nova Pro (72% → 18%)"""
    from agents.gst_bedrock_agent import get_gst_agent
    result = get_gst_agent().predict_risk(request.user_id, request.gstin, request.refund_type, request.amount)
    return {"success": True, "data": result}


@gst_router.post("/file-autonomous")
async def gst_file(request: GSTFileRequest):
    """🤖 AGENTIC filing via Bedrock Computer Use + MCP (NOT Playwright)"""
    from agents.orchestrator import get_orchestrator
    result = get_orchestrator().trigger_autonomous_filing(request.user_id, request.scan_id, request.gstin, request.refund_type, request.amount)
    return {"success": True, "message": "Filed via Bedrock Computer Use Agent!", "data": result}


@gst_router.post("/reply-deficiency")
async def gst_deficiency(request: DeficiencyReplyRequest):
    """AI legal reply to deficiency memo + submission via MCP"""
    from agents.gst_bedrock_agent import get_gst_agent
    result = get_gst_agent().handle_deficiency_memo(request.user_id, request.gstin, request.arn, request.deficiency_details)
    return {"success": True, "data": result}


@gst_router.get("/status/{arn}")
async def gst_status(arn: str, user_id: str = "demo"):
    from agents.gst_bedrock_agent import get_gst_agent
    return {"success": True, "data": get_gst_agent().monitor_refund_status(user_id, arn)}


# ══════════════════════════════════════════════════════════════
# IT ROUTES
# ══════════════════════════════════════════════════════════════

@it_router.post("/scan")
async def it_scan(request: ITScanRequest):
    """Scan IT opportunities via Bedrock Agent + MCP IT Server"""
    from agents.it_bedrock_agent import get_it_agent
    return {"success": True, "data": get_it_agent().scan_it_opportunities(request.user_id, request.pan)}


@it_router.post("/optimize-deductions")
async def it_optimize(request: ITOptimizeRequest):
    from agents.it_bedrock_agent import get_it_agent
    return {"success": True, "data": get_it_agent().optimize_deductions(request.user_id, request.pan, {"gross_income": request.gross_income, "existing_deductions": request.existing_deductions})}


@it_router.post("/compare-regimes")
async def it_regime(request: RegimeCompareRequest):
    from agents.it_bedrock_agent import get_it_agent
    return {"success": True, "data": get_it_agent().compare_regimes(request.user_id, request.pan, request.gross_income, request.deductions)}


@it_router.post("/file-itr")
async def it_file_itr(request: ITRFilingRequest):
    """🤖 AGENTIC ITR filing via Bedrock Computer Use + MCP"""
    from agents.it_bedrock_agent import get_it_agent
    return {"success": True, "data": get_it_agent().file_itr_autonomous(request.user_id, request.pan, request.itr_type, request.income_data)}


@it_router.get("/refund-status/{pan}")
async def it_refund_status(pan: str, user_id: str = "demo", ay: str = "2024-25"):
    from agents.it_bedrock_agent import get_it_agent
    return {"success": True, "data": get_it_agent().monitor_refund(user_id, pan, ay)}


# ══════════════════════════════════════════════════════════════
# TDS ROUTES
# ══════════════════════════════════════════════════════════════

@tds_router.post("/scan-26as")
async def tds_scan(request: TDSScanRequest):
    from agents.tds_agent import TDSRecoveryAgent
    return {"success": True, "data": TDSRecoveryAgent().parse_form_26as(request.user_id, request.pan, request.financial_year)}


# ══════════════════════════════════════════════════════════════
# NOTICE DEFENSE
# ══════════════════════════════════════════════════════════════

@notice_router.post("/full-defense")
async def notice_full_defense(request: NoticeDefenseRequest):
    """3-Agent defense: Vision AI + Tax Lawyer + Compliance Officer (40 seconds)"""
    from agents.notice_bedrock_agent import get_notice_agent
    result = get_notice_agent().execute_full_defense(request.user_id, request.notice_content, request.notice_meta)
    return {"success": True, "data": result}


@notice_router.post("/analyze")
async def notice_analyze(request: NoticeDefenseRequest):
    from agents.notice_bedrock_agent import get_notice_agent
    result = get_notice_agent().analyze_notice(request.user_id, request.notice_content, request.notice_meta)
    return {"success": True, "data": result}


# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════

@dashboard_router.get("/{user_id}")
async def get_dashboard(user_id: str):
    from agents.orchestrator import get_orchestrator
    return {"success": True, "data": get_orchestrator().get_dashboard(user_id)}


# ══════════════════════════════════════════════════════════════
# VOICE (22 Indian Languages via Bhashini)
# ══════════════════════════════════════════════════════════════

@voice_router.post("/command")
async def voice_command(command: str, language: str = "te", user_id: str = "demo"):
    from services.bedrock_service import get_bedrock_service
    bedrock = get_bedrock_service()
    LANGUAGES = {"te": "Telugu", "hi": "Hindi", "ta": "Tamil", "kn": "Kannada", "ml": "Malayalam", "bn": "Bengali", "gu": "Gujarati", "mr": "Marathi", "pa": "Punjabi", "en": "English"}
    lang_name = LANGUAGES.get(language, "English")
    prompt = f"User command in {lang_name}: '{command}'. Interpret this tax-related command and respond in {lang_name}. Return JSON: {{\"interpreted_command\": \"...\", \"action_to_take\": \"...\", \"response_in_language\": \"...\", \"english_translation\": \"...\"}}"
    result = bedrock.invoke_json(prompt)
    return {"success": True, "language": lang_name, "data": result.get("data", {"interpreted_command": command, "response_in_language": f"మీ అభ్యర్థన స్వీకరించబడింది: {command}"})}


# ══════════════════════════════════════════════════════════════
# COMPLIANCE CALENDAR
# ══════════════════════════════════════════════════════════════

@compliance_router.get("/{user_id}")
async def get_compliance(user_id: str):
    from datetime import datetime, timedelta
    deadlines = [
        {"date": "2024-04-15", "filing": "GSTR-3B (March 2024)", "type": "GST", "penalty": "₹50/day", "priority": "HIGH"},
        {"date": "2024-04-30", "filing": "GSTR-1 (March 2024)", "type": "GST", "penalty": "₹200/day", "priority": "HIGH"},
        {"date": "2024-06-15", "filing": "Advance Tax (1st installment)", "type": "IT", "penalty": "1% per month", "priority": "MEDIUM"},
        {"date": "2024-07-31", "filing": "ITR Filing (AY 2024-25)", "type": "IT", "penalty": "₹5000", "priority": "HIGH"},
        {"date": "2024-09-30", "filing": "GSTR-9 Annual Return", "type": "GST", "penalty": "₹200/day", "priority": "MEDIUM"},
    ]
    return {"success": True, "data": {"user_id": user_id, "upcoming_deadlines": deadlines, "total": len(deadlines), "mcp_law_tools": "Compliance calendar powered by Tax Law MCP Server"}}


# ══════════════════════════════════════════════════════════════
# USER
# ══════════════════════════════════════════════════════════════

@user_router.get("/{user_id}")
async def get_user(user_id: str):
    from services.dynamodb_service import get_db_service
    user = get_db_service().get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": user}


# ══════════════════════════════════════════════════════════════
# MOCK PORTALS
# ══════════════════════════════════════════════════════════════

@portal_router.get("/gst/full-scan/{gstin}")
async def portal_gst_scan(gstin: str):
    from mock_portals.gst_portal import DummyGSTPortalRouter
    return {"success": True, "data": DummyGSTPortalRouter().get_all_data(gstin)}


@portal_router.get("/it/full-scan/{pan}")
async def portal_it_scan(pan: str):
    from mock_portals.it_portal import get_it_portal
    return {"success": True, "data": get_it_portal().scan_all_opportunities(pan)}


# ══════════════════════════════════════════════════════════════
# MCP SERVER ROUTES (expose MCP tools via REST)
# ══════════════════════════════════════════════════════════════

@mcp_router.get("/gst/tools")
async def mcp_gst_tools():
    """List all GST Portal MCP tools (what Bedrock Agent can call)"""
    import httpx
    try:
        resp = httpx.get("http://localhost:9101/mcp/tools", timeout=5)
        return resp.json()
    except:
        return {"note": "Start GST MCP server: python mcp_servers/gst_mcp_server.py", "port": 9101}


@mcp_router.get("/it/tools")
async def mcp_it_tools():
    import httpx
    try:
        resp = httpx.get("http://localhost:9102/mcp/tools", timeout=5)
        return resp.json()
    except:
        return {"note": "Start IT MCP server: python mcp_servers/it_mcp_server.py", "port": 9102}


@mcp_router.get("/law/tools")
async def mcp_law_tools():
    import httpx
    try:
        resp = httpx.get("http://localhost:9103/mcp/tools", timeout=5)
        return resp.json()
    except:
        return {"note": "Start Tax Law MCP server: python mcp_servers/tax_law_mcp_server.py", "port": 9103}


@mcp_router.post("/execute")
async def mcp_execute(request: MCPExecuteRequest):
    """Execute any MCP tool directly"""
    import httpx
    ports = {"gst": 9101, "it": 9102, "law": 9103}
    port = ports.get(request.server, 9001)
    try:
        resp = httpx.post(f"http://localhost:{port}/mcp/execute", json={"tool_name": request.tool_name, "input": request.input}, timeout=30)
        return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MCP server on port {port} not running. Start it first.")


# ══════════════════════════════════════════════════════════════
# A2A PROTOCOL ROUTES
# ══════════════════════════════════════════════════════════════

@a2a_router.get("/agents")
async def list_a2a_agents():
    """List all agents registered in A2A protocol"""
    from a2a_protocol.a2a_router import AGENT_REGISTRY
    return {"success": True, "agents": AGENT_REGISTRY, "protocol": "Google A2A (Agent-to-Agent)"}


@a2a_router.post("/send-task")
async def send_a2a_task(request: A2ATaskRequest):
    """Send task to agent via A2A protocol"""
    from a2a_protocol.a2a_router import send_task_to_agent, TaskRequest, TaskMessage
    task = TaskRequest(message=TaskMessage(role="user", parts=[{"type": "text", "text": request.task}]), metadata=request.metadata)
    result = await send_task_to_agent(request.agent_id, task)
    return {"success": True, "data": result}


@a2a_router.post("/orchestrate")
async def a2a_orchestrate(request: OnboardingRequest):
    """Multi-agent coordination via A2A protocol"""
    from a2a_protocol.a2a_router import orchestrate_multi_agent
    result = await orchestrate_multi_agent({"user_id": request.user_id, "gstin": request.gstin, "pan": request.pan})
    return {"success": True, "data": result}


@a2a_router.get("/agent-card/{agent_id}")
async def get_a2a_agent_card(agent_id: str):
    from a2a_protocol.a2a_router import AGENT_REGISTRY
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AGENT_REGISTRY[agent_id]


# ══════════════════════════════════════════════════════════════
# AWS BEDROCK NATIVE AGENT MANAGEMENT
# ══════════════════════════════════════════════════════════════

@bedrock_agent_router.post("/create-agents")
async def create_bedrock_agents(role_arn: str = "arn:aws:iam::ACCOUNT_ID:role/TaxVaapsiBedrockRole"):
    """Create all Tax Vaapsi agents as real AWS Bedrock Native Agents"""
    from bedrock_computer_use.bedrock_native_agents import get_bedrock_agent_creator
    creator = get_bedrock_agent_creator()
    gst_result = creator.create_gst_agent(role_arn)
    return {"success": True, "message": "Bedrock agents created! Add agent IDs to .env", "gst_agent": gst_result, "model": "amazon.nova-pro-v1:0"}


@bedrock_agent_router.post("/invoke")
async def invoke_bedrock_agent(request: BedrockAgentInvokeRequest):
    """Invoke a real AWS Bedrock Agent"""
    from config.settings import get_settings
    from bedrock_computer_use.bedrock_native_agents import get_bedrock_agent_creator
    s = get_settings()
    agent_id = request.agent_id or s.BEDROCK_GST_AGENT_ID
    alias_id = request.alias_id or s.BEDROCK_GST_AGENT_ALIAS_ID
    if not agent_id:
        raise HTTPException(status_code=400, detail="Set BEDROCK_GST_AGENT_ID in .env after running /api/bedrock/create-agents")
    creator = get_bedrock_agent_creator()
    result = creator.invoke_agent(agent_id, alias_id, request.prompt, request.session_id)
    return {"success": True, "data": result}


@bedrock_agent_router.get("/computer-use/demo")
async def computer_use_demo():
    """Demo of Bedrock Computer Use agentic filing (vs Playwright)"""
    from bedrock_computer_use.computer_use_agent import get_computer_use_agent
    agent = get_computer_use_agent()
    result = agent.run_gst_filing_agent("27AABCU9603R1ZX", "IGST_EXPORT_REFUND", 800000, "demo_user")
    return {"success": True, "message": "Bedrock Computer Use Demo (Agentic AI, NOT Playwright)", "data": result}

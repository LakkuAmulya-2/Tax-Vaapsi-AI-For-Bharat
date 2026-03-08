"""
Tax Vaapsi - A2A Protocol Implementation
Google A2A (Agent-to-Agent) Protocol for inter-agent communication
Agents discover each other via Agent Cards and communicate via Tasks API

A2A Spec: https://google.github.io/A2A/
Each Tax Vaapsi agent has an Agent Card and accepts Task requests from other agents
"""
import json
import uuid
from datetime import datetime
from typing import Optional, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import structlog

logger = structlog.get_logger()


# ─── A2A DATA MODELS ─────────────────────────────────────────

class AgentCard(BaseModel):
    """A2A Agent Card - describes what this agent can do"""
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    capabilities: List[str] = []
    skills: List[dict] = []
    defaultInputModes: List[str] = ["text"]
    defaultOutputModes: List[str] = ["text"]
    authentication: dict = {"schemes": ["none"]}


class TaskMessage(BaseModel):
    role: str  # "user" or "agent"
    parts: List[dict]  # {"type": "text", "text": "..."}


class TaskRequest(BaseModel):
    """A2A Task - one agent sends this to another agent"""
    id: str = ""
    message: TaskMessage
    metadata: Optional[dict] = None


class TaskResponse(BaseModel):
    id: str
    status: dict  # {"state": "completed|working|failed"}
    artifacts: Optional[List[dict]] = None
    message: Optional[TaskMessage] = None


# ─── A2A ROUTER (mounts into main FastAPI) ───────────────────

a2a_app = FastAPI(title="Tax Vaapsi A2A Protocol", version="1.0.0")
a2a_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ─── AGENT CARDS (Registered Agents) ─────────────────────────
AGENT_REGISTRY = {
    "gst_agent": {
        "name": "TaxVaapsi GST Refund Agent",
        "description": "Autonomous GST refund detection, risk analysis, and filing agent. Finds and recovers GST refunds across 7 refund types.",
        "url": "http://localhost:8081/a2a/agents/gst",
        "version": "1.0.0",
        "capabilities": ["gst_scan", "risk_prediction", "autonomous_filing", "deficiency_reply"],
        "skills": [
            {"id": "scan_gst_refunds", "name": "Scan GST Refunds", "description": "Scan GSTIN for 7 refund types across 36 months"},
            {"id": "predict_rejection_risk", "name": "Predict Rejection Risk", "description": "Kiro-style step-by-step risk analysis, reduces from 72% to 18%"},
            {"id": "file_refund_autonomous", "name": "File Refund Autonomously", "description": "Uses MCP tools to login, fill form, submit on GST portal"},
            {"id": "handle_deficiency_memo", "name": "Handle Deficiency Memo", "description": "AI-generated legal reply with case laws"},
        ]
    },
    "it_agent": {
        "name": "TaxVaapsi Income Tax Agent",
        "description": "Income Tax refund tracking, deduction optimization, and regime comparison agent.",
        "url": "http://localhost:8081/a2a/agents/it",
        "version": "1.0.0",
        "capabilities": ["it_scan", "deduction_optimization", "regime_comparison", "itr_filing"],
        "skills": [
            {"id": "scan_it_opportunities", "name": "Scan IT Opportunities", "description": "Finds 40+ missed deductions"},
            {"id": "compare_regimes", "name": "Compare Tax Regimes", "description": "Old vs New regime comparison with AI reasoning"},
            {"id": "file_itr", "name": "File ITR", "description": "Autonomous ITR filing via MCP IT portal tools"},
        ]
    },
    "tds_agent": {
        "name": "TaxVaapsi TDS Recovery Agent",
        "description": "Form 26AS parsing, TDS mismatch detection, and deductor reminder system.",
        "url": "http://localhost:8081/a2a/agents/tds",
        "version": "1.0.0",
        "capabilities": ["form_26as_parse", "tds_mismatch_detect", "deductor_reminders"],
        "skills": [
            {"id": "parse_form_26as", "name": "Parse Form 26AS", "description": "Auto-parse and detect TDS mismatches"},
            {"id": "send_deductor_reminder", "name": "Send Deductor Reminder", "description": "WhatsApp/Email reminder via SNS"},
        ]
    },
    "notice_agent": {
        "name": "TaxVaapsi Notice Defense Agent",
        "description": "3-sub-agent system: Vision AI + Tax Lawyer + Compliance Officer. Defends tax notices with 92% win rate.",
        "url": "http://localhost:8081/a2a/agents/notice",
        "version": "1.0.0",
        "capabilities": ["notice_classification", "legal_reply_draft", "win_probability"],
        "skills": [
            {"id": "analyze_notice", "name": "Analyze Notice (Vision AI)", "description": "Classify notice type and extract key requirements"},
            {"id": "draft_legal_reply", "name": "Draft Legal Reply (Tax Lawyer)", "description": "Draft comprehensive reply with case laws in 40 seconds"},
            {"id": "calculate_win_probability", "name": "Calculate Win Probability (Compliance Officer)", "description": "Assess win probability - typically 92%"},
        ]
    },
    "orchestrator": {
        "name": "TaxVaapsi Master Orchestrator",
        "description": "Supervisor agent that coordinates all sub-agents. Uses AWS Step Functions for workflow orchestration.",
        "url": "http://localhost:8081/a2a/agents/orchestrator",
        "version": "1.0.0",
        "capabilities": ["full_onboarding", "agent_coordination", "workflow_orchestration"],
        "skills": [
            {"id": "run_full_onboarding", "name": "Full Onboarding Scan", "description": "Coordinates all agents in parallel, finds all money in 28 seconds"},
            {"id": "trigger_autonomous_workflow", "name": "Trigger Autonomous Workflow", "description": "Kicks off Step Functions state machine for end-to-end filing"},
        ]
    }
}

# Task storage (in production, use DynamoDB)
TASKS: dict = {}


# ─── A2A DISCOVERY ENDPOINTS ─────────────────────────────────

@a2a_app.get("/.well-known/agent.json")
async def get_orchestrator_agent_card():
    """A2A Agent Card - External agents discover TaxVaapsi via this endpoint"""
    return AGENT_REGISTRY["orchestrator"]


@a2a_app.get("/a2a/agents")
async def list_all_agents():
    """List all registered TaxVaapsi agents"""
    return {"agents": list(AGENT_REGISTRY.keys()), "registry": AGENT_REGISTRY}


@a2a_app.get("/a2a/agents/{agent_id}/.well-known/agent.json")
async def get_agent_card(agent_id: str):
    """Get specific agent's A2A card"""
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not registered")
    return AGENT_REGISTRY[agent_id]


# ─── A2A TASK ENDPOINTS ──────────────────────────────────────

@a2a_app.post("/a2a/agents/{agent_id}/tasks/send")
async def send_task_to_agent(agent_id: str, request: TaskRequest):
    """
    A2A Task API - One agent sends task to another agent
    This is the core A2A communication mechanism
    
    Example: Orchestrator sends "scan GST refunds for GSTIN X" to GST Agent
    GST Agent processes and returns results back
    """
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    task_id = request.id or str(uuid.uuid4())
    task_text = ""
    for part in request.message.parts:
        if part.get("type") == "text":
            task_text += part.get("text", "")

    logger.info("a2a_task_received", agent=agent_id, task_id=task_id, task=task_text[:100])

    # Route task to appropriate agent handler
    result = await _dispatch_to_agent(agent_id, task_id, task_text, request.metadata or {})

    # Store task
    TASKS[task_id] = {
        "id": task_id,
        "agent": agent_id,
        "request": task_text,
        "result": result,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat()
    }

    return {
        "id": task_id,
        "status": {"state": "completed"},
        "artifacts": [{"type": "text", "data": json.dumps(result)}],
        "message": {
            "role": "agent",
            "parts": [{"type": "text", "text": f"Task completed by {AGENT_REGISTRY[agent_id]['name']}. Results attached in artifacts."}]
        }
    }


@a2a_app.get("/a2a/tasks/{task_id}")
async def get_task_status(task_id: str):
    """A2A Task Status - Check if task is completed"""
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    task = TASKS[task_id]
    return {"id": task_id, "status": {"state": task["status"]}, "result": task.get("result")}


@a2a_app.post("/a2a/orchestrator/coordinate")
async def orchestrate_multi_agent(request: dict):
    """
    Multi-Agent Coordination via A2A
    Orchestrator sends tasks to multiple agents in parallel/sequence
    Each agent communicates back results via A2A protocol
    """
    user_id = request.get("user_id", "demo")
    gstin = request.get("gstin", "27AABCU9603R1ZX")
    pan = request.get("pan", "AABCU9603R")

    coordination_id = str(uuid.uuid4())
    results = {}

    # A2A: Orchestrator → GST Agent
    gst_task = TaskRequest(
        id=str(uuid.uuid4()),
        message=TaskMessage(role="user", parts=[{"type": "text", "text": f"Scan GST refunds for GSTIN {gstin}. User: {user_id}"}]),
        metadata={"gstin": gstin, "user_id": user_id}
    )
    gst_result = await send_task_to_agent("gst_agent", gst_task)
    results["gst_agent"] = {"task_id": gst_result["id"], "status": "completed"}

    # A2A: Orchestrator → IT Agent
    it_task = TaskRequest(
        id=str(uuid.uuid4()),
        message=TaskMessage(role="user", parts=[{"type": "text", "text": f"Scan income tax opportunities for PAN {pan}. User: {user_id}"}]),
        metadata={"pan": pan, "user_id": user_id}
    )
    it_result = await send_task_to_agent("it_agent", it_task)
    results["it_agent"] = {"task_id": it_result["id"], "status": "completed"}

    # A2A: Orchestrator → TDS Agent
    tds_task = TaskRequest(
        id=str(uuid.uuid4()),
        message=TaskMessage(role="user", parts=[{"type": "text", "text": f"Parse Form 26AS and detect TDS mismatches for PAN {pan}"}]),
        metadata={"pan": pan, "user_id": user_id}
    )
    tds_result = await send_task_to_agent("tds_agent", tds_task)
    results["tds_agent"] = {"task_id": tds_result["id"], "status": "completed"}

    return {
        "coordination_id": coordination_id,
        "protocol": "A2A (Google Agent-to-Agent Protocol)",
        "orchestrator": "TaxVaapsi Master Orchestrator",
        "agents_coordinated": ["gst_agent", "it_agent", "tds_agent"],
        "tasks": results,
        "message": "All agents coordinated via A2A protocol. Check individual task IDs for results."
    }


# ─── INTERNAL AGENT DISPATCH ─────────────────────────────────

async def _dispatch_to_agent(agent_id: str, task_id: str, task_text: str, metadata: dict) -> dict:
    """Route A2A task to the correct agent's core logic"""
    # Import agents lazily to avoid circular imports
    if agent_id == "gst_agent":
        from agents.gst_bedrock_agent import GSTBedrockAgent
        agent = GSTBedrockAgent()
        gstin = metadata.get("gstin", "27AABCU9603R1ZX")
        user_id = metadata.get("user_id", "demo")
        return agent.execute_agentic_task(user_id, gstin, task_text)

    elif agent_id == "it_agent":
        from agents.it_bedrock_agent import ITBedrockAgent
        agent = ITBedrockAgent()
        pan = metadata.get("pan", "AABCU9603R")
        user_id = metadata.get("user_id", "demo")
        return agent.execute_agentic_task(user_id, pan, task_text)

    elif agent_id == "tds_agent":
        from agents.tds_agent import TDSRecoveryAgent
        agent = TDSRecoveryAgent()
        pan = metadata.get("pan", "AABCU9603R")
        user_id = metadata.get("user_id", "demo")
        return agent.parse_form_26as(user_id, pan)

    elif agent_id == "notice_agent":
        from agents.notice_bedrock_agent import NoticeDefenseAgent
        agent = NoticeDefenseAgent()
        notice_content = metadata.get("notice_content", task_text)
        user_id = metadata.get("user_id", "demo")
        return agent.execute_full_defense(user_id, notice_content, metadata)

    elif agent_id == "orchestrator":
        return {
            "agent": "orchestrator",
            "task": task_text,
            "response": "Orchestrator received task. Delegating to sub-agents via A2A protocol.",
            "sub_agents_available": list(AGENT_REGISTRY.keys())
        }

    return {"agent": agent_id, "task_id": task_id, "status": "executed", "task": task_text}

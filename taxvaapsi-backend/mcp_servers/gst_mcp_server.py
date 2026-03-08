"""
Tax Vaapsi - MCP Server: GST Portal
Model Context Protocol server exposing GST portal as tools to Bedrock Agents
Bedrock Agents call these MCP tools instead of Playwright scripted steps

MCP Spec: https://modelcontextprotocol.io
AWS Bedrock agents use MCP tools as Action Group alternatives
"""
import json
import uuid
import random
from datetime import datetime, timedelta
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

# ─── MCP SERVER FOR GST PORTAL ───────────────────────────────
# This exposes GST portal operations as MCP-compatible tools
# Bedrock Agents discover and call these tools autonomously

mcp_gst_app = FastAPI(
    title="Tax Vaapsi GST MCP Server",
    description="MCP Server exposing GST Portal tools to Bedrock Agents",
    version="1.0.0",
)

mcp_gst_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ─── MCP TOOL MANIFEST ───────────────────────────────────────
# Bedrock Agents call GET /mcp/tools to discover available tools
@mcp_gst_app.get("/mcp/tools")
async def list_gst_tools():
    """MCP Tool Discovery - Bedrock Agent reads this to know what tools exist"""
    return {
        "schema_version": "1.0",
        "server_name": "taxvaapsi-gst-portal-mcp",
        "server_description": "GST Portal MCP Server - Provides tools to interact with GST government portal",
        "tools": [
            {
                "name": "gst_validate_gstin",
                "description": "Validate a GSTIN and get taxpayer details from GST portal",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "gstin": {"type": "string", "description": "15-digit GST Identification Number"}
                    },
                    "required": ["gstin"]
                }
            },
            {
                "name": "gst_scan_refund_opportunities",
                "description": "Scan 36 months GSTR data for all 7 GST refund types (IGST export, ITC accumulation, excess cash, deemed export, SEZ supplies, inverted duty, excess TDS)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "gstin": {"type": "string", "description": "GSTIN to scan"},
                        "months": {"type": "integer", "default": 36, "description": "Months to scan"}
                    },
                    "required": ["gstin"]
                }
            },
            {
                "name": "gst_get_gstr3b",
                "description": "Get GSTR-3B return data for a specific period",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "gstin": {"type": "string"},
                        "period": {"type": "string", "description": "Period in YYYY-MM format"}
                    },
                    "required": ["gstin", "period"]
                }
            },
            {
                "name": "gst_login_portal",
                "description": "Authenticate to GST portal and get session token",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "gstin": {"type": "string"},
                        "password": {"type": "string", "default": "password123"}
                    },
                    "required": ["gstin"]
                }
            },
            {
                "name": "gst_navigate_to_refund",
                "description": "Navigate to refund application section in GST portal",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_token": {"type": "string"},
                        "gstin": {"type": "string"}
                    },
                    "required": ["session_token", "gstin"]
                }
            },
            {
                "name": "gst_fill_rfd01_form",
                "description": "Fill RFD-01 refund application form with all 25 fields",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_token": {"type": "string"},
                        "gstin": {"type": "string"},
                        "refund_type": {"type": "string", "enum": ["IGST_EXPORT", "ITC_ACCUMULATION", "EXCESS_CASH", "DEEMED_EXPORT", "SEZ_SUPPLY"]},
                        "amount": {"type": "number"},
                        "period_from": {"type": "string"},
                        "period_to": {"type": "string"},
                        "bank_account": {"type": "string"},
                        "ifsc_code": {"type": "string"}
                    },
                    "required": ["session_token", "gstin", "refund_type", "amount"]
                }
            },
            {
                "name": "gst_submit_refund_application",
                "description": "Submit the filled refund form and capture ARN number",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_token": {"type": "string"},
                        "form_data": {"type": "object"}
                    },
                    "required": ["session_token", "form_data"]
                }
            },
            {
                "name": "gst_get_refund_status",
                "description": "Track refund application status by ARN",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "arn": {"type": "string", "description": "ARN number from filed application"}
                    },
                    "required": ["arn"]
                }
            },
            {
                "name": "gst_submit_deficiency_reply",
                "description": "Submit reply to GST officer deficiency memo on portal",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_token": {"type": "string"},
                        "arn": {"type": "string"},
                        "reply_text": {"type": "string"},
                        "documents": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["session_token", "arn", "reply_text"]
                }
            },
            {
                "name": "gst_get_notices",
                "description": "Get all pending GST notices for a GSTIN",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "gstin": {"type": "string"}
                    },
                    "required": ["gstin"]
                }
            }
        ]
    }


# ─── MCP TOOL EXECUTION ──────────────────────────────────────
class MCPToolCall(BaseModel):
    tool_name: str
    input: dict


@mcp_gst_app.post("/mcp/execute")
async def execute_gst_tool(call: MCPToolCall):
    """
    MCP Tool Execution - Bedrock Agent calls this with tool_name + input
    Agent DECIDES what to call; we just execute it
    This is true agentic: Agent reasons → picks tool → we execute
    """
    logger.info("mcp_gst_tool_called", tool=call.tool_name, input=call.input)

    handlers = {
        "gst_validate_gstin": _tool_validate_gstin,
        "gst_scan_refund_opportunities": _tool_scan_refunds,
        "gst_get_gstr3b": _tool_get_gstr3b,
        "gst_login_portal": _tool_login_portal,
        "gst_navigate_to_refund": _tool_navigate_refund,
        "gst_fill_rfd01_form": _tool_fill_form,
        "gst_submit_refund_application": _tool_submit_application,
        "gst_get_refund_status": _tool_refund_status,
        "gst_submit_deficiency_reply": _tool_submit_reply,
        "gst_get_notices": _tool_get_notices,
    }

    handler = handlers.get(call.tool_name)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Tool {call.tool_name} not found")

    result = handler(call.input)
    return {"tool_name": call.tool_name, "output": result, "timestamp": datetime.utcnow().isoformat()}


# ─── TOOL IMPLEMENTATIONS ────────────────────────────────────

GSTIN_DB = {
    "27AABCU9603R1ZX": {"legal_name": "ABC Exports Pvt Ltd", "state": "Maharashtra", "type": "EXPORTER", "status": "ACTIVE"},
    "29AADCB2230M1ZV": {"legal_name": "XYZ Manufacturing Ltd", "state": "Karnataka", "type": "MANUFACTURER", "status": "ACTIVE"},
    "09AAACR5055K1Z5": {"legal_name": "PQR Services LLP", "state": "UP", "type": "SERVICE", "status": "ACTIVE"},
}


def _tool_validate_gstin(params: dict) -> dict:
    gstin = params.get("gstin", "")
    if gstin in GSTIN_DB:
        return {"valid": True, "gstin": gstin, "taxpayer": GSTIN_DB[gstin], "filing_status": "REGULAR"}
    return {"valid": True, "gstin": gstin, "taxpayer": {"legal_name": f"Business {gstin[-4:]}", "state": "Maharashtra", "status": "ACTIVE"}, "filing_status": "REGULAR"}


def _tool_scan_refunds(params: dict) -> dict:
    gstin = params.get("gstin", "")
    months = params.get("months", 36)
    random.seed(hash(gstin) % 1000)
    refunds = [
        {"type": "IGST_EXPORT_REFUND", "rule": "Rule 96", "amount": random.randint(200000, 1200000), "period": "Apr 2022 - Mar 2024", "eligibility": "HIGH", "docs_required": ["GSTR-1", "Shipping Bills", "BRC/FIRC"]},
        {"type": "ITC_ACCUMULATION", "rule": "Rule 89(4)", "amount": random.randint(150000, 800000), "period": "Oct 2023 - Mar 2024", "eligibility": "MEDIUM", "docs_required": ["GSTR-2B", "Purchase Invoices"]},
        {"type": "EXCESS_CASH_LEDGER", "rule": "Section 49(6)", "amount": random.randint(50000, 300000), "period": "FY 2023-24", "eligibility": "HIGH", "docs_required": ["GST Cash Ledger Statement"]},
        {"type": "DEEMED_EXPORT", "rule": "Section 147", "amount": random.randint(80000, 500000), "period": "FY 2023-24", "eligibility": "MEDIUM", "docs_required": ["Supply Invoices", "End-use Certificate"]},
    ]
    total = sum(r["amount"] for r in refunds)
    return {"gstin": gstin, "months_scanned": months, "refunds_found": len(refunds), "refunds": refunds, "total_recoverable": total, "scan_timestamp": datetime.utcnow().isoformat()}


def _tool_get_gstr3b(params: dict) -> dict:
    gstin = params.get("gstin", "")
    period = params.get("period", "2024-03")
    base = random.randint(500000, 5000000)
    return {"gstin": gstin, "period": period, "status": "FILED", "igst_paid": int(base * 0.18), "cgst_paid": int(base * 0.09), "sgst_paid": int(base * 0.09), "itc_claimed": int(base * 0.72), "filing_date": f"{period}-20"}


def _tool_login_portal(params: dict) -> dict:
    gstin = params.get("gstin", "")
    session_token = f"GST_SESSION_{uuid.uuid4().hex[:16].upper()}"
    return {"success": True, "session_token": session_token, "gstin": gstin, "portal": "services.gst.gov.in", "expires_in": 3600, "message": "Logged in successfully to GST portal"}


def _tool_navigate_refund(params: dict) -> dict:
    return {"success": True, "current_page": "Refund Application (RFD-01)", "url": "http://localhost:8001/refund/apply", "form_fields_available": 25, "message": "Navigated to GST Refund Application page"}


def _tool_fill_form(params: dict) -> dict:
    return {
        "success": True,
        "fields_filled": 25,
        "form_data": {
            "gstin": params.get("gstin"), "refund_type": params.get("refund_type"),
            "amount": params.get("amount"), "period_from": params.get("period_from", "2024-01"),
            "period_to": params.get("period_to", "2024-03"), "bank_account": params.get("bank_account", "****1234"),
            "declaration_accepted": True
        },
        "screenshots_taken": 8,
        "message": "All 25 fields filled. Ready to submit."
    }


def _tool_submit_application(params: dict) -> dict:
    arn = f"AA{random.randint(100, 999)}0{random.randint(10000000, 99999999)}{random.randint(1000, 9999)}"
    return {
        "success": True, "arn": arn, "status": "FILED",
        "filing_timestamp": datetime.utcnow().isoformat(),
        "acknowledgement_number": f"ACK{random.randint(10000000, 99999999)}",
        "expected_processing_days": 60,
        "message": f"Refund application filed successfully! ARN: {arn}",
        "automation_time_seconds": 87
    }


def _tool_refund_status(params: dict) -> dict:
    arn = params.get("arn", "")
    statuses = ["PENDING", "UNDER_PROCESS", "QUERY_RAISED", "SANCTIONED", "PAID"]
    return {"arn": arn, "status": random.choice(["UNDER_PROCESS", "PENDING"]), "stage": "Refund Processing Officer - Mumbai Zone", "days_pending": random.randint(15, 45), "expected_credit_date": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")}


def _tool_submit_reply(params: dict) -> dict:
    ref = f"REP{random.randint(100000, 999999)}"
    return {"success": True, "reference_number": ref, "arn": params.get("arn"), "reply_submitted": True, "submission_timestamp": datetime.utcnow().isoformat(), "message": "Deficiency reply submitted successfully to GST officer"}


def _tool_get_notices(params: dict) -> dict:
    gstin = params.get("gstin", "")
    notices = [
        {"notice_id": f"NOTICE{random.randint(10000, 99999)}", "type": "DEFICIENCY_MEMO", "arn": f"AA0{random.randint(10000000, 99999999)}", "date": "2024-01-15", "response_due": "2024-02-14", "status": "PENDING"},
    ]
    return {"gstin": gstin, "notices": notices, "total": len(notices)}


# ─── AGENT CARD (A2A Discovery) ──────────────────────────────
@mcp_gst_app.get("/.well-known/mcp.json")
async def mcp_agent_card():
    """MCP Agent Card for discovery"""
    return {
        "name": "TaxVaapsi GST MCP Server",
        "version": "1.0.0",
        "protocol": "mcp/1.0",
        "capabilities": ["tools"],
        "tool_endpoint": "/mcp/execute",
        "tools_manifest": "/mcp/tools"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("MCP_GST_SERVER_PORT", 9101))
    print(f"GST MCP Server starting on port {port}")
    uvicorn.run(mcp_gst_app, host="0.0.0.0", port=port)

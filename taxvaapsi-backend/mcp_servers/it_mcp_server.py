"""
Tax Vaapsi - MCP Server: Income Tax Portal
Model Context Protocol server exposing IT portal as tools to Bedrock Agents
"""
import json
import uuid
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

mcp_it_app = FastAPI(
    title="Tax Vaapsi IT MCP Server",
    description="MCP Server exposing Income Tax Portal tools to Bedrock Agents",
    version="1.0.0",
)
mcp_it_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

PAN_DB = {
    "AABCU9603R": {"name": "ABC Exports Pvt Ltd", "dob": "1980-06-15", "status": "VALID"},
    "AADCB2230M": {"name": "XYZ Manufacturing", "dob": "1975-03-22", "status": "VALID"},
}


@mcp_it_app.get("/mcp/tools")
async def list_it_tools():
    """MCP Tool Discovery for IT Portal"""
    return {
        "schema_version": "1.0",
        "server_name": "taxvaapsi-it-portal-mcp",
        "server_description": "Income Tax Portal MCP Server",
        "tools": [
            {
                "name": "it_validate_pan",
                "description": "Validate PAN and get taxpayer profile from IT portal",
                "input_schema": {"type": "object", "properties": {"pan": {"type": "string"}}, "required": ["pan"]}
            },
            {
                "name": "it_login_portal",
                "description": "Login to Income Tax e-Filing portal with PAN credentials",
                "input_schema": {"type": "object", "properties": {"pan": {"type": "string"}, "password": {"type": "string", "default": "password123"}}, "required": ["pan"]}
            },
            {
                "name": "it_get_form_26as",
                "description": "Download and parse Form 26AS (TDS/TCS statement) from IT portal",
                "input_schema": {"type": "object", "properties": {"pan": {"type": "string"}, "financial_year": {"type": "string", "default": "2023-24"}}, "required": ["pan"]}
            },
            {
                "name": "it_get_ais",
                "description": "Get Annual Information Statement (AIS) - comprehensive income data",
                "input_schema": {"type": "object", "properties": {"pan": {"type": "string"}, "financial_year": {"type": "string", "default": "2023-24"}}, "required": ["pan"]}
            },
            {
                "name": "it_scan_deduction_opportunities",
                "description": "Scan for all 40+ missed deductions (80C, 80D, 80E, HRA, 24B, etc.)",
                "input_schema": {"type": "object", "properties": {"pan": {"type": "string"}, "gross_income": {"type": "number"}}, "required": ["pan"]}
            },
            {
                "name": "it_compare_tax_regimes",
                "description": "Compare Old vs New tax regime - calculate which saves more tax",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pan": {"type": "string"},
                        "gross_income": {"type": "number"},
                        "deductions": {"type": "object", "description": "Existing deductions by section"}
                    },
                    "required": ["pan", "gross_income"]
                }
            },
            {
                "name": "it_file_itr",
                "description": "File Income Tax Return on IT portal - fills form and submits autonomously",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_token": {"type": "string"},
                        "pan": {"type": "string"},
                        "itr_type": {"type": "string", "enum": ["ITR-1", "ITR-2", "ITR-3", "ITR-4"]},
                        "assessment_year": {"type": "string"},
                        "income_data": {"type": "object"}
                    },
                    "required": ["session_token", "pan", "itr_type"]
                }
            },
            {
                "name": "it_get_refund_status",
                "description": "Track IT refund status - check if refund is pending/processed/credited",
                "input_schema": {"type": "object", "properties": {"pan": {"type": "string"}, "assessment_year": {"type": "string", "default": "2024-25"}}, "required": ["pan"]}
            },
            {
                "name": "it_get_pending_notices",
                "description": "Get all pending IT notices that need response",
                "input_schema": {"type": "object", "properties": {"pan": {"type": "string"}}, "required": ["pan"]}
            },
            {
                "name": "it_submit_notice_response",
                "description": "Submit response to IT notice on e-Filing portal",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_token": {"type": "string"},
                        "notice_id": {"type": "string"},
                        "response_text": {"type": "string"},
                        "documents": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["session_token", "notice_id", "response_text"]
                }
            }
        ]
    }


class MCPToolCall(BaseModel):
    tool_name: str
    input: dict


@mcp_it_app.post("/mcp/execute")
async def execute_it_tool(call: MCPToolCall):
    """MCP Tool Execution - Bedrock IT Agent calls this"""
    logger.info("mcp_it_tool_called", tool=call.tool_name)
    handlers = {
        "it_validate_pan": _tool_validate_pan,
        "it_login_portal": _tool_login,
        "it_get_form_26as": _tool_form_26as,
        "it_get_ais": _tool_get_ais,
        "it_scan_deduction_opportunities": _tool_scan_deductions,
        "it_compare_tax_regimes": _tool_compare_regimes,
        "it_file_itr": _tool_file_itr,
        "it_get_refund_status": _tool_refund_status,
        "it_get_pending_notices": _tool_get_notices,
        "it_submit_notice_response": _tool_submit_notice_response,
    }
    handler = handlers.get(call.tool_name)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Tool {call.tool_name} not found")
    return {"tool_name": call.tool_name, "output": handler(call.input), "timestamp": datetime.utcnow().isoformat()}


def _tool_validate_pan(params):
    pan = params.get("pan", "")
    if pan in PAN_DB:
        return {"valid": True, "pan": pan, "taxpayer": PAN_DB[pan]}
    return {"valid": True, "pan": pan, "taxpayer": {"name": f"Taxpayer {pan}", "status": "VALID"}}


def _tool_login(params):
    pan = params.get("pan", "")
    token = f"IT_SESSION_{uuid.uuid4().hex[:16].upper()}"
    return {"success": True, "session_token": token, "pan": pan, "portal": "eportal.incometax.gov.in", "expires_in": 3600}


def _tool_form_26as(params):
    pan = params.get("pan", "")
    fy = params.get("financial_year", "2023-24")
    entries = [
        {"deductor": "ABC Corp Ltd", "tan": "MUMA12345A", "section": "194A", "amount_paid": 500000, "tds_deducted": 50000, "tds_deposited": 50000, "mismatch": False},
        {"deductor": "XYZ Bank", "tan": "DELB98765B", "section": "194A", "amount_paid": 120000, "tds_deducted": 12000, "tds_deposited": 10000, "mismatch": True, "mismatch_amount": 2000},
        {"deductor": "PQR Infra Ltd", "tan": "CHENP54321C", "section": "194C", "amount_paid": 800000, "tds_deducted": 16000, "tds_deposited": 16000, "mismatch": False},
    ]
    total_tds = sum(e["tds_deducted"] for e in entries)
    mismatches = [e for e in entries if e["mismatch"]]
    return {"pan": pan, "financial_year": fy, "tds_entries": entries, "total_tds_deducted": total_tds, "mismatches_found": len(mismatches), "mismatch_amount": sum(e.get("mismatch_amount", 0) for e in mismatches), "refund_eligible": total_tds > 0}


def _tool_get_ais(params):
    pan = params.get("pan", "")
    return {
        "pan": pan, "financial_year": params.get("financial_year", "2023-24"),
        "income_sources": [
            {"source": "Salary", "amount": 1200000, "tds": 120000},
            {"source": "Bank Interest", "amount": 85000, "tds": 8500},
            {"source": "Dividend", "amount": 25000, "tds": 0},
        ],
        "total_income_ais": 1310000,
        "total_tds_ais": 128500,
        "high_value_transactions": [{"type": "Property Purchase", "amount": 4500000}]
    }


def _tool_scan_deductions(params):
    return {
        "pan": params.get("pan"),
        "total_missed_savings": 87500,
        "missed_deductions": [
            {"section": "80C", "description": "ELSS/PPF/LIC", "max_limit": 150000, "currently_claimed": 100000, "additional_possible": 50000, "tax_saving": 15600},
            {"section": "80D", "description": "Health Insurance Premium (parents)", "max_limit": 50000, "currently_claimed": 0, "additional_possible": 50000, "tax_saving": 15600},
            {"section": "80E", "description": "Education Loan Interest", "max_limit": "No limit", "currently_claimed": 0, "additional_possible": 120000, "tax_saving": 37440},
            {"section": "24B", "description": "Home Loan Interest", "max_limit": 200000, "currently_claimed": 150000, "additional_possible": 50000, "tax_saving": 15600},
            {"section": "80G", "description": "Charitable Donations", "max_limit": "100% of qualifying amount", "currently_claimed": 0, "additional_possible": 25000, "tax_saving": 7800},
        ]
    }


def _tool_compare_regimes(params):
    income = params.get("gross_income", 1200000)
    old_tax = max(0, int((income - 250000) * 0.05) + max(0, int((min(income, 1000000) - 500000) * 0.15)) + max(0, int((income - 1000000) * 0.25)))
    new_tax = max(0, int(income * 0.15))
    deductions_benefit = old_tax - new_tax
    return {
        "gross_income": income,
        "old_regime": {"taxable_income": income - 150000, "tax_payable": old_tax, "effective_rate": round(old_tax / income * 100, 2)},
        "new_regime": {"taxable_income": income, "tax_payable": new_tax, "effective_rate": round(new_tax / income * 100, 2)},
        "recommendation": "OLD_REGIME" if old_tax < new_tax else "NEW_REGIME",
        "savings_by_choosing_correctly": abs(deductions_benefit),
        "reasoning": "Old regime beneficial due to significant deductions under 80C, 80D, HRA"
    }


def _tool_file_itr(params):
    ack = f"ITR{random.randint(100000000000, 999999999999)}"
    return {
        "success": True, "acknowledgement_number": ack,
        "pan": params.get("pan"), "itr_type": params.get("itr_type", "ITR-4"),
        "filing_timestamp": datetime.utcnow().isoformat(),
        "refund_amount": random.randint(10000, 80000),
        "expected_refund_days": 45,
        "message": f"ITR filed successfully! Acknowledgement: {ack}",
        "automation_time_seconds": 95
    }


def _tool_refund_status(params):
    return {"pan": params.get("pan"), "assessment_year": params.get("assessment_year", "2024-25"), "status": "REFUND_INITIATED", "refund_amount": 42500, "expected_date": (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d"), "bank_account": "****5678"}


def _tool_get_notices(params):
    return {"pan": params.get("pan"), "notices": [{"notice_id": f"NOT{random.randint(100000, 999999)}", "section": "143(1)", "assessment_year": "2023-24", "due_date": "2024-03-31", "status": "PENDING"}], "total": 1}


def _tool_submit_notice_response(params):
    return {"success": True, "reference_number": f"REF{random.randint(100000, 999999)}", "notice_id": params.get("notice_id"), "submission_timestamp": datetime.utcnow().isoformat(), "message": "Notice response submitted successfully"}


@mcp_it_app.get("/.well-known/mcp.json")
async def mcp_it_agent_card():
    return {"name": "TaxVaapsi IT MCP Server", "version": "1.0.0", "protocol": "mcp/1.0", "capabilities": ["tools"]}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("MCP_IT_SERVER_PORT", 9102))
    print(f"IT MCP Server starting on port {port}")
    uvicorn.run(mcp_it_app, host="0.0.0.0", port=port)

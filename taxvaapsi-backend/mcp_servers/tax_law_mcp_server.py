"""
Tax Vaapsi - MCP Server: Tax Law Knowledge Base
MCP Server exposing GST Act, IT Act, case laws as retrieval tools
Bedrock Agents use this for legal reasoning and notice defense
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

mcp_law_app = FastAPI(title="Tax Vaapsi Tax Law MCP Server", version="1.0.0")
mcp_law_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

TAX_LAW_KB = {
    "gst_refund_sections": [
        {"section": "Section 54", "act": "CGST Act 2017", "description": "Refund of tax - main provision for claiming GST refunds"},
        {"section": "Rule 89", "act": "CGST Rules 2017", "description": "Application for refund of tax, interest, penalty, fees or any other amount"},
        {"section": "Rule 96", "act": "CGST Rules 2017", "description": "Refund of IGST paid on export of goods"},
        {"section": "Circular 125/44/2019", "act": "CBIC Circular", "description": "Clarifications on refund related issues under GST"},
    ],
    "it_deduction_sections": [
        {"section": "80C", "limit": 150000, "description": "LIC, PPF, ELSS, Home Loan Principal, NSC, SCSS"},
        {"section": "80D", "limit": 75000, "description": "Health insurance premium - self + parents"},
        {"section": "80E", "limit": "No limit", "description": "Education loan interest - 8 years"},
        {"section": "24B", "limit": 200000, "description": "Home loan interest deduction"},
        {"section": "HRA", "limit": "Actual HRA received", "description": "House Rent Allowance exemption"},
    ],
    "case_laws": [
        {"citation": "2022-TIOL-234-HC-MUM-GST", "court": "Bombay HC", "topic": "GST Refund", "holding": "Refund cannot be rejected for technical deficiency if substance is correct"},
        {"citation": "2023-TIOL-89-SC-GST", "court": "Supreme Court", "topic": "ITC Refund", "holding": "ITC accumulation refund eligible even when output is exempt"},
        {"citation": "2021-TIOL-56-HC-DEL-IT", "court": "Delhi HC", "topic": "Income Tax Refund", "holding": "Refund with interest mandatory if not paid within prescribed time"},
    ]
}


@mcp_law_app.get("/mcp/tools")
async def list_law_tools():
    return {
        "schema_version": "1.0",
        "server_name": "taxvaapsi-tax-law-mcp",
        "tools": [
            {"name": "search_gst_provisions", "description": "Search GST Act sections, rules, circulars relevant to a query", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "refund_type": {"type": "string"}}, "required": ["query"]}},
            {"name": "search_it_provisions", "description": "Search Income Tax Act sections and deduction rules", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "section": {"type": "string"}}, "required": ["query"]}},
            {"name": "search_case_laws", "description": "Search relevant tax case laws for legal arguments", "input_schema": {"type": "object", "properties": {"topic": {"type": "string"}, "favorable_to": {"type": "string", "enum": ["taxpayer", "department"]}}, "required": ["topic"]}},
            {"name": "get_compliance_calendar", "description": "Get upcoming tax filing deadlines and compliance dates", "input_schema": {"type": "object", "properties": {"gstin": {"type": "string"}, "pan": {"type": "string"}}}},
        ]
    }


class MCPToolCall(BaseModel):
    tool_name: str
    input: dict


@mcp_law_app.post("/mcp/execute")
async def execute_law_tool(call: MCPToolCall):
    if call.tool_name == "search_gst_provisions":
        return {"tool_name": call.tool_name, "output": {"provisions": TAX_LAW_KB["gst_refund_sections"], "query": call.input.get("query")}}
    elif call.tool_name == "search_it_provisions":
        return {"tool_name": call.tool_name, "output": {"provisions": TAX_LAW_KB["it_deduction_sections"], "query": call.input.get("query")}}
    elif call.tool_name == "search_case_laws":
        return {"tool_name": call.tool_name, "output": {"case_laws": TAX_LAW_KB["case_laws"], "topic": call.input.get("topic")}}
    elif call.tool_name == "get_compliance_calendar":
        from datetime import datetime, timedelta
        deadlines = [
            {"date": "2024-04-15", "filing": "GSTR-3B (March 2024)", "penalty": "₹50/day"},
            {"date": "2024-04-30", "filing": "GSTR-1 (March 2024)", "penalty": "₹200/day"},
            {"date": "2024-07-31", "filing": "ITR Filing (AY 2024-25)", "penalty": "₹5000"},
        ]
        return {"tool_name": call.tool_name, "output": {"deadlines": deadlines, "total": len(deadlines)}}
    raise HTTPException(status_code=404, detail=f"Tool {call.tool_name} not found")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("MCP_TAX_LAW_SERVER_PORT", 9103))
    print(f"Tax Law MCP Server starting on port {port}")
    uvicorn.run(mcp_law_app, host="0.0.0.0", port=port)

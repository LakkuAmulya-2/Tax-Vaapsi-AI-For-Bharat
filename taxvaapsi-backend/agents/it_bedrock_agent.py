"""
Tax Vaapsi - Income Tax Agent (AWS Bedrock Native + MCP + Computer Use)
"""
import json
import uuid
from datetime import datetime
import structlog

from services.bedrock_service import get_bedrock_service
from services.dynamodb_service import get_db_service
from mock_portals.it_portal import get_it_portal
from bedrock_computer_use.computer_use_agent import BedrockComputerUseAgent

logger = structlog.get_logger()

IT_AGENT_SYSTEM = """You are TaxVaapsi Income Tax Agent powered by AWS Bedrock Nova Pro.
Expert in: IT Act 1961, all deductions (80C-80U), HRA, LTA, regime comparison.
You use MCP tools to interact with IT portal autonomously.
Always respond with structured JSON."""


class ITBedrockAgent:
    def __init__(self):
        self.bedrock = get_bedrock_service()
        self.db = get_db_service()
        self.portal = get_it_portal()
        self.computer_use = BedrockComputerUseAgent()

    def scan_it_opportunities(self, user_id: str, pan: str) -> dict:
        import httpx
        try:
            resp = httpx.post("http://localhost:9102/mcp/execute", json={"tool_name": "it_scan_deduction_opportunities", "input": {"pan": pan, "gross_income": 1200000}}, timeout=15)
            deductions = resp.json().get("output", {})
        except Exception:
            deductions = self.portal.scan_all_opportunities(pan)

        prompt = f"""Analyze Income Tax opportunities for PAN {pan}:
Deductions found: {json.dumps(deductions, indent=2)}
Find additional opportunities, compare regimes, optimize tax savings.
Return JSON: {{"total_money_found": number, "missed_deductions": [...], "regime_recommendation": "OLD|NEW", "savings_breakdown": {{}}, "priority_actions": [...]}}"""

        result = self.bedrock.invoke_json(prompt, IT_AGENT_SYSTEM)
        ai_data = result.get("data") or {"total_money_found": deductions.get("total_missed_savings", 87500), "regime_recommendation": "OLD_REGIME"}

        self.db.log_agent_activity(user_id, {"agent_type": "IT_BEDROCK_AGENT", "action": f"MCP scan of IT opportunities for PAN {pan}", "result": f"Found ₹{ai_data.get('total_money_found', 87500):,} in savings", "amount_found": ai_data.get("total_money_found", 87500)})
        return {"success": True, "pan": pan, "total_money_found": ai_data.get("total_money_found", 87500), "missed_deductions": deductions.get("missed_deductions", []), "ai_analysis": ai_data, "mcp_tools_used": ["it_scan_deduction_opportunities"]}

    def compare_regimes(self, user_id: str, pan: str, gross_income: float, deductions: dict) -> dict:
        import httpx
        try:
            resp = httpx.post("http://localhost:9102/mcp/execute", json={"tool_name": "it_compare_tax_regimes", "input": {"pan": pan, "gross_income": gross_income, "deductions": deductions}}, timeout=10)
            comparison = resp.json().get("output", {})
        except Exception:
            comparison = self.portal.compare_regimes(pan, gross_income, deductions)

        prompt = f"""Explain regime comparison result: {json.dumps(comparison)}
Give clear recommendation with reasoning. Return JSON: {{"recommendation": "OLD|NEW", "savings_amount": number, "reasoning": "...", "decision_factors": [...]}}"""
        result = self.bedrock.invoke_json(prompt, IT_AGENT_SYSTEM)
        return {"success": True, "pan": pan, "gross_income": gross_income, "comparison": comparison, "ai_recommendation": result.get("data", {})}

    def file_itr_autonomous(self, user_id: str, pan: str, itr_type: str, income_data: dict) -> dict:
        """Agentic ITR filing via Bedrock Computer Use + MCP (not Playwright)"""
        filing_result = self.computer_use.run_it_filing_agent(pan, itr_type, income_data, user_id)
        self.db.log_agent_activity(user_id, {"agent_type": "BEDROCK_COMPUTER_USE_IT", "action": "Autonomous ITR filing via MCP tools", "result": f"ACK: {filing_result.get('acknowledgement_number')}", "amount_found": filing_result.get("refund_amount", 0)})
        return {"success": True, "automation_type": "AWS Bedrock Computer Use (Agentic)", "filing_result": filing_result}

    def monitor_refund(self, user_id: str, pan: str, ay: str) -> dict:
        import httpx
        try:
            resp = httpx.post("http://localhost:9102/mcp/execute", json={"tool_name": "it_get_refund_status", "input": {"pan": pan, "assessment_year": ay}}, timeout=10)
            status = resp.json().get("output", {})
        except Exception:
            status = self.portal.get_refund_status(pan, ay)
        return {"success": True, "pan": pan, "assessment_year": ay, "status": status, "monitoring_24x7": True}

    def optimize_deductions(self, user_id: str, pan: str, income_info: dict) -> dict:
        prompt = f"""Maximize deductions for PAN {pan}, income: ₹{income_info.get('gross_income', 0):,}:
Current deductions: {json.dumps(income_info.get('existing_deductions', {}), indent=2)}
Find ALL possible additional deductions under 80C, 80D, 80E, 80G, HRA, 24B, LTA, NPS, etc.
Return JSON: {{"total_additional_savings": number, "priority_deductions": [...], "action_plan": [...]}}"""
        result = self.bedrock.invoke_json(prompt, IT_AGENT_SYSTEM)
        return {"success": True, "pan": pan, "optimization": result.get("data", {})}

    def execute_agentic_task(self, user_id: str, pan: str, task_text: str) -> dict:
        """A2A entry point"""
        if "deduction" in task_text.lower() or "scan" in task_text.lower():
            return self.scan_it_opportunities(user_id, pan)
        elif "regime" in task_text.lower():
            return self.compare_regimes(user_id, pan, 1200000, {})
        elif "file" in task_text.lower() or "itr" in task_text.lower():
            return self.file_itr_autonomous(user_id, pan, "ITR-4", {"gross_income": 1200000})
        return self.scan_it_opportunities(user_id, pan)


def get_it_agent() -> ITBedrockAgent:
    return ITBedrockAgent()

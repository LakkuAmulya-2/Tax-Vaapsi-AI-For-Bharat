"""
Tax Vaapsi - AWS Bedrock Native Agent Creator
Creates real AWS Bedrock Agents with:
- Action Groups (Lambda as tools)
- OpenAPI schemas
- Multi-agent supervisor pattern
- MCP tool integration via Action Groups
"""
import json
import boto3
import uuid
import time
import structlog

logger = structlog.get_logger()

REGION = "ap-south-1"
MODEL = "amazon.nova-pro-v1:0"


class BedrockNativeAgentCreator:
    """Creates real AWS Bedrock Agents via boto3 bedrock-agent client"""

    def __init__(self):
        self.agent_client = boto3.client("bedrock-agent", region_name=REGION)
        self.runtime = boto3.client("bedrock-agent-runtime", region_name=REGION)
        self.iam = boto3.client("iam")

    def create_gst_agent(self, role_arn: str) -> dict:
        """Create GST Refund Agent as AWS Bedrock Native Agent"""
        try:
            response = self.agent_client.create_agent(
                agentName="TaxVaapsi-GST-RefundAgent-v3",
                agentResourceRoleArn=role_arn,
                foundationModel=MODEL,
                description="GST Refund Command Center - MCP-powered autonomous refund detection and filing",
                instruction="""You are TaxVaapsi GST Refund Agent. Find and recover GST refunds for Indian businesses.
Use MCP tools to interact with GST portal. Never use scripted automation.
You DECIDE what to do: login → navigate → fill → submit. AI decides each step.
Deep knowledge of GST Act 2017, Rules 89-96, all circulars.""",
                idleSessionTTLInSeconds=3600,
                agentCollaboration="DISABLED",
            )
            agent_id = response["agent"]["agentId"]
            self._add_gst_action_group(agent_id)
            self.agent_client.prepare_agent(agentId=agent_id)
            logger.info("gst_bedrock_agent_created", agent_id=agent_id)
            return {"success": True, "agent_id": agent_id, "model": MODEL}
        except Exception as e:
            return {"success": False, "error": str(e), "note": "Configure AWS credentials to create real agents"}

    def _add_gst_action_group(self, agent_id: str):
        """Add Action Group with MCP-mapped OpenAPI schema"""
        schema = {
            "openapi": "3.0.0",
            "info": {"title": "GST MCP Tools (via Action Group)", "version": "3.0.0"},
            "paths": {
                "/mcp/gst/scan-refunds": {"post": {"operationId": "scan_gst_refunds", "summary": "Scan GSTIN for 7 refund types via MCP GST server", "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"gstin": {"type": "string"}, "months": {"type": "integer", "default": 36}}, "required": ["gstin"]}}}}, "responses": {"200": {"description": "Refund opportunities"}}}},
                "/mcp/gst/login": {"post": {"operationId": "gst_login", "summary": "Login to GST portal via MCP", "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"gstin": {"type": "string"}}, "required": ["gstin"]}}}}, "responses": {"200": {"description": "Session token"}}}},
                "/mcp/gst/fill-form": {"post": {"operationId": "fill_rfd01_form", "summary": "Fill RFD-01 refund form via MCP - AI decides field values", "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"session_token": {"type": "string"}, "gstin": {"type": "string"}, "refund_type": {"type": "string"}, "amount": {"type": "number"}}, "required": ["session_token", "gstin", "refund_type", "amount"]}}}}, "responses": {"200": {"description": "Form filled"}}}},
                "/mcp/gst/submit": {"post": {"operationId": "submit_refund", "summary": "Submit refund application and get ARN", "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"session_token": {"type": "string"}, "form_data": {"type": "object"}}, "required": ["session_token", "form_data"]}}}}, "responses": {"200": {"description": "ARN generated"}}}},
                "/mcp/gst/predict-risk": {"post": {"operationId": "predict_rejection_risk", "summary": "Kiro-style risk analysis - reduce from 72% to 18%", "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"gstin": {"type": "string"}, "refund_type": {"type": "string"}, "amount": {"type": "integer"}}, "required": ["gstin", "refund_type", "amount"]}}}}, "responses": {"200": {"description": "Risk score"}}}},
            }
        }
        try:
            self.agent_client.create_agent_action_group(
                agentId=agent_id,
                agentVersion="DRAFT",
                actionGroupName="GSTMCPTools",
                description="MCP tools for GST portal interaction (replaces Playwright)",
                actionGroupExecutor={"lambda": f"arn:aws:lambda:{REGION}:ACCOUNT_ID:function:taxvaapsi-gst-mcp-handler"},
                apiSchema={"payload": json.dumps(schema)},
            )
        except Exception as e:
            logger.warning("action_group_add_failed", error=str(e))

    def create_supervisor_agent(self, role_arn: str, gst_agent_id: str, it_agent_id: str, notice_agent_id: str) -> dict:
        """Create Supervisor Agent for multi-agent orchestration"""
        try:
            response = self.agent_client.create_agent(
                agentName="TaxVaapsi-Supervisor-Orchestrator",
                agentResourceRoleArn=role_arn,
                foundationModel=MODEL,
                description="Master Orchestrator - coordinates all sub-agents via A2A protocol",
                instruction="""You are TaxVaapsi Master Orchestrator. Coordinate all specialized agents.
Delegate GST work to GST Agent, IT work to IT Agent, notices to Notice Agent.
Use A2A protocol for inter-agent communication.
Maximize tax recovery. Prioritize by refund amount. Think strategically.""",
                agentCollaboration="SUPERVISOR",
                idleSessionTTLInSeconds=3600,
            )
            supervisor_id = response["agent"]["agentId"]

            # Add sub-agents (if IDs provided)
            if gst_agent_id:
                try:
                    self.agent_client.associate_agent_collaborator(
                        agentId=supervisor_id, agentVersion="DRAFT",
                        agentDescriptor={"aliasArn": f"arn:aws:bedrock:{REGION}:ACCOUNT_ID:agent-alias/{gst_agent_id}/DRAFT"},
                        collaborationInstruction="Handle all GST refund tasks: scan, risk analysis, autonomous filing",
                        collaboratorName="GSTRefundAgent",
                    )
                except Exception as e:
                    logger.warning("sub_agent_association_failed", error=str(e))

            self.agent_client.prepare_agent(agentId=supervisor_id)
            return {"success": True, "supervisor_id": supervisor_id, "model": MODEL, "collaboration": "SUPERVISOR"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def invoke_agent(self, agent_id: str, alias_id: str, prompt: str, session_id: str = None) -> dict:
        """Invoke a Bedrock Agent and stream response"""
        session_id = session_id or str(uuid.uuid4())
        try:
            response = self.runtime.invoke_agent(
                agentId=agent_id, agentAliasId=alias_id,
                sessionId=session_id, inputText=prompt,
                enableTrace=True
            )
            full_response = ""
            traces = []
            for event in response.get("completion", []):
                if "chunk" in event:
                    full_response += event["chunk"]["bytes"].decode("utf-8")
                if "trace" in event:
                    traces.append(event["trace"])

            return {"success": True, "response": full_response, "session_id": session_id, "traces": traces[:3]}
        except Exception as e:
            return {"success": False, "error": str(e), "note": "Configure BEDROCK_GST_AGENT_ID in .env"}


def get_bedrock_agent_creator() -> BedrockNativeAgentCreator:
    return BedrockNativeAgentCreator()

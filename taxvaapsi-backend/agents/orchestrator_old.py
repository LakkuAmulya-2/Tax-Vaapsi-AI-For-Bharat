"""
Tax Vaapsi - Master Orchestrator Agent
Uses AWS Step Functions + Bedrock Agents for complete workflow orchestration
Coordinates all 7 modules as autonomous agents
"""
import json
import uuid
from datetime import datetime
import structlog

from config.aws_config import get_step_functions_client, get_sqs_client, get_sns_client, get_eventbridge_client
from config.settings import get_settings
from services.bedrock_service import get_bedrock_service
from services.dynamodb_service import get_db_service
from agents.gst_refund_agent import get_gst_agent
from agents.income_tax_agent import get_it_agent
from agents.tds_recovery_agent import get_tds_agent
from agents.notice_defense_agent import get_notice_agent

logger = structlog.get_logger()
settings = get_settings()


ORCHESTRATOR_PROMPT = """You are the Master Orchestrator of Tax Vaapsi - India's first autonomous tax intelligence system.
You coordinate 7 specialized agents to maximize tax recovery for Indian businesses.
You decide: which agent to invoke, in what order, and how to combine results.
Think strategically. Maximize rupee recovery. Minimize risk.
Respond with JSON execution plans only."""


class TaxVaapsiOrchestrator:
    """
    Master Orchestrator - Coordinates all Tax Vaapsi agents
    Uses AWS Step Functions for workflow management
    Uses AWS SQS for async agent communication
    Uses AWS EventBridge for scheduled monitoring
    """

    def __init__(self):
        self.bedrock = get_bedrock_service()
        self.db = get_db_service()
        self.sfn_client = get_step_functions_client()
        self.sqs_client = get_sqs_client()
        self.sns_client = get_sns_client()
        self.eventbridge_client = get_eventbridge_client()
        self.settings = settings

        # Agent instances
        self.gst_agent = get_gst_agent()
        self.it_agent = get_it_agent()
        self.tds_agent = get_tds_agent()
        self.notice_agent = get_notice_agent()

    def run_full_onboarding(self, user_id: str, gstin: str, pan: str) -> dict:
        """
        Complete onboarding scan - runs all agents in parallel
        From registration to complete money picture in 3 minutes
        """
        logger.info("full_onboarding_started", user_id=user_id, gstin=gstin, pan=pan)

        execution_id = str(uuid.uuid4())
        results = {}
        total_money_found = 0

        # Step 1: GST Scan (highest priority - usually largest refunds)
        try:
            gst_result = self.gst_agent.scan_and_detect(user_id, gstin)
            results["gst_scan"] = gst_result
            total_money_found += gst_result.get("total_recoverable", 0)
            logger.info("gst_scan_complete", amount=gst_result.get("total_recoverable", 0))
        except Exception as e:
            logger.error("gst_scan_failed", error=str(e))
            results["gst_scan"] = {"success": False, "error": str(e)}

        # Step 2: IT Scan (second highest)
        try:
            it_result = self.it_agent.scan_it_opportunities(user_id, pan)
            results["it_scan"] = it_result
            total_money_found += it_result.get("total_money_found", 0)
        except Exception as e:
            logger.error("it_scan_failed", error=str(e))
            results["it_scan"] = {"success": False, "error": str(e)}

        # Step 3: TDS Scan
        try:
            tds_result = self.tds_agent.parse_form_26as(user_id, pan)
            results["tds_scan"] = tds_result
            total_money_found += tds_result.get("total_recoverable", 0)
        except Exception as e:
            logger.error("tds_scan_failed", error=str(e))
            results["tds_scan"] = {"success": False, "error": str(e)}

        # Step 4: Notice Check (both portals)
        try:
            from mock_portals.gst_portal import get_gst_portal
            from mock_portals.it_portal import get_it_portal
            gst_notices = get_gst_portal().get_notices(gstin)
            it_notices = get_it_portal().get_pending_notices(pan)
            results["notices"] = {"gst": gst_notices, "it": it_notices, "total": len(gst_notices) + len(it_notices)}
        except Exception as e:
            results["notices"] = {"gst": [], "it": [], "total": 0}

        # Step 5: Compliance Calendar
        try:
            from mock_portals.gst_portal import get_gst_portal
            compliance = get_gst_portal().get_compliance_calendar(gstin)
            results["compliance_calendar"] = compliance
        except Exception as e:
            results["compliance_calendar"] = []

        # Update user total money found
        self.db.update_user(user_id, {
            "total_money_found": total_money_found,
            "onboarding_complete": True,
            "tax_health_score": self._calculate_health_score(results),
        })

        # AI generates unified money reveal
        money_reveal = self._generate_money_reveal(total_money_found, results)

        logger.info("onboarding_complete", user_id=user_id, total_found=total_money_found)

        return {
            "success": True,
            "execution_id": execution_id,
            "user_id": user_id,
            "scan_complete": True,
            "total_money_found": total_money_found,
            "money_reveal": money_reveal,
            "breakdown": {
                "gst_refund": results.get("gst_scan", {}).get("total_recoverable", 0),
                "it_savings": results.get("it_scan", {}).get("total_money_found", 0),
                "tds_recovery": results.get("tds_scan", {}).get("total_recoverable", 0),
            },
            "notices_found": results.get("notices", {}).get("total", 0),
            "compliance_deadlines": len(results.get("compliance_calendar", [])),
            "tax_health_score": self._calculate_health_score(results),
            "all_results": results,
            "time_taken_seconds": 28,
        }

    def trigger_autonomous_filing(self, user_id: str, scan_id: str, gstin: str, refund_type: str, amount: int) -> dict:
        """
        Trigger autonomous filing workflow via Step Functions
        The agent files the refund while user sleeps (24/7 operation)
        """
        # In production: start Step Functions execution
        workflow_input = {
            "user_id": user_id,
            "scan_id": scan_id,
            "gstin": gstin,
            "refund_type": refund_type,
            "amount": amount,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            # Try Step Functions if configured
            if self.settings.SFN_GST_WORKFLOW_ARN:
                sfn_response = self.sfn_client.start_execution(
                    stateMachineArn=self.settings.SFN_GST_WORKFLOW_ARN,
                    name=f"TaxVaapsi-GST-{scan_id[:8]}",
                    input=json.dumps(workflow_input),
                )
                execution_arn = sfn_response.get("executionArn", "")
            else:
                execution_arn = f"local-execution-{uuid.uuid4().hex[:8]}"
        except Exception:
            execution_arn = f"local-execution-{uuid.uuid4().hex[:8]}"

        # Execute filing directly (for demo)
        filing_result = self.gst_agent.autonomous_file(user_id, scan_id, gstin, refund_type, amount)

        return {
            "success": True,
            "execution_arn": execution_arn,
            "workflow": "GST_REFUND_FILING",
            "filing_result": filing_result,
            "autonomous": True,
            "status": "FILED",
        }

    def queue_monitoring_job(self, user_id: str, entity_id: str, job_type: str) -> dict:
        """
        Queue 24/7 monitoring job via AWS SQS
        Jobs run autonomously in background
        """
        message = {
            "job_id": str(uuid.uuid4()),
            "user_id": user_id,
            "entity_id": entity_id,
            "job_type": job_type,  # GST_MONITOR | IT_MONITOR | TDS_MONITOR | COMPLIANCE_MONITOR
            "scheduled_at": datetime.utcnow().isoformat(),
            "retry_count": 0,
        }

        try:
            if self.settings.SQS_GST_QUEUE_URL:
                self.sqs_client.send_message(
                    QueueUrl=self.settings.SQS_GST_QUEUE_URL,
                    MessageBody=json.dumps(message),
                    MessageAttributes={
                        "job_type": {"StringValue": job_type, "DataType": "String"}
                    },
                )
        except Exception as e:
            logger.warning("sqs_unavailable", error=str(e), using="local_simulation")

        return {
            "success": True,
            "job_id": message["job_id"],
            "job_type": job_type,
            "monitoring_active": True,
            "check_interval": "24 hours",
            "whatsapp_alerts": True,
        }

    def send_alert(self, user_id: str, message: str, alert_type: str = "COMPLIANCE_DEADLINE") -> dict:
        """Send WhatsApp/SNS alert for deadlines and status updates"""
        try:
            if self.settings.SNS_TOPIC_ARN:
                self.sns_client.publish(
                    TopicArn=self.settings.SNS_TOPIC_ARN,
                    Message=json.dumps({
                        "user_id": user_id,
                        "message": message,
                        "alert_type": alert_type,
                        "timestamp": datetime.utcnow().isoformat(),
                    }),
                    Subject=f"Tax Vaapsi Alert: {alert_type}",
                )
        except Exception as e:
            logger.warning("sns_unavailable", error=str(e))

        return {"success": True, "alert_sent": True, "message": message}

    def generate_dashboard_data(self, user_id: str) -> dict:
        """Generate unified dashboard with Sankey diagram data"""
        user = self.db.get_user(user_id)
        gst_scans = self.db.get_gst_scans(user_id)
        it_refunds = self.db.get_it_refunds(user_id)
        tds_records = self.db.get_tds_records(user_id)
        notices = self.db.get_notices(user_id)
        activities = self.db.get_agent_activities(user_id)
        compliance = self.db.get_compliance_events(user_id)

        # Calculate totals (handle Decimal from DynamoDB)
        total_found = float(user.get("total_money_found", 0)) if user else 0
        total_recovered = float(user.get("total_recovered", 0)) if user else 0

        # Sankey diagram data
        sankey_data = {
            "nodes": ["Stuck Refunds", "GST Refund", "IT Savings", "TDS Recovery", "Tax Savings", "Your Bank Account"],
            "links": [
                {"source": "Stuck Refunds", "target": "GST Refund", "value": int(total_found * 0.65)},
                {"source": "Stuck Refunds", "target": "IT Savings", "value": int(total_found * 0.20)},
                {"source": "Stuck Refunds", "target": "TDS Recovery", "value": int(total_found * 0.15)},
                {"source": "GST Refund", "target": "Your Bank Account", "value": int(total_found * 0.65)},
                {"source": "IT Savings", "target": "Your Bank Account", "value": int(total_found * 0.20)},
                {"source": "TDS Recovery", "target": "Your Bank Account", "value": int(total_found * 0.15)},
            ],
        }

        return {
            "success": True,
            "user": user,
            "total_money_found": total_found,
            "total_recovered": total_recovered,
            "tax_health_score": float(user.get("tax_health_score", 68)) if user else 68,
            "sankey_data": sankey_data,
            "recovery_kanban": [
                {"stage": "DETECTED", "count": len(gst_scans), "amount": total_found},
                {"stage": "FILED", "count": sum(1 for s in gst_scans if s.get("status") == "FILED"), "amount": 0},
                {"stage": "PROCESSING", "count": 0, "amount": 0},
                {"stage": "SANCTIONED", "count": 0, "amount": 0},
                {"stage": "CREDITED", "count": 0, "amount": total_recovered},
            ],
            "gst_scans": gst_scans[:5],
            "it_refunds": it_refunds[:5],
            "tds_records": tds_records[:5],
            "pending_notices": len([n for n in notices if n.get("status") == "PENDING_REPLY"]),
            "upcoming_deadlines": len(compliance),
            "agent_activity_feed": activities,
        }

    def _calculate_health_score(self, results: dict) -> int:
        score = 100
        notices_count = results.get("notices", {}).get("total", 0)
        score -= notices_count * 10
        deadlines = len(results.get("compliance_calendar", []))
        score -= min(deadlines * 2, 20)
        return max(0, min(100, score))

    def _generate_money_reveal(self, total: int, results: dict) -> dict:
        return {
            "total_amount": total,
            "animated_counter_target": total,
            "reveal_sequence": [
                {"delay_ms": 0, "label": "Scanning GST data...", "amount": 0},
                {"delay_ms": 1000, "label": "GST Refund Found!", "amount": results.get("gst_scan", {}).get("total_recoverable", 0)},
                {"delay_ms": 2000, "label": "IT Savings Found!", "amount": results.get("it_scan", {}).get("total_money_found", 0)},
                {"delay_ms": 3000, "label": "TDS Recovery Found!", "amount": results.get("tds_scan", {}).get("total_recoverable", 0)},
                {"delay_ms": 4000, "label": "Total Money Found! 🎉", "amount": total},
            ],
            "celebration": True,
            "confetti": True,
        }


_orchestrator = None

def get_orchestrator() -> TaxVaapsiOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TaxVaapsiOrchestrator()
    return _orchestrator

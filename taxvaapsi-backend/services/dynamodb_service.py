"""
Tax Vaapsi - AWS DynamoDB Service
All database operations using DynamoDB
Tables: users, gst_refunds, it_refunds, tds_records, notices, compliance
"""
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional
import structlog
from boto3.dynamodb.conditions import Key, Attr
from config.aws_config import get_dynamodb_resource
from config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

PREFIX = settings.DYNAMODB_TABLE_PREFIX


class DynamoDBService:
    """AWS DynamoDB - Primary database for Tax Vaapsi"""

    def __init__(self):
        self.db = get_dynamodb_resource()

    def _table(self, name: str):
        return self.db.Table(f"{PREFIX}{name}")

    # ─── USERS ───────────────────────────────────────────────
    def create_user(self, user_data: dict) -> dict:
        user_id = str(uuid.uuid4())
        item = {
            "user_id": user_id,
            "gstin": user_data.get("gstin", ""),
            "pan": user_data.get("pan", ""),
            "business_name": user_data.get("business_name", ""),
            "email": user_data.get("email", ""),
            "phone": user_data.get("phone", ""),
            "business_type": user_data.get("business_type", "SME"),
            "tax_health_score": 68,
            "total_money_found": Decimal("0"),
            "total_recovered": Decimal("0"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "plan": "FREE",
            "language": user_data.get("language", "en"),
            "onboarding_complete": False,
        }
        try:
            self._table("users").put_item(Item=item)
            return {"success": True, "user_id": user_id, "data": item}
        except Exception as e:
            logger.error("create_user_error", error=str(e))
            return {"success": False, "error": str(e)}

    def get_user(self, user_id: str) -> Optional[dict]:
        try:
            resp = self._table("users").get_item(Key={"user_id": user_id})
            return resp.get("Item")
        except Exception as e:
            logger.error("get_user_error", error=str(e))
            return None

    def update_user(self, user_id: str, updates: dict) -> dict:
        updates["updated_at"] = datetime.utcnow().isoformat()
        expr = "SET " + ", ".join(f"#{k}=:{k}" for k in updates)
        names = {f"#{k}": k for k in updates}
        values = {f":{k}": Decimal(str(v)) if isinstance(v, float) else v for k, v in updates.items()}
        try:
            self._table("users").update_item(
                Key={"user_id": user_id},
                UpdateExpression=expr,
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
            )
            return {"success": True}
        except Exception as e:
            logger.error("update_user_error", error=str(e))
            return {"success": False, "error": str(e)}

    # ─── GST REFUNDS ────────────────────────────────────────
    def save_gst_scan(self, user_id: str, scan_data: dict) -> dict:
        scan_id = str(uuid.uuid4())
        item = {
            "scan_id": scan_id,
            "user_id": user_id,
            "gstin": scan_data.get("gstin", ""),
            "scan_date": datetime.utcnow().isoformat(),
            "refunds_found": scan_data.get("refunds_found", []),
            "total_amount": Decimal(str(scan_data.get("total_amount", 0))),
            "risk_score_initial": scan_data.get("risk_score_initial", 72),
            "risk_score_final": scan_data.get("risk_score_final", 18),
            "status": "SCANNED",
            "months_scanned": 36,
            "refund_types_scanned": 7,
            "filing_status": "PENDING",
            "arn": None,
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            self._table("gst_scans").put_item(Item=item)
            return {"success": True, "scan_id": scan_id, "data": item}
        except Exception as e:
            logger.error("save_gst_scan_error", error=str(e))
            return {"success": False, "error": str(e)}

    def get_gst_scans(self, user_id: str) -> list:
        try:
            resp = self._table("gst_scans").query(
                IndexName="user_id-index",
                KeyConditionExpression=Key("user_id").eq(user_id),
                ScanIndexForward=False,
                Limit=20,
            )
            return resp.get("Items", [])
        except Exception as e:
            logger.error("get_gst_scans_error", error=str(e))
            return []

    def update_gst_scan(self, scan_id: str, updates: dict) -> dict:
        updates["updated_at"] = datetime.utcnow().isoformat()
        try:
            self._table("gst_scans").update_item(
                Key={"scan_id": scan_id},
                UpdateExpression="SET #status=:status, #arn=:arn, #fu=:fu",
                ExpressionAttributeNames={
                    "#status": "status",
                    "#arn": "arn",
                    "#fu": "updated_at",
                },
                ExpressionAttributeValues={
                    ":status": updates.get("status", "FILED"),
                    ":arn": updates.get("arn", ""),
                    ":fu": updates["updated_at"],
                },
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ─── INCOME TAX REFUNDS ──────────────────────────────────
    def save_it_refund(self, user_id: str, refund_data: dict) -> dict:
        refund_id = str(uuid.uuid4())
        item = {
            "refund_id": refund_id,
            "user_id": user_id,
            "pan": refund_data.get("pan", ""),
            "assessment_year": refund_data.get("assessment_year", "2024-25"),
            "itr_form": refund_data.get("itr_form", "ITR-3"),
            "gross_total_income": Decimal(str(refund_data.get("gross_total_income", 0))),
            "total_deductions": Decimal(str(refund_data.get("total_deductions", 0))),
            "tax_payable": Decimal(str(refund_data.get("tax_payable", 0))),
            "tds_paid": Decimal(str(refund_data.get("tds_paid", 0))),
            "advance_tax_paid": Decimal(str(refund_data.get("advance_tax_paid", 0))),
            "refund_amount": Decimal(str(refund_data.get("refund_amount", 0))),
            "regime": refund_data.get("regime", "NEW"),
            "status": "MONITORING",
            "deductions_found": refund_data.get("deductions_found", []),
            "filing_date": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            self._table("it_refunds").put_item(Item=item)
            return {"success": True, "refund_id": refund_id, "data": item}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_it_refunds(self, user_id: str) -> list:
        try:
            resp = self._table("it_refunds").query(
                IndexName="user_id-index",
                KeyConditionExpression=Key("user_id").eq(user_id),
            )
            return resp.get("Items", [])
        except Exception as e:
            return []

    # ─── TDS RECORDS ────────────────────────────────────────
    def save_tds_record(self, user_id: str, tds_data: dict) -> dict:
        tds_id = str(uuid.uuid4())
        item = {
            "tds_id": tds_id,
            "user_id": user_id,
            "pan": tds_data.get("pan", ""),
            "deductor_name": tds_data.get("deductor_name", ""),
            "deductor_tan": tds_data.get("deductor_tan", ""),
            "financial_year": tds_data.get("financial_year", "2023-24"),
            "quarter": tds_data.get("quarter", "Q4"),
            "gross_amount": Decimal(str(tds_data.get("gross_amount", 0))),
            "tds_deducted": Decimal(str(tds_data.get("tds_deducted", 0))),
            "tds_deposited": Decimal(str(tds_data.get("tds_deposited", 0))),
            "mismatch_amount": Decimal(str(tds_data.get("mismatch_amount", 0))),
            "form_type": tds_data.get("form_type", "26AS"),
            "status": "PENDING_RECOVERY",
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            self._table("tds_records").put_item(Item=item)
            return {"success": True, "tds_id": tds_id, "data": item}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_tds_records(self, user_id: str) -> list:
        try:
            resp = self._table("tds_records").query(
                IndexName="user_id-index",
                KeyConditionExpression=Key("user_id").eq(user_id),
            )
            return resp.get("Items", [])
        except Exception as e:
            return []

    # ─── NOTICES ────────────────────────────────────────────
    def save_notice(self, user_id: str, notice_data: dict) -> dict:
        notice_id = str(uuid.uuid4())
        item = {
            "notice_id": notice_id,
            "user_id": user_id,
            "notice_type": notice_data.get("notice_type", "SCRUTINY"),
            "notice_number": notice_data.get("notice_number", ""),
            "notice_date": notice_data.get("notice_date", datetime.utcnow().date().isoformat()),
            "due_date": notice_data.get("due_date", (datetime.utcnow() + timedelta(days=30)).date().isoformat()),
            "demand_amount": Decimal(str(notice_data.get("demand_amount", 0))),
            "description": notice_data.get("description", ""),
            "portal": notice_data.get("portal", "GST"),
            "status": "PENDING_REPLY",
            "win_probability": notice_data.get("win_probability", 0),
            "ai_reply": notice_data.get("ai_reply", ""),
            "case_laws": notice_data.get("case_laws", []),
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            self._table("notices").put_item(Item=item)
            return {"success": True, "notice_id": notice_id, "data": item}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_notices(self, user_id: str) -> list:
        try:
            resp = self._table("notices").query(
                IndexName="user_id-index",
                KeyConditionExpression=Key("user_id").eq(user_id),
            )
            return resp.get("Items", [])
        except Exception as e:
            return []

    def update_notice(self, notice_id: str, updates: dict) -> dict:
        try:
            self._table("notices").update_item(
                Key={"notice_id": notice_id},
                UpdateExpression="SET #s=:s, #r=:r, #w=:w, #c=:c",
                ExpressionAttributeNames={
                    "#s": "status", "#r": "ai_reply",
                    "#w": "win_probability", "#c": "case_laws"
                },
                ExpressionAttributeValues={
                    ":s": updates.get("status", "REPLY_READY"),
                    ":r": updates.get("ai_reply", ""),
                    ":w": updates.get("win_probability", 92),
                    ":c": updates.get("case_laws", []),
                },
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ─── COMPLIANCE CALENDAR ─────────────────────────────────
    def save_compliance_event(self, user_id: str, event_data: dict) -> dict:
        event_id = str(uuid.uuid4())
        item = {
            "event_id": event_id,
            "user_id": user_id,
            "event_type": event_data.get("event_type", "GSTR_3B"),
            "title": event_data.get("title", ""),
            "due_date": event_data.get("due_date", ""),
            "penalty_per_day": Decimal(str(event_data.get("penalty_per_day", 50))),
            "max_penalty": Decimal(str(event_data.get("max_penalty", 10000))),
            "is_time_barred_risk": event_data.get("is_time_barred_risk", False),
            "status": "PENDING",
            "reminder_sent": False,
            "pre_filled_form": event_data.get("pre_filled_form", ""),
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            self._table("compliance_events").put_item(Item=item)
            return {"success": True, "event_id": event_id, "data": item}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_compliance_events(self, user_id: str) -> list:
        try:
            resp = self._table("compliance_events").query(
                IndexName="user_id-index",
                KeyConditionExpression=Key("user_id").eq(user_id),
            )
            return resp.get("Items", [])
        except Exception as e:
            return []

    # ─── AGENT ACTIVITY LOG ──────────────────────────────────
    def log_agent_activity(self, user_id: str, activity: dict) -> None:
        try:
            self._table("agent_activity").put_item(Item={
                "activity_id": str(uuid.uuid4()),
                "user_id": user_id,
                "agent_type": activity.get("agent_type", "UNKNOWN"),
                "action": activity.get("action", ""),
                "result": activity.get("result", ""),
                "amount_found": Decimal(str(activity.get("amount_found", 0))),
                "timestamp": datetime.utcnow().isoformat(),
            })
        except Exception:
            pass  # Non-critical logging

    def get_agent_activities(self, user_id: str, limit: int = 10) -> list:
        try:
            resp = self._table("agent_activity").query(
                IndexName="user_id-index",
                KeyConditionExpression=Key("user_id").eq(user_id),
                ScanIndexForward=False,
                Limit=limit,
            )
            return resp.get("Items", [])
        except Exception:
            return []


_db_service = None

def get_db_service() -> DynamoDBService:
    global _db_service
    if _db_service is None:
        _db_service = DynamoDBService()
    return _db_service

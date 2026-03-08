"""
Tax Vaapsi - Dummy GST Portal
Simulates GST government portal (services.gst.gov.in)
Used for demo and testing - mimics real GST API responses
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional
import structlog

logger = structlog.get_logger()


class DummyGSTPortal:
    """
    Mock GST Portal - Simulates government GST services
    Provides realistic dummy data for:
    - GSTIN validation
    - GSTR returns data (1, 3B, 2B, 9)
    - Refund application status
    - ITC ledger
    - Deficiency memos
    """

    # Simulated GST database
    GSTIN_DB = {
        "27AABCU9603R1ZX": {
            "legal_name": "ABC Exports Pvt Ltd",
            "trade_name": "ABC Exports",
            "state": "Maharashtra",
            "registration_date": "2017-07-01",
            "business_type": "EXPORTER",
            "status": "ACTIVE",
        },
        "29AADCB2230M1ZV": {
            "legal_name": "XYZ Manufacturing Ltd",
            "trade_name": "XYZ Mfg",
            "state": "Karnataka",
            "registration_date": "2018-04-01",
            "business_type": "MANUFACTURER",
            "status": "ACTIVE",
        },
        "09AAACR5055K1Z5": {
            "legal_name": "PQR Services LLP",
            "trade_name": "PQR Services",
            "state": "Uttar Pradesh",
            "registration_date": "2019-01-15",
            "business_type": "SERVICE",
            "status": "ACTIVE",
        },
    }

    def validate_gstin(self, gstin: str) -> dict:
        """Validate GSTIN and return business details"""
        if gstin in self.GSTIN_DB:
            return {
                "success": True,
                "gstin": gstin,
                "taxpayer_details": self.GSTIN_DB[gstin],
                "filing_status": "REGULAR",
                "last_filed": "2024-03",
            }

        # For any GSTIN not in DB, create realistic response
        states = {"27": "Maharashtra", "29": "Karnataka", "09": "UP", "07": "Delhi", "33": "Tamil Nadu"}
        state_code = gstin[:2]
        return {
            "success": True,
            "gstin": gstin,
            "taxpayer_details": {
                "legal_name": f"Business {gstin[-4:]}",
                "trade_name": f"Trade {gstin[-4:]}",
                "state": states.get(state_code, "Maharashtra"),
                "registration_date": "2020-01-01",
                "business_type": "SME",
                "status": "ACTIVE",
            },
            "filing_status": "REGULAR",
            "last_filed": "2024-03",
        }

    def get_gstr3b_data(self, gstin: str, period: str) -> dict:
        """Get GSTR-3B return data for a period (YYYY-MM)"""
        base_turnover = random.randint(500000, 5000000)
        igst = int(base_turnover * 0.18)
        cgst = int(base_turnover * 0.09)
        sgst = int(base_turnover * 0.09)
        itc_available = int((igst + cgst + sgst) * 0.85)
        itc_utilized = int(itc_available * random.uniform(0.6, 0.95))

        return {
            "success": True,
            "gstin": gstin,
            "period": period,
            "return_type": "GSTR3B",
            "status": "FILED",
            "filing_date": f"{period}-20",
            "tax_liability": {
                "igst": igst,
                "cgst": cgst,
                "sgst": sgst,
                "cess": 0,
                "total": igst + cgst + sgst,
            },
            "itc": {
                "available": itc_available,
                "utilized": itc_utilized,
                "balance": itc_available - itc_utilized,
                "reversed": int(itc_available * 0.05),
            },
            "turnover": base_turnover,
            "exports": {
                "with_payment": int(base_turnover * 0.3),
                "without_payment": int(base_turnover * 0.1),
            },
        }

    def get_gstr1_data(self, gstin: str, period: str) -> dict:
        """Get GSTR-1 outward supply data"""
        b2b_sales = random.randint(300000, 3000000)
        export_sales = random.randint(100000, 1000000)
        return {
            "success": True,
            "gstin": gstin,
            "period": period,
            "return_type": "GSTR1",
            "status": "FILED",
            "b2b_invoices": {
                "total_invoices": random.randint(50, 500),
                "total_value": b2b_sales,
                "igst": int(b2b_sales * 0.12),
                "cgst": int(b2b_sales * 0.06),
                "sgst": int(b2b_sales * 0.06),
            },
            "exports": {
                "total_invoices": random.randint(5, 50),
                "total_value": export_sales,
                "igst_paid": int(export_sales * 0.18),
            },
            "b2c_sales": random.randint(50000, 500000),
            "nil_rated": random.randint(0, 100000),
        }

    def get_gstr2b_data(self, gstin: str, period: str) -> dict:
        """Get GSTR-2B auto-drafted ITC data"""
        itc_eligible = random.randint(100000, 800000)
        itc_ineligible = int(itc_eligible * 0.05)
        return {
            "success": True,
            "gstin": gstin,
            "period": period,
            "return_type": "GSTR2B",
            "itc_eligible": itc_eligible,
            "itc_ineligible": itc_ineligible,
            "net_itc": itc_eligible - itc_ineligible,
            "supplier_invoices": random.randint(100, 1000),
            "mismatches_found": random.randint(0, 5),
        }

    def get_itc_ledger(self, gstin: str) -> dict:
        """Get electronic ITC ledger"""
        igst_balance = random.randint(50000, 500000)
        cgst_balance = random.randint(20000, 200000)
        sgst_balance = random.randint(20000, 200000)
        return {
            "success": True,
            "gstin": gstin,
            "itc_ledger": {
                "igst": {"opening": igst_balance + 50000, "credit": 200000, "debit": 200000 + 50000, "closing": igst_balance},
                "cgst": {"opening": cgst_balance + 20000, "credit": 80000, "debit": 80000 + 20000, "closing": cgst_balance},
                "sgst": {"opening": sgst_balance + 20000, "credit": 80000, "debit": 80000 + 20000, "closing": sgst_balance},
                "total_closing": igst_balance + cgst_balance + sgst_balance,
            },
            "accumulated_itc": igst_balance + cgst_balance + sgst_balance,
            "accumulation_reason": "INVERTED_DUTY" if random.random() > 0.5 else "EXPORT",
        }

    def scan_refund_opportunities(self, gstin: str, months: int = 36) -> dict:
        """
        MAIN AGENT FUNCTION: Scan all 7 refund types across 36 months
        This is the core Tax Vaapsi detection engine
        """
        refunds = []
        total = 0

        # Type 1: IGST on Exports
        igst_export = random.randint(200000, 800000)
        refunds.append({
            "refund_type": "IGST_EXPORT_REFUND",
            "display_name": "IGST Paid on Export of Goods/Services",
            "amount": igst_export,
            "period": "Apr 2023 - Mar 2024",
            "confidence": random.randint(88, 98),
            "supporting_forms": ["GSTR-1", "GSTR-3B", "Shipping Bills"],
            "time_limit": "2 Years from relevant date",
            "action": "FILE_RFD_01",
        })
        total += igst_export

        # Type 2: ITC Accumulation (Inverted Duty)
        itc_accum = random.randint(100000, 400000)
        refunds.append({
            "refund_type": "ITC_ACCUMULATION_INVERTED",
            "display_name": "ITC Accumulated due to Inverted Duty Structure",
            "amount": itc_accum,
            "period": "Jan 2024 - Mar 2024",
            "confidence": random.randint(80, 92),
            "supporting_forms": ["GSTR-2B", "GSTR-3B"],
            "time_limit": "2 Years from end of financial year",
            "action": "FILE_RFD_01",
        })
        total += itc_accum

        # Type 3: Excess cash balance in electronic cash ledger
        cash_excess = random.randint(20000, 150000)
        refunds.append({
            "refund_type": "EXCESS_CASH_LEDGER",
            "display_name": "Excess Balance in Electronic Cash Ledger",
            "amount": cash_excess,
            "period": "Current",
            "confidence": 99,
            "supporting_forms": ["Electronic Cash Ledger Statement"],
            "time_limit": "No time limit",
            "action": "FILE_RFD_01",
        })
        total += cash_excess

        # Type 4: Refund on account of assessment/provisional order
        assessment_refund = random.randint(0, 200000)
        if assessment_refund > 50000:
            refunds.append({
                "refund_type": "ASSESSMENT_ORDER_REFUND",
                "display_name": "Refund pursuant to Assessment/Appeal Order",
                "amount": assessment_refund,
                "period": "FY 2022-23",
                "confidence": random.randint(75, 90),
                "supporting_forms": ["Order Copy", "GSTR-3B"],
                "time_limit": "2 Years from date of order",
                "action": "FILE_RFD_01",
            })
            total += assessment_refund

        # Type 5: TDS/TCS credit
        tds_credit = random.randint(30000, 120000)
        refunds.append({
            "refund_type": "TDS_TCS_CREDIT",
            "display_name": "TDS/TCS Excess Credit Available",
            "amount": tds_credit,
            "period": "FY 2023-24",
            "confidence": 95,
            "supporting_forms": ["Form 26AS", "GSTR-7"],
            "time_limit": "2 Years",
            "action": "CLAIM_IN_GSTR_3B",
        })
        total += tds_credit

        # Type 6: SEZ supplies refund
        sez_refund = random.randint(0, 300000)
        if sez_refund > 100000:
            refunds.append({
                "refund_type": "SEZ_SUPPLY_REFUND",
                "display_name": "Tax Paid on Supply to SEZ without payment",
                "amount": sez_refund,
                "period": "FY 2023-24",
                "confidence": random.randint(82, 95),
                "supporting_forms": ["GSTR-1", "SEZ Certificate", "LUT"],
                "time_limit": "2 Years",
                "action": "FILE_RFD_01",
            })
            total += sez_refund

        # Type 7: Pre-deposit refund on appeal
        pre_deposit = random.randint(0, 100000)
        if pre_deposit > 25000:
            refunds.append({
                "refund_type": "PRE_DEPOSIT_REFUND",
                "display_name": "Pre-deposit refund on successful appeal",
                "amount": pre_deposit,
                "period": "Appeal pending",
                "confidence": random.randint(70, 88),
                "supporting_forms": ["Appeal Order", "Payment Receipt"],
                "time_limit": "Within 2 years of order",
                "action": "FILE_RFD_01",
            })
            total += pre_deposit

        return {
            "success": True,
            "gstin": gstin,
            "scan_complete": True,
            "months_scanned": months,
            "refund_types_scanned": 7,
            "refunds_found": len(refunds),
            "refunds": refunds,
            "total_recoverable": total,
            "scan_time_seconds": 28,
            "vendor_fraud_detected": random.random() > 0.8,
            "vendor_fraud_amount": random.randint(5000, 50000) if random.random() > 0.8 else 0,
        }

    def file_refund_application(self, gstin: str, refund_type: str, amount: int, documents: list) -> dict:
        """
        Autonomous filing via Computer Use automation
        Simulates GST portal form filling (90 seconds process)
        """
        arn = f"GST-RFD-{random.randint(100000, 999999)}"
        return {
            "success": True,
            "arn": arn,
            "status": "FILED",
            "filing_timestamp": datetime.utcnow().isoformat(),
            "gstin": gstin,
            "refund_type": refund_type,
            "amount_filed": amount,
            "documents_uploaded": len(documents),
            "processing_time_days": random.randint(30, 60),
            "acknowledgement": f"ACK-{uuid.uuid4().hex[:8].upper()}",
            "portal_response": "Application submitted successfully",
        }

    def get_refund_status(self, arn: str) -> dict:
        """Track refund application status"""
        statuses = [
            {"status": "PENDING_SCRUTINY", "days_elapsed": 10, "officer": "GST Officer - Mumbai"},
            {"status": "DEFICIENCY_MEMO", "days_elapsed": 15, "officer": "GST Officer - Delhi", "deficiency": "Bank account details mismatch"},
            {"status": "SANCTIONED", "days_elapsed": 45, "officer": "GST Officer - Bangalore", "sanction_amount": None},
        ]
        return random.choice(statuses) | {"arn": arn, "success": True}

    def get_notices(self, gstin: str) -> list:
        """Get all pending notices for GSTIN"""
        notice_types = [
            {"type": "DRC_01", "title": "Show Cause Notice - ITC Mismatch", "section": "Section 73"},
            {"type": "DRC_03", "title": "Intimation of Payment Shortfall", "section": "Section 73"},
            {"type": "ASMT_10", "title": "Notice for Mismatch in GSTR-1 and GSTR-3B", "section": "Section 61"},
            {"type": "REG_17", "title": "Show Cause Notice - Cancellation of Registration", "section": "Section 29"},
        ]

        notices = []
        for i in range(random.randint(0, 3)):
            n = random.choice(notice_types)
            demand = random.randint(50000, 500000)
            notices.append({
                "notice_id": f"NOT-{uuid.uuid4().hex[:8].upper()}",
                "notice_type": n["type"],
                "title": n["title"],
                "section": n["section"],
                "notice_date": (datetime.now() - timedelta(days=random.randint(5, 60))).strftime("%Y-%m-%d"),
                "due_date": (datetime.now() + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d"),
                "demand_amount": demand,
                "interest": int(demand * 0.18),
                "penalty": int(demand * 0.10),
                "portal": "GST",
                "gstin": gstin,
            })
        return notices

    def get_compliance_calendar(self, gstin: str) -> list:
        """Get all upcoming compliance deadlines"""
        today = datetime.now()
        deadlines = [
            {
                "event_type": "GSTR_1",
                "title": "GSTR-1 Filing (Monthly)",
                "due_date": (today + timedelta(days=11)).strftime("%Y-%m-%d"),
                "penalty_per_day": 50,
                "max_penalty": 10000,
                "is_time_barred_risk": False,
                "pre_filled_form": "GSTR-1 auto-populated from e-invoices",
            },
            {
                "event_type": "GSTR_3B",
                "title": "GSTR-3B Filing",
                "due_date": (today + timedelta(days=20)).strftime("%Y-%m-%d"),
                "penalty_per_day": 50,
                "max_penalty": 10000,
                "is_time_barred_risk": False,
                "pre_filled_form": "Auto-calculated from GSTR-2B",
            },
            {
                "event_type": "GSTR_9",
                "title": "GSTR-9 Annual Return",
                "due_date": (today + timedelta(days=120)).strftime("%Y-%m-%d"),
                "penalty_per_day": 200,
                "max_penalty": 50000,
                "is_time_barred_risk": True,
                "pre_filled_form": "Annual reconciliation ready",
            },
            {
                "event_type": "RFD_01_DEADLINE",
                "title": "2-Year Refund Claim Deadline (Apr 2022 onwards)",
                "due_date": (today + timedelta(days=45)).strftime("%Y-%m-%d"),
                "penalty_per_day": 0,
                "max_penalty": 0,
                "is_time_barred_risk": True,
                "pre_filled_form": "RFD-01 pre-filled",
            },
        ]
        return deadlines


class DummyGSTPortalRouter:
    """
    Expose dummy portal as FastAPI router for demo
    Simulates actual GST government API endpoints
    """
    portal = DummyGSTPortal()

    def get_all_data(self, gstin: str) -> dict:
        """Complete data pull for a GSTIN - used during onboarding"""
        validation = self.portal.validate_gstin(gstin)
        scan = self.portal.scan_refund_opportunities(gstin)
        notices = self.portal.get_notices(gstin)
        itc = self.portal.get_itc_ledger(gstin)
        compliance = self.portal.get_compliance_calendar(gstin)

        return {
            "gstin": gstin,
            "taxpayer": validation.get("taxpayer_details", {}),
            "refund_scan": scan,
            "notices": notices,
            "itc_ledger": itc,
            "compliance_calendar": compliance,
            "total_money_found": scan.get("total_recoverable", 0),
            "data_pulled_at": datetime.utcnow().isoformat(),
        }


def get_gst_portal() -> DummyGSTPortal:
    return DummyGSTPortal()

"""
Tax Vaapsi - Dummy Income Tax Portal
Simulates IT portal (eportal.incometax.gov.in)
Provides realistic mock data for:
- PAN validation, ITR filing, refund tracking
- Form 26AS, Form 16, AIS
- Deduction opportunities (80C, 80D, 80E, 80G)
"""
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional
import structlog

logger = structlog.get_logger()


class DummyITPortal:
    """
    Mock Income Tax Portal
    Simulates all IT department services
    """

    REGIME_SLABS = {
        "OLD": [
            (250000, 0.0),
            (500000, 0.05),
            (1000000, 0.20),
            (float("inf"), 0.30),
        ],
        "NEW": [
            (300000, 0.0),
            (600000, 0.05),
            (900000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (float("inf"), 0.30),
        ],
    }

    DEDUCTION_SECTIONS = {
        "80C": {
            "name": "Life Insurance, PPF, ELSS, EPF, NSC, Tuition Fees",
            "max_limit": 150000,
            "category": "INVESTMENT",
        },
        "80D": {
            "name": "Medical Insurance Premium (Self + Family + Parents)",
            "max_limit": 75000,
            "category": "HEALTH",
        },
        "80E": {
            "name": "Education Loan Interest",
            "max_limit": None,  # No limit
            "category": "EDUCATION",
        },
        "80G": {
            "name": "Donations to Charitable Institutions",
            "max_limit": None,
            "category": "DONATION",
        },
        "80TTA": {
            "name": "Interest from Savings Bank Account",
            "max_limit": 10000,
            "category": "INTEREST",
        },
        "80TTB": {
            "name": "Interest Income for Senior Citizens",
            "max_limit": 50000,
            "category": "INTEREST",
        },
        "HRA": {
            "name": "House Rent Allowance",
            "max_limit": None,
            "category": "ALLOWANCE",
        },
        "24B": {
            "name": "Home Loan Interest (Self-occupied)",
            "max_limit": 200000,
            "category": "HOUSING",
        },
        "80EEA": {
            "name": "Additional Home Loan Interest (Affordable Housing)",
            "max_limit": 150000,
            "category": "HOUSING",
        },
        "80CCD1B": {
            "name": "NPS Additional Contribution",
            "max_limit": 50000,
            "category": "RETIREMENT",
        },
    }

    def validate_pan(self, pan: str) -> dict:
        """Validate PAN and return taxpayer details"""
        # PAN format: AAAAA9999A
        if len(pan) == 10 and pan[:5].isalpha() and pan[5:9].isdigit() and pan[9].isalpha():
            return {
                "success": True,
                "pan": pan,
                "name": f"Taxpayer {pan[-4:]}",
                "dob": "1985-06-15",
                "status": "VALID",
                "linked_mobile": f"98XXXXXX{random.randint(10, 99)}",
                "linked_email": f"taxpayer{pan[-4:].lower()}@email.com",
                "filing_category": "INDIVIDUAL",
            }
        return {"success": False, "error": "Invalid PAN format"}

    def get_form_26as(self, pan: str, financial_year: str = "2023-24") -> dict:
        """Get Form 26AS - TDS/TCS details"""
        entries = []
        deductors = [
            ("AAACB1234N", "Employer Pvt Ltd", "192", "SALARY"),
            ("AADCE5678K", "Bank Ltd", "194A", "INTEREST"),
            ("AABCF9012P", "Client Corp", "194J", "PROFESSIONAL"),
        ]

        total_tds = 0
        for tan, name, section, nature in deductors:
            gross = random.randint(300000, 2000000)
            tds = int(gross * random.uniform(0.05, 0.30))
            total_tds += tds
            entries.append({
                "deductor_tan": tan,
                "deductor_name": name,
                "tds_section": section,
                "nature_of_payment": nature,
                "gross_amount": gross,
                "tds_deducted": tds,
                "tds_deposited": tds,
                "quarter": "Q4",
                "financial_year": financial_year,
                "mismatch": random.random() > 0.85,
                "mismatch_amount": random.randint(1000, 10000) if random.random() > 0.85 else 0,
            })

        return {
            "success": True,
            "pan": pan,
            "financial_year": financial_year,
            "part_a_tds": entries,
            "total_tds_deducted": total_tds,
            "total_tds_deposited": int(total_tds * 0.98),
            "tds_mismatch": int(total_tds * 0.02),
            "part_b_tcs": [],
            "part_c_advance_tax": random.randint(0, 50000),
            "self_assessment_tax": random.randint(0, 30000),
        }

    def get_ais(self, pan: str, financial_year: str = "2023-24") -> dict:
        """Get Annual Information Statement (AIS)"""
        return {
            "success": True,
            "pan": pan,
            "financial_year": financial_year,
            "salary_income": random.randint(800000, 3000000),
            "interest_income": random.randint(10000, 150000),
            "dividend_income": random.randint(0, 50000),
            "capital_gains": {
                "stcg": random.randint(0, 200000),
                "ltcg": random.randint(0, 500000),
            },
            "professional_income": random.randint(0, 500000),
            "other_income": random.randint(0, 50000),
            "high_value_transactions": [
                {"type": "PROPERTY_PURCHASE", "amount": random.randint(2000000, 10000000), "date": "2023-08-15"}
                if random.random() > 0.7 else None
            ],
            "foreign_remittances": random.randint(0, 200000),
        }

    def detect_missed_deductions(self, pan: str, income_data: dict) -> dict:
        """
        CORE FEATURE: Find all missed deductions using AI analysis
        Scans 40+ deduction sections
        """
        gross_income = income_data.get("gross_income", 1200000)
        existing_deductions = income_data.get("existing_deductions", {})
        missed = []
        total_missed = 0

        for section, details in self.DEDUCTION_SECTIONS.items():
            existing_claimed = existing_deductions.get(section, 0)
            max_limit = details["max_limit"] or 200000

            # Calculate what could have been claimed
            potential = random.randint(int(max_limit * 0.3), max_limit)
            if potential > existing_claimed:
                missed_amount = potential - existing_claimed
                tax_saved = int(missed_amount * 0.30)  # Assume 30% bracket
                missed.append({
                    "section": section,
                    "name": details["name"],
                    "category": details["category"],
                    "max_limit": max_limit,
                    "claimed": existing_claimed,
                    "potential": potential,
                    "missed_amount": missed_amount,
                    "tax_saving": tax_saved,
                    "documents_needed": self._get_docs_for_section(section),
                    "can_claim_now": section in ["80C", "80D", "80G", "80CCD1B"],
                })
                total_missed += missed_amount

        return {
            "success": True,
            "pan": pan,
            "deductions_scanned": len(self.DEDUCTION_SECTIONS),
            "missed_deductions": sorted(missed, key=lambda x: x["tax_saving"], reverse=True),
            "total_missed_deductions": total_missed,
            "total_additional_tax_saving": int(total_missed * 0.30),
            "regime_recommendation": self.compare_regimes(gross_income, existing_deductions),
        }

    def _get_docs_for_section(self, section: str) -> list:
        docs = {
            "80C": ["LIC receipt", "PPF passbook", "ELSS statement"],
            "80D": ["Insurance premium receipt", "Medical bills for preventive health"],
            "80E": ["Loan certificate from bank"],
            "80G": ["Donation receipt with 80G certificate"],
            "HRA": ["Rent receipts", "Landlord PAN", "Rental agreement"],
            "24B": ["Home loan interest certificate"],
        }
        return docs.get(section, ["Relevant documents"])

    def compare_regimes(self, gross_income: int, deductions: dict) -> dict:
        """Compare Old vs New tax regime"""
        total_deductions = sum(deductions.values()) if deductions else 150000

        # Old regime tax
        old_taxable = max(0, gross_income - total_deductions - 50000)  # 50k standard deduction
        old_tax = self._calculate_tax(old_taxable, "OLD")

        # New regime tax
        new_taxable = max(0, gross_income - 75000)  # 75k standard deduction in new regime
        new_tax = self._calculate_tax(new_taxable, "NEW")

        saving = abs(old_tax - new_tax)
        recommended = "OLD" if old_tax < new_tax else "NEW"

        return {
            "old_regime_tax": old_tax,
            "new_regime_tax": new_tax,
            "recommended_regime": recommended,
            "savings_if_switched": saving,
            "switch_recommended": saving > 10000,
        }

    def _calculate_tax(self, taxable_income: int, regime: str) -> int:
        tax = 0
        slabs = self.REGIME_SLABS[regime]
        prev = 0
        for limit, rate in slabs:
            if taxable_income <= prev:
                break
            slab_income = min(taxable_income, limit) - prev
            tax += int(slab_income * rate)
            prev = limit
        surcharge = int(tax * 0.10) if taxable_income > 5000000 else 0
        cess = int((tax + surcharge) * 0.04)
        return tax + surcharge + cess

    def get_refund_status(self, pan: str, assessment_year: str = "2024-25") -> dict:
        """Track IT refund status"""
        statuses = [
            {
                "status": "REFUND_ISSUED",
                "amount": random.randint(5000, 100000),
                "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                "mode": "NEFT",
                "bank": "SBI XXXX1234",
            },
            {
                "status": "PROCESSING",
                "message": "Your refund is being processed",
                "expected_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
            },
            {
                "status": "ITR_PROCESSED_WITH_DEMAND",
                "demand_amount": random.randint(5000, 50000),
                "message": "ITR processed. Outstanding demand raised.",
            },
            {
                "status": "PENDING_VERIFICATION",
                "message": "ITR e-verified. Processing started.",
            },
        ]

        return {
            "success": True,
            "pan": pan,
            "assessment_year": assessment_year,
            "itr_form": f"ITR-{random.randint(1, 4)}",
            "filing_date": (datetime.now() - timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d"),
            "refund_details": random.choice(statuses),
        }

    def get_advance_tax_schedule(self, pan: str, estimated_income: int) -> dict:
        """Calculate and track advance tax payment schedule"""
        tax = self._calculate_tax(max(0, estimated_income - 75000), "NEW")
        return {
            "success": True,
            "pan": pan,
            "estimated_annual_tax": tax,
            "schedule": [
                {"installment": "1st", "due_date": "June 15", "percentage": 15, "amount": int(tax * 0.15), "paid": True},
                {"installment": "2nd", "due_date": "September 15", "percentage": 45, "amount": int(tax * 0.45), "paid": True},
                {"installment": "3rd", "due_date": "December 15", "percentage": 75, "amount": int(tax * 0.75), "paid": False},
                {"installment": "4th", "due_date": "March 15", "percentage": 100, "amount": tax, "paid": False},
            ],
            "penalty_if_missed": int(tax * 0.01),
        }

    def get_pending_notices(self, pan: str) -> list:
        """Get all pending IT notices"""
        notice_types = [
            {"type": "139_9", "title": "Defective Return Notice", "section": "139(9)"},
            {"type": "142_1", "title": "Notice for filing ITR", "section": "142(1)"},
            {"type": "143_1", "title": "Intimation u/s 143(1)", "section": "143(1)"},
            {"type": "148", "title": "Notice for Income Escaping Assessment", "section": "148"},
            {"type": "245", "title": "Notice for Refund Adjustment", "section": "245"},
        ]

        notices = []
        for i in range(random.randint(0, 2)):
            n = random.choice(notice_types)
            notices.append({
                "notice_id": f"IT-NOT-{uuid.uuid4().hex[:8].upper()}",
                "notice_type": n["type"],
                "title": n["title"],
                "section": n["section"],
                "notice_date": (datetime.now() - timedelta(days=random.randint(5, 45))).strftime("%Y-%m-%d"),
                "due_date": (datetime.now() + timedelta(days=random.randint(15, 30))).strftime("%Y-%m-%d"),
                "assessment_year": "2024-25",
                "demand_amount": random.randint(10000, 200000),
                "portal": "INCOME_TAX",
                "pan": pan,
            })
        return notices

    def scan_all_opportunities(self, pan: str) -> dict:
        """Complete scan of all IT refund and savings opportunities"""
        ais = self.get_ais(pan)
        form26as = self.get_form_26as(pan)
        gross_income = (
            ais["salary_income"]
            + ais["interest_income"]
            + ais["professional_income"]
            + ais["dividend_income"]
        )

        deductions = self.detect_missed_deductions(pan, {"gross_income": gross_income, "existing_deductions": {}})
        advance_tax = self.get_advance_tax_schedule(pan, gross_income)
        notices = self.get_pending_notices(pan)
        refund = self.get_refund_status(pan)

        total_savings = deductions["total_additional_tax_saving"] + form26as["tds_mismatch"]

        return {
            "success": True,
            "pan": pan,
            "gross_income": gross_income,
            "ais_data": ais,
            "form_26as": form26as,
            "missed_deductions": deductions,
            "advance_tax": advance_tax,
            "notices": notices,
            "refund_status": refund,
            "total_money_recoverable": total_savings,
            "regime_recommendation": deductions["regime_recommendation"],
        }


def get_it_portal() -> DummyITPortal:
    return DummyITPortal()

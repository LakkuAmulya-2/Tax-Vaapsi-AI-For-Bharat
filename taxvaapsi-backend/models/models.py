"""
Tax Vaapsi - Pydantic Models
Request/Response models for all API endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


# ─── AUTH MODELS ──────────────────────────────────────────────
class RegisterRequest(BaseModel):
    gstin: str = Field(..., min_length=15, max_length=15, description="15-digit GSTIN")
    pan: str = Field(..., min_length=10, max_length=10, description="10-character PAN")
    business_name: str
    email: str
    phone: str
    business_type: str = "SME"  # SME, EXPORTER, MANUFACTURER, STARTUP, FREELANCER
    language: str = "en"  # en, hi, te, ta, gu, mr, bn, kn, ml


class LoginRequest(BaseModel):
    email: str
    password: str


# ─── GST MODELS ───────────────────────────────────────────────
class GSTScanRequest(BaseModel):
    user_id: str
    gstin: str
    months: int = 36


class GSTRiskRequest(BaseModel):
    user_id: str
    gstin: str
    refund_type: str
    amount: int


class GSTFileRequest(BaseModel):
    user_id: str
    scan_id: str
    gstin: str
    refund_type: str
    amount: int


class DeficiencyReplyRequest(BaseModel):
    user_id: str
    gstin: str
    arn: str
    deficiency_details: str


# ─── IT MODELS ────────────────────────────────────────────────
class ITScanRequest(BaseModel):
    user_id: str
    pan: str


class ITOptimizeRequest(BaseModel):
    user_id: str
    pan: str
    gross_income: int
    salary_income: int = 0
    professional_income: int = 0
    existing_deductions: dict = {}
    regime: str = "NEW"


class RegimeCompareRequest(BaseModel):
    user_id: str
    pan: str
    gross_income: int
    deductions: dict = {}


# ─── TDS MODELS ───────────────────────────────────────────────
class TDSScanRequest(BaseModel):
    user_id: str
    pan: str
    financial_year: str = "2023-24"


class TDSReminderRequest(BaseModel):
    user_id: str
    deductor_name: str
    deductor_tan: str
    mismatch_amount: int


# ─── NOTICE MODELS ────────────────────────────────────────────
class NoticeAnalyzeRequest(BaseModel):
    user_id: str
    notice_text: str
    portal: str = "GST"  # GST | INCOME_TAX


class NoticeDefenseRequest(BaseModel):
    user_id: str
    notice_text: str
    portal: str = "GST"
    business_name: str = ""
    gstin: str = ""
    pan: str = ""
    additional_facts: str = ""


# ─── ONBOARDING MODELS ────────────────────────────────────────
class OnboardingRequest(BaseModel):
    user_id: str
    gstin: str
    pan: str


class DashboardRequest(BaseModel):
    user_id: str


# ─── VOICE MODELS ─────────────────────────────────────────────
class VoiceCommandRequest(BaseModel):
    user_id: str
    language: str = "en"
    command_text: str  # Transcribed voice command


class VoiceResponse(BaseModel):
    text_response: str
    action_taken: Optional[str] = None
    action_result: Optional[dict] = None
    speak_this: str  # Text to convert to speech (Bhashini TTS)


# ─── COMPLIANCE MODELS ────────────────────────────────────────
class ComplianceRequest(BaseModel):
    user_id: str
    gstin: str


# ─── DOCUMENT MODELS ──────────────────────────────────────────
class DocumentAnalyzeRequest(BaseModel):
    user_id: str
    document_type: str  # INVOICE | NOTICE | FORM_26AS | FORM_16 | GSTR
    s3_key: Optional[str] = None
    document_text: Optional[str] = None


# ─── API RESPONSE MODELS ──────────────────────────────────────
class APIResponse(BaseModel):
    success: bool
    message: str = ""
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MoneyRevealResponse(BaseModel):
    total_money_found: int
    breakdown: dict
    refunds: list
    animated_counter: bool = True
    celebration: bool = True

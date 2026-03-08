"""
TAX VAAPSI - DUMMY GST PORTAL
Actual running web server simulating services.gst.gov.in
Port: 8001
Playwright automation will open real browser and interact with THIS portal
"""
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from flask_cors import CORS
import random, uuid, json
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = "taxvaapsi-gst-portal-secret"
CORS(app)

# ─── IN-MEMORY DB (simulates GST backend) ────────────────────
GSTIN_DB = {
    "27AABCU9603R1ZX": {
        "legal_name": "ABC Exports Pvt Ltd",
        "trade_name": "ABC Exports",
        "state": "Maharashtra",
        "status": "ACTIVE",
        "email": "abc@exports.com",
        "password": "password123",
        "registration_date": "2017-07-01",
        "business_type": "EXPORTER",
    },
    "29AADCB2230M1ZV": {
        "legal_name": "XYZ Manufacturing Ltd",
        "trade_name": "XYZ Mfg",
        "state": "Karnataka",
        "status": "ACTIVE",
        "email": "xyz@mfg.com",
        "password": "password123",
        "registration_date": "2018-04-01",
        "business_type": "MANUFACTURER",
    },
}

REFUND_APPLICATIONS = {}  # ARN -> application data
FILED_RETURNS = {}         # GSTIN -> list of returns


# ─── PORTAL HTML TEMPLATE ────────────────────────────────────
BASE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GST Portal - {title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: Arial, sans-serif; background: #f0f2f5; }}
    .header {{ background: #1a472a; color: white; padding: 12px 20px; display: flex; align-items: center; gap: 15px; }}
    .header img {{ width: 60px; }}
    .header h1 {{ font-size: 20px; }}
    .header p {{ font-size: 12px; opacity: 0.8; }}
    .nav {{ background: #2d6a4f; padding: 8px 20px; }}
    .nav a {{ color: white; text-decoration: none; margin-right: 20px; font-size: 13px; }}
    .container {{ max-width: 1100px; margin: 30px auto; padding: 0 20px; }}
    .card {{ background: white; border-radius: 4px; padding: 25px; margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
    .card h2 {{ font-size: 18px; color: #1a472a; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-bottom: 20px; }}
    .form-group {{ margin-bottom: 16px; }}
    .form-group label {{ display: block; font-size: 13px; font-weight: bold; margin-bottom: 6px; color: #333; }}
    .form-group label .req {{ color: red; }}
    .form-group input, .form-group select, .form-group textarea {{
      width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 3px; font-size: 14px;
    }}
    .form-group input:focus, .form-group select:focus {{ border-color: #2d6a4f; outline: none; }}
    .btn {{ padding: 10px 24px; border: none; border-radius: 3px; cursor: pointer; font-size: 14px; font-weight: bold; }}
    .btn-primary {{ background: #1a472a; color: white; }}
    .btn-primary:hover {{ background: #2d6a4f; }}
    .btn-secondary {{ background: #6c757d; color: white; margin-left: 10px; }}
    .alert {{ padding: 12px 16px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }}
    .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
    .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
    .alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
    .badge-success {{ background: #28a745; color: white; }}
    .badge-warning {{ background: #ffc107; color: black; }}
    .badge-danger {{ background: #dc3545; color: white; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th {{ background: #1a472a; color: white; padding: 10px; text-align: left; }}
    td {{ padding: 10px; border-bottom: 1px solid #eee; }}
    tr:hover {{ background: #f9f9f9; }}
    .sidebar {{ display: flex; gap: 20px; }}
    .sidebar-menu {{ width: 220px; background: white; border-radius: 4px; padding: 15px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); height: fit-content; }}
    .sidebar-menu a {{ display: block; padding: 8px 12px; color: #333; text-decoration: none; font-size: 13px; border-radius: 3px; margin-bottom: 4px; }}
    .sidebar-menu a:hover, .sidebar-menu a.active {{ background: #e8f5e9; color: #1a472a; font-weight: bold; }}
    .sidebar-content {{ flex: 1; }}
    .progress {{ background: #e9ecef; border-radius: 4px; height: 20px; }}
    .progress-bar {{ background: #28a745; height: 100%; border-radius: 4px; text-align: center; color: white; font-size: 12px; line-height: 20px; }}
    .step-indicator {{ display: flex; margin-bottom: 25px; }}
    .step {{ flex: 1; text-align: center; position: relative; }}
    .step-circle {{ width: 32px; height: 32px; border-radius: 50%; background: #ccc; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; font-weight: bold; font-size: 14px; }}
    .step.active .step-circle {{ background: #1a472a; }}
    .step.done .step-circle {{ background: #28a745; }}
    .step-label {{ font-size: 11px; color: #666; }}
    .step.active .step-label {{ color: #1a472a; font-weight: bold; }}
    .info-row {{ display: flex; gap: 20px; margin-bottom: 10px; font-size: 13px; }}
    .info-row .label {{ color: #666; width: 180px; }}
    .info-row .value {{ font-weight: bold; }}
    .tax-amount {{ font-size: 24px; font-weight: bold; color: #1a472a; }}
    .footer {{ background: #1a472a; color: white; padding: 20px; text-align: center; font-size: 12px; margin-top: 40px; }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div style="font-size:24px; font-weight:bold;">🇮🇳 GST</div>
    </div>
    <div>
      <h1>Goods and Services Tax Portal</h1>
      <p>Government of India | Ministry of Finance</p>
    </div>
    <div style="margin-left:auto; font-size:13px; text-align:right;">
      {user_info}
    </div>
  </div>
  <div class="nav">
    <a href="/">Home</a>
    <a href="/services">Services</a>
    <a href="/refund">Refunds</a>
    <a href="/returns">Returns</a>
    <a href="/notices">Notices</a>
    <a href="/taxpayer-info">Taxpayer Info</a>
  </div>
  {content}
  <div class="footer">
    <p>© 2024 Goods and Services Tax Network (GSTN) | Helpdesk: 1800-103-4786</p>
    <p>Best viewed in Chrome, Firefox | Version 2.1.0</p>
  </div>
</body>
</html>"""


def render(title, content, user_info=""):
    return BASE_HTML.format(title=title, content=content, user_info=user_info)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "gstin" not in session:
            return redirect("/login?next=" + request.path)
        return f(*args, **kwargs)
    return decorated


# ════════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════════

@app.route("/")
def home():
    content = """
    <div class="container">
      <div style="background: linear-gradient(135deg, #1a472a, #2d6a4f); color: white; padding: 40px; border-radius: 8px; margin-bottom: 25px; text-align:center;">
        <h2 style="font-size: 28px; margin-bottom: 10px;">Welcome to GST Portal</h2>
        <p style="opacity: 0.9;">File Returns | Apply for Refunds | Track Applications | Respond to Notices</p>
        <a href="/login" class="btn btn-primary" style="margin-top: 20px; background: white; color: #1a472a; display:inline-block;">Login to Portal</a>
      </div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
        <div class="card" style="text-align:center;">
          <div style="font-size: 40px;">📋</div>
          <h3 style="margin: 10px 0 8px;">File Returns</h3>
          <p style="font-size: 13px; color: #666;">GSTR-1, GSTR-3B, GSTR-9 Annual Return</p>
        </div>
        <div class="card" style="text-align:center;">
          <div style="font-size: 40px;">💰</div>
          <h3 style="margin: 10px 0 8px;">Apply for Refund</h3>
          <p style="font-size: 13px; color: #666;">RFD-01 for IGST, ITC, Cash Ledger excess</p>
        </div>
        <div class="card" style="text-align:center;">
          <div style="font-size: 40px;">🔔</div>
          <h3 style="margin: 10px 0 8px;">Notices & Demand</h3>
          <p style="font-size: 13px; color: #666;">View and respond to DRC-01, SCN notices</p>
        </div>
      </div>
    </div>"""
    return render("Home", content)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        gstin = request.form.get("gstin", "").upper().strip()
        password = request.form.get("password", "").strip()

        taxpayer = GSTIN_DB.get(gstin)
        # Accept any GSTIN with valid format + any password for demo
        if taxpayer and len(gstin) == 15:
            session["gstin"] = gstin
            session["legal_name"] = taxpayer["legal_name"]
            session["state"] = taxpayer["state"]
            next_url = request.args.get("next", "/dashboard")
            return redirect(next_url)
        elif len(gstin) == 15 and password:
            # Accept any valid format GSTIN
            session["gstin"] = gstin
            session["legal_name"] = f"Business {gstin[-4:]}"
            session["state"] = "Maharashtra"
            return redirect(request.args.get("next", "/dashboard"))
        else:
            error = "Invalid GSTIN or password. Please try again."

    content = f"""
    <div class="container" style="max-width: 500px;">
      <div class="card" style="margin-top: 40px;">
        <h2>Login to GST Portal</h2>
        {'<div class="alert alert-danger">' + error + '</div>' if error else ''}
        <form method="POST" id="loginForm">
          <div class="form-group">
            <label>GSTIN <span class="req">*</span></label>
            <input type="text" name="gstin" id="gstin" placeholder="e.g. 27AABCU9603R1ZX" maxlength="15" style="text-transform:uppercase;" required>
            <small style="color: #666; font-size: 12px;">Enter your 15-digit GSTIN</small>
          </div>
          <div class="form-group">
            <label>Password <span class="req">*</span></label>
            <input type="password" name="password" id="password" placeholder="Enter password" required>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <button type="submit" class="btn btn-primary" id="loginBtn">Login</button>
            <a href="#" style="font-size: 13px; color: #1a472a;">Forgot Password?</a>
          </div>
        </form>
        <div style="margin-top: 20px; padding: 12px; background: #f0f8f0; border-radius: 4px; font-size: 12px;">
          <strong>Demo Credentials:</strong><br>
          GSTIN: 27AABCU9603R1ZX | Password: password123<br>
          GSTIN: 29AADCB2230M1ZV | Password: password123
        </div>
      </div>
    </div>"""
    return render("Login", content)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard")
@login_required
def dashboard():
    gstin = session["gstin"]
    name = session.get("legal_name", gstin)
    user_info = f"<strong>{name}</strong><br>GSTIN: {gstin} | <a href='/logout' style='color:#aed6b8;'>Logout</a>"

    # Random realistic data
    pending_refund = random.randint(200000, 1200000)
    itc_balance = random.randint(50000, 400000)

    content = f"""
    <div class="container">
      <div class="alert alert-info" style="margin-top:20px;">
        👋 Welcome back, <strong>{name}</strong>! You have pending actions.
      </div>
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;">
        <div class="card" style="text-align:center; padding: 15px;">
          <div style="font-size: 13px; color: #666; margin-bottom: 5px;">Pending Refund</div>
          <div class="tax-amount">₹{pending_refund:,.0f}</div>
          <div style="font-size: 11px; color: #28a745; margin-top: 5px;">Claimable Now</div>
        </div>
        <div class="card" style="text-align:center; padding: 15px;">
          <div style="font-size: 13px; color: #666; margin-bottom: 5px;">ITC Balance</div>
          <div class="tax-amount" style="color: #0066cc;">₹{itc_balance:,.0f}</div>
          <div style="font-size: 11px; color: #666; margin-top: 5px;">Electronic Credit Ledger</div>
        </div>
        <div class="card" style="text-align:center; padding: 15px;">
          <div style="font-size: 13px; color: #666; margin-bottom: 5px;">Returns Filed</div>
          <div class="tax-amount" style="color: #28a745;">36</div>
          <div style="font-size: 11px; color: #666; margin-top: 5px;">Last 3 years</div>
        </div>
        <div class="card" style="text-align:center; padding: 15px;">
          <div style="font-size: 13px; color: #666; margin-bottom: 5px;">Pending Notices</div>
          <div class="tax-amount" style="color: #dc3545;">{random.randint(0, 2)}</div>
          <div style="font-size: 11px; color: #dc3545; margin-top: 5px;">Action Required</div>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
        <div class="card">
          <h2>Quick Actions</h2>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
            <a href="/refund/apply" style="display: block; padding: 15px; background: #e8f5e9; border-radius: 4px; text-decoration: none; color: #1a472a; text-align: center;">
              <div style="font-size: 24px;">💰</div>
              <div style="font-weight: bold; margin-top: 5px;">Apply for Refund</div>
              <div style="font-size: 12px; color: #666;">RFD-01</div>
            </a>
            <a href="/returns/file" style="display: block; padding: 15px; background: #e3f2fd; border-radius: 4px; text-decoration: none; color: #1a472a; text-align: center;">
              <div style="font-size: 24px;">📋</div>
              <div style="font-weight: bold; margin-top: 5px;">File Return</div>
              <div style="font-size: 12px; color: #666;">GSTR-1 / GSTR-3B</div>
            </a>
            <a href="/refund/status" style="display: block; padding: 15px; background: #fff3e0; border-radius: 4px; text-decoration: none; color: #1a472a; text-align: center;">
              <div style="font-size: 24px;">📊</div>
              <div style="font-weight: bold; margin-top: 5px;">Track Refund</div>
              <div style="font-size: 12px; color: #666;">Application Status</div>
            </a>
            <a href="/notices" style="display: block; padding: 15px; background: #fce4ec; border-radius: 4px; text-decoration: none; color: #1a472a; text-align: center;">
              <div style="font-size: 24px;">🔔</div>
              <div style="font-weight: bold; margin-top: 5px;">View Notices</div>
              <div style="font-size: 12px; color: #666;">DRC, SCN, Orders</div>
            </a>
          </div>
        </div>
        <div class="card">
          <h2>Filing Deadlines</h2>
          <div style="font-size: 13px;">
            <div style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;">
              <span>GSTR-1</span><span class="badge badge-warning">11 Mar</span>
            </div>
            <div style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;">
              <span>GSTR-3B</span><span class="badge badge-warning">20 Mar</span>
            </div>
            <div style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;">
              <span>GSTR-9</span><span class="badge badge-success">31 Dec</span>
            </div>
            <div style="padding: 8px 0; display: flex; justify-content: space-between;">
              <span>RFD-01 (2-yr limit)</span><span class="badge badge-danger">Urgent!</span>
            </div>
          </div>
        </div>
      </div>
    </div>"""
    return render("Dashboard", content, user_info)


@app.route("/refund/apply", methods=["GET", "POST"])
@login_required
def refund_apply():
    gstin = session["gstin"]
    name = session.get("legal_name", gstin)
    user_info = f"<strong>{name}</strong><br>GSTIN: {gstin} | <a href='/logout' style='color:#aed6b8;'>Logout</a>"
    
    arn = None
    success = False
    
    if request.method == "POST":
        # Generate ARN
        arn = f"GST-RFD-{random.randint(100000, 999999)}"
        refund_type = request.form.get("refund_type", "IGST_EXPORT")
        amount = request.form.get("refund_amount", "0")
        
        REFUND_APPLICATIONS[arn] = {
            "arn": arn,
            "gstin": gstin,
            "refund_type": refund_type,
            "amount": int(amount),
            "filed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ARN_GENERATED",
            "period_from": request.form.get("period_from", ""),
            "period_to": request.form.get("period_to", ""),
            "bank_account": request.form.get("bank_account", ""),
            "bank_ifsc": request.form.get("bank_ifsc", ""),
        }
        success = True
    
    success_html = f"""
    <div class="alert alert-success">
      ✅ <strong>Application Submitted Successfully!</strong><br>
      ARN: <strong id="arn-number">{arn}</strong><br>
      Your refund application has been filed. Track status at <a href="/refund/status">Refund Status</a>.
    </div>""" if success else ""
    
    content = f"""
    <div class="container">
      <div style="margin-top:20px;" class="sidebar">
        <div class="sidebar-menu">
          <strong style="font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 10px; display:block;">Refund Services</strong>
          <a href="/refund/apply" class="active">Apply for Refund (RFD-01)</a>
          <a href="/refund/status">Track Application</a>
          <a href="/refund/history">Application History</a>
        </div>
        <div class="sidebar-content">
          {success_html}
          <div class="card">
            <h2>Apply for GST Refund (Form RFD-01)</h2>
            <div class="step-indicator">
              <div class="step active"><div class="step-circle">1</div><div class="step-label">Basic Details</div></div>
              <div class="step"><div class="step-circle">2</div><div class="step-label">Documents</div></div>
              <div class="step"><div class="step-circle">3</div><div class="step-label">Bank Details</div></div>
              <div class="step"><div class="step-circle">4</div><div class="step-label">Submit</div></div>
            </div>
            <form method="POST" id="refundForm" enctype="multipart/form-data">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                  <label>GSTIN <span class="req">*</span></label>
                  <input type="text" name="gstin" value="{gstin}" readonly style="background:#f5f5f5;">
                </div>
                <div class="form-group">
                  <label>Taxpayer Name</label>
                  <input type="text" value="{name}" readonly style="background:#f5f5f5;">
                </div>
                <div class="form-group">
                  <label>Refund Type <span class="req">*</span></label>
                  <select name="refund_type" id="refund_type" required>
                    <option value="">-- Select Refund Type --</option>
                    <option value="IGST_EXPORT">IGST paid on Export of Goods/Services</option>
                    <option value="ITC_ACCUMULATION">ITC Accumulated due to Inverted Duty Structure</option>
                    <option value="EXCESS_CASH_LEDGER">Excess Balance in Electronic Cash Ledger</option>
                    <option value="ASSESSMENT_ORDER">Refund pursuant to Assessment Order/Appeal</option>
                    <option value="TDS_TCS_CREDIT">TDS/TCS Excess Credit</option>
                    <option value="SEZ_SUPPLY">Tax paid on Supply to SEZ (Without Payment)</option>
                    <option value="PRE_DEPOSIT">Pre-deposit refund on successful appeal</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Refund Amount (₹) <span class="req">*</span></label>
                  <input type="number" name="refund_amount" id="refund_amount" placeholder="Enter amount in rupees" required min="1">
                </div>
                <div class="form-group">
                  <label>Tax Period From <span class="req">*</span></label>
                  <input type="month" name="period_from" id="period_from" required>
                </div>
                <div class="form-group">
                  <label>Tax Period To <span class="req">*</span></label>
                  <input type="month" name="period_to" id="period_to" required>
                </div>
                <div class="form-group">
                  <label>Bank Account Number <span class="req">*</span></label>
                  <input type="text" name="bank_account" id="bank_account" placeholder="Enter bank account number" required>
                </div>
                <div class="form-group">
                  <label>Bank IFSC Code <span class="req">*</span></label>
                  <input type="text" name="bank_ifsc" id="bank_ifsc" placeholder="e.g. SBIN0000123" required>
                </div>
                <div class="form-group">
                  <label>HSN/SAC Code</label>
                  <input type="text" name="hsn_code" id="hsn_code" placeholder="e.g. 8471 for computers">
                </div>
                <div class="form-group">
                  <label>Port Code (for exports)</label>
                  <input type="text" name="port_code" id="port_code" placeholder="e.g. INMAA1">
                </div>
              </div>
              <div class="form-group">
                <label>Upload Supporting Documents</label>
                <div style="border: 2px dashed #ccc; border-radius: 4px; padding: 20px; text-align: center; font-size: 13px; color: #666;">
                  <input type="file" name="documents" id="documents" multiple accept=".pdf,.jpg,.png" style="display:none;">
                  <label for="documents" style="cursor: pointer; color: #1a472a; font-weight: bold;">📎 Click to Upload Documents</label><br>
                  <span style="font-size: 12px;">GSTR-3B, Shipping Bills, LUT Copy, Bank Realization Certificate (Max 5MB each)</span>
                </div>
              </div>
              <div class="form-group">
                <label>
                  <input type="checkbox" name="declaration" id="declaration" required style="width:auto; margin-right: 8px;">
                  I hereby declare that the information furnished is true and correct to the best of my knowledge.
                </label>
              </div>
              <button type="submit" class="btn btn-primary" id="submitBtn">Submit Application</button>
              <button type="button" class="btn btn-secondary" onclick="saveDraft()">Save as Draft</button>
            </form>
          </div>
        </div>
      </div>
    </div>
    <script>
      function saveDraft() {{ alert('Draft saved successfully!'); }}
      document.getElementById('refundForm').onsubmit = function() {{
        document.getElementById('submitBtn').textContent = 'Submitting...';
        document.getElementById('submitBtn').disabled = true;
      }};
    </script>"""
    return render("Apply for Refund", content, user_info)


@app.route("/refund/status")
@login_required
def refund_status():
    gstin = session["gstin"]
    name = session.get("legal_name", gstin)
    user_info = f"<strong>{name}</strong><br>GSTIN: {gstin} | <a href='/logout' style='color:#aed6b8;'>Logout</a>"
    arn = request.args.get("arn", "")
    
    # Build applications list for this GSTIN
    user_apps = {k: v for k, v in REFUND_APPLICATIONS.items() if v["gstin"] == gstin}
    
    # Add some demo applications
    if not user_apps:
        demo_arn = f"GST-RFD-{random.randint(100000, 999999)}"
        user_apps[demo_arn] = {
            "arn": demo_arn, "gstin": gstin,
            "refund_type": "IGST_EXPORT", "amount": 684000,
            "filed_date": "2024-10-15 10:30:00", "status": "PENDING_SCRUTINY",
            "period_from": "2024-04", "period_to": "2024-09",
        }
    
    rows = ""
    for app_arn, app in user_apps.items():
        status = app["status"]
        badge_class = {"ARN_GENERATED": "badge-warning", "PENDING_SCRUTINY": "badge-warning",
                      "SANCTIONED": "badge-success", "DEFICIENCY_MEMO": "badge-danger",
                      "REJECTED": "badge-danger"}.get(status, "badge-warning")
        rows += f"""
        <tr>
          <td><strong id="arn-{app_arn}">{app_arn}</strong></td>
          <td>{app.get('refund_type', '').replace('_', ' ')}</td>
          <td>₹{app.get('amount', 0):,.0f}</td>
          <td>{app.get('filed_date', '')[:10]}</td>
          <td><span class="badge {badge_class}">{status.replace('_', ' ')}</span></td>
          <td><a href="/refund/detail?arn={app_arn}" style="color: #1a472a; font-size: 12px;">View Details</a></td>
        </tr>"""
    
    content = f"""
    <div class="container">
      <div class="card" style="margin-top: 20px;">
        <h2>Track Refund Application Status</h2>
        <div class="form-group" style="max-width: 400px;">
          <label>Search by ARN</label>
          <div style="display: flex; gap: 10px;">
            <input type="text" id="arnSearch" placeholder="Enter ARN number" value="{arn}">
            <button class="btn btn-primary" onclick="searchArn()">Search</button>
          </div>
        </div>
        <h3 style="font-size: 15px; margin-bottom: 15px;">Your Applications</h3>
        <table id="applicationsTable">
          <thead>
            <tr><th>ARN</th><th>Refund Type</th><th>Amount</th><th>Filed Date</th><th>Status</th><th>Action</th></tr>
          </thead>
          <tbody>{rows if rows else '<tr><td colspan="6" style="text-align:center; color:#666;">No applications found</td></tr>'}</tbody>
        </table>
      </div>
    </div>
    <script>
      function searchArn() {{
        var arn = document.getElementById('arnSearch').value;
        if(arn) window.location.href = '/refund/status?arn=' + arn;
      }}
    </script>"""
    return render("Refund Status", content, user_info)


@app.route("/notices")
@login_required
def notices():
    gstin = session["gstin"]
    name = session.get("legal_name", gstin)
    user_info = f"<strong>{name}</strong><br>GSTIN: {gstin} | <a href='/logout' style='color:#aed6b8;'>Logout</a>"

    content = f"""
    <div class="container">
      <div class="card" style="margin-top: 20px;">
        <h2>Notices & Demands</h2>
        <table>
          <thead>
            <tr><th>Notice No.</th><th>Section</th><th>Description</th><th>Date</th><th>Due Date</th><th>Demand</th><th>Status</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr>
              <td>DRC-01/2024/001</td>
              <td>Section 73</td>
              <td>ITC Mismatch - GSTR-2B vs GSTR-3B</td>
              <td>2024-11-01</td>
              <td><span style="color:red; font-weight:bold;">2025-03-20</span></td>
              <td>₹1,25,000</td>
              <td><span class="badge badge-danger">Pending Reply</span></td>
              <td><a href="/notices/reply/001" style="color:#1a472a; font-size:12px;">Reply</a></td>
            </tr>
            <tr>
              <td>ASMT-10/2024/002</td>
              <td>Section 61</td>
              <td>Mismatch in GSTR-1 and GSTR-3B data</td>
              <td>2024-10-15</td>
              <td>2025-03-30</td>
              <td>₹45,000</td>
              <td><span class="badge badge-warning">Under Review</span></td>
              <td><a href="/notices/reply/002" style="color:#1a472a; font-size:12px;">Reply</a></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>"""
    return render("Notices", content, user_info)


@app.route("/notices/reply/<notice_id>", methods=["GET", "POST"])
@login_required
def notice_reply(notice_id):
    gstin = session["gstin"]
    name = session.get("legal_name", gstin)
    user_info = f"<strong>{name}</strong><br>GSTIN: {gstin} | <a href='/logout' style='color:#aed6b8;'>Logout</a>"
    
    submitted = request.method == "POST"
    ack = f"GSTACK{random.randint(10000000, 99999999)}" if submitted else ""
    
    content = f"""
    <div class="container">
      <div class="card" style="margin-top:20px;">
        <h2>Reply to Notice - {notice_id}</h2>
        {'<div class="alert alert-success">✅ Reply submitted successfully! Acknowledgement: <strong>' + ack + '</strong></div>' if submitted else ''}
        <form method="POST" enctype="multipart/form-data">
          <div class="form-group">
            <label>Notice Reference <span class="req">*</span></label>
            <input type="text" value="DRC-01/2024/{notice_id}" readonly style="background:#f5f5f5;">
          </div>
          <div class="form-group">
            <label>Reply / Statement <span class="req">*</span></label>
            <textarea name="reply_text" id="reply_text" rows="10" placeholder="Enter your reply to the notice..." required style="font-size: 13px;"></textarea>
          </div>
          <div class="form-group">
            <label>Upload Supporting Documents</label>
            <input type="file" name="reply_docs" multiple accept=".pdf">
            <small style="color:#666; font-size:12px;">Attach invoices, statements, reconciliation documents</small>
          </div>
          <button type="submit" class="btn btn-primary" id="replySubmitBtn">Submit Reply</button>
        </form>
      </div>
    </div>"""
    return render("Notice Reply", content, user_info)


@app.route("/returns/file", methods=["GET", "POST"])
@login_required
def file_return():
    gstin = session["gstin"]
    name = session.get("legal_name", gstin)
    user_info = f"<strong>{name}</strong><br>GSTIN: {gstin} | <a href='/logout' style='color:#aed6b8;'>Logout</a>"
    
    submitted = request.method == "POST"
    ack = f"GSTRACK{random.randint(10000000, 99999999)}" if submitted else ""
    
    content = f"""
    <div class="container">
      <div class="card" style="margin-top:20px;">
        <h2>File GST Return</h2>
        {'<div class="alert alert-success">✅ Return filed! Acknowledgement No: <strong>' + ack + '</strong></div>' if submitted else ''}
        <form method="POST" id="returnForm">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div class="form-group">
              <label>GSTIN</label>
              <input type="text" value="{gstin}" readonly style="background:#f5f5f5;">
            </div>
            <div class="form-group">
              <label>Return Type <span class="req">*</span></label>
              <select name="return_type" id="return_type" required>
                <option value="GSTR1">GSTR-1 (Outward Supplies)</option>
                <option value="GSTR3B">GSTR-3B (Monthly Summary)</option>
                <option value="GSTR9">GSTR-9 (Annual Return)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Tax Period <span class="req">*</span></label>
              <input type="month" name="tax_period" id="tax_period" required>
            </div>
            <div class="form-group">
              <label>Total Turnover (₹)</label>
              <input type="number" name="turnover" id="turnover" placeholder="0">
            </div>
            <div class="form-group">
              <label>Total Tax Paid (₹)</label>
              <input type="number" name="tax_paid" id="tax_paid" placeholder="0">
            </div>
            <div class="form-group">
              <label>ITC Claimed (₹)</label>
              <input type="number" name="itc_claimed" id="itc_claimed" placeholder="0">
            </div>
          </div>
          <button type="submit" class="btn btn-primary" id="returnSubmitBtn">File Return</button>
        </form>
      </div>
    </div>"""
    return render("File Return", content, user_info)


@app.route("/taxpayer-info")
@login_required
def taxpayer_info():
    gstin = session["gstin"]
    name = session.get("legal_name", gstin)
    taxpayer = GSTIN_DB.get(gstin, {"legal_name": name, "state": "Maharashtra", "status": "ACTIVE", "registration_date": "2020-01-01", "business_type": "SME"})
    user_info = f"<strong>{name}</strong><br>GSTIN: {gstin} | <a href='/logout' style='color:#aed6b8;'>Logout</a>"
    
    content = f"""
    <div class="container">
      <div class="card" style="margin-top:20px;">
        <h2>Taxpayer Information</h2>
        <div class="info-row"><div class="label">GSTIN</div><div class="value">{gstin}</div></div>
        <div class="info-row"><div class="label">Legal Name</div><div class="value">{taxpayer.get('legal_name', name)}</div></div>
        <div class="info-row"><div class="label">Trade Name</div><div class="value">{taxpayer.get('trade_name', name)}</div></div>
        <div class="info-row"><div class="label">State</div><div class="value">{taxpayer.get('state', 'Maharashtra')}</div></div>
        <div class="info-row"><div class="label">Registration Date</div><div class="value">{taxpayer.get('registration_date', '2020-01-01')}</div></div>
        <div class="info-row"><div class="label">Business Type</div><div class="value">{taxpayer.get('business_type', 'SME')}</div></div>
        <div class="info-row"><div class="label">Status</div><div class="value"><span class="badge badge-success">{taxpayer.get('status', 'ACTIVE')}</span></div></div>
      </div>
    </div>"""
    return render("Taxpayer Info", content, user_info)


# ─── API ENDPOINTS (for backend to call directly) ────────────
@app.route("/api/validate-gstin/<gstin>")
def api_validate(gstin):
    taxpayer = GSTIN_DB.get(gstin.upper())
    if taxpayer:
        return jsonify({"valid": True, "taxpayer": taxpayer})
    if len(gstin) == 15:
        return jsonify({"valid": True, "taxpayer": {"legal_name": f"Business {gstin[-4:]}", "status": "ACTIVE", "state": "Maharashtra"}})
    return jsonify({"valid": False, "error": "Invalid GSTIN"}), 400


@app.route("/api/refund-status/<arn>")
def api_refund_status(arn):
    app_data = REFUND_APPLICATIONS.get(arn)
    if app_data:
        return jsonify({"success": True, "application": app_data})
    statuses = ["PENDING_SCRUTINY", "DEFICIENCY_MEMO", "SANCTIONED"]
    return jsonify({"success": True, "arn": arn, "status": random.choice(statuses), "amount": random.randint(100000, 1000000)})


@app.route("/api/applications/<gstin>")
def api_applications(gstin):
    apps = {k: v for k, v in REFUND_APPLICATIONS.items() if v["gstin"] == gstin.upper()}
    return jsonify({"success": True, "applications": list(apps.values()), "count": len(apps)})


if __name__ == "__main__":
    print("🟢 GST Portal running at http://localhost:8001")
    app.run(port=8001, debug=True)

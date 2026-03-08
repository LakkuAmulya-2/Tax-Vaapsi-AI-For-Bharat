"""
TAX VAAPSI - DUMMY INCOME TAX PORTAL
Actual running web server simulating eportal.incometax.gov.in
Port: 8002
Playwright automation will navigate this real web portal
"""
from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
import random, uuid, json
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = "taxvaapsi-it-portal-secret"
CORS(app)

PAN_DB = {
    "AABCU9603R": {"name": "ABC Exports Pvt Ltd", "dob": "1980-06-15", "status": "VALID", "email": "abc@exports.com", "password": "password123"},
    "AADCB2230M": {"name": "XYZ Manufacturing", "dob": "1975-03-22", "status": "VALID", "email": "xyz@mfg.com", "password": "password123"},
}

ITR_SUBMISSIONS = {}

BASE_HTML = """<!DOCTYPE html>
<html><head>
  <meta charset="UTF-8">
  <title>e-Filing Portal - {title}</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family: Arial, sans-serif; background:#f5f5f5;}}
    .header{{background: #003580; color:white; padding:12px 20px; display:flex; align-items:center; gap:15px;}}
    .header h1{{font-size:18px;}}
    .header p{{font-size:11px; opacity:0.8;}}
    .nav{{background: #0050a0; padding:8px 20px;}}
    .nav a{{color:white; text-decoration:none; margin-right:18px; font-size:13px;}}
    .container{{max-width:1100px; margin:25px auto; padding:0 20px;}}
    .card{{background:white; border-radius:4px; padding:25px; margin-bottom:20px; box-shadow:0 1px 4px rgba(0,0,0,0.1);}}
    .card h2{{font-size:17px; color:#003580; border-bottom:2px solid #e0e0e0; padding-bottom:10px; margin-bottom:20px;}}
    .form-group{{margin-bottom:15px;}}
    .form-group label{{display:block; font-size:13px; font-weight:bold; margin-bottom:5px; color:#333;}}
    .form-group input,.form-group select,.form-group textarea{{width:100%; padding:8px 12px; border:1px solid #ccc; border-radius:3px; font-size:14px;}}
    .btn{{padding:10px 22px; border:none; border-radius:3px; cursor:pointer; font-size:14px; font-weight:bold;}}
    .btn-primary{{background:#003580; color:white;}}
    .btn-primary:hover{{background:#0050a0;}}
    .btn-success{{background:#28a745; color:white; margin-left:10px;}}
    .alert{{padding:12px 16px; border-radius:4px; margin-bottom:16px; font-size:14px;}}
    .alert-success{{background:#d4edda; color:#155724; border:1px solid #c3e6cb;}}
    .alert-danger{{background:#f8d7da; color:#721c24;}}
    .alert-info{{background:#d1ecf1; color:#0c5460;}}
    .badge{{display:inline-block; padding:3px 8px; border-radius:3px; font-size:12px; font-weight:bold;}}
    .badge-success{{background:#28a745; color:white;}}
    .badge-warning{{background:#ffc107; color:black;}}
    .badge-danger{{background:#dc3545; color:white;}}
    .badge-info{{background:#17a2b8; color:white;}}
    table{{width:100%; border-collapse:collapse; font-size:13px;}}
    th{{background:#003580; color:white; padding:10px; text-align:left;}}
    td{{padding:10px; border-bottom:1px solid #eee;}}
    tr:hover{{background:#f9f9f9;}}
    .sidebar{{display:flex; gap:20px;}}
    .sidebar-menu{{width:220px; background:white; border-radius:4px; padding:15px; box-shadow:0 1px 4px rgba(0,0,0,0.1); height:fit-content;}}
    .sidebar-menu a{{display:block; padding:8px 12px; color:#333; text-decoration:none; font-size:13px; border-radius:3px; margin-bottom:4px;}}
    .sidebar-menu a:hover,.sidebar-menu a.active{{background:#e3f2fd; color:#003580; font-weight:bold;}}
    .sidebar-content{{flex:1;}}
    .amount-big{{font-size:28px; font-weight:bold; color:#003580;}}
    .footer{{background:#003580; color:white; padding:20px; text-align:center; font-size:12px; margin-top:40px;}}
    .req{{color:red;}}
    .grid-2{{display:grid; grid-template-columns:1fr 1fr; gap:15px;}}
    .deduction-item{{padding:12px; border:1px solid #eee; border-radius:4px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;}}
    .deduction-item:hover{{background:#f9f9f9;}}
  </style>
</head><body>
  <div class="header">
    <div style="font-size:20px; font-weight:bold;">🇮🇳</div>
    <div>
      <h1>Income Tax e-Filing Portal</h1>
      <p>Government of India | Income Tax Department | CBDT</p>
    </div>
    <div style="margin-left:auto; font-size:13px; text-align:right;">{user_info}</div>
  </div>
  <div class="nav">
    <a href="/">Home</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/itr/file">File ITR</a>
    <a href="/refund/status">Refund Status</a>
    <a href="/form26as">Form 26AS</a>
    <a href="/notices">Notices</a>
    <a href="/deductions">Deductions</a>
  </div>
  {content}
  <div class="footer"><p>© 2024 Income Tax Department, Ministry of Finance, Government of India</p><p>Helpdesk: 1800-103-0025 | CPC Bangalore: 1800-425-2229</p></div>
</body></html>"""


def render(title, content, user_info=""):
    return BASE_HTML.format(title=title, content=content, user_info=user_info)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "pan" not in session:
            return redirect("/login?next=" + request.path)
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def home():
    content = """
    <div class="container">
      <div style="background:linear-gradient(135deg,#003580,#0050a0); color:white; padding:40px; border-radius:8px; margin-bottom:25px; text-align:center;">
        <h2 style="font-size:26px; margin-bottom:10px;">Income Tax e-Filing Portal</h2>
        <p style="opacity:0.9;">File ITR | Claim Refund | Respond to Notices | Check 26AS</p>
        <a href="/login" class="btn btn-primary" style="margin-top:20px; background:white; color:#003580; display:inline-block;">Login / Register</a>
      </div>
      <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:15px;">
        <div class="card" style="text-align:center; padding:15px;"><div style="font-size:35px;">📝</div><h3 style="margin:10px 0 5px; font-size:14px;">File ITR</h3><p style="font-size:12px; color:#666;">ITR-1 to ITR-7</p></div>
        <div class="card" style="text-align:center; padding:15px;"><div style="font-size:35px;">💰</div><h3 style="margin:10px 0 5px; font-size:14px;">Track Refund</h3><p style="font-size:12px; color:#666;">Check refund status</p></div>
        <div class="card" style="text-align:center; padding:15px;"><div style="font-size:35px;">📄</div><h3 style="margin:10px 0 5px; font-size:14px;">Form 26AS/AIS</h3><p style="font-size:12px; color:#666;">Tax credit statement</p></div>
        <div class="card" style="text-align:center; padding:15px;"><div style="font-size:35px;">⚖️</div><h3 style="margin:10px 0 5px; font-size:14px;">e-Proceedings</h3><p style="font-size:12px; color:#666;">Notice responses</p></div>
      </div>
    </div>"""
    return render("Home", content)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        pan = request.form.get("pan", "").upper().strip()
        password = request.form.get("password", "")
        taxpayer = PAN_DB.get(pan)
        if taxpayer and password:
            session["pan"] = pan
            session["name"] = taxpayer["name"]
            return redirect(request.args.get("next", "/dashboard"))
        elif len(pan) == 10 and pan[:5].isalpha() and pan[5:9].isdigit() and pan[9].isalpha() and password:
            session["pan"] = pan
            session["name"] = f"Taxpayer {pan[-4:]}"
            return redirect(request.args.get("next", "/dashboard"))
        else:
            error = "Invalid PAN or Password."

    content = f"""
    <div class="container" style="max-width:500px;">
      <div class="card" style="margin-top:40px;">
        <h2>Login to e-Filing Portal</h2>
        {'<div class="alert alert-danger">' + error + '</div>' if error else ''}
        <form method="POST" id="itLoginForm">
          <div class="form-group">
            <label>PAN <span class="req">*</span></label>
            <input type="text" name="pan" id="pan" placeholder="e.g. AABCU9603R" maxlength="10" style="text-transform:uppercase;" required>
          </div>
          <div class="form-group">
            <label>Password <span class="req">*</span></label>
            <input type="password" name="password" id="password" required>
          </div>
          <button type="submit" class="btn btn-primary" id="itLoginBtn">Login</button>
        </form>
        <div style="margin-top:20px; padding:12px; background:#f0f4ff; border-radius:4px; font-size:12px;">
          <strong>Demo:</strong> PAN: AABCU9603R | Password: password123
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
    pan = session["pan"]
    name = session.get("name", pan)
    user_info = f"<strong>{name}</strong><br>PAN: {pan} | <a href='/logout' style='color:#aed6f1;'>Logout</a>"

    refund = random.randint(20000, 150000)
    content = f"""
    <div class="container">
      <div class="alert alert-info" style="margin-top:20px;">👋 Welcome, <strong>{name}</strong>! Assessment Year 2024-25</div>
      <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:15px; margin-bottom:25px;">
        <div class="card" style="text-align:center; padding:15px;">
          <div style="font-size:13px; color:#666; margin-bottom:5px;">Pending Refund</div>
          <div class="amount-big">₹{refund:,.0f}</div>
          <div style="font-size:11px; color:#28a745; margin-top:5px;">In Processing</div>
        </div>
        <div class="card" style="text-align:center; padding:15px;">
          <div style="font-size:13px; color:#666; margin-bottom:5px;">TDS Deducted</div>
          <div class="amount-big" style="color:#0050a0;">₹{random.randint(80000,400000):,.0f}</div>
        </div>
        <div class="card" style="text-align:center; padding:15px;">
          <div style="font-size:13px; color:#666; margin-bottom:5px;">Tax Savings Possible</div>
          <div class="amount-big" style="color:#28a745;">₹{random.randint(30000,120000):,.0f}</div>
          <div style="font-size:11px; color:#28a745; margin-top:5px;">via Deductions</div>
        </div>
        <div class="card" style="text-align:center; padding:15px;">
          <div style="font-size:13px; color:#666; margin-bottom:5px;">Pending Notices</div>
          <div class="amount-big" style="color:#dc3545;">{random.randint(0,2)}</div>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:2fr 1fr; gap:20px;">
        <div class="card">
          <h2>Quick Actions</h2>
          <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:12px;">
            <a href="/itr/file" style="display:block; padding:15px; background:#e3f2fd; border-radius:4px; text-decoration:none; color:#003580; text-align:center;">
              <div style="font-size:24px;">📝</div><div style="font-weight:bold; margin-top:5px;">File ITR</div><div style="font-size:12px; color:#666;">ITR-1/2/3/4</div>
            </a>
            <a href="/deductions" style="display:block; padding:15px; background:#e8f5e9; border-radius:4px; text-decoration:none; color:#003580; text-align:center;">
              <div style="font-size:24px;">💡</div><div style="font-weight:bold; margin-top:5px;">Find Deductions</div><div style="font-size:12px; color:#666;">80C, 80D, 80G...</div>
            </a>
            <a href="/form26as" style="display:block; padding:15px; background:#fff3e0; border-radius:4px; text-decoration:none; color:#003580; text-align:center;">
              <div style="font-size:24px;">📄</div><div style="font-weight:bold; margin-top:5px;">Form 26AS</div><div style="font-size:12px; color:#666;">TDS Credit Statement</div>
            </a>
            <a href="/refund/status" style="display:block; padding:15px; background:#fce4ec; border-radius:4px; text-decoration:none; color:#003580; text-align:center;">
              <div style="font-size:24px;">🔍</div><div style="font-weight:bold; margin-top:5px;">Track Refund</div><div style="font-size:12px; color:#666;">Refund Status</div>
            </a>
          </div>
        </div>
        <div class="card">
          <h2>Filing Deadlines</h2>
          <div style="font-size:13px;">
            <div style="padding:8px 0; border-bottom:1px solid #eee; display:flex; justify-content:space-between;"><span>ITR Filing</span><span class="badge badge-warning">31 Jul</span></div>
            <div style="padding:8px 0; border-bottom:1px solid #eee; display:flex; justify-content:space-between;"><span>Advance Tax Q4</span><span class="badge badge-warning">15 Mar</span></div>
            <div style="padding:8px 0; border-bottom:1px solid #eee; display:flex; justify-content:space-between;"><span>TDS Return Q3</span><span class="badge badge-success">Filed</span></div>
            <div style="padding:8px 0; display:flex; justify-content:space-between;"><span>Belated ITR</span><span class="badge badge-danger">31 Dec</span></div>
          </div>
        </div>
      </div>
    </div>"""
    return render("Dashboard", content, user_info)


@app.route("/itr/file", methods=["GET", "POST"])
@login_required
def file_itr():
    pan = session["pan"]
    name = session.get("name", pan)
    user_info = f"<strong>{name}</strong><br>PAN: {pan} | <a href='/logout' style='color:#aed6f1;'>Logout</a>"

    ack = None
    if request.method == "POST":
        ack_num = f"23{pan[0:4]}{random.randint(100000000, 999999999)}"
        ITR_SUBMISSIONS[pan] = {
            "ack_number": ack_num,
            "pan": pan,
            "ay": request.form.get("assessment_year", "2024-25"),
            "itr_form": request.form.get("itr_form", "ITR-3"),
            "gross_income": request.form.get("gross_income", "0"),
            "total_deductions": request.form.get("total_deductions", "0"),
            "tax_payable": request.form.get("tax_payable", "0"),
            "refund_amount": request.form.get("refund_amount", "0"),
            "filed_date": datetime.now().isoformat(),
            "status": "FILED_PENDING_VERIFICATION",
        }
        ack = ack_num

    content = f"""
    <div class="container">
      <div class="card" style="margin-top:20px;">
        <h2>File Income Tax Return</h2>
        {'<div class="alert alert-success">✅ ITR Filed Successfully! Acknowledgement No: <strong id="ack-number">' + ack + '</strong><br>Please e-verify within 30 days.</div>' if ack else ''}
        <form method="POST" id="itrForm">
          <div class="grid-2">
            <div class="form-group">
              <label>PAN</label>
              <input type="text" value="{pan}" readonly style="background:#f5f5f5;">
            </div>
            <div class="form-group">
              <label>Assessment Year <span class="req">*</span></label>
              <select name="assessment_year" id="assessment_year" required>
                <option value="2024-25">2024-25</option>
                <option value="2023-24">2023-24</option>
                <option value="2022-23">2022-23</option>
              </select>
            </div>
            <div class="form-group">
              <label>ITR Form <span class="req">*</span></label>
              <select name="itr_form" id="itr_form" required>
                <option value="ITR-1">ITR-1 (Salary + House Property)</option>
                <option value="ITR-2">ITR-2 (Capital Gains)</option>
                <option value="ITR-3" selected>ITR-3 (Business/Profession)</option>
                <option value="ITR-4">ITR-4 (Presumptive Income)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Tax Regime <span class="req">*</span></label>
              <select name="tax_regime" id="tax_regime" required>
                <option value="NEW">New Regime (Default)</option>
                <option value="OLD">Old Regime (with deductions)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Gross Total Income (₹) <span class="req">*</span></label>
              <input type="number" name="gross_income" id="gross_income" placeholder="0" required>
            </div>
            <div class="form-group">
              <label>Total Deductions (₹)</label>
              <input type="number" name="total_deductions" id="total_deductions" placeholder="0">
            </div>
            <div class="form-group">
              <label>Total Tax Payable (₹)</label>
              <input type="number" name="tax_payable" id="tax_payable" placeholder="Auto-calculated">
            </div>
            <div class="form-group">
              <label>TDS Paid (₹)</label>
              <input type="number" name="tds_paid" id="tds_paid" placeholder="From Form 26AS">
            </div>
            <div class="form-group">
              <label>Advance Tax Paid (₹)</label>
              <input type="number" name="advance_tax" id="advance_tax" placeholder="0">
            </div>
            <div class="form-group">
              <label>Refund Amount (₹)</label>
              <input type="number" name="refund_amount" id="refund_amount" placeholder="Auto-calculated">
            </div>
            <div class="form-group">
              <label>Bank Account (for refund credit) <span class="req">*</span></label>
              <input type="text" name="bank_account" id="bank_account" placeholder="Enter account number" required>
            </div>
            <div class="form-group">
              <label>Bank IFSC <span class="req">*</span></label>
              <input type="text" name="bank_ifsc" id="bank_ifsc" placeholder="e.g. SBIN0000123" required>
            </div>
          </div>
          <div class="form-group">
            <label><input type="checkbox" id="itr_declaration" name="declaration" required style="width:auto; margin-right:8px;">
            I declare that the information provided is true and correct.</label>
          </div>
          <button type="submit" class="btn btn-primary" id="itrSubmitBtn">Submit ITR</button>
          <button type="button" class="btn btn-success" onclick="previewReturn()">Preview</button>
        </form>
      </div>
    </div>
    <script>
      function previewReturn() {{ alert('Preview: ITR-3 for AY 2024-25\\nGross Income: ₹' + document.getElementById('gross_income').value || '0'); }}
    </script>"""
    return render("File ITR", content, user_info)


@app.route("/form26as")
@login_required
def form26as():
    pan = session["pan"]
    name = session.get("name", pan)
    user_info = f"<strong>{name}</strong><br>PAN: {pan} | <a href='/logout' style='color:#aed6f1;'>Logout</a>"

    entries = [
        {"deductor": "Employer Pvt Ltd", "tan": "MUML12345E", "section": "192", "nature": "Salary", "gross": 2400000, "tds": 360000, "deposited": 360000, "q": "Q4"},
        {"deductor": "Bank of India", "tan": "BOMK98765A", "section": "194A", "nature": "Interest", "gross": 85000, "tds": 8500, "deposited": 7500, "q": "Q3"},
        {"deductor": "Client Corp", "tan": "DELC54321B", "section": "194J", "nature": "Professional Fees", "gross": 500000, "tds": 50000, "deposited": 50000, "q": "Q4"},
    ]

    rows = ""
    total_tds = 0
    total_dep = 0
    for e in entries:
        mismatch = e["tds"] - e["deposited"]
        total_tds += e["tds"]
        total_dep += e["deposited"]
        rows += f"""<tr>
          <td>{e['deductor']}</td><td>{e['tan']}</td><td>{e['section']}</td>
          <td>{e['nature']}</td><td>₹{e['gross']:,.0f}</td><td>₹{e['tds']:,.0f}</td>
          <td>₹{e['deposited']:,.0f}</td><td>{e['q']}</td>
          <td>{'<span class="badge badge-danger">₹' + str(mismatch) + ' Mismatch!</span>' if mismatch > 0 else '<span class="badge badge-success">OK</span>'}</td>
        </tr>"""

    content = f"""
    <div class="container">
      <div class="card" style="margin-top:20px;">
        <h2>Form 26AS - Tax Credit Statement</h2>
        <div style="display:flex; gap:20px; margin-bottom:20px;">
          <div class="form-group" style="margin:0;">
            <label>PAN</label>
            <input type="text" value="{pan}" id="form26as_pan" readonly style="background:#f5f5f5; width:200px;">
          </div>
          <div class="form-group" style="margin:0;">
            <label>Financial Year</label>
            <select id="fy_selector" style="width:150px; padding:8px; border:1px solid #ccc; border-radius:3px;">
              <option value="2023-24" selected>2023-24</option>
              <option value="2022-23">2022-23</option>
              <option value="2021-22">2021-22</option>
            </select>
          </div>
          <div style="display:flex; align-items:flex-end;">
            <button class="btn btn-primary" id="view26asBtn">View Statement</button>
          </div>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:15px; margin-bottom:20px;">
          <div style="padding:15px; background:#e3f2fd; border-radius:4px; text-align:center;">
            <div style="font-size:12px; color:#666;">Total TDS Deducted</div>
            <div id="total_tds" style="font-size:22px; font-weight:bold; color:#003580;">₹{total_tds:,.0f}</div>
          </div>
          <div style="padding:15px; background:#e8f5e9; border-radius:4px; text-align:center;">
            <div style="font-size:12px; color:#666;">Total Deposited</div>
            <div style="font-size:22px; font-weight:bold; color:#28a745;">₹{total_dep:,.0f}</div>
          </div>
          <div style="padding:15px; background:#fce4ec; border-radius:4px; text-align:center;">
            <div style="font-size:12px; color:#666;">Mismatch Amount</div>
            <div id="tds_mismatch" style="font-size:22px; font-weight:bold; color:#dc3545;">₹{total_tds-total_dep:,.0f}</div>
          </div>
        </div>
        <h3 style="font-size:14px; margin-bottom:10px;">Part A - TDS Deducted</h3>
        <table>
          <thead><tr><th>Deductor Name</th><th>TAN</th><th>Section</th><th>Nature</th><th>Gross Amount</th><th>TDS Deducted</th><th>TDS Deposited</th><th>Quarter</th><th>Status</th></tr></thead>
          <tbody id="tds_table_body">{rows}</tbody>
        </table>
      </div>
    </div>"""
    return render("Form 26AS", content, user_info)


@app.route("/deductions")
@login_required
def deductions():
    pan = session["pan"]
    name = session.get("name", pan)
    user_info = f"<strong>{name}</strong><br>PAN: {pan} | <a href='/logout' style='color:#aed6f1;'>Logout</a>"

    deductions_list = [
        ("80C", "Life Insurance, PPF, ELSS, EPF", 150000, 0, 45000),
        ("80D", "Medical Insurance Premium", 75000, 25000, 22500),
        ("80E", "Education Loan Interest", None, 0, 18000),
        ("80G", "Donations to charitable institutions", None, 0, 5000),
        ("HRA", "House Rent Allowance", None, 0, 36000),
        ("24B", "Home Loan Interest", 200000, 0, 60000),
        ("80CCD(1B)", "NPS Additional Contribution", 50000, 0, 15000),
        ("80TTA", "Interest from Savings Account", 10000, 10000, 0),
    ]

    rows = ""
    total_saving = 0
    for section, desc, limit, claimed, potential_saving in deductions_list:
        rows += f"""
        <div class="deduction-item">
          <div>
            <div style="font-weight:bold; font-size:14px;">Section {section}</div>
            <div style="font-size:12px; color:#666; margin-top:3px;">{desc}</div>
            <div style="font-size:12px; color:#999; margin-top:2px;">Limit: {'No limit' if not limit else '₹' + str(limit)}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:13px; color:#666;">Claimed: ₹{claimed:,}</div>
            <div style="font-size:15px; font-weight:bold; color:#28a745; margin-top:3px;">Save ₹{potential_saving:,}</div>
          </div>
        </div>"""
        total_saving += potential_saving

    content = f"""
    <div class="container">
      <div class="alert alert-success" style="margin-top:20px;">
        💡 <strong>Tax Vaapsi AI found ₹{total_saving:,} in additional tax savings!</strong> 
        These deductions may be available for you.
      </div>
      <div class="card">
        <h2>Deduction Optimizer - 40+ Sections Scanned</h2>
        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:15px; margin-bottom:20px;">
          <div style="padding:15px; background:#e8f5e9; border-radius:4px; text-align:center;">
            <div style="font-size:12px; color:#666;">Total Potential Savings</div>
            <div id="total_savings" style="font-size:24px; font-weight:bold; color:#28a745;">₹{total_saving:,}</div>
          </div>
          <div style="padding:15px; background:#e3f2fd; border-radius:4px; text-align:center;">
            <div style="font-size:12px; color:#666;">Deductions Available</div>
            <div style="font-size:24px; font-weight:bold; color:#003580;">{len(deductions_list)}</div>
          </div>
          <div style="padding:15px; background:#fff3e0; border-radius:4px; text-align:center;">
            <div style="font-size:12px; color:#666;">Recommended Regime</div>
            <div id="recommended_regime" style="font-size:20px; font-weight:bold; color:#f57c00;">OLD REGIME</div>
          </div>
        </div>
        {rows}
      </div>
    </div>"""
    return render("Deductions", content, user_info)


@app.route("/refund/status")
@login_required
def refund_status():
    pan = session["pan"]
    name = session.get("name", pan)
    user_info = f"<strong>{name}</strong><br>PAN: {pan} | <a href='/logout' style='color:#aed6f1;'>Logout</a>"

    sub = ITR_SUBMISSIONS.get(pan, {})
    refund_amount = random.randint(15000, 85000)

    content = f"""
    <div class="container">
      <div class="card" style="margin-top:20px;">
        <h2>Refund Status</h2>
        <div class="form-group" style="max-width:400px;">
          <label>PAN</label>
          <input type="text" id="refund_pan" value="{pan}" style="background:#f5f5f5;" readonly>
        </div>
        <div class="form-group" style="max-width:400px;">
          <label>Assessment Year</label>
          <select id="refund_ay">
            <option value="2024-25" selected>2024-25</option>
            <option value="2023-24">2023-24</option>
          </select>
        </div>
        <button class="btn btn-primary" id="checkRefundBtn" onclick="checkRefund()">Check Refund Status</button>
        <div id="refundStatusResult" style="margin-top:20px;">
          <div style="padding:20px; background:#e8f5e9; border-radius:4px; border-left:4px solid #28a745;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div>
                <div style="font-size:12px; color:#666;">Acknowledgement No:</div>
                <div style="font-weight:bold;">{sub.get('ack_number', 'ACK2024ABCDE12345')}</div>
              </div>
              <div>
                <div style="font-size:12px; color:#666;">Status:</div>
                <span class="badge badge-{'success' if not sub else 'warning'}">{'REFUND_ISSUED' if not sub else 'PROCESSING'}</span>
              </div>
              <div>
                <div style="font-size:12px; color:#666;">Refund Amount:</div>
                <div id="it_refund_amount" style="font-size:22px; font-weight:bold; color:#28a745;">₹{refund_amount:,}</div>
              </div>
            </div>
            <div style="margin-top:12px; font-size:13px; color:#666;">
              Refund credited to Bank Account: XXXX{''.join([str(random.randint(0,9)) for _ in range(4)])} | NEFT Mode
            </div>
          </div>
        </div>
      </div>
    </div>
    <script>
      function checkRefund() {{
        document.getElementById('checkRefundBtn').textContent = 'Checking...';
        setTimeout(() => {{
          document.getElementById('checkRefundBtn').textContent = 'Check Refund Status';
          document.getElementById('refundStatusResult').style.display = 'block';
        }}, 1500);
      }}
    </script>"""
    return render("Refund Status", content, user_info)


@app.route("/notices")
@login_required
def notices():
    pan = session["pan"]
    name = session.get("name", pan)
    user_info = f"<strong>{name}</strong><br>PAN: {pan} | <a href='/logout' style='color:#aed6f1;'>Logout</a>"

    content = f"""
    <div class="container">
      <div class="card" style="margin-top:20px;">
        <h2>Notices & Proceedings</h2>
        <table>
          <thead><tr><th>Notice No.</th><th>Section</th><th>Description</th><th>Date</th><th>Due Date</th><th>Demand</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            <tr>
              <td>NOT143/2024/001</td><td>143(1)</td><td>Intimation u/s 143(1) - Demand raised</td>
              <td>2024-10-01</td><td style="color:red; font-weight:bold;">2025-03-25</td>
              <td>₹35,000</td><td><span class="badge badge-danger">Response Pending</span></td>
              <td><a href="/notices/respond/001" style="color:#003580; font-size:12px;">Respond</a></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>"""
    return render("Notices", content, user_info)


@app.route("/notices/respond/<nid>", methods=["GET", "POST"])
@login_required
def respond_notice(nid):
    pan = session["pan"]
    name = session.get("name", pan)
    user_info = f"<strong>{name}</strong><br>PAN: {pan} | <a href='/logout' style='color:#aed6f1;'>Logout</a>"
    submitted = request.method == "POST"
    ack = f"NRESP{random.randint(10000000, 99999999)}" if submitted else ""

    content = f"""
    <div class="container">
      <div class="card" style="margin-top:20px;">
        <h2>Respond to Notice</h2>
        {'<div class="alert alert-success">✅ Response submitted! Ack: <strong>' + ack + '</strong></div>' if submitted else ''}
        <form method="POST" enctype="multipart/form-data">
          <div class="form-group">
            <label>Notice Reference</label>
            <input value="NOT143/2024/{nid}" readonly style="background:#f5f5f5;">
          </div>
          <div class="form-group">
            <label>Response <span class="req">*</span></label>
            <textarea name="response_text" id="it_notice_response" rows="8" required placeholder="Enter your response..."></textarea>
          </div>
          <div class="form-group">
            <label>Attach Documents</label>
            <input type="file" name="docs" multiple accept=".pdf">
          </div>
          <button type="submit" class="btn btn-primary" id="itNoticeSubmitBtn">Submit Response</button>
        </form>
      </div>
    </div>"""
    return render("Respond to Notice", content, user_info)


# ─── API ENDPOINTS ────────────────────────────────────────────
@app.route("/api/validate-pan/<pan>")
def api_validate_pan(pan):
    pan = pan.upper()
    taxpayer = PAN_DB.get(pan)
    if taxpayer:
        return jsonify({"valid": True, "taxpayer": taxpayer})
    if len(pan) == 10:
        return jsonify({"valid": True, "taxpayer": {"name": f"Taxpayer {pan[-4:]}", "status": "VALID"}})
    return jsonify({"valid": False}), 400


@app.route("/api/refund-status/<pan>")
def api_refund_status(pan):
    sub = ITR_SUBMISSIONS.get(pan.upper(), {})
    return jsonify({
        "pan": pan.upper(),
        "assessment_year": "2024-25",
        "status": sub.get("status", "REFUND_ISSUED"),
        "refund_amount": random.randint(15000, 100000),
        "ack_number": sub.get("ack_number", f"ACK{random.randint(10000000000, 99999999999)}"),
    })


if __name__ == "__main__":
    print("🟢 IT Portal running at http://localhost:8002")
    app.run(port=8002, debug=True)

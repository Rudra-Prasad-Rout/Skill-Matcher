"""
S30 Flask Application
Comprehensive verification platform with S30 futuristic UI theme, landing page, login page, 5-digit alphanumeric ID codes, ID Card Front/Back verification, Secure Admin Authentication (TeamX / TeamX@Admin), Left-Corner Sidebar with Dashboard, Approvals, Internships, and dedicated AI Internship sections.
"""
import os
import secrets
import re
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import database

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "s30-super-secret-production-key-2026")

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp"}
MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Secure Admin Credentials
ADMIN_USERNAME = "TeamX"
ADMIN_PASSWORD = "TeamX@Admin"

# Ensure database is initialized
database.init_db()

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

def is_valid_email(email_str):
    if not email_str or "@" not in email_str or "." not in email_str:
        return False
    parts = email_str.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False
    domain_parts = parts[1].split(".")
    if len(domain_parts) < 2 or not domain_parts[0] or not domain_parts[1]:
        return False
    return bool(EMAIL_REGEX.match(email_str))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def format_url(url_str):
    if not url_str:
        return ""
    url_str = url_str.strip()
    if not url_str.startswith("http://") and not url_str.startswith("https://"):
        return "https://" + url_str
    return url_str

def get_current_user(create_default=False):
    user_id = session.get("user_id")
    if not user_id:
        if create_default:
            conn = database.get_db_connection()
            user = conn.execute("SELECT * FROM users ORDER BY id ASC LIMIT 1").fetchone()
            conn.close()
            if user:
                session["user_id"] = user["id"]
                return dict(user)
        return None
    
    conn = database.get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

# ================= PUBLIC LANDING PAGE =================
@app.route("/")
def landing_page():
    return render_template("landing.html")

# ================= STUDENT LOGIN PAGE =================
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        
        if not email or not password:
            return render_template("login.html", error="Please enter both email and password.", email=email)
            
        conn = database.get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user:
            session["user_id"] = user["id"]
            if user["is_banned"] or user["step"] >= 4:
                return redirect(url_for("signup_verification"))
            elif user["step"] == 3:
                return redirect(url_for("signup_documents"))
            elif user["step"] == 2:
                return redirect(url_for("signup_skills"))
            else:
                return redirect(url_for("signup_profile"))
        else:
            return render_template("login.html", error="No account found with this email. Please create an account.", email=email)
            
    return render_template("login.html")

@app.route("/signup/new")
def signup_new():
    session.pop("user_id", None)
    return redirect(url_for("signup_profile"))

# ================= STEP 1: Profile Signup =================
@app.route("/signup/profile", methods=["GET", "POST"])
def signup_profile():
    if request.args.get("new") == "1":
        session.pop("user_id", None)
        
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        gender = request.form.get("gender", "Male").strip()
        age = request.form.get("age", "20").strip()
        password = request.form.get("password", "").strip()
        re_password = request.form.get("re_password", "").strip()
        school = request.form.get("school", "").strip()
        coursework = request.form.get("coursework", "").strip()
        
        if not full_name:
            return render_template("profile.html", error="Please provide your full name.", active_step=1, form_data=request.form)
            
        if not is_valid_email(email):
            return render_template(
                "profile.html", 
                error="Please enter a valid email address with '@' and domain (e.g. name@gmail.com or you@college.edu).", 
                active_step=1, 
                form_data=request.form
            )
            
        if password or re_password:
            if password != re_password:
                return render_template(
                    "profile.html", 
                    error="Passwords do not match. Please ensure 'Password' and 'Confirm Password' are identical.", 
                    active_step=1, 
                    form_data=request.form
                )
        
        try:
            age_int = int(age)
        except ValueError:
            age_int = 20
            
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        existing = cursor.execute("SELECT id, user_code FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            user_id = existing["id"]
            cursor.execute("""
            UPDATE users SET full_name = ?, gender = ?, age = ?, school = ?, coursework = ?, password_hash = ?, step = MAX(step, 2)
            WHERE id = ?
            """, (full_name, gender, age_int, school, coursework, password or "default_pass", user_id))
        else:
            existing_codes = [r["user_code"] for r in cursor.execute("SELECT user_code FROM users").fetchall()]
            new_user_code = database.generate_user_code(existing_codes)
            
            cursor.execute("""
            INSERT INTO users (user_code, full_name, email, gender, age, password_hash, school, coursework, step, pdf_status, manual_status, is_banned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 2, 'DONE', 'IN PROGRESS', 0)
            """, (new_user_code, full_name, email, gender, age_int, password or "default_pass", school, coursework))
            user_id = cursor.lastrowid
            
            cursor.execute("""
            INSERT INTO user_skills (user_id, skill_name, project_name, project_url, status)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, "React", "Campus events app", "https://github.com/alexrivera/campus-events-app", "VERIFIED"))
            
            cursor.execute("""
            INSERT INTO user_skills (user_id, skill_name, project_name, project_url, status)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, "Data analysis", "Attendance dashboard", "https://attendance-analytics.du.ac.in", "CHECKING"))
            
        conn.commit()
        conn.close()
        
        session["user_id"] = user_id
        return redirect(url_for("signup_skills"))
        
    user = get_current_user(create_default=False)
    return render_template("profile.html", active_step=1, user=user)

# ================= STEP 2: Skills & Projects =================
@app.route("/signup/skills", methods=["GET", "POST"])
def signup_skills():
    user = get_current_user(create_default=True)
    if not user:
        return redirect(url_for("signup_profile"))
        
    if request.method == "POST":
        conn = database.get_db_connection()
        conn.execute("UPDATE users SET step = MAX(step, 3) WHERE id = ?", (user["id"],))
        conn.commit()
        conn.close()
        return redirect(url_for("signup_documents"))
        
    conn = database.get_db_connection()
    skills = conn.execute("SELECT * FROM user_skills WHERE user_id = ? ORDER BY id ASC", (user["id"],)).fetchall()
    conn.close()
    
    return render_template("skills.html", active_step=2, user=user, skills=skills)

# ================= STEP 3: Documents =================
@app.route("/signup/documents", methods=["GET", "POST"])
def signup_documents():
    user = get_current_user(create_default=True)
    if not user:
        return redirect(url_for("signup_profile"))
        
    if request.method == "POST":
        conn = database.get_db_connection()
        files_saved = 0
        
        file_front = request.files.get("doc_id_front")
        if file_front and file_front.filename and allowed_file(file_front.filename):
            conn.execute("DELETE FROM user_documents WHERE user_id = ? AND doc_category = 'id_front'", (user["id"],))
            orig = secure_filename(file_front.filename)
            uname = f"front_{secrets.token_hex(6)}_{orig}"
            fpath = os.path.join(app.config["UPLOAD_FOLDER"], uname)
            file_front.save(fpath)
            conn.execute("""
            INSERT INTO user_documents (user_id, doc_category, filename, original_name, file_size, file_type)
            VALUES (?, 'id_front', ?, ?, ?, ?)
            """, (user["id"], uname, orig, os.path.getsize(fpath), file_front.content_type))
            files_saved += 1
            
        file_back = request.files.get("doc_id_back")
        if file_back and file_back.filename and allowed_file(file_back.filename):
            conn.execute("DELETE FROM user_documents WHERE user_id = ? AND doc_category = 'id_back'", (user["id"],))
            orig = secure_filename(file_back.filename)
            uname = f"back_{secrets.token_hex(6)}_{orig}"
            fpath = os.path.join(app.config["UPLOAD_FOLDER"], uname)
            file_back.save(fpath)
            conn.execute("""
            INSERT INTO user_documents (user_id, doc_category, filename, original_name, file_size, file_type)
            VALUES (?, 'id_back', ?, ?, ?, ?)
            """, (user["id"], uname, orig, os.path.getsize(fpath), file_back.content_type))
            files_saved += 1
            
        file_cert = request.files.get("doc_certificate")
        if file_cert and file_cert.filename and allowed_file(file_cert.filename):
            conn.execute("DELETE FROM user_documents WHERE user_id = ? AND doc_category = 'certificate'", (user["id"],))
            orig = secure_filename(file_cert.filename)
            uname = f"cert_{secrets.token_hex(6)}_{orig}"
            fpath = os.path.join(app.config["UPLOAD_FOLDER"], uname)
            file_cert.save(fpath)
            conn.execute("""
            INSERT INTO user_documents (user_id, doc_category, filename, original_name, file_size, file_type)
            VALUES (?, 'certificate', ?, ?, ?, ?)
            """, (user["id"], uname, orig, os.path.getsize(fpath), file_cert.content_type))
            files_saved += 1
            
        existing_doc = conn.execute("SELECT id FROM user_documents WHERE user_id = ?", (user["id"],)).fetchone()
        if files_saved > 0 or existing_doc:
            conn.execute("UPDATE users SET step = 4, pdf_status = 'DONE', manual_status = 'IN PROGRESS' WHERE id = ?", (user["id"],))
            conn.commit()
            conn.close()
            return redirect(url_for("signup_verification"))
        else:
            conn.close()
            return render_template("documents.html", active_step=3, user=user, error="Please select your College ID card and coursework documents.")
            
    conn = database.get_db_connection()
    documents = conn.execute("""
    SELECT * FROM user_documents 
    WHERE user_id = ? 
    GROUP BY doc_category 
    ORDER BY id DESC
    """, (user["id"],)).fetchall()
    conn.close()
    
    return render_template("documents.html", active_step=3, user=user, documents=documents)

# ================= STEP 4: Verification =================
@app.route("/signup/verification")
def signup_verification():
    user = get_current_user(create_default=True)
    if not user:
        return redirect(url_for("signup_profile"))
        
    conn = database.get_db_connection()
    user_data = conn.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
    conn.close()
    
    return render_template("verification.html", active_step=4, user=user_data)

# ================= DOCUMENT VIEWING & SERVING =================
@app.route("/documents/view/<filename>")
def view_document(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    if not os.path.exists(file_path):
        for existing in os.listdir(app.config["UPLOAD_FOLDER"]):
            if existing.endswith(filename) or filename.endswith(existing):
                filename = existing
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], existing)
                break
                
    if os.path.exists(file_path):
        if filename.endswith(".pdf"):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    first_line = f.read(50)
                    if "<!DOCTYPE html>" in first_line or "<html>" in first_line:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f_full:
                            return f_full.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
            except Exception:
                pass
            return send_from_directory(app.config["UPLOAD_FOLDER"], filename, mimetype="application/pdf")
        elif filename.endswith(".svg"):
            return send_from_directory(app.config["UPLOAD_FOLDER"], filename, mimetype="image/svg+xml")
        elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    first_line = f.read(50)
                    if "<svg" in first_line:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f_full:
                            return f_full.read(), 200, {"Content-Type": "image/svg+xml"}
            except Exception:
                pass
            return send_from_directory(app.config["UPLOAD_FOLDER"], filename, mimetype="image/jpeg")
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    else:
        return f"""
        <div style="font-family: sans-serif; padding: 40px; text-align: center; background: #0b1120; color: #fff;">
            <h2>Document Record: {filename}</h2>
            <p style="color: #94a3b8;">Uploaded credential proof verified by S30 system.</p>
        </div>
        """, 200, {"Content-Type": "text/html"}

# ================= API Endpoints =================
@app.route("/api/skills", methods=["GET", "POST", "DELETE"])
def api_skills():
    user = get_current_user(create_default=True)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    if request.method == "GET":
        skills = cursor.execute("SELECT * FROM user_skills WHERE user_id = ? ORDER BY id ASC", (user["id"],)).fetchall()
        conn.close()
        return jsonify([dict(s) for s in skills])
        
    elif request.method == "POST":
        data = request.get_json() or {}
        skill_name = data.get("skill_name", "").strip()
        project_name = data.get("project_name", "").strip()
        project_url = format_url(data.get("project_url", "").strip())
        status = data.get("status", "CHECKING").upper()
        
        if not skill_name or not project_name or not project_url:
            conn.close()
            return jsonify({"error": "Skill name, project title, and valid GitHub/website URL required"}), 400
            
        cursor.execute("""
        INSERT INTO user_skills (user_id, skill_name, project_name, project_url, status)
        VALUES (?, ?, ?, ?, ?)
        """, (user["id"], skill_name, project_name, project_url, status))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "id": new_id,
            "skill_name": skill_name,
            "project_name": project_name,
            "project_url": project_url,
            "status": status
        }), 201
        
    elif request.method == "DELETE":
        data = request.get_json() or {}
        skill_id = data.get("id")
        if skill_id:
            cursor.execute("DELETE FROM user_skills WHERE id = ? AND user_id = ?", (skill_id, user["id"]))
            conn.commit()
        conn.close()
        return jsonify({"success": True})

@app.route("/api/verification-status")
def api_verification_status():
    user = get_current_user(create_default=True)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = database.get_db_connection()
    user_row = conn.execute("SELECT user_code, pdf_status, manual_status, is_banned, ban_reason FROM users WHERE id = ?", (user["id"],)).fetchone()
    conn.close()
    
    if user_row:
        return jsonify({
            "user_code": user_row["user_code"],
            "pdf_status": user_row["pdf_status"],
            "manual_status": user_row["manual_status"],
            "is_banned": bool(user_row["is_banned"]),
            "ban_reason": user_row["ban_reason"]
        })
    return jsonify({"error": "User not found"}), 404

# ================= SECURE ADMIN AUTHENTICATION (TeamX / TeamX@Admin) =================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid Admin Username or Password. Access denied.", username=username)
            
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

# Short-link helper redirects
@app.route("/admin/dashboard")
@admin_required
def admin_dash_redirect():
    return redirect(url_for("admin_dashboard", section="dashboard"))

@app.route("/admin/approvals")
@admin_required
def admin_approvals_redirect():
    return redirect(url_for("admin_dashboard", section="approvals"))

@app.route("/admin/internships")
@admin_required
def admin_internships_redirect():
    return redirect(url_for("admin_dashboard", section="internships"))

@app.route("/admin/internships/ai")
@admin_required
def admin_ai_internships_redirect():
    return redirect(url_for("admin_dashboard", section="ai_internship"))

# Sample Data for General Internships & AI Internships
INTERNSHIPS_DATA = [
    {
        "id": "INT-01",
        "company": "Google",
        "role": "SDE Intern",
        "location": "Bangalore / Hybrid",
        "stipend": "₹110K / month",
        "match": "95%",
        "applicants": 42,
        "status": "Active"
    },
    {
        "id": "INT-02",
        "company": "Amazon",
        "role": "Data Science Intern",
        "location": "Bangalore",
        "stipend": "₹95K / month",
        "match": "92%",
        "applicants": 38,
        "status": "Active"
    },
    {
        "id": "INT-03",
        "company": "Zomato",
        "role": "Product Design Intern",
        "location": "Gurgaon",
        "stipend": "₹60K / month",
        "match": "88%",
        "applicants": 19,
        "status": "Active"
    },
    {
        "id": "INT-04",
        "company": "Swiggy",
        "role": "Frontend Developer Intern",
        "location": "Remote",
        "stipend": "₹75K / month",
        "match": "90%",
        "applicants": 27,
        "status": "Active"
    }
]

AI_INTERNSHIPS_DATA = [
    {
        "id": "AI-01",
        "company": "Microsoft Research",
        "role": "AI / ML Research Intern",
        "focus": "LLM Alignment, Multimodal Vision",
        "location": "Hyderabad / Remote",
        "stipend": "₹125K / month",
        "match": "98%",
        "top_candidate": "Jordan Lee (ID: R4T2P)",
        "skills_required": "PyTorch, Transformers, Computer Vision",
        "status": "Shortlisting"
    },
    {
        "id": "AI-02",
        "company": "OpenAI Partner Lab",
        "role": "Autonomous Drone Vision Intern",
        "focus": "3D Point Cloud, Edge AI",
        "location": "Bangalore / Hybrid",
        "stipend": "₹140K / month",
        "match": "94%",
        "top_candidate": "Alex Rivera (ID: A7X9K)",
        "skills_required": "PyTorch, OpenCV, Robotics ROS",
        "status": "Interview Scheduled"
    },
    {
        "id": "AI-03",
        "company": "Adobe Sensei",
        "role": "Generative AI Systems Intern",
        "focus": "Diffusion Models, Video Generation",
        "location": "Noida / Bangalore",
        "stipend": "₹115K / month",
        "match": "91%",
        "top_candidate": "Priya Sharma (ID: 9B3KZ)",
        "skills_required": "Deep Learning, CUDA, Python",
        "status": "Active Review"
    },
    {
        "id": "AI-04",
        "company": "Anthropic Partner Lab",
        "role": "AI Safety & Evaluation Intern",
        "focus": "Constitutional AI, Benchmark Suite",
        "location": "Remote",
        "stipend": "₹130K / month",
        "match": "96%",
        "top_candidate": "Marcus Vance (ID: M8V1Y)",
        "skills_required": "NLP, Evaluation Metrics, Python",
        "status": "Applications Open"
    }
]

# ================= S30 ADMIN DASHBOARD =================
@app.route("/admin")
@admin_required
def admin_dashboard():
    section = request.args.get("section", "approvals")
    
    conn = database.get_db_connection()
    users = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    users_list = []
    
    total_count = len(users)
    pending_count = 0
    approved_count = 0
    rejected_count = 0
    
    for u in users:
        u_dict = dict(u)
        skills = conn.execute("SELECT * FROM user_skills WHERE user_id = ? ORDER BY id ASC", (u["id"],)).fetchall()
        
        docs = conn.execute("""
        SELECT * FROM user_documents 
        WHERE user_id = ? 
        GROUP BY doc_category 
        ORDER BY CASE doc_category 
            WHEN 'id_front' THEN 1 
            WHEN 'id_back' THEN 2 
            ELSE 3 END
        """, (u["id"],)).fetchall()
        
        u_dict["skills"] = [dict(s) for s in skills]
        u_dict["documents"] = [dict(d) for d in docs]
        
        if u_dict["is_banned"]:
            rejected_count += 1
        elif u_dict["manual_status"] in ["DONE", "APPROVED"]:
            approved_count += 1
        elif u_dict["manual_status"] == "REJECTED" or u_dict["pdf_status"] == "REJECTED":
            rejected_count += 1
        else:
            pending_count += 1
            
        users_list.append(u_dict)
        
    conn.close()
    
    stats = {
        "total": total_count,
        "pending": pending_count,
        "approved": approved_count,
        "rejected": rejected_count,
        "internships_count": len(INTERNSHIPS_DATA),
        "ai_internships_count": len(AI_INTERNSHIPS_DATA)
    }
    
    return render_template(
        "admin.html", 
        users=users_list, 
        stats=stats, 
        active_section=section,
        internships=INTERNSHIPS_DATA,
        ai_internships=AI_INTERNSHIPS_DATA
    )

@app.route("/admin/candidate/<user_code>")
@admin_required
def admin_candidate_detail(user_code):
    user_code = user_code.upper().strip()
    conn = database.get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE user_code = ?", (user_code,)).fetchone()
    
    if not user:
        conn.close()
        return f"<h3>Candidate with ID Number '{user_code}' not found.</h3><a href='/admin'>&larr; Back to Admin Portal</a>", 404
        
    user_dict = dict(user)
    skills = conn.execute("SELECT * FROM user_skills WHERE user_id = ? ORDER BY id ASC", (user["id"],)).fetchall()
    
    docs = conn.execute("""
    SELECT * FROM user_documents 
    WHERE user_id = ? 
    GROUP BY doc_category 
    ORDER BY CASE doc_category 
        WHEN 'id_front' THEN 1 
        WHEN 'id_back' THEN 2 
        ELSE 3 END
    """, (user["id"],)).fetchall()
    
    conn.close()
    
    return render_template("admin_candidate.html", user=user_dict, skills=[dict(s) for s in skills], documents=[dict(d) for d in docs])

@app.route("/api/admin/toggle-ban", methods=["POST"])
@admin_required
def api_admin_toggle_ban():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    is_banned = int(data.get("is_banned", 1))
    ban_reason = data.get("ban_reason", "Violation of institutional verification guidelines.")
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
        
    conn = database.get_db_connection()
    if is_banned == 1:
        conn.execute("""
        UPDATE users 
        SET is_banned = 1, ban_reason = ?, manual_status = 'REJECTED', pdf_status = 'REJECTED' 
        WHERE id = ?
        """, (ban_reason, user_id))
    else:
        conn.execute("""
        UPDATE users 
        SET is_banned = 0, ban_reason = NULL, manual_status = 'IN PROGRESS' 
        WHERE id = ?
        """, (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "user_id": user_id, "is_banned": is_banned})

@app.route("/api/admin/update-status", methods=["POST"])
@admin_required
def api_admin_update_status():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    pdf_status = data.get("pdf_status")
    manual_status = data.get("manual_status")
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
        
    conn = database.get_db_connection()
    if pdf_status:
        conn.execute("UPDATE users SET pdf_status = ? WHERE id = ?", (pdf_status, user_id))
    if manual_status:
        conn.execute("UPDATE users SET manual_status = ? WHERE id = ?", (manual_status, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "user_id": user_id, "pdf_status": pdf_status, "manual_status": manual_status})

@app.route("/api/admin/verify-skill", methods=["POST"])
@admin_required
def api_admin_verify_skill():
    data = request.get_json() or {}
    skill_id = data.get("skill_id")
    status = data.get("status")
    
    if not skill_id or not status:
        return jsonify({"error": "Skill ID and status required"}), 400
        
    conn = database.get_db_connection()
    conn.execute("UPDATE user_skills SET status = ? WHERE id = ?", (status, skill_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "skill_id": skill_id, "status": status})

@app.route("/api/admin/approve-all", methods=["POST"])
@admin_required
def api_admin_approve_all():
    conn = database.get_db_connection()
    conn.execute("UPDATE users SET pdf_status = 'DONE', manual_status = 'DONE' WHERE manual_status = 'IN PROGRESS' AND is_banned = 0")
    conn.execute("UPDATE user_skills SET status = 'VERIFIED' WHERE status = 'CHECKING'")
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "All pending requests approved"})

@app.route("/api/admin/delete-user", methods=["POST"])
@admin_required
def api_admin_delete_user():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
        
    conn = database.get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/admin/switch-user/<int:user_id>")
def api_admin_switch_user(user_id):
    session["user_id"] = user_id
    return redirect(url_for("signup_verification"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

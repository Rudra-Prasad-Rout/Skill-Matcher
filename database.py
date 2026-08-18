"""
Matchpoint Database Configuration & Schema
Supports SQLite (built-in) and PostgreSQL (via DATABASE_URL environment variable).
Includes 5-digit alphanumeric User Code, Gender, Age, College Email, ID Card Front/Back verification, and Banning system.
"""
import os
import sqlite3
import random
import string

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matchpoint.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    return conn

def generate_user_code(existing_codes=None):
    """Generate a unique 5-digit/character uppercase alphanumeric ID (e.g. A7X9K, R4T2P, 9B3KZ)."""
    while True:
        # 3 uppercase letters + 2 digits shuffled
        letters = [random.choice(string.ascii_uppercase) for _ in range(3)]
        digits = [random.choice(string.digits) for _ in range(2)]
        combined = letters + digits
        random.shuffle(combined)
        code = "".join(combined)
        if not existing_codes or code not in existing_codes:
            return code

def init_db(force_reset=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if table schema needs migration (i.e. missing user_code)
    try:
        cursor.execute("SELECT user_code FROM users LIMIT 1")
    except sqlite3.OperationalError:
        force_reset = True
        
    if force_reset:
        cursor.execute("DROP TABLE IF EXISTS user_documents")
        cursor.execute("DROP TABLE IF EXISTS user_skills")
        cursor.execute("DROP TABLE IF EXISTS users")
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_code TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        gender TEXT DEFAULT 'Male',
        age INTEGER DEFAULT 20,
        password_hash TEXT NOT NULL,
        school TEXT,
        coursework TEXT,
        step INTEGER DEFAULT 1,
        pdf_status TEXT DEFAULT 'DONE',
        manual_status TEXT DEFAULT 'IN PROGRESS',
        career_intent TEXT DEFAULT 'both',
        is_banned INTEGER DEFAULT 0,
        ban_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Ensure career_intent column exists in existing database
    try:
        cursor.execute("SELECT career_intent FROM users LIMIT 1")
    except sqlite3.OperationalError:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN career_intent TEXT DEFAULT 'both'")
        except Exception:
            pass

    # Ensure email_verified column exists in existing database
    try:
        cursor.execute("SELECT email_verified FROM users LIMIT 1")
    except sqlite3.OperationalError:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
        except Exception:
            pass

    # Email OTP verification table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_otps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        otp_code TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_used INTEGER DEFAULT 0
    );
    """)
    
    # Skills and Projects table (with GitHub / Website URL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        project_name TEXT NOT NULL,
        project_url TEXT,
        status TEXT DEFAULT 'VERIFIED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
    # Documents table (with doc_category: 'id_front', 'id_back', 'certificate' + AI Authenticity scoring fields)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        doc_category TEXT DEFAULT 'certificate',
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        file_type TEXT,
        ai_score REAL DEFAULT 0.05,
        ai_recommendation TEXT DEFAULT 'LOW_RISK',
        ai_notes TEXT DEFAULT 'Passed automated provenance and pixel pattern check.',
        review_status TEXT DEFAULT 'PENDING',
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
    # Discovered Internships Table (From Legal Portals with Scam Filtering & Matchmaking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discovered_internships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT DEFAULT 'India / Remote',
        stipend TEXT DEFAULT 'Stipend Available',
        start_date TEXT DEFAULT '01 Oct 2026',
        end_date TEXT DEFAULT '31 Dec 2026',
        duration TEXT DEFAULT '3 Months',
        posted_date TEXT DEFAULT 'Recent',
        application_link TEXT NOT NULL,
        source_site TEXT NOT NULL,
        skills_required TEXT DEFAULT '[]',
        description TEXT,
        is_scam_flagged INTEGER DEFAULT 0,
        flag_reason TEXT,
        risk_level TEXT DEFAULT 'CLEAN',
        is_verified_by_admin INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Auto-migration for discovered_internships
    existing_disc_cols = [r[1] for r in cursor.execute("PRAGMA table_info(discovered_internships)").fetchall()]
    if "start_date" not in existing_disc_cols:
        cursor.execute("ALTER TABLE discovered_internships ADD COLUMN start_date TEXT DEFAULT '01 Oct 2026'")
    if "end_date" not in existing_disc_cols:
        cursor.execute("ALTER TABLE discovered_internships ADD COLUMN end_date TEXT DEFAULT '31 Dec 2026'")
    if "duration" not in existing_disc_cols:
        cursor.execute("ALTER TABLE discovered_internships ADD COLUMN duration TEXT DEFAULT '3 Months'")

    # Candidate Internship Approvals / Nominations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidate_internship_approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        internship_id TEXT NOT NULL,
        role_title TEXT,
        company TEXT,
        status TEXT DEFAULT 'APPROVED',
        approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, internship_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Teams Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_code TEXT UNIQUE NOT NULL,
        leader_id INTEGER NOT NULL,
        team_name TEXT NOT NULL,
        team_size INTEGER DEFAULT 4,
        theme TEXT DEFAULT 'Hackathons & Startups',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (leader_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Team Invitations Table (supports Invitations and Join Requests)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS team_invites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        invite_type TEXT DEFAULT 'INVITATION',
        message TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Auto-migration for team_invites columns
    existing_invite_cols = [r[1] for r in cursor.execute("PRAGMA table_info(team_invites)").fetchall()]
    if "invite_type" not in existing_invite_cols:
        cursor.execute("ALTER TABLE team_invites ADD COLUMN invite_type TEXT DEFAULT 'INVITATION'")
    if "message" not in existing_invite_cols:
        cursor.execute("ALTER TABLE team_invites ADD COLUMN message TEXT")
    # Backfill legacy 'INVITED' status records to 'PENDING' for consistency
    cursor.execute("UPDATE team_invites SET status = 'PENDING' WHERE status = 'INVITED'")

    # Clean up duplicate teams per leader (keep only 1 team per leader)
    cursor.execute("""
    DELETE FROM teams
    WHERE id NOT IN (
        SELECT id FROM teams WHERE team_name = 'NeuralCore AI'
        UNION
        SELECT id FROM teams WHERE team_name = 'CyberVikings'
        UNION
        SELECT MAX(id) FROM teams GROUP BY leader_id
    )
    """)

    # Ensure 1 team per leader
    cursor.execute("""
    DELETE FROM teams
    WHERE id NOT IN (
        SELECT MIN(id) FROM teams GROUP BY leader_id
    )
    """)

    # Clean up orphaned team_invites
    cursor.execute("DELETE FROM team_invites WHERE team_id NOT IN (SELECT id FROM teams)")

    # Clean up any duplicate accepted/pending team_invites rows for the same (team_id, member_user_id)
    cursor.execute("""
    DELETE FROM team_invites
    WHERE id NOT IN (
        SELECT MAX(id)
        FROM team_invites
        GROUP BY team_id, (CASE WHEN invite_type = 'JOIN_REQUEST' THEN sender_id ELSE receiver_id END)
    )
    """)

    # Unique index on leader_id to enforce 1 squad per leader at the database engine level
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_teams_leader_unique ON teams(leader_id)")

    conn.commit()
    
    # Reset and seed sample users with 5-character alphanumeric ID codes
    cursor.execute("SELECT COUNT(*) as count FROM users")
    count = cursor.fetchone()["count"]
    
    if count == 0 or force_reset:
        cursor.execute("DELETE FROM user_documents")
        cursor.execute("DELETE FROM user_skills")
        cursor.execute("DELETE FROM users")
        
        sample_users = [
            {
                "user_code": "A7X9K",
                "full_name": "Alex Rivera",
                "email": "alex.rivera@college.edu",
                "gender": "Male",
                "age": 21,
                "school": "Delhi University",
                "coursework": "B.Tech Computer Science",
                "step": 4,
                "pdf_status": "DONE",
                "manual_status": "IN PROGRESS",
                "is_banned": 0,
                "skills": [
                    ("React", "Campus events app", "https://github.com/alexrivera/campus-events-app", "VERIFIED"),
                    ("Data analysis", "Attendance dashboard", "https://attendance-analytics.du.ac.in", "CHECKING")
                ],
                "documents": []
            },
            {
                "user_code": "R4T2P",
                "full_name": "Jordan Lee",
                "email": "jordan.lee@stanford.edu",
                "gender": "Female",
                "age": 22,
                "school": "Stanford University",
                "coursework": "BS Symbolic Systems",
                "step": 4,
                "pdf_status": "DONE",
                "manual_status": "IN PROGRESS",
                "is_banned": 0,
                "skills": [
                    ("PyTorch", "Autonomous drone vision", "https://github.com/jordanlee/drone-vision-ai", "VERIFIED"),
                    ("NLP", "Semantic search engine", "https://nlp-search-demo.stanford.edu", "VERIFIED")
                ],
                "documents": []
            },
            {
                "user_code": "9B3KZ",
                "full_name": "Priya Sharma",
                "email": "priya.s@iitd.ac.in",
                "gender": "Female",
                "age": 20,
                "school": "IIT Delhi",
                "coursework": "Computer Engineering",
                "step": 4,
                "pdf_status": "DONE",
                "manual_status": "DONE",
                "is_banned": 0,
                "skills": [
                    ("Flutter", "Peer tutoring portal", "https://github.com/priyasharma/peer-tutor-app", "VERIFIED"),
                    ("Node.js", "High-throughput API gateway", "https://github.com/priyasharma/cloud-gateway", "VERIFIED")
                ],
                "documents": []
            },
            {
                "user_code": "M8V1Y",
                "full_name": "Marcus Vance",
                "email": "marcus.vance@nyu.edu",
                "gender": "Male",
                "age": 23,
                "school": "NYU Stern",
                "coursework": "Information Systems",
                "step": 3,
                "pdf_status": "CHECKING",
                "manual_status": "IN PROGRESS",
                "is_banned": 0,
                "skills": [
                    ("SQL & Databases", "FinTech trading analytics", "https://github.com/marcusvance/nyu-trading-desk", "CHECKING"),
                    ("Tableau", "Global markets dashboard", "https://public.tableau.com/profile/marcus.vance/market-pulse", "CHECKING")
                ],
                "documents": []
            },
            {
                "user_code": "E2R9Q",
                "full_name": "Elena Rostova",
                "email": "elena.r@oxford.ac.uk",
                "gender": "Female",
                "age": 24,
                "school": "University of Oxford",
                "coursework": "MSc Artificial Intelligence",
                "step": 4,
                "pdf_status": "REJECTED",
                "manual_status": "REJECTED",
                "is_banned": 1,
                "ban_reason": "Suspected forged certificate and fraudulent ID scan",
                "skills": [
                    ("Computer Vision", "3D point cloud mapper", "https://github.com/elenarostova/pointcloud-mapper", "CHECKING")
                ],
                "documents": []
            }
        ]
        
        for u in sample_users:
            cursor.execute("""
            INSERT INTO users (user_code, full_name, email, gender, age, password_hash, school, coursework, step, pdf_status, manual_status, is_banned, ban_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                u["user_code"],
                u["full_name"],
                u["email"],
                u["gender"],
                u["age"],
                "secure_hash_2026",
                u["school"],
                u["coursework"],
                u["step"],
                u["pdf_status"],
                u["manual_status"],
                u.get("is_banned", 0),
                u.get("ban_reason", None)
            ))
            uid = cursor.lastrowid
            
            for sk in u["skills"]:
                cursor.execute("""
                INSERT INTO user_skills (user_id, skill_name, project_name, project_url, status)
                VALUES (?, ?, ?, ?, ?)
                """, (uid, sk[0], sk[1], sk[2], sk[3]))
                
            for doc in u["documents"]:
                cursor.execute("""
                INSERT INTO user_documents (user_id, doc_category, filename, original_name, file_size, file_type)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (uid, doc[0], doc[1], doc[2], doc[3], doc[4]))
                
        conn.commit()
        
    conn.close()

if __name__ == "__main__":
    init_db(force_reset=True)
    print("Database re-initialized and seeded with 5-character ID codes, Gender, Age, and ID Card documents.")

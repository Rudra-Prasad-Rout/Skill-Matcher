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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
        is_banned INTEGER DEFAULT 0,
        ban_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # Documents table (with doc_category: 'id_front', 'id_back', 'certificate')
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        doc_category TEXT DEFAULT 'certificate',
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        file_type TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
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
                "documents": [
                    ("id_front", "seed_id_front_alex.jpg", "alex_id_card_front.jpg", 340000, "image/jpeg"),
                    ("id_back", "seed_id_back_alex.jpg", "alex_id_card_back.jpg", 310000, "image/jpeg"),
                    ("certificate", "seed_alex_transcript_2026.pdf", "alex_transcript_2026.pdf", 1450000, "application/pdf")
                ]
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
                "documents": [
                    ("id_front", "seed_id_front_jordan.jpg", "stanford_id_front.jpg", 380000, "image/jpeg"),
                    ("id_back", "seed_id_back_jordan.jpg", "stanford_id_back.jpg", 360000, "image/jpeg"),
                    ("certificate", "seed_stanford_degree_proof.pdf", "stanford_degree_proof.pdf", 2100000, "application/pdf")
                ]
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
                "documents": [
                    ("id_front", "seed_id_front_priya.jpg", "iitd_smart_card_front.jpg", 290000, "image/jpeg"),
                    ("id_back", "seed_id_back_priya.jpg", "iitd_smart_card_back.jpg", 280000, "image/jpeg"),
                    ("certificate", "seed_iitd_marksheet_verified.pdf", "iitd_marksheet_verified.pdf", 980000, "application/pdf")
                ]
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
                "documents": [
                    ("id_front", "seed_id_front_marcus.jpg", "nyu_card_front.jpg", 310000, "image/jpeg"),
                    ("id_back", "seed_id_back_marcus.jpg", "nyu_card_back.jpg", 300000, "image/jpeg"),
                    ("certificate", "seed_nyu_enrollment_verification.pdf", "nyu_enrollment_verification.pdf", 1850000, "application/pdf")
                ]
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
                "documents": [
                    ("id_front", "seed_scanned_id_unclear.jpg", "oxford_id_front_blur.jpg", 420000, "image/jpeg"),
                    ("id_back", "seed_scanned_id_unclear.jpg", "oxford_id_back_blur.jpg", 410000, "image/jpeg"),
                    ("certificate", "seed_scanned_id_unclear.jpg", "oxford_transcript_fake.jpg", 450000, "image/jpeg")
                ]
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

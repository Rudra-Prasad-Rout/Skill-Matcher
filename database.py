"""
Matchpoint Database Configuration & Schema
Supports SQLite (built-in local) and PostgreSQL (via DATABASE_URL environment variable).
Includes 5-digit alphanumeric User Code, Gender, Age, College Email, ID Card Front/Back verification, and Banning system.
"""
import os
import sqlite3
import random
import string

DB_PATH = os.environ.get("SQLITE_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "matchpoint.db"))
os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

class PgRow(dict):
    """Row wrapper that supports dict conversion, column name lookup, and numeric tuple indexing."""
    def __init__(self, cols, values):
        super().__init__(zip(cols, values))
        self._values = list(values)
        self._cols = list(cols)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._values[item]
        return super().__getitem__(item)

class PgCursorWrapper:
    def __init__(self, pg_cursor):
        self._cur = pg_cursor

    def execute(self, query, params=None):
        clean_q = query.replace('?', '%s')
        if params is not None:
            if isinstance(params, (list, tuple)):
                self._cur.execute(clean_q, params)
            else:
                self._cur.execute(clean_q, (params,))
        else:
            self._cur.execute(clean_q)
        return self

    def fetchone(self):
        row = self._cur.fetchone()
        if row is None:
            return None
        cols = [desc[0] for desc in self._cur.description]
        return PgRow(cols, row)

    def fetchall(self):
        rows = self._cur.fetchall()
        if not rows:
            return []
        cols = [desc[0] for desc in self._cur.description]
        return [PgRow(cols, r) for r in rows]

    @property
    def lastrowid(self):
        try:
            return self._cur.fetchone()[0]
        except Exception:
            return None

    @property
    def rowcount(self):
        return self._cur.rowcount

    def close(self):
        self._cur.close()

class PgConnectionWrapper:
    def __init__(self, pg_conn):
        self._conn = pg_conn

    def cursor(self):
        return PgCursorWrapper(self._conn.cursor())

    def execute(self, query, params=None):
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

def is_postgres():
    return bool(os.environ.get("DATABASE_URL"))

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        try:
            import psycopg2
            if db_url.startswith("postgres://"):
                db_url = "postgresql://" + db_url[len("postgres://"):]
            raw_conn = psycopg2.connect(db_url)
            raw_conn.autocommit = False
            return PgConnectionWrapper(raw_conn)
        except Exception as e:
            print(f"[DB WARN] PostgreSQL connection failed ({e}). Falling back to SQLite.")

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
    using_pg = is_postgres() and isinstance(conn, PgConnectionWrapper)
    
    id_type = "SERIAL PRIMARY KEY" if using_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"

    if force_reset:
        cursor.execute("DROP TABLE IF EXISTS user_documents")
        cursor.execute("DROP TABLE IF EXISTS user_skills")
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS email_otps")
        cursor.execute("DROP TABLE IF EXISTS teams")
        cursor.execute("DROP TABLE IF EXISTS team_invites")
        cursor.execute("DROP TABLE IF EXISTS candidate_internship_approvals")
        cursor.execute("DROP TABLE IF EXISTS discovered_internships")
    
    # Users table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS users (
        id {id_type},
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
    except Exception:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN career_intent TEXT DEFAULT 'both'")
        except Exception:
            pass

    # Ensure email_verified column exists in existing database
    try:
        cursor.execute("SELECT email_verified FROM users LIMIT 1")
    except Exception:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
        except Exception:
            pass

    # Email OTP verification table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS email_otps (
        id {id_type},
        email TEXT NOT NULL,
        otp_code TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_used INTEGER DEFAULT 0
    );
    """)
    
    # Skills and Projects table (with GitHub / Website URL)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS user_skills (
        id {id_type},
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        project_name TEXT NOT NULL,
        project_url TEXT,
        status TEXT DEFAULT 'VERIFIED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
    # Documents table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS user_documents (
        id {id_type},
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
    
    # Discovered Internships Table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS discovered_internships (
        id {id_type},
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

    # Candidate Internship Approvals / Nominations Table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS candidate_internship_approvals (
        id {id_type},
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
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS teams (
        id {id_type},
        team_code TEXT UNIQUE NOT NULL,
        leader_id INTEGER NOT NULL,
        team_name TEXT NOT NULL,
        team_size INTEGER DEFAULT 4,
        theme TEXT DEFAULT 'Hackathons & Startups',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (leader_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Team Invitations Table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS team_invites (
        id {id_type},
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

    try:
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_teams_leader_unique ON teams(leader_id)")
    except Exception:
        pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db(force_reset=False)
    print("Database schema initialized cleanly.")

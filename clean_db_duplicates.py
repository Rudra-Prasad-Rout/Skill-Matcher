import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matchpoint.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Remove duplicate document entries keeping only the latest ID for each (user_id, doc_category)
cursor.execute("""
DELETE FROM user_documents 
WHERE id NOT IN (
    SELECT MAX(id) 
    FROM user_documents 
    GROUP BY user_id, doc_category
);
""")
conn.commit()

print(f"Duplicates cleaned. Current documents count: {cursor.execute('SELECT COUNT(*) FROM user_documents').fetchone()[0]}")
conn.close()

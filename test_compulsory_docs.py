import io
import unittest
from app import app
import database

class TestCompulsoryDocumentsAndAdminApproval(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        # Initialize fresh DB
        database.init_db(force_reset=True)

    def tearDown(self):
        # Always clean up test data so database is completely clear
        conn = database.get_db_connection()
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM user_skills")
        conn.execute("DELETE FROM user_documents")
        conn.execute("DELETE FROM email_otps")
        conn.execute("DELETE FROM candidate_internship_approvals")
        conn.execute("DELETE FROM teams")
        conn.execute("DELETE FROM team_invites")
        conn.commit()
        conn.close()

    def test_navbar_unauthenticated(self):
        """1. Unauthenticated landing page should show LOGIN and GET STARTED."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("LOGIN", html)
        self.assertIn("GET STARTED", html)
        self.assertNotIn("LOGOUT", html)
        print("[PASS] Unauthenticated landing page shows LOGIN and GET STARTED.")

    def test_signup_flow_admin_approval_and_analysis_gating(self):
        """2. Complete flow testing compulsory documents, admin approval requirement, and analysis unlocking."""
        # Step 1: Set verified email in session and Create profile
        with self.client.session_transaction() as sess:
            sess["verified_signup_email"] = "test.student@univ.edu"
            sess["verified_signup_time"] = 9999999999
            
        resp = self.client.post("/signup/profile", data={
            "full_name": "Test Student",
            "email": "test.student@univ.edu",
            "gender": "Female",
            "age": "21",
            "password": "password123",
            "re_password": "password123",
            "school": "Delhi University",
            "coursework": "B.Tech Computer Science"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        
        # When logged in, navbar should show ID badge and LOGOUT, NOT LOGIN / GET STARTED
        self.assertIn("LOGOUT", html)
        self.assertNotIn("GET STARTED", html)
        print("[PASS] Logged in student sees ID and LOGOUT in navbar.")

        # Step 2: Add skill & proceed from skills to documents
        conn = database.get_db_connection()
        user_row = conn.execute("SELECT id FROM users WHERE email = 'test.student@univ.edu'").fetchone()
        conn.execute("INSERT INTO user_skills (user_id, skill_name, project_name, project_url, status) VALUES (?, 'Python', 'Web App', 'https://github.com/test/app', 'VERIFIED')", (user_row["id"],))
        conn.commit()
        conn.close()

        resp = self.client.post("/signup/skills", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Passport Size Photo", resp.get_data(as_text=True))
        print("[PASS] Step 3 Documents shows Passport Size Photo compulsory upload box.")

        # Test submitting without Passport Photo (should fail compulsory check)
        fake_front = (io.BytesIO(b"fake image data front"), "college_id_front.png")
        fake_back = (io.BytesIO(b"fake image data back"), "college_id_back.png")
        resp = self.client.post("/signup/documents", data={
            "doc_id_front": fake_front,
            "doc_id_back": fake_back
        }, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Passport Size Photo", resp.get_data(as_text=True))
        print("[PASS] Missing Passport Photo correctly rejected with compulsory error.")

        # Test submitting with ALL Passport Photo, Front, and Back ID
        fake_photo = (io.BytesIO(b"fake image data photo"), "passport_photo.png")
        fake_front = (io.BytesIO(b"fake image data front"), "college_id_front.png")
        fake_back = (io.BytesIO(b"fake image data back"), "college_id_back.png")
        resp = self.client.post("/signup/documents", data={
            "doc_passport_photo": fake_photo,
            "doc_id_front": fake_front,
            "doc_id_back": fake_back
        }, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("Verification Progress", html)
        self.assertIn("Awaiting Staff & Admin Approval", html)
        self.assertIn("AWAITING ADMIN APPROVAL TO ANALYZE", html)
        print("[PASS] User redirected to Verification; status is 'Awaiting Staff & Admin Approval'.")

        # Test Gating: Try accessing /analysis or /signup/analysis BEFORE Admin Approval
        resp = self.client.get("/analysis", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("signup/verification", resp.headers["Location"])
        print("[PASS] Accessing /analysis before Admin approval correctly blocked and redirected to verification.")

        resp = self.client.get("/signup/analysis", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("signup/verification", resp.headers["Location"])
        print("[PASS] Accessing /signup/analysis before Admin approval correctly blocked.")

        resp = self.client.get("/api/profile-analysis")
        self.assertEqual(resp.status_code, 403)
        print("[PASS] /api/profile-analysis returns HTTP 403 when unapproved.")

        # Now simulate Admin Approval for this student (e.g. Admin marks candidate manual_status='APPROVED')
        conn = database.get_db_connection()
        user_row = conn.execute("SELECT id FROM users WHERE email = 'test.student@univ.edu'").fetchone()
        user_id = user_row["id"]
        conn.execute("UPDATE users SET manual_status = 'APPROVED', pdf_status = 'DONE' WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

        # Check /api/verification-status returns is_approved: true
        resp = self.client.get("/api/verification-status")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json.get("is_approved"))
        print("[PASS] /api/verification-status reports is_approved: true after admin approval.")

        # Verification page now shows Approved state and unlocked button
        resp = self.client.get("/signup/verification")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("Application Approved by Admin", html)
        self.assertIn("UNLOCK & VIEW AI PROFILE ANALYSIS", html)
        print("[PASS] Verification page reveals UNLOCK & VIEW AI PROFILE ANALYSIS button.")

        # Now test accessing /analysis AFTER Admin Approval (should succeed HTTP 200)
        resp = self.client.get("/analysis")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertNotIn("s30-stepper", html)
        self.assertIn("Personalized Internship Opportunities", html)
        print("[PASS] /analysis dashboard renders successfully after Admin Approval.")

if __name__ == "__main__":
    unittest.main()

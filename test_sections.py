import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://127.0.0.1:5000"

def test_admin_sections():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    print("1. Logging in as TeamX...")
    login_data = urllib.parse.urlencode({
        "username": "TeamX",
        "password": "TeamX@Admin"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/admin/login", data=login_data)
    resp = opener.open(req)
    assert resp.status == 200

    print("2. Testing Approvals Section (All Approval Requests)...")
    resp = opener.open(f"{BASE}/admin?section=approvals")
    html = resp.read().decode('utf-8').upper()
    assert "CANDIDATE VERIFICATION" in html or "APPROVAL" in html
    print("[PASS] Approvals section 200 OK")

    print("3. Testing Dashboard Section...")
    resp = opener.open(f"{BASE}/admin?section=dashboard")
    html = resp.read().decode('utf-8').upper()
    assert "EXECUTIVE" in html or "DASHBOARD" in html
    print("[PASS] Dashboard section 200 OK")

    print("4. Testing Internship Section...")
    resp = opener.open(f"{BASE}/admin?section=internships")
    html = resp.read().decode('utf-8').upper()
    assert "INTERNSHIP" in html
    print("[PASS] Internship section 200 OK")

    print("5. Testing AI Internship Section (under Internship)...")
    resp = opener.open(f"{BASE}/admin?section=ai_internship")
    html = resp.read().decode('utf-8').upper()
    assert "AI" in html and "INTERNSHIP" in html
    print("[PASS] AI Internship section 200 OK")

    print("\nAll Admin navigation and sections verified successfully!")

if __name__ == "__main__":
    test_admin_sections()

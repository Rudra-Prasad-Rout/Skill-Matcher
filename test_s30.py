import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://127.0.0.1:5000"

def test_s30_platform():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    print("1. Testing S30 Landing Page (GET /)...")
    resp = opener.open(f"{BASE}/")
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert "Verified Students" in html
    assert "S30" in html
    print("[PASS] S30 Landing Page 200 OK")

    print("2. Testing S30 Login Page (GET /login)...")
    resp = opener.open(f"{BASE}/login")
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert "Log in to S30" in html
    print("[PASS] S30 Login Page 200 OK")

    print("3. Testing S30 Signup Flow (GET /signup/profile)...")
    resp = opener.open(f"{BASE}/signup/profile")
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert "Create your account" in html
    print("[PASS] S30 Signup Profile Page 200 OK")

    print("4. Testing S30 Admin Login & Dashboard...")
    login_data = urllib.parse.urlencode({"username": "TeamX", "password": "TeamX@Admin"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/admin/login", data=login_data)
    resp = opener.open(req)
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert "Total Students" in html
    print("[PASS] S30 Admin Dashboard 200 OK")

    print("5. Testing S30 Candidate Dossier (GET /admin/candidate/A7X9K)...")
    resp = opener.open(f"{BASE}/admin/candidate/A7X9K")
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert "A7X9K" in html
    print("[PASS] S30 Candidate Dossier 200 OK")

    print("\nAll S30 platform endpoints verified successfully!")

if __name__ == "__main__":
    test_s30_platform()

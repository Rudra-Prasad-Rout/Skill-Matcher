import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://127.0.0.1:5000"

def test_admin_security():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    print("1. Checking that Main Website navbar has NO Admin links...")
    resp = opener.open(f"{BASE}/")
    html = resp.read().decode('utf-8')
    assert "Staff Admin" not in html
    print("[PASS] Public Landing Page has NO Admin links.")

    print("2. Checking that unauthenticated /admin redirects to /admin/login...")
    resp = opener.open(f"{BASE}/admin")
    html = resp.read().decode('utf-8')
    assert "Staff Portal Login" in html
    assert "Admin Username" in html
    print("[PASS] Unauthenticated /admin properly protected.")

    print("3. Testing invalid Admin credentials...")
    login_data = urllib.parse.urlencode({
        "username": "wrong_user",
        "password": "wrong_password"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/admin/login", data=login_data)
    resp = opener.open(req)
    html = resp.read().decode('utf-8')
    assert "Invalid Admin Username or Password" in html
    print("[PASS] Invalid credentials rejected.")

    print("4. Testing valid TeamX credentials (TeamX / TeamX@Admin)...")
    login_data = urllib.parse.urlencode({
        "username": "TeamX",
        "password": "TeamX@Admin"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/admin/login", data=login_data)
    resp = opener.open(req)
    html = resp.read().decode('utf-8')
    assert "Total Students" in html
    assert "TeamX" in html
    print("[PASS] Admin login successful with TeamX / TeamX@Admin!")

    print("5. Testing Admin Logout...")
    resp = opener.open(f"{BASE}/admin/logout")
    html = resp.read().decode('utf-8')
    assert "Staff Portal Login" in html
    print("[PASS] Admin logout successful.")

    print("\nAll Admin security and authentication tests passed!")

if __name__ == "__main__":
    test_admin_security()

import urllib.request
import urllib.parse
import http.cookiejar
import json

BASE = "http://127.0.0.1:5000"

def test_full_system():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    print("0. Logging in as Admin TeamX...")
    login_data = urllib.parse.urlencode({"username": "TeamX", "password": "TeamX@Admin"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/admin/login", data=login_data)
    resp = opener.open(req)
    assert resp.status == 200

    print("1. Testing Admin Dashboard...")
    req = urllib.request.Request(f"{BASE}/admin")
    resp = opener.open(req)
    assert resp.status == 200
    print("Admin Dashboard HTTP 200 OK")

    print("2. Testing Candidate Detail by 5-Digit ID 'A7X9K'...")
    req = urllib.request.Request(f"{BASE}/admin/candidate/A7X9K")
    resp = opener.open(req)
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert "Alex Rivera" in html
    assert "A7X9K" in html
    print("Candidate Detail Page HTTP 200 OK")

    print("3. Testing Ban Action...")
    payload = json.dumps({"user_id": 1, "is_banned": 1, "ban_reason": "Testing ban functionality"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/api/admin/toggle-ban", data=payload, headers={"Content-Type": "application/json"})
    resp = opener.open(req)
    assert resp.status == 200
    print("Ban Candidate API Response:", resp.read().decode())

    print("4. Testing Unban Action...")
    payload = json.dumps({"user_id": 1, "is_banned": 0}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/api/admin/toggle-ban", data=payload, headers={"Content-Type": "application/json"})
    resp = opener.open(req)
    assert resp.status == 200
    print("Unban Candidate API Response:", resp.read().decode())

    print("5. Testing Skill 1-by-1 Verification...")
    payload = json.dumps({"skill_id": 1, "status": "VERIFIED"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/api/admin/verify-skill", data=payload, headers={"Content-Type": "application/json"})
    resp = opener.open(req)
    assert resp.status == 200
    print("Skill Verify API Response:", resp.read().decode())

    print("All tests passed successfully!")

if __name__ == "__main__":
    test_full_system()

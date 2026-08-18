import urllib.request
import urllib.parse
import http.cookiejar
import json

BASE = "http://127.0.0.1:5000"

def test_api():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    print("0. Logging in as Admin TeamX...")
    login_data = urllib.parse.urlencode({"username": "TeamX", "password": "TeamX@Admin"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/admin/login", data=login_data)
    resp = opener.open(req)
    assert resp.status == 200

    print("Testing verification status...")
    req = urllib.request.Request(f"{BASE}/api/verification-status")
    resp = opener.open(req)
    print("Status code:", resp.status)
    data = json.loads(resp.read().decode())
    print("Response:", data)
    assert "pdf_status" in data
    assert "manual_status" in data

    print("Testing admin update...")
    payload = json.dumps({"user_id": 1, "manual_status": "DONE"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/api/admin/update-status", data=payload, headers={"Content-Type": "application/json"})
    resp = opener.open(req)
    print("Admin update response:", resp.read().decode())

    print("Testing status after update...")
    req = urllib.request.Request(f"{BASE}/api/verification-status")
    resp = opener.open(req)
    data = json.loads(resp.read().decode())
    print("Updated response:", data)
    assert data["manual_status"] == "DONE"

    # Reset back to IN PROGRESS
    payload = json.dumps({"user_id": 1, "manual_status": "IN PROGRESS"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/api/admin/update-status", data=payload, headers={"Content-Type": "application/json"})
    resp = opener.open(req)

    print("All backend integration tests passed successfully!")

if __name__ == "__main__":
    test_api()

import urllib.request
import urllib.parse
import json

BASE = "http://127.0.0.1:5000"

def test_api():
    print("Testing verification status...")
    req = urllib.request.Request(f"{BASE}/api/verification-status")
    with urllib.request.urlopen(req) as resp:
        print("Status code:", resp.status)
        data = json.loads(resp.read().decode())
        print("Response:", data)
        assert "pdf_status" in data
        assert "manual_status" in data

    print("Testing admin update...")
    payload = json.dumps({"user_id": 1, "manual_status": "DONE"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/api/admin/update-status", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        print("Admin update response:", resp.read().decode())

    print("Testing status after update...")
    req = urllib.request.Request(f"{BASE}/api/verification-status")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("Updated response:", data)
        assert data["manual_status"] == "DONE"

    # Reset back to IN PROGRESS to match screenshot 4
    payload = json.dumps({"user_id": 1, "manual_status": "IN PROGRESS"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/api/admin/update-status", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        pass

    print("All backend integration tests passed successfully!")

if __name__ == "__main__":
    test_api()

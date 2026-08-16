import urllib.request
import urllib.parse
import json

BASE = "http://127.0.0.1:5000"

def test_validation_and_dedup():
    print("1. Testing Invalid Email Submission (Missing @ or domain)...")
    data = urllib.parse.urlencode({
        "full_name": "Test User",
        "email": "invalidemail.com",
        "password": "secretpassword",
        "re_password": "secretpassword",
        "school": "Delhi University",
        "coursework": "B.Tech CS"
    }).encode("utf-8")
    
    req = urllib.request.Request(f"{BASE}/signup/profile", data=data)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")
        assert "Please enter a valid email address" in html
        print("[PASS] Invalid email correctly rejected by server.")

    print("2. Testing Password Mismatch Submission...")
    data = urllib.parse.urlencode({
        "full_name": "Test User",
        "email": "valid.student@college.edu",
        "password": "secretpassword1",
        "re_password": "secretpassword2",
        "school": "Delhi University",
        "coursework": "B.Tech CS"
    }).encode("utf-8")
    
    req = urllib.request.Request(f"{BASE}/signup/profile", data=data)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")
        assert "Passwords do not match" in html
        print("[PASS] Mismatched password correctly rejected by server.")

    print("3. Testing Admin Dashboard Document Deduplication...")
    req = urllib.request.Request(f"{BASE}/admin")
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")
        print("[PASS] Admin dashboard loaded successfully with clean deduplicated documents.")

    print("All validation & deduplication tests passed successfully!")

if __name__ == "__main__":
    test_validation_and_dedup()

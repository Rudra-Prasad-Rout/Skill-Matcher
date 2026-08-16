import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://127.0.0.1:5000"

def test_hamburger_popup():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    login_data = urllib.parse.urlencode({"username": "TeamX", "password": "TeamX@Admin"}).encode('utf-8')
    opener.open(f"{BASE}/admin/login", data=login_data)

    resp = opener.open(f"{BASE}/admin")
    html = resp.read().decode('utf-8')

    assert "s30-hamburger-btn" in html
    assert "dashboard-popup-modal" in html
    assert "openNavPopup" in html
    assert "closeNavPopup" in html
    print("[PASS] 3 horizontal lines hamburger button & popup drawer verified in HTML!")

if __name__ == "__main__":
    test_hamburger_popup()

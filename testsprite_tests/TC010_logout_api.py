import requests
import sys

BASE_URL = "http://localhost:5001"
TIMEOUT = 30

def test_logout_api():
    session = requests.Session()
    try:
        # Login as demo student
        login_url = f"{BASE_URL}/api/auth/students/login"
        login_payload = {"email": "kareena@college.edu", "password": "Password123!"}
        headers = {"Content-Type": "application/json"}

        resp = session.post(login_url, json=login_payload, headers=headers, timeout=TIMEOUT, allow_redirects=False)
        assert resp.status_code in (200, 201, 202, 204, 302, 303), f"Login request failed: {resp.status_code} - {resp.text}"

        # Optional: ensure some authentication evidence in response JSON if present
        try:
            data = resp.json()
        except ValueError:
            data = None
        if data:
            assert any(k in data for k in ("token", "access_token", "user", "success", "session")), f"Login response missing expected auth fields: {data}"

        # Verify access to a protected endpoint before logout
        profile_url = f"{BASE_URL}/api/student/profile"
        pre_logout = session.get(profile_url, timeout=TIMEOUT, allow_redirects=False)
        # Before logout we expect access (not unauthorized or redirect to landing)
        assert pre_logout.status_code not in (401, 403), f"Unexpected unauthorized before logout: {pre_logout.status_code} - {pre_logout.text}"

        # Perform logout
        logout_url = f"{BASE_URL}/api/auth/logout"
        logout_resp = session.post(logout_url, timeout=TIMEOUT, allow_redirects=False)
        assert logout_resp.status_code in (200, 202, 204, 302, 303), f"Logout request failed: {logout_resp.status_code} - {logout_resp.text}"

        # After logout, protected endpoint should be inaccessible or redirect to landing
        post_logout = session.get(profile_url, timeout=TIMEOUT, allow_redirects=False)
        assert post_logout.status_code in (401, 403, 302, 303), f"Protected resource still accessible after logout: {post_logout.status_code} - {post_logout.text}"

        # If server redirects after trying to access protected endpoint, check redirect location points to landing ("/" or base URL)
        if post_logout.status_code in (302, 303):
            location = post_logout.headers.get("Location", "")
            assert location in ("/", BASE_URL + "/", BASE_URL, ""), f"Unexpected redirect location after logout: {location}"

        print("TC010 logout_api: PASS")
    except AssertionError as e:
        print("TC010 logout_api: FAIL -", str(e))
        raise
    except Exception as e:
        print("TC010 logout_api: ERROR -", str(e))
        raise
    finally:
        # Ensure session is cleared on server side as best-effort cleanup
        try:
            session.post(f"{BASE_URL}/api/auth/logout", timeout=TIMEOUT)
        except Exception:
            pass

if __name__ == "__main__":
    test_logout_api()
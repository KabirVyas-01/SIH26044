import requests
import sys

BASE_URL = "http://localhost:5001"
TIMEOUT = 30

def test_institute_login_api():
    url = f"{BASE_URL}/api/auth/institute/login"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "email": "tnp@msu.edu",
        "password": "Password123!"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        raise AssertionError(f"Request to {url} timed out after {TIMEOUT} seconds")
    except requests.exceptions.ConnectionError as e:
        raise AssertionError(f"Connection error when connecting to {url}: {e}")
    except Exception as e:
        raise AssertionError(f"Unexpected error during request to {url}: {e}")

    # Basic status code check
    assert resp.status_code in (200, 201), f"Expected 200/201 but got {resp.status_code}: {resp.text}"

    # Try to parse JSON body
    try:
        body = resp.json()
    except ValueError:
        body = None

    # Helper to recursively search for token-like keys in JSON
    def extract_token(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k and isinstance(k, str) and k.lower() in ("token", "access_token", "accesstoken", "jwt"):
                    return v
                found = extract_token(v)
                if found:
                    return found
        elif isinstance(obj, list):
            for item in obj:
                found = extract_token(item)
                if found:
                    return found
        return None

    token = extract_token(body) if body is not None else None

    # Accept either a token in the JSON or cookies set by the server (session cookie)
    if token:
        assert isinstance(token, (str, int)) and str(token).strip() != "", "Received empty token value"
    else:
        # If no token found in JSON, ensure cookies were set (server-side session)
        assert resp.cookies and len(resp.cookies) > 0, "No auth token in response JSON and no cookies set; authentication likely failed"

    # Optionally validate that response contains some user info if present
    def find_role(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k and isinstance(k, str) and k.lower() in ("role", "user_role", "type"):
                    return v
                found = find_role(v)
                if found:
                    return found
        elif isinstance(obj, list):
            for item in obj:
                found = find_role(item)
                if found:
                    return found
        return None

    role = find_role(body) if body is not None else None
    if role is not None:
        # If role is provided, it should be non-empty. Preferably indicate institute/university.
        assert str(role).strip() != "", "Role field present but empty"
        # If role contains text, it's acceptable; no strict enforcement to avoid false negatives

    print("Institute login test passed. Status:", resp.status_code)

if __name__ == "__main__":
    try:
        test_institute_login_api()
    except AssertionError as e:
        print("TEST FAILED:", e)
        sys.exit(1)
    except Exception as ex:
        print("UNEXPECTED ERROR:", ex)
        sys.exit(2)
    else:
        print("TEST SUCCEEDED")
        sys.exit(0)
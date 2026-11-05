import requests
import sys

BASE_URL = "http://localhost:5001"
TIMEOUT = 30.0

def test_academician_login_api():
    url = f"{BASE_URL}/api/auth/academician/login"
    payload = {
        "email": "xyz@msu.edu",
        "password": "Password123!"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"Request to {url} failed: {e}")

    # Basic status code check
    try:
        assert resp.status_code == 200, f"Expected status 200, got {resp.status_code}. Response text: {resp.text}"
    except AssertionError:
        # Provide more context for non-200 responses
        raise

    # Parse JSON body
    try:
        body = resp.json()
    except ValueError:
        raise AssertionError(f"Response is not valid JSON. Status: {resp.status_code}, Text: {resp.text}")

    # Validate presence of authentication token(s)
    def has_token(obj):
        if not isinstance(obj, dict):
            return False
        token_keys = {"access_token", "token", "auth_token", "jwt"}
        if any(k in obj for k in token_keys):
            return True
        # nested data.user or data tokens
        if "data" in obj and isinstance(obj["data"], dict):
            if any(k in obj["data"] for k in token_keys):
                return True
            if "user" in obj["data"] and isinstance(obj["data"]["user"], dict):
                return False  # user object presence is checked separately
        return False

    tokens_found = has_token(body)
    # also check nested places
    if not tokens_found and isinstance(body.get("data"), dict):
        tokens_found = has_token(body["data"])
    assert tokens_found, f"No authentication token found in response JSON: {body}"

    # If user info is returned, validate email and role if present
    user_obj = None
    if "user" in body and isinstance(body["user"], dict):
        user_obj = body["user"]
    elif isinstance(body.get("data"), dict) and isinstance(body["data"].get("user"), dict):
        user_obj = body["data"]["user"]

    if user_obj:
        # email should match
        assert "email" in user_obj, f"'user' object missing 'email' field: {user_obj}"
        assert user_obj["email"].lower() == payload["email"].lower(), f"Returned user email does not match login email: {user_obj.get('email')}"
        # role or type may indicate academician; if provided, check it
        role = user_obj.get("role") or user_obj.get("type") or user_obj.get("user_type")
        if role is not None:
            assert "academician" in str(role).lower() or "faculty" in str(role).lower(), f"User role does not indicate academician: {role}"

    print("TC004 - academician_login_api: PASSED")

if __name__ == "__main__":
    try:
        test_academician_login_api()
    except AssertionError as e:
        print(f"TC004 - academician_login_api: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC004 - academician_login_api: ERROR - {e}")
        sys.exit(2)
    sys.exit(0)
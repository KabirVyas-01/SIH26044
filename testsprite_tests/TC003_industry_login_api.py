import requests
import sys

BASE_URL = "http://localhost:5001"
TIMEOUT = 30

def test_industry_login_api():
    """
    TC003: industry_login_api
    Verify that an industry partner can log in by sending a POST request to /api/auth/industry/login
    with valid credentials and gain access to the industry portal.
    """
    url = f"{BASE_URL}/api/auth/industry/login"
    headers = {"Content-Type": "application/json"}
    valid_payload = {
        "email": "recruitment@adoratech.io",
        "password": "Password123!"
    }

    try:
        # Attempt login with valid credentials
        resp = requests.post(url, json=valid_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request to {url} failed: {e}")

    # Expect a successful status code (commonly 200)
    assert resp.status_code == 200, f"Expected status 200 for valid login, got {resp.status_code}. Body: {resp.text}"

    try:
        resp_json = resp.json()
    except ValueError:
        raise AssertionError(f"Response is not valid JSON. Body: {resp.text}")

    # Validate presence of an authentication token in common fields or within data
    token_keys = {"access_token", "token", "auth_token", "id_token", "jwt", "accessToken"}
    found_token = False

    # Check top-level keys
    for key in token_keys:
        if key in resp_json:
            found_token = True
            break

    # Check nested 'data' or 'user' objects
    if not found_token:
        for container_key in ("data", "user", "result"):
            container = resp_json.get(container_key)
            if isinstance(container, dict):
                if any(k in container for k in token_keys):
                    found_token = True
                    break

    assert found_token, f"No authentication token found in response JSON: {resp_json}"

    # Optionally verify role information if provided
    role = resp_json.get("role") or (resp_json.get("data") or {}).get("role") or (resp_json.get("user") or {}).get("role")
    if role is not None:
        assert str(role).lower() == "industry", f"Expected role 'industry' in response, got '{role}'"

    # Negative test: wrong password should not authenticate
    bad_payload = {
        "email": "recruitment@adoratech.io",
        "password": "WrongPassword!"
    }
    try:
        bad_resp = requests.post(url, json=bad_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"Request to {url} with wrong credentials failed: {e}")

    # Expect a client error (401/400/403) for invalid credentials
    assert 400 <= bad_resp.status_code < 500, f"Expected 4xx status for invalid credentials, got {bad_resp.status_code}. Body: {bad_resp.text}"

    # If error body is JSON, ensure it indicates authentication failure
    try:
        bad_json = bad_resp.json()
        msg = ""
        if isinstance(bad_json, dict):
            # common message fields
            msg = " ".join(str(bad_json.get(k, "")) for k in ("message", "error", "detail", "msg"))
        if msg:
            assert any(tok in msg.lower() for tok in ("invalid", "credential", "unauthorized", "incorrect", "denied")), \
                f"Invalid-credentials response did not indicate auth failure. Body: {bad_json}"
    except ValueError:
        # non-JSON body is acceptable as long as status is 4xx
        pass

    print("TC003 passed: Industry login (positive and negative) behaved as expected.")

if __name__ == "__main__":
    try:
        test_industry_login_api()
    except AssertionError as e:
        print(f"TC003 failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC003 encountered an unexpected error: {e}")
        sys.exit(2)
    sys.exit(0)
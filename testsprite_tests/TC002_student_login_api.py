import requests

BASE_URL = "http://localhost:5001"
TIMEOUT = 30


def test_student_login_api():
    url = f"{BASE_URL}/api/auth/students/login"
    payload = {
        "email": "kareena@college.edu",
        "password": "Password123!"
    }
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise AssertionError(f"HTTP request failed: {e}")

    assert resp is not None, "No response received"
    assert resp.status_code == 200, f"Expected status 200 OK, got {resp.status_code}. Body: {resp.text}"

    try:
        data = resp.json()
    except ValueError:
        raise AssertionError("Response is not valid JSON")

    # Helper to recursively search for token-like keys
    token_keys = {"access_token", "token", "accessToken", "auth_token", "auth", "jwt", "id_token", "refresh_token", "refreshToken"}

    def contains_any_key(obj, keys):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in keys:
                    return True
                if contains_any_key(v, keys):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if contains_any_key(item, keys):
                    return True
        return False

    has_token = contains_any_key(data, token_keys)
    assert has_token, f"No authentication token found in response JSON. Keys present: {list(data.keys())}"

    # Try to validate returned user/email/role if present
    def find_user_info(obj):
        if isinstance(obj, dict):
            # common patterns
            if "user" in obj and isinstance(obj["user"], dict):
                return obj["user"]
            if "data" in obj and isinstance(obj["data"], dict):
                return find_user_info(obj["data"])
            if "email" in obj or "role" in obj or "type" in obj:
                return obj
            for v in obj.values():
                res = find_user_info(v)
                if res:
                    return res
        elif isinstance(obj, list):
            for item in obj:
                res = find_user_info(item)
                if res:
                    return res
        return None

    user_info = find_user_info(data)
    if user_info:
        # check email if returned
        email = user_info.get("email") or user_info.get("username") or user_info.get("user_email")
        if email:
            assert email.lower() == payload["email"].lower(), f"Returned email '{email}' does not match login email '{payload['email']}'"
        # check role if returned
        role = user_info.get("role") or user_info.get("type")
        if role:
            assert "student" in str(role).lower(), f"Returned role '{role}' does not indicate a student"

    print("TC002 student_login_api: PASSED")


if __name__ == "__main__":
    test_student_login_api()
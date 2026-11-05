import requests
import time
import uuid
import sys

BASE_URL = "http://localhost:5001"
SIGNUP_PATH = "/api/auth/students/signup"
LOGIN_PATH = "/api/auth/students/login"
TIMEOUT = 30  # seconds

def _extract_value_from_json(obj, keys):
    if not isinstance(obj, (dict, list)):
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys:
                return v
            found = _extract_value_from_json(v, keys)
            if found is not None:
                return found
    else:
        for item in obj:
            found = _extract_value_from_json(item, keys)
            if found is not None:
                return found
    return None

def test_student_registration_api():
    unique_email = f"test_student_{int(time.time())}_{uuid.uuid4().hex[:6]}@college.edu"
    password = "Password123!"
    payload = {
        "name": "Test Student",
        "email": unique_email,
        "password": password,
        "college": "Test College",
        "skills": ["python", "testing"]
    }
    signup_url = BASE_URL + SIGNUP_PATH

    created_user_id = None
    auth_token = None
    signup_response_json = None

    try:
        try:
            resp = requests.post(signup_url, json=payload, headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Signup request failed: {e}")

        # Validate HTTP status
        if resp.status_code not in (200, 201):
            # attempt to include body for debugging
            body = None
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise AssertionError(f"Expected 200 or 201 from signup, got {resp.status_code}. Response body: {body}")

        try:
            signup_response_json = resp.json()
        except ValueError:
            raise AssertionError("Signup response is not valid JSON")

        # Try to find user/email in response
        # Accept flexible shapes: { "user": {...} }, { "data": {...} }, or flat
        found_email = _extract_value_from_json(signup_response_json, {"email", "user_email"})
        if isinstance(found_email, dict):
            # if extraction returned a dict, try deeper
            found_email = _extract_value_from_json(found_email, {"email", "user_email"})
        # fallback: check if email string appears somewhere in response JSON string
        if not found_email:
            if unique_email not in str(signup_response_json):
                raise AssertionError(f"Signup response does not contain the registered email '{unique_email}'. Full response: {signup_response_json}")

        # Extract created user id if present
        created_user_id = _extract_value_from_json(signup_response_json, {"id", "_id", "user_id", "uid"})

        # If not found, maybe nested under 'user' or 'data'
        if created_user_id is None:
            user_obj = signup_response_json.get("user") if isinstance(signup_response_json, dict) else None
            if user_obj:
                created_user_id = _extract_value_from_json(user_obj, {"id", "_id", "user_id", "uid"})

        # Final assertion: signup considered successful
        assert True, "Student signup succeeded"

        # Attempt to login to obtain token for cleanup (if needed)
        try:
            login_resp = requests.post(BASE_URL + LOGIN_PATH, json={"email": unique_email, "password": password}, headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
            if login_resp.status_code in (200, 201):
                try:
                    login_json = login_resp.json()
                    # extract common token keys
                    token = _extract_value_from_json(login_json, {"access_token", "token", "jwt", "auth_token"})
                    if token and isinstance(token, str):
                        auth_token = token
                    else:
                        # Sometimes token is under data.token
                        data_token = None
                        if isinstance(login_json, dict):
                            data_token = _extract_value_from_json(login_json.get("data", {}), {"access_token", "token", "jwt", "auth_token"})
                        if data_token:
                            auth_token = data_token
                except ValueError:
                    auth_token = None
        except requests.RequestException:
            auth_token = None

    finally:
        # Cleanup: attempt to delete the created student resource if possible.
        # Try multiple strategies: DELETE /api/auth/students/{id} (with/without auth),
        # DELETE /api/student/profile (requires auth), or other plausible endpoints.
        if created_user_id is None and auth_token is None and signup_response_json:
            # try to extract id one more time from any nested location
            created_user_id = _extract_value_from_json(signup_response_json, {"id", "_id", "user_id", "uid"})

        deletion_attempted = False
        deletion_errors = []

        # 1) If we have auth_token, try DELETE /api/student/profile
        if auth_token:
            try:
                del_url = BASE_URL + "/api/student/profile"
                headers = {"Authorization": f"Bearer {auth_token}"}
                try:
                    del_resp = requests.delete(del_url, headers=headers, timeout=TIMEOUT)
                    deletion_attempted = True
                    # Accept 200,204 as success; if 404/405, try other endpoints
                    if del_resp.status_code in (200, 204):
                        pass
                except requests.RequestException as e:
                    deletion_errors.append(f"DELETE {del_url} failed: {e}")
            except Exception as e:
                deletion_errors.append(str(e))

        # 2) If we have an ID, try DELETE /api/auth/students/{id} (with auth if available)
        if created_user_id is not None:
            try:
                del_url = BASE_URL + f"/api/auth/students/{created_user_id}"
                headers = {"Content-Type": "application/json"}
                if auth_token:
                    headers["Authorization"] = f"Bearer {auth_token}"
                try:
                    del_resp = requests.delete(del_url, headers=headers, timeout=TIMEOUT)
                    deletion_attempted = True
                    # treat 200/204/202 as success; otherwise record
                    if del_resp.status_code not in (200, 202, 204):
                        deletion_errors.append(f"DELETE {del_url} returned status {del_resp.status_code}, body: {del_resp.text}")
                except requests.RequestException as e:
                    deletion_errors.append(f"DELETE {del_url} failed: {e}")
            except Exception as e:
                deletion_errors.append(str(e))

        # 3) Try DELETE /api/student/{id}
        if created_user_id is not None:
            try:
                del_url = BASE_URL + f"/api/student/{created_user_id}"
                headers = {"Content-Type": "application/json"}
                if auth_token:
                    headers["Authorization"] = f"Bearer {auth_token}"
                try:
                    del_resp = requests.delete(del_url, headers=headers, timeout=TIMEOUT)
                    deletion_attempted = True
                    if del_resp.status_code not in (200, 202, 204):
                        deletion_errors.append(f"DELETE {del_url} returned status {del_resp.status_code}, body: {del_resp.text}")
                except requests.RequestException as e:
                    deletion_errors.append(f"DELETE {del_url} failed: {e}")
            except Exception as e:
                deletion_errors.append(str(e))

        # If no deletion strategy applied, just note it (but do not fail the test)
        if not deletion_attempted:
            # best-effort: no deletion performed
            pass

        # If there were errors during deletion, print them to stderr (do not fail the test)
        if deletion_errors:
            print("Warning: cleanup encountered errors:", file=sys.stderr)
            for err in deletion_errors:
                print(err, file=sys.stderr)

if __name__ == "__main__":
    test_student_registration_api()
import requests
import sys
import traceback

BASE_URL = "http://localhost:5001"
LOGIN_URL = f"{BASE_URL}/api/auth/students/login"
PROFILE_URL = f"{BASE_URL}/api/student/profile"
TIMEOUT = 30

def test_student_profile_management():
    session = requests.Session()
    credentials = {"email": "kareena@college.edu", "password": "Password123!"}
    original_profile = None
    try:
        # Login
        resp = session.post(LOGIN_URL, json=credentials, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
        login_json = {}
        try:
            login_json = resp.json()
        except ValueError:
            pass

        # Extract token if present and set Authorization header; otherwise rely on session cookies
        token = None
        for key in ("access_token", "token", "auth_token", "jwt"):
            if isinstance(login_json, dict) and key in login_json:
                token = login_json.get(key)
                break
        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            # Ensure we have some session cookie or at least a successful login response
            if not resp.cookies:
                raise AssertionError("No auth token returned and no session cookie set on login.")

        # GET current profile
        get_resp = session.get(PROFILE_URL, timeout=TIMEOUT)
        assert get_resp.status_code == 200, f"GET profile failed: {get_resp.status_code} {get_resp.text}"
        original_profile = get_resp.json()
        assert isinstance(original_profile, dict), "Original profile response is not a JSON object"

        # Prepare update payload (modify some fields)
        updated_payload = original_profile.copy()
        # Use known profile fields per PRD; set safe defaults if missing.
        updated_payload.update({
            "github_url": "https://github.com/test-kareena-tc006",
            "leetcode_url": "https://leetcode.com/test-kareena-tc006",
            "codeforces_url": "https://codeforces.com/profile/test-kareena-tc006",
            "resume_url": "https://example.com/resume/test-kareena-tc006.pdf",
            "desired_role": "Software Engineer Intern - TC006",
            # If skills is a list, replace; if string, set as comma-separated
            "skills": ["Python", "Algorithms", "Data Structures", "TC006-Test"]
        })

        # PUT update
        put_resp = session.put(PROFILE_URL, json=updated_payload, timeout=TIMEOUT)
        assert put_resp.status_code in (200, 201), f"PUT profile failed: {put_resp.status_code} {put_resp.text}"
        try:
            put_json = put_resp.json()
        except ValueError:
            put_json = None

        # Validate the response contains updated fields
        if isinstance(put_json, dict):
            for key in ("github_url", "leetcode_url", "codeforces_url", "resume_url", "desired_role"):
                assert put_json.get(key) == updated_payload.get(key), f"PUT response missing/incorrect {key}"
            # skills may be returned as list
            returned_skills = put_json.get("skills")
            assert returned_skills is not None, "PUT response missing skills"
            # Convert to set comparison for robustness
            if isinstance(returned_skills, list):
                assert set(returned_skills) >= set(updated_payload["skills"]), "PUT response skills do not include updates"
        else:
            # If server returned no JSON, at least ensure GET reflects update
            pass

        # GET again to ensure persistence
        get2_resp = session.get(PROFILE_URL, timeout=TIMEOUT)
        assert get2_resp.status_code == 200, f"Second GET profile failed: {get2_resp.status_code} {get2_resp.text}"
        profile_after_update = get2_resp.json()
        assert isinstance(profile_after_update, dict), "Profile after update is not JSON object"

        # Validate persisted values
        for key in ("github_url", "leetcode_url", "codeforces_url", "resume_url", "desired_role"):
            assert profile_after_update.get(key) == updated_payload.get(key), f"Persisted {key} does not match updated value"
        returned_skills = profile_after_update.get("skills")
        assert returned_skills is not None, "Persisted profile missing skills"
        if isinstance(returned_skills, list):
            assert set(returned_skills) >= set(updated_payload["skills"]), "Persisted skills do not include updates"

        print("TC006 passed: Student profile retrieved, updated, and persisted successfully.")

    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        raise AssertionError(f"Network/request error during test: {e}")
    except AssertionError:
        traceback.print_exc()
        raise
    except Exception:
        traceback.print_exc()
        raise
    finally:
        # Revert profile to original if we fetched it
        try:
            if original_profile:
                # Use session headers/cookies as before for auth
                revert_resp = session.put(PROFILE_URL, json=original_profile, timeout=TIMEOUT)
                if revert_resp.status_code not in (200, 201):
                    # Attempt to log warning but do not fail the finally block
                    print(f"Warning: failed to revert profile (status {revert_resp.status_code}): {revert_resp.text}", file=sys.stderr)
        except Exception:
            print("Exception occurred while attempting to revert profile.", file=sys.stderr)
            traceback.print_exc()

if __name__ == "__main__":
    test_student_profile_management()
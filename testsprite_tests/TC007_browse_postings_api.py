import requests
import sys
import time

BASE_URL = "http://localhost:5001"
TIMEOUT = 30

STUDENT_CREDENTIALS = {"email": "kareena@college.edu", "password": "Password123!"}
INDUSTRY_CREDENTIALS = {"email": "recruitment@adoratech.io", "password": "Password123!"}

def _extract_token(resp_json):
    # Try common token locations
    for key in ("access_token", "token", "jwt"):
        if key in resp_json:
            return resp_json[key]
    # Common nested patterns
    if isinstance(resp_json.get("data"), dict):
        for key in ("access_token", "token", "jwt"):
            if key in resp_json["data"]:
                return resp_json["data"][key]
    return None

def test_browse_postings_api():
    session = requests.Session()
    created_posting_id = None
    industry_token = None

    try:
        # 1) Student login
        login_url = f"{BASE_URL}/api/auth/students/login"
        r = session.post(login_url, json=STUDENT_CREDENTIALS, timeout=TIMEOUT)
        assert r.status_code == 200, f"Student login failed: {r.status_code} - {r.text}"
        login_json = r.json()
        student_token = _extract_token(login_json)
        assert student_token, f"No token found in student login response: {login_json}"
        student_headers = {"Authorization": f"Bearer {student_token}", "Content-Type": "application/json"}

        # 2) GET postings
        postings_url = f"{BASE_URL}/api/student/postings"
        r = session.get(postings_url, headers=student_headers, timeout=TIMEOUT)
        assert r.status_code == 200, f"GET postings failed: {r.status_code} - {r.text}"
        postings_json = r.json()
        # Expect list either at top-level or under 'data'
        postings_list = None
        if isinstance(postings_json, list):
            postings_list = postings_json
        elif isinstance(postings_json.get("data"), list):
            postings_list = postings_json["data"]
        elif isinstance(postings_json.get("postings"), list):
            postings_list = postings_json["postings"]
        else:
            # try to find list anywhere in response
            for v in postings_json.values():
                if isinstance(v, list):
                    postings_list = v
                    break

        assert postings_list is not None, f"No postings list found in response: {postings_json}"

        # If no postings exist, create one via industry account
        if len(postings_list) == 0:
            # Industry login
            ind_login_url = f"{BASE_URL}/api/auth/industry/login"
            r = session.post(ind_login_url, json=INDUSTRY_CREDENTIALS, timeout=TIMEOUT)
            assert r.status_code == 200, f"Industry login failed: {r.status_code} - {r.text}"
            ind_login_json = r.json()
            industry_token = _extract_token(ind_login_json)
            assert industry_token, f"No token found in industry login response: {ind_login_json}"
            industry_headers = {"Authorization": f"Bearer {industry_token}", "Content-Type": "application/json"}

            # Create posting
            create_posting_url = f"{BASE_URL}/api/industry/postings"
            posting_payload = {
                "title": f"Test Posting {int(time.time())}",
                "description": "Automated test posting for TC007",
                "skills": ["python", "testing"],
                "type": "internship",
                "location": "Remote"
            }
            r = session.post(create_posting_url, headers=industry_headers, json=posting_payload, timeout=TIMEOUT)
            assert r.status_code in (200, 201), f"Create posting failed: {r.status_code} - {r.text}"
            created_json = r.json()
            # try to extract id
            posting_id = None
            if isinstance(created_json, dict):
                for key in ("id", "posting_id", "postingId", "_id"):
                    if key in created_json:
                        posting_id = created_json[key]
                        break
                if posting_id is None and isinstance(created_json.get("data"), dict):
                    for key in ("id", "posting_id", "postingId", "_id"):
                        if key in created_json["data"]:
                            posting_id = created_json["data"][key]
                            break
            assert posting_id, f"Created posting response missing id: {created_json}"
            created_posting_id = posting_id

            # Refresh postings_list by calling student postings again
            r = session.get(postings_url, headers=student_headers, timeout=TIMEOUT)
            assert r.status_code == 200, f"GET postings after create failed: {r.status_code} - {r.text}"
            pj = r.json()
            if isinstance(pj, list):
                postings_list = pj
            elif isinstance(pj.get("data"), list):
                postings_list = pj["data"]
            else:
                # fallback: append created posting id into list for apply step
                postings_list = [{"id": created_posting_id}]

        # 3) Select a posting to apply to
        selected_posting = postings_list[0]
        # Determine posting id from common fields
        posting_id = None
        if isinstance(selected_posting, dict):
            for key in ("id", "posting_id", "postingId", "_id"):
                if key in selected_posting:
                    posting_id = selected_posting[key]
                    break
            # sometimes posting object itself is the id
        if posting_id is None and not isinstance(selected_posting, dict):
            posting_id = selected_posting

        assert posting_id, f"Could not determine posting id from: {selected_posting}"

        # 4) Student apply to posting
        apply_url = f"{BASE_URL}/api/student/apply"
        apply_payload = {"posting_id": posting_id}
        r = session.post(apply_url, headers=student_headers, json=apply_payload, timeout=TIMEOUT)
        assert r.status_code in (200, 201, 202), f"Apply request failed: {r.status_code} - {r.text}"
        apply_json = r.json()
        # Validate application acknowledged
        applied = False
        # Common signs: application id, status 'applied', message containing 'appl'
        if isinstance(apply_json, dict):
            if any(k in apply_json for k in ("application_id", "applicationId", "id")):
                applied = True
            if "status" in apply_json and str(apply_json["status"]).lower() in ("applied", "success"):
                applied = True
            msg = str(apply_json.get("message", "")).lower()
            if "appl" in msg or "success" in msg:
                applied = True
            if isinstance(apply_json.get("data"), dict):
                d = apply_json["data"]
                if any(k in d for k in ("application_id", "id")):
                    applied = True

        assert applied, f"Apply response did not indicate success: {apply_json}"

        print("TC007 passed: Browse postings and apply flow succeeded.")

    except AssertionError:
        raise
    except Exception as e:
        raise
    finally:
        # Cleanup: delete created posting if any
        if created_posting_id and industry_token:
            try:
                industry_headers = {"Authorization": f"Bearer {industry_token}"}
                delete_url = f"{BASE_URL}/api/industry/postings/{created_posting_id}"
                r = session.delete(delete_url, headers=industry_headers, timeout=TIMEOUT)
                # Accept 200/204 as successful delete; if not supported, ignore but log
                if r.status_code not in (200, 204):
                    # attempt alternative delete pattern
                    alt_url = f"{BASE_URL}/api/industry/postings/{created_posting_id}/delete"
                    session.post(alt_url, headers=industry_headers, timeout=TIMEOUT)
            except Exception:
                pass

if __name__ == "__main__":
    test_browse_postings_api()
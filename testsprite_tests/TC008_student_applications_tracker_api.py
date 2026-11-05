import requests
import sys
import traceback

BASE_URL = "http://localhost:5001"
TIMEOUT = 30

STUDENT_EMAIL = "kareena@college.edu"
STUDENT_PASSWORD = "Password123!"

def test_student_applications_tracker_api():
    session = requests.Session()
    application_id = None

    try:
        # 1) Login as student
        login_url = f"{BASE_URL}/api/auth/students/login"
        login_payload = {"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
        resp = session.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert resp.status_code in (200, 201), f"Login failed: {resp.status_code} - {resp.text}"
        try:
            login_json = resp.json()
        except ValueError:
            login_json = {}

        # Attach token if provided, otherwise rely on session cookies
        token = login_json.get("access_token") or login_json.get("token") or login_json.get("jwt") or login_json.get("auth_token")
        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})

        # 2) Retrieve postings to create an application if needed
        postings_url = f"{BASE_URL}/api/student/postings"
        resp = session.get(postings_url, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Failed to fetch postings: {resp.status_code} - {resp.text}"
        try:
            postings_data = resp.json()
        except ValueError:
            postings_data = []

        # Normalize postings list
        if isinstance(postings_data, dict):
            postings_list = postings_data.get("postings") or postings_data.get("data") or postings_data.get("results") or []
        elif isinstance(postings_data, list):
            postings_list = postings_data
        else:
            postings_list = []

        # 3) If there are postings, apply to the first one to ensure there's an application to track
        if postings_list:
            first = postings_list[0]
            # Try to locate posting id in common fields
            posting_id = first.get("id") if isinstance(first, dict) else None
            if not posting_id:
                posting_id = first.get("_id") if isinstance(first, dict) else None
            if not posting_id and isinstance(first, dict):
                # try nested
                for k in ("posting_id", "postingId", "id"):
                    if k in first:
                        posting_id = first[k]
                        break

            assert posting_id, "Could not determine posting id from postings response"

            apply_url = f"{BASE_URL}/api/student/apply"
            apply_payload_candidates = [
                {"posting_id": posting_id},
                {"postingId": posting_id},
                {"id": posting_id}
            ]
            apply_resp = None
            for payload in apply_payload_candidates:
                try:
                    apply_resp = session.post(apply_url, json=payload, timeout=TIMEOUT)
                except Exception:
                    apply_resp = None
                if apply_resp is not None and apply_resp.status_code in (200,201,202):
                    break

            assert apply_resp is not None, "Apply request failed to send"
            assert apply_resp.status_code in (200,201,202), f"Apply failed: {apply_resp.status_code} - {apply_resp.text}"
            try:
                apply_json = apply_resp.json()
            except ValueError:
                apply_json = {}

            # Try to extract application id from response
            if isinstance(apply_json, dict):
                application_id = apply_json.get("id") or apply_json.get("_id") or apply_json.get("application_id") or apply_json.get("applicationId")
                # maybe response wraps application object
                if not application_id:
                    app_obj = apply_json.get("application") or apply_json.get("data")
                    if isinstance(app_obj, dict):
                        application_id = app_obj.get("id") or app_obj.get("_id") or app_obj.get("application_id")
        else:
            # No postings available; proceed to check applications list which may be empty
            posting_id = None

        # 4) Retrieve student's applications
        apps_url = f"{BASE_URL}/api/student/applications"
        resp = session.get(apps_url, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Failed to fetch applications: {resp.status_code} - {resp.text}"
        try:
            apps_data = resp.json()
        except ValueError:
            apps_data = []

        # Normalize applications list
        if isinstance(apps_data, dict):
            apps_list = apps_data.get("applications") or apps_data.get("data") or apps_data.get("results") or []
        elif isinstance(apps_data, list):
            apps_list = apps_data
        else:
            apps_list = []

        assert isinstance(apps_list, list), f"Applications endpoint returned unexpected type: {type(apps_list)}"

        # If we created an application, ensure it appears in the list with a valid status
        if application_id:
            matched = None
            for app in apps_list:
                if not isinstance(app, dict):
                    continue
                aid = app.get("id") or app.get("_id") or app.get("application_id") or app.get("applicationId")
                # some APIs may embed posting id instead; try to match by posting_id
                associated_posting = app.get("posting_id") or app.get("postingId") or (app.get("posting") and app["posting"].get("id"))
                if aid and str(aid) == str(application_id):
                    matched = app
                    break
                if posting_id and associated_posting and str(associated_posting) == str(posting_id):
                    matched = app
                    break

            assert matched is not None, "Created application not found in applications list"

            status = matched.get("status") or matched.get("application_status") or matched.get("state")
            assert status is not None, f"Application found but status field missing: {matched}"
            assert status.lower() in ("applied", "shortlisted", "rejected", "selected"), f"Unexpected application status value: {status}"
        else:
            # No application created; just validate that returned applications (if any) have valid status fields
            for app in apps_list:
                if not isinstance(app, dict):
                    continue
                status = app.get("status") or app.get("application_status") or app.get("state")
                assert status is not None, f"Application item missing status: {app}"
                assert status.lower() in ("applied", "shortlisted", "rejected", "selected"), f"Unexpected application status value: {status}"

        print("TC008 passed: Student applications tracker API returned expected data and statuses.")

    except AssertionError:
        traceback.print_exc()
        raise
    except Exception:
        traceback.print_exc()
        raise
    finally:
        # Cleanup: attempt to delete the created application if API supports it
        if application_id:
            try:
                delete_url = f"{BASE_URL}/api/student/applications/{application_id}"
                del_resp = session.delete(delete_url, timeout=TIMEOUT)
                # accept 200/204/202 or 404 if already removed/unsupported
                if del_resp.status_code not in (200, 202, 204, 404):
                    print(f"Warning: unexpected delete response {del_resp.status_code} - {del_resp.text}")
            except Exception:
                # best-effort cleanup; ignore errors
                pass

if __name__ == "__main__":
    try:
        test_student_applications_tracker_api()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    sys.exit(0)
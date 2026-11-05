import requests
import sys
import traceback

BASE_URL = "http://localhost:5001"
TIMEOUT = 30.0

INDUSTRY_EMAIL = "recruitment@adoratech.io"
INDUSTRY_PASSWORD = "Password123!"

def test_industry_post_opportunity_api():
    session = requests.Session()
    created_post_id = None

    try:
        # 1) Login as industry partner
        login_url = f"{BASE_URL}/api/auth/industry/login"
        login_payload = {"email": INDUSTRY_EMAIL, "password": INDUSTRY_PASSWORD}
        login_headers = {"Content-Type": "application/json"}

        resp = session.post(login_url, json=login_payload, headers=login_headers, timeout=TIMEOUT)
        assert resp.status_code == 200, f"Industry login failed: {resp.status_code} - {resp.text}"

        # Try to obtain token; if present, add to session headers for Authorization
        token = None
        try:
            login_json = resp.json()
            token = login_json.get("access_token") or login_json.get("token") or login_json.get("jwt")
        except Exception:
            login_json = None

        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})

        # 2) Create a new posting
        create_url = f"{BASE_URL}/api/industry/postings"
        post_title = "Test Automation Engineer Internship - TC009"
        create_payload = {
            "title": post_title,
            "description": "Internship for Test Automation engineers. Work on backend testing and integration.",
            "required_skills": ["testing", "python", "automation"],
            "posting_type": "internship",
            "location": "Remote",
            "salary": "0-20000",
        }
        resp = session.post(create_url, json=create_payload, timeout=TIMEOUT)
        assert resp.status_code in (200, 201), f"Create posting failed: {resp.status_code} - {resp.text}"

        try:
            created_json = resp.json()
        except ValueError:
            created_json = {}

        # attempt to extract created id from common fields
        created_post_id = (
            created_json.get("id")
            or created_json.get("_id")
            or created_json.get("posting_id")
            or created_json.get("post_id")
        )

        # Validate response contains the title or an id
        assert (created_post_id is not None) or (created_json.get("title") == post_title) or (post_title in str(created_json)), \
            f"Created posting response did not contain expected data: {created_json}"

        # 3) Verify posting is listed for the industry user
        list_url_candidates = [
            f"{BASE_URL}/api/industry/postings",
            f"{BASE_URL}/api/student/postings"
        ]
        listed = False
        last_list_resp_text = None

        for list_url in list_url_candidates:
            try:
                resp = session.get(list_url, timeout=TIMEOUT)
            except Exception as e:
                last_list_resp_text = f"Request error: {e}"
                continue

            if resp.status_code != 200:
                last_list_resp_text = f"{resp.status_code} - {resp.text}"
                continue

            try:
                listings = resp.json()
            except ValueError:
                listings = None

            # Normalize listings: could be a list or dict containing list
            items = []
            if isinstance(listings, list):
                items = listings
            elif isinstance(listings, dict):
                # common keys that might contain postings
                for k in ("postings", "data", "results", "items"):
                    if isinstance(listings.get(k), list):
                        items = listings.get(k)
                        break
                # if none found, but dict may directly represent a single posting
                if not items and ("title" in listings or "id" in listings):
                    items = [listings]

            # Search for our title in items
            for it in items:
                try:
                    title = it.get("title") if isinstance(it, dict) else None
                except Exception:
                    title = None
                if title == post_title or (isinstance(it, str) and post_title in it) or (post_title in str(it)):
                    listed = True
                    break

            if listed:
                break
            else:
                last_list_resp_text = str(listings)

        assert listed, f"Created posting was not found in listings. Last list response: {last_list_resp_text}"

        print("TC009 passed: industry partner created a posting and it is listed.")

    except AssertionError:
        traceback.print_exc()
        raise
    except Exception:
        traceback.print_exc()
        raise
    finally:
        # cleanup: attempt to delete the created posting if we have an id
        if created_post_id:
            try:
                delete_url = f"{BASE_URL}/api/industry/postings/{created_post_id}"
                resp = session.delete(delete_url, timeout=TIMEOUT)
                # Accept 200/204/202 as successful deletion; ignore other statuses but print
                if resp.status_code not in (200, 202, 204):
                    print(f"Warning: deletion returned status {resp.status_code}: {resp.text}")
            except Exception:
                print("Warning: exception occurred while trying to delete the created posting.")
        session.close()


if __name__ == "__main__":
    try:
        test_industry_post_opportunity_api()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    else:
        sys.exit(0)
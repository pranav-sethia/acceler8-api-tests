import requests
import pytest
from config import API_HOST, ORG_HEADERS as HEADERS

ASSESS_URL = f"{API_HOST}/backend/v1/assessment"


@pytest.fixture(scope="module")
def created_assessment():
    """Create one assessment under which we’ll attach prepare-content."""
    body = {
        "capabilities":    ["TECHNICAL SKILLS 1"],
        "name":            "Test assessment for prepare-content",
        "show_onboarding": False,
        "assessment_type": "EMPLOYEE"
    }
    r = requests.post(ASSESS_URL, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text
    aid = r.json()["data"]["id"]
    yield aid
    requests.delete(f"{ASSESS_URL}/{aid}", headers=HEADERS)


@pytest.fixture(scope="module")
def created_employee(created_assessment):
    """
    Add a real employee so that prepare-content endpoints will accept our requests.
    """
    url = f"{API_HOST}/backend/v1/assessment/{created_assessment}/employee"

    body = {
        "email":                     "test_pranav_email",
        "name":                      "E1",
        "position":                  "A",
        "title":                     "A",
        "number_of_direct_reports":  "1",
        "number_of_indirect_reports":"1",
        "join_date":                 "2025-06-01",
        "tenure":                    1,
        "years_to_retirement":       1,
        "manager": {
            "email":                      "test_pranav_manager_email",
            "name":                       "A",
            "position":                   "A",
            "title":                      "A",
            "number_of_direct_reports":   None,
            "number_of_indirect_reports": None,
            "join_date":                  None,
            "tenure":                     None,
            "years_to_retirement":        None,
            "performance_rating":         None,
            "voice_of_customer_results":  None,
            "team_attrition_rate_current_year":   None,
            "team_attrition_rate_previous_year":  None,
            "voice_of_employee_results":          None
        },
        "performance_rating":           "1",
        "voice_of_customer_results":    "1",
        "team_attrition_rate_current_year":  "1",
        "team_attrition_rate_previous_year": "1",
        "voice_of_employee_results":    "1"
    }

    r = requests.post(url, json=body, headers=HEADERS)
    assert r.status_code == 201, r.text
    eid = r.json()["data"]["id"]
    yield eid
    requests.delete(f"{url}/{eid}", headers=HEADERS)


@pytest.fixture(scope="module")
def created_prepare_content(created_assessment, created_employee):
    """
    Create one prepare-content, now that the assessment has at least one employee.
    """
    base       = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    create_url = f"{base}/prepare-content"

    body = {
        "title": "A",
        "embed_items": [
            {
                "id": 1,
                "type": "TEXT",
                "content": "A"
            }
        ],
        "attachments_title": "",
        "quiz_title": "",
        "send_date": "2025-06-11",
        "send_time": "12:54:10",
        "timezone": "Asia/Calcutta",
        "attachments": [],
        "quizzes": [
            {
                "id": 0,
                "type": "SUBJECTIVE",
                "question": "A",
                "options": [],
                "submitted": False,
                "correct_options": [],
                "correct_options_count": 0
            }
        ],
        "recipient_emails": [],
        "send_to_all": True,
        "organisation_id": "4540c249-64bc-4356-b6fc-37ac600d3627"
    }

    r = requests.post(create_url, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text
    pc_id = r.json()["data"]["id"]
    yield pc_id

    requests.delete(f"{create_url}/{pc_id}", headers=HEADERS)


def test_list_prepare_contents(created_assessment, created_prepare_content):
    """
    GET /assessment/:aid/prepare-contents should include our new item.
    """
    url = f"{API_HOST}/backend/v1/assessment/{created_assessment}/prepare-contents"
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200
    items = r.json()
    ids = [i["id"] for i in items["data"]]
    assert created_prepare_content in ids


def test_get_prepare_content_details(created_assessment, created_prepare_content):
    """
    GET /assessment/:aid/prepare-content/:pcId returns the correct object.
    """
    url = (
        f"{API_HOST}/backend/v1/assessment/"
        f"{created_assessment}/prepare-content/{created_prepare_content}"
    )
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["id"] == created_prepare_content
    assert data["title"] == "A"


def test_update_prepare_content(created_assessment, created_prepare_content):
    """
    PUT /assessment/:aid/prepare-content/:pcId with the exact update body.
    """
    base       = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    update_url = f"{base}/prepare-content/{created_prepare_content}"

    body = {
        "title": "B",
        "embed_items": [
            {
                "id": 1,
                "type": "TEXT",
                "content": "A"
            }
        ],
        "attachments_title": "",
        "quiz_title": "",
        "send_date": "2025-06-11",
        "send_time": "12:54:10",
        "timezone": "Asia/Calcutta",
        "attachments": [],
        "quizzes": [
            {
                "id": 0,
                "type": "SUBJECTIVE",
                "question": "A",
                "options": [],
                "submitted": False,
                "correct_options": [],
                "correct_options_count": 0
            }
        ],
        "recipient_emails": [],
        "send_to_all": True,
        "organisation_id": "4540c249-64bc-4356-b6fc-37ac600d3627"
    }

    r = requests.put(update_url, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text

    r2 = requests.get(update_url, headers=HEADERS)
    assert r2.status_code == 200
    assert r2.json()["data"]["title"] == "B"


def test_delete_prepare_content(created_assessment):
    """
    Create a disposable prepare-content and then delete it.
    """
    base       = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    create_url = f"{base}/prepare-content"

    body = {
        "title": "To delete",
        "embed_items": [
            {
                "id": 1,
                "type": "TEXT",
                "content": "X"
            }
        ],
        "attachments_title": "",
        "quiz_title": "",
        "send_date": "2025-06-11",
        "send_time": "12:54:10",
        "timezone": "Asia/Calcutta",
        "attachments": [],
        "quizzes": [],
        "recipient_emails": [],
        "send_to_all": True,
        "organisation_id": "4540c249-64bc-4356-b6fc-37ac600d3627"
    }

    r0 = requests.post(create_url, json=body, headers=HEADERS)
    assert r0.status_code == 200, r0.text
    pid = r0.json()["data"]["id"]

    r1 = requests.delete(f"{create_url}/{pid}", headers=HEADERS)
    assert r1.status_code in (200, 204)

    r2 = requests.get(f"{create_url}/{pid}", headers=HEADERS)
    assert r2.status_code in (403, 404)

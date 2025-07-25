import requests
import pytest
from config import API_HOST, HEADERS

ASSESS_URL      = f"{API_HOST}/backend/v1/assessment"
ASSESS_LIST_URL = f"{API_HOST}/backend/v1/assessments"

@pytest.fixture(scope="module")
def created_assessment():
    body = {
        "capabilities":    ["TECHNICAL SKILLS 1"],
        "name":            "Test assessment for action‐items",
        "show_onboarding": False,
        "assessment_type": "EMPLOYEE"
    }

    r = requests.post(ASSESS_URL, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text
    aid = r.json()["data"]["id"]
    yield aid
    requests.delete(f"{ASSESS_URL}/{aid}", headers=HEADERS)


@pytest.fixture(scope="module")
def created_action_item(created_assessment):
    base         = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    create_url   = f"{base}/action-item"

    body = {
        "title": "A",
        "embed_items": [
            {
                "id": 1,
                "type": "TEXT",
                "content": ""
            }
        ],
        "attachments_title": "",
        "quiz_title": "",
        "send_date": "2025-06-10",
        "send_time": "12:34:46",
        "timezone": "Asia/Calcutta",
        "attachments": [],
        "quizzes": [
            {
                "id": 0,
                "type": "SUBJECTIVE",
                "question": "Question",
                "options": [],
                "submitted": False,
                "correct_options": [],
                "correct_options_count": 0
            }
        ],
        "recipient_emails": [],
        "send_to_all": True,
        "organisation_id": "2c940cb1-0431-40f7-a114-9c481194e0fc"
    }

    r = requests.post(create_url, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text
    action_id = r.json()["data"]["id"]
    yield action_id
    requests.delete(f"{create_url}/{action_id}", headers=HEADERS)


def test_get_action_item_details(created_assessment, created_action_item):
    url = (
        f"{API_HOST}/backend/v1/assessment/"
        f"{created_assessment}/action-item/{created_action_item}"
    )
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["id"] == created_action_item
    assert data["title"] == "A"


def test_update_action_item(created_assessment, created_action_item):
    base       = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    update_url = f"{base}/action-item/{created_action_item}"

    body = {
        "title": "B",
        "embed_items": [
            {
                "id": 1,
                "type": "TEXT",
                "content": ""
            }
        ],
        "attachments_title": "",
        "quiz_title": "",
        "send_date": "2025-06-10",
        "send_time": "12:34:46",
        "timezone": "Asia/Calcutta",
        "attachments": [],
        "quizzes": [
            {
                "id": 0,
                "type": "SUBJECTIVE",
                "question": "Question",
                "options": [],
                "submitted": False,
                "correct_options": [],
                "correct_options_count": 0
            }
        ],
        "recipient_emails": [],
        "send_to_all": True,
        "organisation_id": "2c940cb1-0431-40f7-a114-9c481194e0fc"
    }

    r = requests.put(update_url, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text

    r2 = requests.get(update_url, headers=HEADERS)
    assert r2.status_code == 200
    assert r2.json()["data"]["title"] == "B"


def test_list_action_items(created_assessment, created_action_item):
    url = (
        f"{API_HOST}/backend/v1/assessment/"
        f"{created_assessment}/action-items"
        "?page_number=1&page_size=1"
    )
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200
    page = r.json()
    items = page["data"]
    assert created_action_item in [i["id"] for i in items]


def test_delete_action_item(created_assessment):
    base       = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    create_url = f"{base}/action-item"

    body = {
        "title": "To delete",
        "embed_items": [
            {
                "id": 1,
                "type": "TEXT",
                "content": ""
            }
        ],
        "attachments_title": "",
        "quiz_title": "",
        "send_date": "2025-06-10",
        "send_time": "12:34:46",
        "timezone": "Asia/Calcutta",
        "attachments": [],
        "quizzes": [],
        "recipient_emails": [],
        "send_to_all": True,
        "organisation_id": "2c940cb1-0431-40f7-a114-9c481194e0fc"
    }
    r0 = requests.post(create_url, json=body, headers=HEADERS)
    assert r0.status_code == 200, r0.text
    did = r0.json()["data"]["id"]

    r1 = requests.delete(f"{create_url}/{did}", headers=HEADERS)
    assert r1.status_code in (200, 204)

    r2 = requests.get(f"{create_url}/{did}", headers=HEADERS)
    assert r2.status_code in (403, 404)
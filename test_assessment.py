import requests
import pytest
import json

from config import API_HOST, ORG_HEADERS as HEADERS

ASSESS_URL = f"{API_HOST}/backend/v1/assessment"
ASSESS_LIST_URL = f"{API_HOST}/backend/v1/assessments"

@pytest.fixture(scope="module")
def created_assessment():
    body = {
        "capabilities":     ["TECHNICAL SKILLS 1"],
        "name":             "Pranav test 1",
        "show_onboarding":  False,
        "assessment_type":  "EMPLOYEE"
    }
    response = requests.post(ASSESS_URL, json=body, headers=HEADERS)
    assert response.status_code == 200, f"POST failed: {response.text}"
    aid = response.json()["data"]["id"]
    yield aid

    dr = requests.delete(f"{ASSESS_URL}/{aid}", headers=HEADERS)
    assert dr.status_code == 204


def test_get_assessment_details(created_assessment):
    response = requests.get(f"{ASSESS_URL}/{created_assessment}", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == created_assessment
    assert data["name"] == "Pranav test 1"

def test_update_assessment(created_assessment):
    upd = {"name": "Pranav test updated"}
    response1 = requests.put(f"{ASSESS_URL}/{created_assessment}", json=upd, headers=HEADERS)
    assert response1.status_code == 200

    response2 = requests.get(f"{ASSESS_URL}/{created_assessment}", headers=HEADERS)
    assert response2.json()["data"]["name"] == "Pranav test updated"


def test_list_assessments(created_assessment):
    response = requests.get(ASSESS_LIST_URL, headers=HEADERS)
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["data"]]
    assert created_assessment in ids


def test_delete_assessment():
    body = {
        "capabilities":     ["TECHNICAL SKILLS 1"],
        "name":             "ToBeDeleted",
        "show_onboarding":  False,
        "assessment_type":  "EMPLOYEE"
    }
    response0 = requests.post(ASSESS_URL, json=body, headers=HEADERS)
    assert response0.status_code == 200
    aid = response0.json()["data"]["id"]

    response1 = requests.delete(f"{ASSESS_URL}/{aid}", headers=HEADERS)
    assert response1.status_code == 204

    response2 = requests.get(f"{ASSESS_URL}/{aid}", headers=HEADERS)
    assert response2.status_code in (404, 403)


"""
Onboarding tests
Tests employee onboarding configuration and workflows
"""
import requests
import pytest
import random
import string
from config import API_HOST, ORG_HEADERS as HEADERS

ASSESS_URL = f"{API_HOST}/backend/v1/assessment"

@pytest.fixture(scope="module")
def created_assessment():
    """Create an assessment for onboarding tests"""
    body = {
        "capabilities": ["TECHNICAL SKILLS 1"],
        "name": "Test Assessment for Onboarding",
        "show_onboarding": False,
        "assessment_type": "EMPLOYEE"
    }
    r = requests.post(ASSESS_URL, json=body, headers=HEADERS)
    r.raise_for_status()
    aid = r.json()["data"]["id"]
    yield aid
    # Cleanup: delete assessment after tests
    requests.delete(f"{ASSESS_URL}/{aid}", headers=HEADERS)


@pytest.fixture(scope="module")
def created_employee(created_assessment):
    """Create an employee for onboarding tests"""
    rand_id = "".join(random.choices(string.ascii_lowercase, k=5))
    create_url = f"{ASSESS_URL}/{created_assessment}/employee"
    body = {
        "email": f"onboarding_emp_{rand_id}@example.com",
        "name": "Onboarding Employee",
        "manager": {"email": f"onboarding_mgr_{rand_id}@example.com", "name": "Onboarding Manager"}
    }
    r = requests.post(create_url, json=body, headers=HEADERS)
    assert r.status_code == 201, r.text
    eid = r.json()["data"]["id"]
    yield eid
    # Cleanup: delete employee after tests
    delete_url = f"{API_HOST}/backend/v1/employee/{eid}"
    requests.delete(delete_url, headers=HEADERS)


def test_setup_and_get_onboarding_data(created_assessment, created_employee):
    """Test setting up onboarding configuration and retrieving it"""
    base_onboarding_url = f"{ASSESS_URL}/{created_assessment}/onboarding/home"

    # Setup onboarding configuration
    setup_body = {
        "program_name": "P1",
        "service_personalization": [
            {"service": "LETTER_TO_YOURSELF", "position": 0},
            {"service": "PREPARE", "position": 1},
            {"service": "ACCELER8_CAPABILITY_JOURNEY", "position": 2}
        ],
        "number_of_days": 103
    }
    r_setup = requests.post(base_onboarding_url, json=setup_body, headers=HEADERS)
    assert r_setup.status_code == 200, r_setup.text

    # Get onboarding data for specific employee
    get_url = f"{base_onboarding_url}?employee_id={created_employee}"
    r_get = requests.get(get_url, headers=HEADERS)
    assert r_get.status_code == 200, r_get.text
    
    data = r_get.json()["data"]
    assert data["program_name"] == "P1"
    assert data["number_of_days"] == 103
    assert len(data["service_personalization"]) == 3
    assert data["service_personalization"][0]["service"] == "LETTER_TO_YOURSELF"


def test_send_onboarding_email(created_assessment):
    """Test sending onboarding emails to employees"""
    setup_url = f"{ASSESS_URL}/{created_assessment}/onboarding/home"
    
    # Setup onboarding first
    setup_body = {
        "program_name": "Email Test",
        "service_personalization": [
            {"service": "LETTER_TO_YOURSELF", "position": 0},
            {"service": "PREPARE", "position": 1}
        ],
        "number_of_days": 10
    }
    requests.post(setup_url, json=setup_body, headers=HEADERS).raise_for_status()

    # Send onboarding emails
    email_url = f"{ASSESS_URL}/{created_assessment}/onboarding/email"
    r_email = requests.post(email_url, headers=HEADERS)
    assert r_email.status_code == 200, r_email.text


def test_admin_can_edit_onboarding_content(created_assessment):
    """Test that admin can update onboarding configuration"""
    onboarding_url = f"{ASSESS_URL}/{created_assessment}/onboarding/home"

    # Initial setup
    setup_body = {
        "program_name": "Initial Program Name",
        "service_personalization": [{"service": "LETTER_TO_YOURSELF", "position": 0}],
        "number_of_days": 30
    }
    r_setup = requests.post(onboarding_url, json=setup_body, headers=HEADERS)
    assert r_setup.status_code == 200, f"Onboarding setup failed: {r_setup.text}"

    # Update configuration
    update_body = {
        "program_name": "Updated Program Name",
        "service_personalization": [
            {"service": "LETTER_TO_YOURSELF", "position": 0},
            {"service": "PREPARE", "position": 1}
        ],
        "number_of_days": 45
    }
    r_update = requests.post(onboarding_url, json=update_body, headers=HEADERS)
    assert r_update.status_code == 200, f"Onboarding update failed: {r_update.text}"

    # Verify the update
    r_get = requests.get(onboarding_url, headers=HEADERS)
    assert r_get.status_code == 200
    updated_data = r_get.json()["data"]

    assert updated_data["program_name"] == "Updated Program Name"
    assert updated_data["number_of_days"] == 45
    assert len(updated_data["service_personalization"]) == 2
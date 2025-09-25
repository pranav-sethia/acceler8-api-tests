"""
Master questions tests
Tests global question bank management
"""
import requests
import pytest
import random
import string
from config import API_HOST, ORG_HEADERS as HEADERS

QUESTION_URL = f"{API_HOST}/backend/v1/question"

@pytest.fixture
def created_question_id():
    """Create a basic question for testing and clean up after"""
    body = {
        "capabilities": "Test Capability", "capabilities_label": "Test Label",
        "sub_capability": f"Test Sub-Cap {random.randint(100, 999)}",
        "type": "OBJECTIVE_SINGLE", "question": "Original Question Text?",
        "options": [{"value": "A", "input_required": False}], "ranking": [1], "sl_no": 1
    }
    response = requests.post(QUESTION_URL, json=body, headers=HEADERS)
    assert response.status_code == 200, f"Fixture setup failed: {response.text}"
    qid = response.json()["id"]
    yield qid
    # Cleanup: delete question after test
    requests.delete(f"{QUESTION_URL}/{qid}", headers=HEADERS)

def test_create_ranking_question():
    """Test creating a ranking type question"""
    body = {
        "capabilities": "Ranking Capability", "capabilities_label": "Ranking Label",
        "sub_capability": f"Ranking Sub-Cap {random.randint(100, 999)}",
        "type": "OBJECTIVE_RANKING", "question": "Please rank these options.",
        "options": [{"value": "Option 1"}, {"value": "Option 2"}], "ranking": [2, 1], "sl_no": 1
    }
    r = requests.post(QUESTION_URL, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["type"] == "OBJECTIVE_RANKING"
    # Cleanup
    requests.delete(f"{QUESTION_URL}/{data['id']}", headers=HEADERS)

def test_create_and_publish_employee_only_question():
    """Test creating employee-only question and publishing it"""
    body = {
        "capabilities": "Employee-Only Cap", "capabilities_label": "Employee-Only Label",
        "sub_capability": f"Emp-Only Sub-Cap {random.randint(100, 999)}",
        "type": "OBJECTIVE_SINGLE", "question": "This is an employee-only question.",
        "visibility": ["EMPLOYEE"], "options": [{"value": "OK"}],
        "ranking": [1], "sl_no": 1, "manager_question": None
    }
    r_create = requests.post(QUESTION_URL, json=body, headers=HEADERS)
    assert r_create.status_code == 200, r_create.text
    created_question = r_create.json()
    question_id = created_question["id"]
    assert created_question["status"] == "DRAFT"
    
    # Publish the question
    created_question["status"] = "PUBLISHED"
    update_body = {"questions_to_update": [created_question]}
    
    r_update = requests.post(f"{QUESTION_URL}/bulk", json=update_body, headers=HEADERS)
    assert r_update.status_code == 200, r_update.text
    assert r_update.json()[0]["status"] == "PUBLISHED"
    # Cleanup
    requests.delete(f"{QUESTION_URL}/{question_id}", headers=HEADERS)

def test_update_question(created_question_id):
    """Test updating an existing question"""
    r_get = requests.get(f"{QUESTION_URL}/{created_question_id}", headers=HEADERS)
    assert r_get.status_code == 200
    original_question = r_get.json()

    # Modify the question
    original_question["question"] = "This is the updated question text."
    original_question["sub_capability"] = "Updated Sub-Cap"
    
    update_body = {"questions_to_update": [original_question]}
    r_update = requests.post(f"{QUESTION_URL}/bulk", json=update_body, headers=HEADERS)
    assert r_update.status_code == 200, r_update.text

    # Verify the update
    r_get_updated = requests.get(f"{QUESTION_URL}/{created_question_id}", headers=HEADERS)
    assert r_get_updated.status_code == 200
    updated_data = r_get_updated.json()
    assert updated_data["question"] == "This is the updated question text."
    assert updated_data["sub_capability"] == "Updated Sub-Cap"

def test_create_question_fails_with_manager_only():
    """Test validation: manager-only questions should fail"""
    body = {
        "capabilities": "Manager-Only Fail Test", "capabilities_label": "Manager-Only Fail Label",
        "sub_capability": f"Mgr-Only Sub-Cap {random.randint(100, 999)}", "type": "OBJECTIVE_SINGLE",
        "question": None, "manager_question": "This is a manager-only question."  # No employee question
    }
    r = requests.post(QUESTION_URL, json=body, headers=HEADERS)
    assert r.status_code == 400

def test_create_question_validation_failures():
    """Test various validation failures"""
    # Empty sub-capability should fail
    body_empty_sub_cap = {"capabilities": "Val", "capabilities_label": "Val", "sub_capability": "", "type": "OBJECTIVE_SINGLE", "question": "Q?", "options": [{"value": "A"}], "ranking": [1], "sl_no": 1}
    r1 = requests.post(QUESTION_URL, json=body_empty_sub_cap, headers=HEADERS)
    assert r1.status_code == 400

    # Missing type should fail
    body_no_type = {"capabilities": "Val", "capabilities_label": "Val", "sub_capability": "No Type", "question": "Q?", "options": [{"value": "A"}], "ranking": [1], "sl_no": 1}
    r2 = requests.post(QUESTION_URL, json=body_no_type, headers=HEADERS)
    assert r2.status_code == 400

    # No options for multiple choice should fail
    body_no_options = {"capabilities": "Val", "capabilities_label": "Val", "sub_capability": "No Options", "type": "OBJECTIVE_MULTIPLE", "question": "Q?", "options": [], "sl_no": 1}
    r3 = requests.post(QUESTION_URL, json=body_no_options, headers=HEADERS)
    assert r3.status_code == 500

@pytest.mark.xfail(reason="API currently allows duplicate options, which is a bug.")
def test_validation_duplicate_options():
    """Test that duplicate options should be rejected"""
    body = {"capabilities": "Val", "capabilities_label": "Val", "sub_capability": "Duplicate Options", "type": "OBJECTIVE_SINGLE", "question": "Q?", "options": [{"value": "A"}, {"value": "A"}], "ranking": [2, 1], "sl_no": 1}
    r = requests.post(QUESTION_URL, json=body, headers=HEADERS)
    assert r.status_code == 400

@pytest.mark.xfail(reason="API currently allows duplicate ranking points, which is a bug.")
def test_validation_duplicate_ranking_points():
    """Test that duplicate ranking points should be rejected"""
    body = {"capabilities": "Val", "capabilities_label": "Val", "sub_capability": "Duplicate Ranking", "type": "OBJECTIVE_SINGLE", "question": "Q?", "options": [{"value": "A"}, {"value": "B"}], "ranking": [1, 1], "sl_no": 1}
    r = requests.post(QUESTION_URL, json=body, headers=HEADERS)
    assert r.status_code == 400

@pytest.mark.xfail(reason="API currently allows duplicate sub-capabilities, which is a bug.")
def test_create_question_fails_with_duplicate_sub_capability():
    """Test that duplicate sub-capabilities should be rejected"""
    cap = "Duplicate Test Capability"
    sub_cap = f"Duplicate Sub-Cap {random.randint(100, 999)}"
    body = {"capabilities": cap, "capabilities_label": "Label", "sub_capability": sub_cap, "type": "OBJECTIVE_SINGLE", "question": "Q1", "options": [{"value": "A"}], "ranking": [1], "sl_no": 1}
    q1_id = None
    try:
        r1 = requests.post(QUESTION_URL, json=body, headers=HEADERS)
        assert r1.status_code == 200
        q1_id = r1.json()["id"]
        # Try to create another question with same sub-capability
        body2 = {"capabilities": cap, "capabilities_label": "Label", "sub_capability": sub_cap, "type": "OBJECTIVE_SINGLE", "question": "Q2", "options": [{"value": "B"}], "ranking": [1], "sl_no": 2}
        r2 = requests.post(QUESTION_URL, json=body2, headers=HEADERS)
        assert r2.status_code == 409
    finally:
        # Cleanup
        if q1_id:
            requests.delete(f"{QUESTION_URL}/{q1_id}", headers=HEADERS)
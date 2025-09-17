import requests
import pytest
from config import API_HOST, ORG_HEADERS as HEADERS

ASSESS_URL = f"{API_HOST}/backend/v1/assessment"
ASSESS_LIST_URL  = f"{API_HOST}/backend/v1/assessments"

@pytest.fixture(scope="module")
def created_assessment(): 
    body = {
        "capabilities":    ["TECHNICAL SKILLS 1"],
        "name":            "Test assessment questions API",
        "show_onboarding": False,
        "assessment_type": "EMPLOYEE"
    }
    r = requests.post(ASSESS_URL, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text
    aid = r.json()["data"]["id"]
    yield aid

    requests.delete(f"{ASSESS_URL}/{aid}", headers=HEADERS)

@pytest.fixture(scope="module")
def created_assessment_question(created_assessment):
    base = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    create_q_url = f"{base}/question"
    body = {
        "capabilities": "Technical Skills 1",
        "sub_capability": "Java 1",
        "capabilities_label": "Technical Skills 1 Label",
        "type": "OBJECTIVE_SINGLE",
        "question": "What is your proficiency level in Java?",
        "options": [
            {"value": "Beginner",     "input_required": False},
            {"value": "Intermediate", "input_required": False},
            {"value": "Advanced",     "input_required": False}
        ],
        "ranking":            [4, 3, 2, 1],
        "sl_no":              1,
        "capabilities_sl_no": 1,
        "manager_question_type": "OBJECTIVE_SINGLE",
        "manager_question":      "Rate the employee's Java proficiency",
        "manager_options": [
            {"value": "Beginner",     "input_required": False},
            {"value": "Intermediate", "input_required": False},
            {"value": "Advanced",     "input_required": False}
        ],
        "manager_ranking":    [4, 3, 2, 1]
    }

    response = requests.post(create_q_url, json=body, headers=HEADERS)
    assert response.status_code == 200, response.text
    qid = response.json()["id"]
    yield qid

    requests.delete(f"{create_q_url}/{qid}", headers=HEADERS)

def test_list_assessment_questions(created_assessment, created_assessment_question):
    base = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    list_url = f"{base}/questions"

    r = requests.get(list_url, headers=HEADERS)
    assert r.status_code == 200
    questions = r.json()
    assert isinstance(questions, list)
    ids = [q["id"] for q in questions]
    assert created_assessment_question in ids

def test_get_assessment_question_details(created_assessment, created_assessment_question):
    base = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    get_url = f"{base}/question/{created_assessment_question}"

    r = requests.get(get_url, headers=HEADERS)
    assert r.status_code == 200
    q = r.json()
    assert q["id"] == created_assessment_question
    assert q["question"] == "What is your proficiency level in Java?"

def test_delete_assessment_question(created_assessment):
    base = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    create_q_url = f"{base}/question"

    body = {
        "capabilities": "Technical Skills 1",
        "sub_capability": "Java 1",
        "capabilities_label": "Technical Skills 1 Label",
        "type": "OBJECTIVE_SINGLE",
        "question": "Temp delete?",
        "options": [
            {"value": "Yes", "input_required": False},
            {"value": "No",  "input_required": False}
        ],
        "ranking": [2, 1],
        "sl_no": 99,
        "capabilities_sl_no": 9,
        "manager_question_type": "OBJECTIVE_SINGLE",
        "manager_question": "Temp manager?",
        "manager_options": [
            {"value": "Yes", "input_required": False},
            {"value": "No",  "input_required": False}
        ],
        "manager_ranking": [2, 1]
    }
    r0 = requests.post(create_q_url, json=body, headers=HEADERS)
    assert r0.status_code == 200
    did = r0.json()["id"]

    r1 = requests.delete(f"{create_q_url}/{did}", headers=HEADERS)
    assert r1.status_code == 204

    r2 = requests.get(f"{create_q_url}/{did}", headers=HEADERS)
    assert r2.status_code in (403, 404)

def test_bulk_create_update_and_delete(created_assessment):
    base       = f"{API_HOST}/backend/v1/assessment/{created_assessment}"
    create_q   = f"{base}/question"
    bulk_url   = f"{base}/question/bulk"
    get_q      = lambda qid: f"{create_q}/{qid}"

    resp_u = requests.post(create_q, json={
        "capabilities": "To update",
        "sub_capability": "Subcap",
        "capabilities_label": "To update label",
        "type": "OBJECTIVE_SINGLE",
        "question": "Original text?",
        "options": [{"value":"X","input_required":False}],
        "ranking":[1],"sl_no":42,"capabilities_sl_no":42,
        "manager_question_type":"OBJECTIVE_SINGLE",
        "manager_question":"Orig mgr?",
        "manager_options":[{"value":"X","input_required":False}],
        "manager_ranking":[1]
    }, headers=HEADERS)
    assert resp_u.status_code == 200, resp_u.text
    q_update_id = resp_u.json()["id"]

    resp_d = requests.post(create_q, json={
        "capabilities": "To delete",
        "sub_capability": "Subcap",
        "capabilities_label": "To delete label",
        "type": "OBJECTIVE_SINGLE",
        "question": "Please delete me",
        "options":[{"value":"Y","input_required":False}],
        "ranking":[1],"sl_no":99,"capabilities_sl_no":99,
        "manager_question_type":"OBJECTIVE_SINGLE",
        "manager_question":"Del mgr?",
        "manager_options":[{"value":"Y","input_required":False}],
        "manager_ranking":[1]
    }, headers=HEADERS)
    assert resp_d.status_code == 200, resp_d.text
    q_delete_id = resp_d.json()["id"]

    bulk_body = {
        "questions_to_create": [
            {
                "capabilities": "Technical Skills",
                "capabilities_label": "Technical Skills", 
                "sub_capability": "Java",
                "type": "OBJECTIVE_SINGLE",
                "question": "What is your proficiency level in Java?",
                "options": [
                    {"value":"Beginner","input_required":False},
                    {"value":"Intermediate","input_required":False},
                    {"value":"Advanced","input_required":False}
                ],
                "ranking":[4,3,2,1],
                "sl_no":1,
                "manager_question_type":"OBJECTIVE_SINGLE",
                "manager_question":"Rate the employee's Java proficiency",
                "manager_options":[
                    {"value":"Beginner","input_required":False},
                    {"value":"Intermediate","input_required":False},
                    {"value":"Advanced","input_required":False}
                ],
                "manager_ranking":[4,3,2,1]
            }
        ],
        "questions_to_update": [
            {
                "id": q_update_id,
                "status": "PUBLISHED",
                "capabilities": "Powerful Storyteller V3",
                "capabilities_label": "Powerful Storyteller V3 Label",
                "sub_capability": "Narrative Construction and Story-Telling",
                "visibility": ["EMPLOYEE"],
                "type": "SUBJECTIVE",
                "manager_question_type": None,
                "question": (
                    "Think of a timeeeee when you told a story at work that you "
                    "feel best represents who you are—either personally or professionally.\n"
                    "Briefly describe the moment, who the audience was, and why that story mattered to you?"
                ),
                "manager_question": None,
                "options": None,
                "manager_options": None,
                "description": None,
                "ranking": None,
                "manager_ranking": None,
                "sl_no": 110,
                "assessment": None
            }
        ],
        "question_ids_to_delete": [q_delete_id]
    }

    r_bulk = requests.post(bulk_url, json=bulk_body, headers=HEADERS)
    assert r_bulk.status_code == 200, r_bulk.text

    results = r_bulk.json()
    updated = next(q for q in results if q["id"] == q_update_id)
    created = next(q for q in results if q["id"] != q_update_id)

    assert updated["capabilities_label"] == "Powerful Storyteller V3 Label"
    assert updated["capabilities"] == "Powerful Storyteller V3"
    assert updated["status"] == "PUBLISHED"

    assert created["capabilities_label"] == "Technical Skills"
    assert created["capabilities"] == "Technical Skills"

    rd = requests.get(get_q(q_delete_id), headers=HEADERS)
    assert rd.status_code in (403, 404)

def test_create_assessment_fails_with_empty_capabilities():
    body = {
        "capabilities":    [], 
        "name":            "Test with empty capabilities",
        "show_onboarding": False,
        "assessment_type": "EMPLOYEE"
    }
    
    r_create = requests.post(ASSESS_URL, json=body, headers=HEADERS)
    
    assert r_create.status_code == 404

def test_arrange_subcapabilities_sequence(created_assessment):
    base_url = f"{ASSESS_URL}/{created_assessment}"
    create_q_url = f"{base_url}/question"
    arrange_url = f"{base_url}/success-capabilities/update-sequence"

    q1_body = {
        "capabilities": "First Cap", "sub_capability": "A", "capabilities_label": "First Cap Label",
        "type": "OBJECTIVE_SINGLE", "question": "Q1", "options": [{"value": "A", "input_required": False}],
        "ranking": [1], "sl_no": 1, "capabilities_sl_no": 1, "manager_question_type": "OBJECTIVE_SINGLE",
        "manager_question": "Manager Q1", "manager_options": [{"value": "A", "input_required": False}], "manager_ranking": [1]
    }
    q2_body = {
        "capabilities": "Second Cap", "sub_capability": "B", "capabilities_label": "Second Cap Label",
        "type": "OBJECTIVE_SINGLE", "question": "Q2", "options": [{"value": "B", "input_required": False}],
        "ranking": [1], "sl_no": 2, "capabilities_sl_no": 2, "manager_question_type": "OBJECTIVE_SINGLE",
        "manager_question": "Manager Q2", "manager_options": [{"value": "B", "input_required": False}], "manager_ranking": [1]
    }
    requests.post(create_q_url, json=q1_body, headers=HEADERS).raise_for_status()
    requests.post(create_q_url, json=q2_body, headers=HEADERS).raise_for_status()
    
    list_url = f"{base_url}/questions"
    r_list = requests.get(list_url, headers=HEADERS)
    r_list.raise_for_status()
    questions = r_list.json()

    all_capabilities = list(dict.fromkeys(q['capabilities'] for q in questions))

    new_sequence_body = list(reversed(all_capabilities))

    r_arrange = requests.post(arrange_url, json=new_sequence_body, headers=HEADERS)
    assert r_arrange.status_code == 200, r_arrange.text

    r_final_list = requests.get(list_url, headers=HEADERS)
    final_questions = r_final_list.json()
    final_capabilities_order = list(dict.fromkeys(q['capabilities'] for q in final_questions))

    assert final_capabilities_order == new_sequence_body
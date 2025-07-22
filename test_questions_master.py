import requests
import pytest
import json

from config import API_HOST, HEADERS

QUESTION_URL       = f"{API_HOST}/backend/v1/question"
QUESTIONS_LIST_URL = f"{API_HOST}/backend/v1/questions"

@pytest.fixture(scope="module")
def created_question():
    body = {
        "capabilities": "Technical Skills 1",
        "sub_capability": "Java 1",
        "capabilities_label" : "Technical Skills 1 Label",
        "type": "OBJECTIVE_SINGLE",
        "question": "What is your proficiency level in Java?",
        "options": [
            {
                "value": "Beginner",
                "input_required": False
            },
            {
                "value": "Intermediate",
                "input_required": False
            },
            {
                "value": "Advanced",
                "input_required": False
            }
        ],
        "ranking": [
            4,
            3,
            2,
            1
        ],
        "sl_no": 1,
        "capabilities_sl_no": 1,
        "manager_question_type": "OBJECTIVE_SINGLE",
        "manager_question": "Rate the employee's Java proficiency",
        "manager_options": [
            {
                "value": "Beginner",
                "input_required": False
            },
            {
                "value": "Intermediate",
                "input_required": False
            },
            {
                "value": "Advanced",
                "input_required": False
            }
        ],
        "manager_ranking": [
            4,
            3,
            2,
            1
        ]
    }

    response = requests.post(QUESTION_URL, json=body, headers=HEADERS)
    assert response.status_code == 200, f"POST failed: {resp.text}"
    qid = response.json()["id"]
    yield qid

    dr = requests.delete(f"{QUESTION_URL}/{qid}", headers=HEADERS)
    assert dr.status_code == 204

def test_get_question_details(created_question):
    response = requests.get(f"{QUESTION_URL}/{created_question}", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == created_question
    assert "What is your proficiency level in Java?" in data["question"]

def test_list_questions(created_question):
    response = requests.get(QUESTIONS_LIST_URL, headers=HEADERS)
    assert response.status_code == 200
    ids = [q['id'] for q in response.json()]
    assert created_question in ids


def test_delete_question():
    body = {
        "capabilities": "Technical Skills 1",
        "sub_capability": "Java 1",
        "capabilities_label": "Technical Skills 1 Label",
        "type": "OBJECTIVE_SINGLE",
        "question": "Temp delete?",
        "options": [
            {
                "value": "Yes",
                "input_required": False
            },
            {
                "value": "No",
                "input_required": False
            }
        ],
        "ranking": [
            2,
            1
        ],
        "sl_no": 99,
        "capabilities_sl_no": 9,
        "manager_question_type": "OBJECTIVE_SINGLE",
        "manager_question": "Temp manager?",
        "manager_options": [
            {
                "value": "Yes",
                "input_required": False
            },
            {
                "value": "No",
                "input_required": False
            }
        ],
        "manager_ranking": [
            2,
            1
        ]
    }

    response0 = requests.post(QUESTION_URL, json=body, headers=HEADERS)
    assert response0.status_code == 200
    qid = response0.json()["id"]

    response1 = requests.delete(f"{QUESTION_URL}/{qid}", headers=HEADERS)
    assert response1.status_code == 204

    response2 = requests.get(f"{QUESTION_URL}/{qid}", headers=HEADERS)
    assert response2.status_code in (404, 403)
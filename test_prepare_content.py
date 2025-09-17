import requests
import pytest
import io
import time
import random
import string
from openpyxl import load_workbook
from config import API_HOST, ORG_HEADERS as HEADERS, RAPIDAPI_KEY

ASSESS_URL = f"{API_HOST}/backend/v1/assessment"
INBOXES_API = "https://inboxes-com.p.rapidapi.com"
MAILTM_API = "https://api.mail.tm"


INBOXES_API_TOKEN = RAPIDAPI_KEY


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

@pytest.fixture(scope="module")
def mailtm_account():
    r = requests.get(f"{MAILTM_API}/domains")
    assert r.status_code == 200, r.text
    domains = r.json()["hydra:member"]
    assert domains, "No Mail.tm domains available"
    domain = domains[0]["domain"]

    local = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    address = f"{local}@{domain}"
    password = "".join(random.choices(string.ascii_letters + string.digits, k=12))

    r = requests.post(
        f"{MAILTM_API}/accounts",
        json={"address": address, "password": password}
    )
    assert r.status_code == 201, r.text
    account_id = r.json()["id"]

    r = requests.post(
        f"{MAILTM_API}/token",
        json={"address": address, "password": password}
    )
    assert r.status_code == 200, r.text
    token = r.json()["token"]

    print(address)

    yield {
        "address": address,
        "password": password,
        "token": token,
        "account_id": account_id
    }

    requests.delete(
        f"{MAILTM_API}/accounts/{account_id}",
        headers={"Authorization": f"Bearer {token}"}
    )


def test_download_action_item_responses(created_assessment, created_prepare_content):
    url = (
        f"{API_HOST}/backend/v1/assessment/"
        f"{created_assessment}/prepare-content/{created_prepare_content}/responses/export"
    )
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200, r.text

    wb = load_workbook(io.BytesIO(r.content), read_only=True, data_only=True)
    ws = wb.active

    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    assert headers == ['SN', 'Employee Name', 'Completed', 'Q1: A']

    found = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[1] == "E1":
            found = row
            break

    assert found == (1.0, 'E1', 'No', '')

def test_employee_can_view_and_submit_prepare_content(created_assessment, created_prepare_content, created_employee):
    base_url = f"{ASSESS_URL}/{created_assessment}/employee/{created_employee}"

    list_url = f"{base_url}/prepare-contents"
    r_list = requests.get(list_url, headers=HEADERS)
    assert r_list.status_code == 200
    content_ids = [item['id'] for item in r_list.json()['data']]
    assert created_prepare_content in content_ids

    details_url = f"{base_url}/prepare-content/{created_prepare_content}"
    r_details = requests.get(details_url, headers=HEADERS)
    assert r_details.status_code == 200
    assert r_details.json()['data']['id'] == created_prepare_content

    submit_url = f"{details_url}/submit"
    submit_body = {
        "response": [{
            "quiz_id": "0",
            "quiz_type": "SUBJECTIVE",
            "answer": "Employee response to prepare content quiz.",
            "options": []
        }],
        "completed": True
    }
    r_submit = requests.post(submit_url, json=submit_body, headers=HEADERS)
    assert r_submit.status_code == 200, r_submit.text



def test_send_reminder_and_check_inbox(created_assessment, created_prepare_content, mailtm_account):
    create_emp_url = f"{ASSESS_URL}/{created_assessment}/employee"
    employee_email = mailtm_account["address"]

    emp_body = {
        "email": employee_email,
        "name": "Reminder Recipient",
        "position": "Test Position",
        "title": "Test Title",
        "join_date": "2025-01-01",
        "manager": {
            "email": f"reminder.manager@example.com",
            "name": "Reminder Manager"
        }
    }
    
    r_emp = requests.post(create_emp_url, json=emp_body, headers=HEADERS)
    assert r_emp.status_code == 201, r_emp.text # This should now pass
    employee_id = r_emp.json()["data"]["id"]

    reminder_url = f"{ASSESS_URL}/{created_assessment}/prepare-content/{created_prepare_content}/send-reminder"
    reminder_body = { "employee_ids": [employee_id] }
    r_remind = requests.post(reminder_url, json=reminder_body, headers=HEADERS)
    assert r_remind.status_code == 200

    headers = {"Authorization": f"Bearer {mailtm_account['token']}"}
    messages = []
    for _ in range(60): 
        r_mail = requests.get(f"{MAILTM_API}/messages", headers=headers)
        assert r_mail.status_code in (200, 201)
        messages = r_mail.json()["hydra:member"]
        if messages:
            break
        time.sleep(1)

    assert messages, "Reminder email was not received in the inbox"
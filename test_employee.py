import requests
import pytest
import random
import string
import io
import os
from config import API_HOST, ORG_HEADERS as HEADERS

BASE_URL = f"{API_HOST}/backend/v1"

@pytest.fixture(scope="module")
def created_organisation():
    body = {
        "internal_name": f"TestAutoOrg{''.join(random.choices(string.digits, k=4))}",
        "name": "Test Employee Org",
        "colour_theme": "DRIVEN_RED",
        "logo": "comet.jpg"
    }
    url = f"{BASE_URL}/organisation"
    r = requests.post(url, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text
    oid = r.json()["data"]["id"]
    
    yield oid
    
    requests.delete(f"{url}/{oid}", headers=HEADERS)

@pytest.fixture(scope="module")
def created_assessment(created_organisation):
    body = {
        "organisation_id": created_organisation,
        "capabilities": ["TECHNICAL SKILLS 1"],
        "name": "Employee Test Assessment",
        "show_onboarding": False,
        "assessment_type": "EMPLOYEE"
    }
    url = f"{BASE_URL}/assessment"
    r = requests.post(url, json=body, headers=HEADERS)
    assert r.status_code == 200, r.text
    aid = r.json()["data"]["id"]
    
    yield aid
    
    requests.delete(f"{url}/{aid}", headers=HEADERS)

@pytest.fixture(scope="module")
def created_employee(created_assessment):
    rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    employee_email = f"emp+{rand_suffix}@example.com"
    manager_email = f"mgr+{rand_suffix}@example.com"
    
    body = {
        "email": employee_email,
        "name": "Test Employee E1",
        "position": "Analyst",
        "manager": {
            "email": manager_email,
            "name": "Test Manager M1"
        }
    }
    
    url = f"{BASE_URL}/assessment/{created_assessment}/employee"
    r = requests.post(url, json=body, headers=HEADERS)
    assert r.status_code == 201, r.text
    
    data = r.json()["data"]
    employee_id = data["id"]
    employee_code = data["employee_code"]
    manager_id = data["manager"]["id"]
    
    yield {
        "employee_id": employee_id,
        "employee_code": employee_code,
        "manager_id": manager_id
    }
    
    requests.delete(f"{BASE_URL}/employee/{employee_id}", headers=HEADERS)

def test_upload_employee_assessment_file(created_assessment):
    file_path = "copy.xlsx" 

    if not os.path.exists(file_path):
        pytest.fail(f"The required test file was not found at: {file_path}")

    with open(file_path, "rb") as excel_file:
        files = {
            'file': (os.path.basename(file_path), excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        upload_headers = {
            "Authorization": HEADERS["Authorization"]
        }
        
        url = f"{BASE_URL}/assessment/{created_assessment}/employee/upload"
        r = requests.post(url, headers=upload_headers, files=files)
    
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "success"

def test_get_assessment_employees_pagination(created_assessment, created_employee):
    url = f"{BASE_URL}/assessment/{created_assessment}/employees?page=1&size=10"
    r = requests.get(url, headers=HEADERS)
    
    assert r.status_code == 200, r.text
    page = r.json()
    assert page["status"] == 200
    assert page["current_page"] == 1
    
    employee_ids = [emp["id"] for emp in page["data"]]
    assert created_employee["employee_id"] in employee_ids

def test_update_assessment_employee(created_assessment, created_employee):
    employee_id = created_employee["employee_id"]
    url = f"{BASE_URL}/assessment/{created_assessment}/employee/{employee_id}"
    
    update_body = {
        "name": "Updated Test Employee",
        "position": "Senior Analyst",
    }
    
    r_put = requests.put(url, json=update_body, headers=HEADERS)
    assert r_put.status_code == 200, r_put.text
    
    r_get = requests.get(f"{BASE_URL}/employee/{employee_id}", headers=HEADERS)
    assert r_get.status_code == 200, r_get.text
    
    updated_data = r_get.json()["data"]
    assert updated_data["name"] == "Updated Test Employee"
    assert updated_data["position"] == "Senior Analyst"

def test_get_employee_by_code(created_assessment, created_employee):
    employee_code = created_employee["employee_code"]
    url = f"{BASE_URL}/assessment/{created_assessment}/employee/by_code?code={employee_code}"
    r = requests.get(url, headers=HEADERS)
    
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["id"] == created_employee["employee_id"]
    assert data["employee_code"] == employee_code

def test_get_employee_by_id(created_employee):
    employee_id = created_employee["employee_id"]
    url = f"{BASE_URL}/employee/{employee_id}"
    r = requests.get(url, headers=HEADERS)
    
    assert r.status_code == 200, r.text
    assert r.json()["data"]["id"] == employee_id

def test_verify_employee_assessment(created_assessment, created_employee):
    employee_id = created_employee["employee_id"]
    url = f"{BASE_URL}/assessment/{created_assessment}/employee/{employee_id}/verify"
    
    r = requests.post(url, headers={})
    
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "success"

def test_get_employee_assessments(created_employee, created_assessment):
    employee_id = created_employee["employee_id"]
    url = f"{BASE_URL}/employee/{employee_id}/assessments"
    r = requests.get(url, headers={})
    
    assert r.status_code == 200, r.text
    page = r.json()
    
    assessment_ids = [assess["id"] for assess in page["data"]]
    assert created_assessment in assessment_ids

def test_get_manager_subordinates(created_assessment, created_employee):
    manager_id = created_employee["manager_id"]
    url = f"{BASE_URL}/assessment/{created_assessment}/manager/{manager_id}/subordinates"
    r = requests.get(url, headers={})
    
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    
    assert data["id"] == manager_id
    
    subordinate_ids = [sub["id"] for sub in data["subordinates"]]
    assert created_employee["employee_id"] in subordinate_ids


def test_export_employee_data(created_assessment):
    url = f"{BASE_URL}/assessment/{created_assessment}/employee/export"
    
    export_body = {
        "select_all": True
    }
    
    r = requests.post(url, json=export_body, headers=HEADERS)
    assert r.status_code == 200, r.text
    
    assert 'attachment' in r.headers.get('Content-Disposition', '')
    assert len(r.content) > 0


def test_notify_employee(created_assessment, created_employee):
    url = f"{BASE_URL}/assessment/{created_assessment}/employee/share-link"
    
    notify_body = {
        "employee_ids": [created_employee["employee_id"]]
    }
    
    r = requests.post(url, json=notify_body, headers=HEADERS)
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "success"
